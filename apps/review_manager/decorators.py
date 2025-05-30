# apps/review_manager/decorators.py
"""
Security decorators for Review Manager app.
Sprint 8: Security & Testing implementation.
"""

import functools
import logging
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from .models import SearchSession, SessionActivity

# Set up logging for security events
security_logger = logging.getLogger('security')


def owns_session(view_func=None, *, redirect_to='review_manager:dashboard', log_attempts=True):
    """
    Decorator to ensure user owns the session.
    
    Args:
        view_func: The view function to wrap
        redirect_to: URL name to redirect to if permission denied
        log_attempts: Whether to log unauthorized access attempts
    
    Returns:
        Wrapped view function that checks session ownership
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped_view(request, session_id, *args, **kwargs):
            # Get session or 404
            session = get_object_or_404(SearchSession, pk=session_id)
            
            # Check ownership
            if session.created_by != request.user:
                # Log security event
                if log_attempts:
                    security_logger.warning(
                        f"Unauthorized session access attempt: "
                        f"User {request.user.username} (ID: {request.user.id}) "
                        f"tried to access session {session_id} owned by "
                        f"{session.created_by.username} (ID: {session.created_by.id})"
                    )
                
                # Handle AJAX requests differently
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Permission denied',
                        'message': "You don't have permission to access this session."
                    }, status=403)
                
                # Add user-friendly error message (only if messages framework is available)
                try:
                    messages.error(
                        request, 
                        "You don't have permission to access this session."
                    )
                except Exception:
                    # Messages framework not available (e.g., in tests)
                    pass
                
                return redirect(redirect_to)
            
            # Add session to request for convenience
            request.session_obj = session
            return view_func(request, session_id, *args, **kwargs)
        
        return wrapped_view
    
    if view_func is None:
        return decorator
    else:
        return decorator(view_func)


def session_status_required(*required_statuses, redirect_on_fail=True):
    """
    Decorator to ensure session is in one of the required statuses.
    
    Args:
        *required_statuses: Status values that are acceptable
        redirect_on_fail: Whether to redirect or raise PermissionDenied
    
    Usage:
        @session_status_required('draft', 'strategy_ready')
        def edit_session(request, session_id):
            # Only accessible for draft or strategy_ready sessions
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped_view(request, session_id, *args, **kwargs):
            session = get_object_or_404(SearchSession, pk=session_id)
            
            # Check ownership first
            if session.created_by != request.user:
                messages.error(request, "You don't have permission to access this session.")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Permission denied'
                    }, status=403)
                return redirect('review_manager:dashboard')
            
            # Check status requirement
            if session.status not in required_statuses:
                error_msg = (
                    f"This action cannot be performed on a session in "
                    f"'{session.get_status_display()}' status."
                )
                
                # Log the attempt
                security_logger.info(
                    f"Status requirement failed: User {request.user.username} "
                    f"tried to access session {session_id} in status '{session.status}' "
                    f"but required statuses are: {required_statuses}"
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Invalid status',
                        'message': error_msg,
                        'current_status': session.status,
                        'required_statuses': list(required_statuses)
                    }, status=400)
                
                # Add user-friendly error message (only if messages framework is available)
                try:
                    messages.error(request, error_msg)
                except Exception:
                    # Messages framework not available (e.g., in tests)
                    pass
                
                if redirect_on_fail:
                    return redirect('review_manager:session_detail', session_id=session_id)
                else:
                    raise PermissionDenied(error_msg)
            
            # Add session to request
            request.session_obj = session
            return view_func(request, session_id, *args, **kwargs)
        
        return wrapped_view
    return decorator


def rate_limit(max_attempts=10, time_window=300, key_func=None):
    """
    Simple rate limiting decorator to prevent abuse.
    
    Args:
        max_attempts: Maximum number of attempts allowed
        time_window: Time window in seconds
        key_func: Function to generate rate limit key (defaults to user ID)
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            from django.core.cache import cache
            import time
            
            # Generate rate limit key
            if key_func:
                key = key_func(request, *args, **kwargs)
            else:
                key = f"rate_limit_{request.user.id}_{view_func.__name__}"
            
            # Get current attempts
            current_time = int(time.time())
            attempts = cache.get(key, [])
            
            # Clean old attempts
            attempts = [t for t in attempts if current_time - t < time_window]
            
            # Check rate limit
            if len(attempts) >= max_attempts:
                security_logger.warning(
                    f"Rate limit exceeded: User {request.user.username} "
                    f"exceeded {max_attempts} attempts for {view_func.__name__}"
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': 'Too many attempts. Please try again later.',
                        'retry_after': time_window
                    }, status=429)
                
                # Add user-friendly error message (only if messages framework is available)
                try:
                    messages.error(request, 'Too many attempts. Please try again later.')
                except Exception:
                    # Messages framework not available (e.g., in tests)
                    pass
                
                return redirect('review_manager:dashboard')
            
            # Record this attempt
            attempts.append(current_time)
            cache.set(key, attempts, time_window)
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


def audit_action(action_type, description_func=None):
    """
    Decorator to automatically log user actions for audit purposes.
    
    Args:
        action_type: Type of action being performed
        description_func: Function to generate description (optional)
    
    Usage:
        @audit_action('SESSION_DELETED', lambda req, sid: f"Deleted session {sid}")
        def delete_session(request, session_id):
            # Action will be logged automatically
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Execute the view
            response = view_func(request, *args, **kwargs)
            
            # Log the action (only for successful operations)
            if hasattr(response, 'status_code') and 200 <= response.status_code < 400:
                try:
                    # Get session if available
                    session = getattr(request, 'session_obj', None)
                    if not session and 'session_id' in kwargs:
                        session = SearchSession.objects.filter(
                            pk=kwargs['session_id']
                        ).first()
                    
                    # Generate description
                    if description_func:
                        description = description_func(request, *args, **kwargs)
                    else:
                        description = f"User performed {action_type}"
                    
                    # Log to SessionActivity if we have a session
                    if session:
                        SessionActivity.log_activity(
                            session=session,
                            action=action_type,
                            description=description,
                            user=request.user,
                            details={
                                'view_name': view_func.__name__,
                                'args': [str(arg) for arg in args],
                                'kwargs': {k: str(v) for k, v in kwargs.items() if k != 'session_id'},
                                'ip_address': get_client_ip(request),
                                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500]
                            }
                        )
                    
                    # Also log to audit logger
                    security_logger.info(
                        f"Audit: User {request.user.username} performed {action_type}: {description}"
                    )
                
                except Exception as e:
                    # Don't fail the request if logging fails
                    security_logger.error(
                        f"Failed to log audit action {action_type}: {str(e)}"
                    )
            
            return response
        
        return wrapped_view
    return decorator


def secure_view(require_csrf=True, never_cache_response=True, log_access=True):
    """
    Composite decorator that applies multiple security measures.
    
    Args:
        require_csrf: Whether to require CSRF protection
        never_cache_response: Whether to prevent caching
        log_access: Whether to log view access
    """
    def decorator(view_func):
        wrapped = view_func
        
        # Apply CSRF protection
        if require_csrf:
            wrapped = csrf_protect(wrapped)
        
        # Prevent caching
        if never_cache_response:
            wrapped = never_cache(wrapped)
        
        # Log access
        if log_access:
            @functools.wraps(wrapped)
            def logged_view(request, *args, **kwargs):
                security_logger.debug(
                    f"View access: {request.user.username} accessed {view_func.__name__} "
                    f"from IP {get_client_ip(request)}"
                )
                return wrapped(request, *args, **kwargs)
            wrapped = logged_view
        
        return wrapped
    
    return decorator


def get_client_ip(request):
    """
    Get the client's IP address from the request.
    Handles various proxy headers.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Class-based view decorators
class SecureSessionMixin:
    """
    Mixin for class-based views that adds session security checks.
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Check if session_id is in kwargs
        if 'session_id' in kwargs:
            session = get_object_or_404(SearchSession, pk=kwargs['session_id'])
            
            # Check ownership
            if session.created_by != request.user:
                security_logger.warning(
                    f"Unauthorized session access: User {request.user.username} "
                    f"tried to access session {kwargs['session_id']}"
                )
                messages.error(request, "You don't have permission to access this session.")
                return redirect('review_manager:dashboard')
            
            # Add session to request
            request.session_obj = session
        
        return super().dispatch(request, *args, **kwargs)


class AuditMixin:
    """
    Mixin that automatically logs successful operations.
    """
    audit_action_type = None
    audit_description = None
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Log the successful action
        if self.audit_action_type and hasattr(self.request, 'session_obj'):
            description = self.audit_description or f"Performed {self.audit_action_type}"
            SessionActivity.log_activity(
                session=self.request.session_obj,
                action=self.audit_action_type,
                description=description,
                user=self.request.user,
                details={
                    'view_class': self.__class__.__name__,
                    'form_data': {k: v for k, v in form.cleaned_data.items() if 'password' not in k.lower()},
                    'ip_address': get_client_ip(self.request)
                }
            )
        
        return response


# Method decorators for common use cases
secure_session_view = method_decorator([
    login_required,
    csrf_protect,
    never_cache
], name='dispatch')

secure_session_post = method_decorator([
    login_required,
    csrf_protect,
    require_http_methods(['POST']),
    never_cache
], name='dispatch')
