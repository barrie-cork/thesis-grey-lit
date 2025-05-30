# apps/review_manager/middleware.py
"""
Security middleware for Review Manager app.
Sprint 8: Security & Testing implementation.
"""

import logging
import time
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

# Set up logging
security_logger = logging.getLogger('security')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    """
    
    def process_response(self, request, response):
        # Add security headers to Review Manager pages
        if request.path.startswith('/review/'):
            # Content Security Policy
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
            
            # Additional security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # HSTS for production
            if not settings.DEBUG:
                response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class SessionChangeTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to track session changes and detect suspicious activity.
    """
    
    def process_request(self, request):
        # Track user session changes for security monitoring
        if request.user.is_authenticated:
            user_id = str(request.user.id)
            session_key = f"user_session_{user_id}"
            
            current_session = request.session.session_key
            stored_session = cache.get(session_key)
            
            if stored_session and stored_session != current_session:
                # Session changed - possible session hijacking
                security_logger.warning(
                    f"Session change detected for user {request.user.username}: "
                    f"Old session {stored_session} -> New session {current_session}"
                )
            
            # Update stored session
            cache.set(session_key, current_session, 3600)  # 1 hour
    
    def process_response(self, request, response):
        # Log any response errors for security monitoring
        if response.status_code >= 400 and request.path.startswith('/review/'):
            security_logger.info(
                f"Error response {response.status_code} for user "
                f"{getattr(request.user, 'username', 'anonymous')} "
                f"on path {request.path}"
            )
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware for application-level rate limiting.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Rate limit configuration
        self.rate_limits = {
            '/review/create/': {'attempts': 5, 'window': 300},  # 5 per 5 minutes
            '/review/ajax/': {'attempts': 30, 'window': 60},    # 30 per minute
            '/review/duplicate/': {'attempts': 3, 'window': 300}, # 3 per 5 minutes
        }
    
    def __call__(self, request):
        # Check rate limits for specific paths
        if request.user.is_authenticated:
            for path_prefix, limits in self.rate_limits.items():
                if request.path.startswith(path_prefix):
                    if self._is_rate_limited(request, path_prefix, limits):
                        return self._rate_limit_response(request)
        
        return self.get_response(request)
    
    def _is_rate_limited(self, request, path_prefix, limits):
        """Check if user has exceeded rate limit for this path."""
        user_id = str(request.user.id)
        key = f"rate_limit_{user_id}_{path_prefix.replace('/', '_')}"
        
        current_time = int(time.time())
        attempts = cache.get(key, [])
        
        # Clean old attempts
        attempts = [t for t in attempts if current_time - t < limits['window']]
        
        if len(attempts) >= limits['attempts']:
            security_logger.warning(
                f"Rate limit exceeded: User {request.user.username} "
                f"exceeded {limits['attempts']} attempts for {path_prefix}"
            )
            return True
        
        # Record this attempt
        attempts.append(current_time)
        cache.set(key, attempts, limits['window'])
        
        return False
    
    def _rate_limit_response(self, request):
        """Return appropriate response for rate limited request."""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Too many attempts. Please try again later.'
            }, status=429)
        
        messages.error(request, 'Too many attempts. Please try again later.')
        return redirect('review_manager:dashboard')


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log security-relevant events.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.sensitive_paths = [
            '/review/create/',
            '/review/edit/',
            '/review/delete/',
            '/review/ajax/'
        ]
    
    def __call__(self, request):
        start_time = time.time()
        
        # Log request for sensitive paths
        if any(request.path.startswith(path) for path in self.sensitive_paths):
            self._log_request(request)
        
        response = self.get_response(request)
        
        # Log response for sensitive paths
        if any(request.path.startswith(path) for path in self.sensitive_paths):
            duration = time.time() - start_time
            self._log_response(request, response, duration)
        
        return response
    
    def _log_request(self, request):
        """Log incoming request details."""
        security_logger.info(
            f"Request: {request.method} {request.path} "
            f"from user {getattr(request.user, 'username', 'anonymous')} "
            f"IP: {self._get_client_ip(request)} "
            f"User-Agent: {request.META.get('HTTP_USER_AGENT', '')[:100]}"
        )
    
    def _log_response(self, request, response, duration):
        """Log response details."""
        security_logger.info(
            f"Response: {response.status_code} for {request.path} "
            f"duration: {duration:.3f}s "
            f"user: {getattr(request.user, 'username', 'anonymous')}"
        )
        
        # Log errors with more detail
        if response.status_code >= 400:
            security_logger.warning(
                f"Error response: {response.status_code} for {request.path} "
                f"user: {getattr(request.user, 'username', 'anonymous')} "
                f"IP: {self._get_client_ip(request)}"
            )
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware to enhance session security.
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Check for session fixation attacks
            self._check_session_fixation(request)
            
            # Update last activity
            self._update_last_activity(request)
            
            # Check for concurrent sessions (if enabled)
            if getattr(settings, 'SINGLE_SESSION_PER_USER', False):
                self._enforce_single_session(request)
    
    def _check_session_fixation(self, request):
        """Check for potential session fixation attacks."""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = self._get_client_ip(request)
        
        # Store user agent and IP in session
        stored_ua = request.session.get('user_agent')
        stored_ip = request.session.get('ip_address')
        
        if stored_ua and stored_ua != user_agent:
            security_logger.warning(
                f"User agent change detected for {request.user.username}: "
                f"'{stored_ua}' -> '{user_agent}'"
            )
        
        if stored_ip and stored_ip != ip_address:
            security_logger.warning(
                f"IP address change detected for {request.user.username}: "
                f"{stored_ip} -> {ip_address}"
            )
        
        # Update stored values
        request.session['user_agent'] = user_agent
        request.session['ip_address'] = ip_address
    
    def _update_last_activity(self, request):
        """Update user's last activity timestamp."""
        cache.set(
            f"last_activity_{request.user.id}",
            int(time.time()),
            3600  # 1 hour
        )
    
    def _enforce_single_session(self, request):
        """Enforce single session per user policy."""
        current_session = request.session.session_key
        stored_session = cache.get(f"active_session_{request.user.id}")
        
        if stored_session and stored_session != current_session:
            # Another session is active - terminate this one
            security_logger.warning(
                f"Multiple sessions detected for {request.user.username}, "
                f"terminating session {current_session}"
            )
            request.session.flush()
            messages.warning(
                request,
                "Your account is being used from another location. "
                "Please log in again."
            )
        else:
            # Store current session as active
            cache.set(
                f"active_session_{request.user.id}",
                current_session,
                3600  # 1 hour
            )
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware for real-time security monitoring and alerting.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_patterns = [
            'script',
            'javascript:',
            'vbscript:',
            'onload=',
            'onerror=',
            'eval(',
            'document.cookie',
            'union select',
            'drop table',
            'insert into'
        ]
    
    def __call__(self, request):
        # Check for suspicious patterns in request
        if self._detect_suspicious_patterns(request):
            self._handle_suspicious_request(request)
        
        response = self.get_response(request)
        
        # Monitor response patterns
        self._monitor_response_patterns(request, response)
        
        return response
    
    def _detect_suspicious_patterns(self, request):
        """Detect suspicious patterns in request data."""
        # Check query parameters
        for key, value in request.GET.items():
            if self._contains_suspicious_pattern(value):
                security_logger.critical(
                    f"Suspicious pattern in GET parameter '{key}': {value[:100]} "
                    f"from user {getattr(request.user, 'username', 'anonymous')} "
                    f"IP: {self._get_client_ip(request)}"
                )
                return True
        
        # Check POST data
        if hasattr(request, 'POST'):
            for key, value in request.POST.items():
                if self._contains_suspicious_pattern(str(value)):
                    security_logger.critical(
                        f"Suspicious pattern in POST parameter '{key}': {str(value)[:100]} "
                        f"from user {getattr(request.user, 'username', 'anonymous')} "
                        f"IP: {self._get_client_ip(request)}"
                    )
                    return True
        
        # Check headers
        for header, value in request.META.items():
            if header.startswith('HTTP_') and self._contains_suspicious_pattern(str(value)):
                security_logger.critical(
                    f"Suspicious pattern in header '{header}': {str(value)[:100]} "
                    f"from user {getattr(request.user, 'username', 'anonymous')} "
                    f"IP: {self._get_client_ip(request)}"
                )
                return True
        
        return False
    
    def _contains_suspicious_pattern(self, text):
        """Check if text contains suspicious patterns."""
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in self.suspicious_patterns)
    
    def _handle_suspicious_request(self, request):
        """Handle detected suspicious request."""
        # Log detailed information
        security_logger.critical(
            f"SECURITY ALERT: Suspicious request detected "
            f"Path: {request.path} "
            f"Method: {request.method} "
            f"User: {getattr(request.user, 'username', 'anonymous')} "
            f"IP: {self._get_client_ip(request)} "
            f"User-Agent: {request.META.get('HTTP_USER_AGENT', '')}"
        )
        
        # Optionally block the user temporarily
        if request.user.is_authenticated:
            cache.set(
                f"security_block_{request.user.id}",
                True,
                300  # 5 minutes
            )
    
    def _monitor_response_patterns(self, request, response):
        """Monitor response patterns for security issues."""
        # Monitor for unusual response times
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            if duration > 5.0:  # More than 5 seconds
                security_logger.warning(
                    f"Slow response detected: {duration:.2f}s for {request.path} "
                    f"user: {getattr(request.user, 'username', 'anonymous')}"
                )
        
        # Monitor for error patterns
        if response.status_code >= 500:
            security_logger.error(
                f"Server error {response.status_code} for {request.path} "
                f"user: {getattr(request.user, 'username', 'anonymous')} "
                f"IP: {self._get_client_ip(request)}"
            )
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
