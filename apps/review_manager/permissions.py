# apps/review_manager/permissions.py
"""
Permission classes for Review Manager app.
Sprint 8: Security & Testing implementation.
"""

import logging
from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from .models import SearchSession

# Set up logging for permission checks
permission_logger = logging.getLogger('permissions')


class SessionOwnershipMixin(AccessMixin):
    """
    Mixin that verifies the user owns the session.
    Works with class-based views that have session_id in URL.
    """
    permission_denied_message = "You don't have permission to access this session."
    redirect_field_name = None  # Don't use next parameter
    
    def dispatch(self, request, *args, **kwargs):
        # Check login first
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Get session if session_id is provided
        if 'session_id' in kwargs:
            try:
                session = get_object_or_404(SearchSession, pk=kwargs['session_id'])
                
                # Check ownership
                if session.created_by != request.user:
                    permission_logger.warning(
                        f"Permission denied: User {request.user.username} "
                        f"attempted to access session {kwargs['session_id']} "
                        f"owned by {session.created_by.username}"
                    )
                    return self.handle_no_permission()
                
                # Store session on request for convenience
                request.session_obj = session
                
            except SearchSession.DoesNotExist:
                permission_logger.warning(
                    f"Session not found: User {request.user.username} "
                    f"attempted to access non-existent session {kwargs['session_id']}"
                )
                return self.handle_no_permission()
        
        return super().dispatch(request, *args, **kwargs)
    
    def handle_no_permission(self):
        """Handle permission denied with appropriate response."""
        # For AJAX requests, return JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': 'Permission denied',
                'message': self.permission_denied_message
            }, status=403)
        
        # Add error message for regular requests (only if messages framework is available)
        if self.request.user.is_authenticated:
            try:
                messages.error(self.request, self.permission_denied_message)
            except Exception:
                # Messages framework not available (e.g., in tests)
                pass
            return redirect('review_manager:dashboard')
        else:
            # Redirect to login if not authenticated
            return super().handle_no_permission()


class SessionStatusPermissionMixin(SessionOwnershipMixin):
    """
    Mixin that checks session status requirements.
    Inherits from SessionOwnershipMixin to ensure ownership first.
    """
    required_statuses = None  # Should be set by subclass
    status_error_message = "This action cannot be performed on a session in '{status}' status."
    
    def dispatch(self, request, *args, **kwargs):
        # First check ownership
        response = super().dispatch(request, *args, **kwargs)
        if response.status_code != 200:  # If ownership check failed
            return response
        
        # Check status requirements
        if self.required_statuses and hasattr(request, 'session_obj'):
            session = request.session_obj
            
            if session.status not in self.required_statuses:
                error_msg = self.status_error_message.format(
                    status=session.get_status_display()
                )
                
                permission_logger.info(
                    f"Status requirement failed: User {request.user.username} "
                    f"tried to access {self.__class__.__name__} for session "
                    f"{session.id} in status '{session.status}' "
                    f"(required: {self.required_statuses})"
                )
                
                # Handle AJAX differently
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Invalid status',
                        'message': error_msg,
                        'current_status': session.status,
                        'required_statuses': list(self.required_statuses)
                    }, status=400)
                
                # Add error message (only if messages framework is available)
                try:
                    messages.error(request, error_msg)
                except Exception:
                    # Messages framework not available (e.g., in tests)
                    pass
                
                return redirect('review_manager:session_detail', session_id=session.id)
        
        return super().dispatch(request, *args, **kwargs)


class DraftSessionPermissionMixin(SessionStatusPermissionMixin):
    """Mixin for views that only work with draft sessions."""
    required_statuses = ['draft']
    status_error_message = "This action can only be performed on draft sessions."


class EditableSessionPermissionMixin(SessionStatusPermissionMixin):
    """Mixin for views that work with editable sessions."""
    required_statuses = ['draft', 'strategy_ready']
    status_error_message = "This session cannot be edited in its current status."


class CompletedSessionPermissionMixin(SessionStatusPermissionMixin):
    """Mixin for views that only work with completed sessions."""
    required_statuses = ['completed']
    status_error_message = "This action can only be performed on completed sessions."


class NonArchivedSessionPermissionMixin(SessionOwnershipMixin):
    """Mixin that prevents access to archived sessions."""
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if response.status_code != 200:
            return response
        
        # Check if session is archived
        if hasattr(request, 'session_obj') and request.session_obj.status == 'archived':
            permission_logger.info(
                f"Archived session access denied: User {request.user.username} "
                f"tried to access archived session {request.session_obj.id}"
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Session archived',
                    'message': 'This session has been archived and cannot be modified.'
                }, status=403)
            
            # Add error message (only if messages framework is available)
            try:
                messages.error(request, 'This session has been archived and cannot be modified.')
            except Exception:
                # Messages framework not available (e.g., in tests)
                pass
            
            return redirect('review_manager:session_detail', session_id=request.session_obj.id)
        
        return super().dispatch(request, *args, **kwargs)


class SessionPermission:
    """
    Utility class for checking session permissions programmatically.
    """
    
    @staticmethod
    def can_view(user, session):
        """Check if user can view the session."""
        return session.created_by == user
    
    @staticmethod
    def can_edit(user, session):
        """Check if user can edit the session."""
        return (session.created_by == user and 
                session.status in ['draft', 'strategy_ready'])
    
    @staticmethod
    def can_delete(user, session):
        """Check if user can delete the session."""
        return (session.created_by == user and 
                session.status == 'draft')
    
    @staticmethod
    def can_duplicate(user, session):
        """Check if user can duplicate the session."""
        return (session.created_by == user and 
                session.status != 'draft')
    
    @staticmethod
    def can_archive(user, session):
        """Check if user can archive the session."""
        return (session.created_by == user and 
                session.status == 'completed')
    
    @staticmethod
    def can_unarchive(user, session):
        """Check if user can unarchive the session."""
        return (session.created_by == user and 
                session.status == 'archived')
    
    @staticmethod
    def can_execute_search(user, session):
        """Check if user can execute searches for the session."""
        return (session.created_by == user and 
                session.status == 'strategy_ready')
    
    @staticmethod
    def can_review_results(user, session):
        """Check if user can review results for the session."""
        return (session.created_by == user and 
                session.status in ['ready_for_review', 'in_review'])
    
    @staticmethod
    def get_allowed_actions(user, session):
        """Get a list of actions the user can perform on the session."""
        actions = []
        
        if SessionPermission.can_view(user, session):
            actions.append('view')
        
        if SessionPermission.can_edit(user, session):
            actions.append('edit')
        
        if SessionPermission.can_delete(user, session):
            actions.append('delete')
        
        if SessionPermission.can_duplicate(user, session):
            actions.append('duplicate')
        
        if SessionPermission.can_archive(user, session):
            actions.append('archive')
        
        if SessionPermission.can_unarchive(user, session):
            actions.append('unarchive')
        
        if SessionPermission.can_execute_search(user, session):
            actions.append('execute_search')
        
        if SessionPermission.can_review_results(user, session):
            actions.append('review_results')
        
        return actions


class RateLimitMixin:
    """
    Mixin that provides rate limiting for views.
    """
    rate_limit_key = None
    rate_limit_attempts = 10
    rate_limit_window = 300  # 5 minutes
    
    def dispatch(self, request, *args, **kwargs):
        from django.core.cache import cache
        import time
        
        # Generate rate limit key
        if self.rate_limit_key:
            key = self.rate_limit_key
        else:
            key = f"rate_limit_{request.user.id}_{self.__class__.__name__}"
        
        # Check rate limit
        current_time = int(time.time())
        attempts = cache.get(key, [])
        
        # Clean old attempts
        attempts = [t for t in attempts if current_time - t < self.rate_limit_window]
        
        if len(attempts) >= self.rate_limit_attempts:
            permission_logger.warning(
                f"Rate limit exceeded: User {request.user.username} "
                f"exceeded {self.rate_limit_attempts} attempts for {self.__class__.__name__}"
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many attempts. Please try again later.',
                    'retry_after': self.rate_limit_window
                }, status=429)
            
            # Add error message (only if messages framework is available)
            try:
                messages.error(request, 'Too many attempts. Please try again later.')
            except Exception:
                # Messages framework not available (e.g., in tests)
                pass
            
            return redirect('review_manager:dashboard')
        
        # Record this attempt
        attempts.append(current_time)
        cache.set(key, attempts, self.rate_limit_window)
        
        return super().dispatch(request, *args, **kwargs)


class SecurityAuditMixin:
    """
    Mixin that logs security-relevant actions.
    """
    audit_action = None
    
    def dispatch(self, request, *args, **kwargs):
        # Log the access attempt
        permission_logger.info(
            f"View access: User {request.user.username} accessed "
            f"{self.__class__.__name__} with args {args} kwargs {kwargs}"
        )
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Log successful form submissions."""
        response = super().form_valid(form)
        
        if self.audit_action:
            permission_logger.info(
                f"Audit: User {self.request.user.username} successfully "
                f"performed {self.audit_action}"
            )
        
        return response
