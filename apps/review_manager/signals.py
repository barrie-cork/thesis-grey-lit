# apps/review_manager/signals.py
"""
Sprint 6: Advanced Signal Handlers for Automatic Status Change Tracking

This module implements comprehensive signal handling for the Review Manager app,
providing automatic status change tracking, activity logging, and statistics updates.
"""

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    SearchSession, SessionActivity, SessionStatusHistory, 
    SessionArchive, UserSessionStats
)

User = get_user_model()


class StatusChangeSignalHandler:
    """
    Handles all status change events with comprehensive tracking and validation.
    Sprint 6: Advanced status change signal handling.
    """
    
    # Track previous status for comparison
    _previous_statuses = {}
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @classmethod
    def pre_save_session(cls, sender, instance, **kwargs):
        """
        Pre-save signal to capture the previous status before changes.
        This allows us to track what changed in the post-save signal.
        """
        if instance.pk:  # Only for existing instances
            try:
                previous_instance = SearchSession.objects.get(pk=instance.pk)
                cls._previous_statuses[instance.pk] = {
                    'status': previous_instance.status,
                    'updated_at': previous_instance.updated_at,
                }
            except SearchSession.DoesNotExist:
                # Handle edge case where instance was deleted between calls
                cls._previous_statuses[instance.pk] = None
        else:
            # New instance - no previous status
            cls._previous_statuses[instance.pk] = None
    
    @classmethod
    def post_save_session(cls, sender, instance, created, **kwargs):
        """
        Post-save signal to handle status changes and create activity logs.
        """
        # Get the user who made the change (from middleware or other context)
        user = getattr(instance, '_changed_by', instance.created_by)
        current_time = timezone.now()
        
        if created:
            # New session created
            cls._handle_session_creation(instance, user, current_time)
        else:
            # Existing session updated
            previous_data = cls._previous_statuses.get(instance.pk)
            if previous_data:
                cls._handle_session_update(instance, user, current_time, previous_data)
        
        # Clean up tracking data
        if instance.pk in cls._previous_statuses:
            del cls._previous_statuses[instance.pk]
        
        # Update user statistics
        cls._update_user_statistics(user)
    
    @classmethod
    def _handle_session_creation(cls, instance, user, current_time):
        """Handle new session creation logging"""
        # Create initial status history
        SessionStatusHistory.objects.create(
            session=instance,
            from_status='',  # Empty for initial creation
            to_status=instance.status,
            changed_by=user,
            changed_at=current_time,
            reason='Initial session creation',
            metadata={
                'created': True,
                'initial_status': instance.status,
            }
        )
        
        # Log creation activity
        SessionActivity.log_activity(
            session=instance,
            action='CREATED',
            description=f'Session "{instance.title}" was created',
            user=user,
            details={
                'initial_status': instance.status,
                'title': instance.title,
                'description': instance.description[:100] if instance.description else '',
            }
        )
    
    @classmethod
    def _handle_session_update(cls, instance, user, current_time, previous_data):
        """Handle session updates and status changes"""
        previous_status = previous_data['status']
        previous_updated_at = previous_data['updated_at']
        
        # Check if status changed
        if instance.status != previous_status:
            cls._handle_status_change(
                instance, user, current_time, 
                previous_status, previous_updated_at
            )
        else:
            # Non-status update (title, description, etc.)
            cls._handle_general_update(instance, user, current_time)
    
    @classmethod
    def _handle_status_change(cls, instance, user, current_time, previous_status, previous_updated_at):
        """Handle status change with comprehensive tracking"""
        # Calculate duration in previous status
        duration_in_previous_status = current_time - previous_updated_at
        
        # Create status history record
        status_history = SessionStatusHistory.objects.create(
            session=instance,
            from_status=previous_status,
            to_status=instance.status,
            changed_by=user,
            changed_at=current_time,
            duration_in_previous_status=duration_in_previous_status,
            metadata={
                'duration_seconds': duration_in_previous_status.total_seconds(),
                'auto_transition': getattr(instance, '_auto_transition', False),
                'transition_reason': getattr(instance, '_transition_reason', ''),
            }
        )
        
        # Determine transition type for activity description
        transition_type = cls._get_transition_type(status_history)
        transition_description = cls._get_transition_description(
            previous_status, instance.status, transition_type
        )
        
        # Log status change activity
        SessionActivity.log_activity(
            session=instance,
            action='STATUS_CHANGED',
            description=transition_description,
            user=user,
            old_status=previous_status,
            new_status=instance.status,
            details={
                'transition_type': transition_type,
                'duration_in_previous_status_seconds': duration_in_previous_status.total_seconds(),
                'is_progression': status_history.is_progression,
                'is_regression': status_history.is_regression,
                'is_error_recovery': status_history.is_error_recovery,
            }
        )
        
        # Handle special status transitions
        cls._handle_special_transitions(instance, user, previous_status)
    
    @classmethod
    def _handle_general_update(cls, instance, user, current_time):
        """Handle non-status updates"""
        SessionActivity.log_activity(
            session=instance,
            action='MODIFIED',
            description=f'Session "{instance.title}" was updated',
            user=user,
            details={
                'update_type': 'general',
                'title': instance.title,
            }
        )
    
    @classmethod
    def _get_transition_type(cls, status_history):
        """Determine the type of status transition"""
        if status_history.is_progression:
            return 'progression'
        elif status_history.is_regression:
            return 'regression'
        elif status_history.is_error_recovery:
            return 'error_recovery'
        elif status_history.to_status == 'failed':
            return 'error'
        else:
            return 'lateral'
    
    @classmethod
    def _get_transition_description(cls, from_status, to_status, transition_type):
        """Generate human-readable transition description"""
        status_display_map = dict(SearchSession.Status.choices)
        from_display = status_display_map.get(from_status, from_status)
        to_display = status_display_map.get(to_status, to_status)
        
        if transition_type == 'progression':
            return f'Session progressed from {from_display} to {to_display}'
        elif transition_type == 'regression':
            return f'Session moved back from {from_display} to {to_display}'
        elif transition_type == 'error_recovery':
            return f'Session recovered from error to {to_display}'
        elif transition_type == 'error':
            return f'Session failed while in {from_display} status'
        else:
            return f'Session status changed from {from_display} to {to_display}'
    
    @classmethod
    def _handle_special_transitions(cls, instance, user, previous_status):
        """Handle special status transitions that require additional actions"""
        
        # Handle archiving
        if instance.status == SearchSession.Status.ARCHIVED:
            cls._handle_archiving(instance, user)
        
        # Handle completion
        elif instance.status == SearchSession.Status.COMPLETED and previous_status != SearchSession.Status.COMPLETED:
            cls._handle_completion(instance, user)
        
        # Handle restoration from archive
        elif previous_status == SearchSession.Status.ARCHIVED and instance.status != SearchSession.Status.ARCHIVED:
            cls._handle_archive_restoration(instance, user)
        
        # Handle error states
        elif instance.status == SearchSession.Status.FAILED:
            cls._handle_failure(instance, user, previous_status)
    
    @classmethod
    def _handle_archiving(cls, instance, user):
        """Handle session archiving"""
        # Create or update archive record
        archive_info, created = SessionArchive.objects.get_or_create(
            session=instance,
            defaults={
                'archived_by': user,
                'stats_snapshot': instance.stats,
                'archive_reason': getattr(instance, '_archive_reason', ''),
            }
        )
        
        if not created:
            # Update existing archive record
            archive_info.archived_by = user
            archive_info.archived_at = timezone.now()
            archive_info.stats_snapshot = instance.stats
            archive_info.save()
        
        # Log archiving activity
        SessionActivity.log_activity(
            session=instance,
            action='SYSTEM',
            description=f'Session "{instance.title}" was archived',
            user=user,
            details={
                'action': 'archive',
                'stats_snapshot': instance.stats,
            }
        )
    
    @classmethod
    def _handle_completion(cls, instance, user):
        """Handle session completion"""
        # Update completion timestamp
        if not instance.completed_date:
            instance.completed_date = timezone.now()
            instance.save(update_fields=['completed_date'])
        
        # Log completion activity
        SessionActivity.log_activity(
            session=instance,
            action='REVIEW_COMPLETED',
            description=f'Session "{instance.title}" was completed',
            user=user,
            details={
                'completion_date': instance.completed_date.isoformat(),
                'stats_at_completion': instance.stats,
            }
        )
    
    @classmethod
    def _handle_archive_restoration(cls, instance, user):
        """Handle restoration from archive"""
        try:
            archive_info = instance.archive_info
            archive_info.restored_at = timezone.now()
            archive_info.restored_by = user
            archive_info.save()
            
            # Log restoration activity
            SessionActivity.log_activity(
                session=instance,
                action='SYSTEM',
                description=f'Session "{instance.title}" was restored from archive',
                user=user,
                details={
                    'action': 'restore',
                    'archived_at': archive_info.archived_at.isoformat(),
                    'days_archived': archive_info.days_archived,
                }
            )
        except SessionArchive.DoesNotExist:
            # Create archive record for tracking purposes
            SessionArchive.objects.create(
                session=instance,
                archived_by=user,
                restored_at=timezone.now(),
                restored_by=user,
                stats_snapshot=instance.stats,
            )
    
    @classmethod
    def _handle_failure(cls, instance, user, previous_status):
        """Handle session failure"""
        # Log error activity
        SessionActivity.log_activity(
            session=instance,
            action='ERROR',
            description=f'Session "{instance.title}" failed while in {previous_status} status',
            user=user,
            details={
                'previous_status': previous_status,
                'failure_context': getattr(instance, '_failure_reason', ''),
                'error_details': getattr(instance, '_error_details', {}),
            }
        )
    
    @classmethod
    def _update_user_statistics(cls, user):
        """Update user statistics after session changes"""
        try:
            UserSessionStats.update_user_stats(user)
        except Exception as e:
            # Log error but don't fail the main operation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to update user statistics for {user}: {e}")


# Register signal handlers
@receiver(pre_save, sender=SearchSession)
def pre_save_search_session(sender, instance, **kwargs):
    """Pre-save signal handler for SearchSession"""
    StatusChangeSignalHandler.pre_save_session(sender, instance, **kwargs)


@receiver(post_save, sender=SearchSession)
def post_save_search_session(sender, instance, created, **kwargs):
    """Post-save signal handler for SearchSession"""
    StatusChangeSignalHandler.post_save_session(sender, instance, created, **kwargs)


@receiver(post_delete, sender=SearchSession)
def post_delete_search_session(sender, instance, **kwargs):
    """Post-delete signal handler for SearchSession"""
    # Update user statistics when session is deleted
    if instance.created_by:
        try:
            UserSessionStats.update_user_stats(instance.created_by)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to update user statistics after session deletion: {e}")


# Middleware helper for tracking user changes
class SessionChangeTrackingMiddleware:
    """
    Middleware to track which user is making changes to sessions.
    This allows the signal handlers to properly attribute changes.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Store request in thread-local storage for signal access
        import threading
        if not hasattr(threading.current_thread(), 'request'):
            threading.current_thread().request = request
        
        response = self.get_response(request)
        
        # Clean up
        if hasattr(threading.current_thread(), 'request'):
            delattr(threading.current_thread(), 'request')
        
        return response
    
    @staticmethod
    def get_current_request():
        """Get the current request from thread-local storage"""
        import threading
        return getattr(threading.current_thread(), 'request', None)
    
    @staticmethod
    def get_current_user():
        """Get the current user from the request"""
        request = SessionChangeTrackingMiddleware.get_current_request()
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return request.user
        return None


# Signal handler utilities
class SignalUtils:
    """Utility functions for signal handling"""
    
    @staticmethod
    def set_change_context(instance, user=None, reason=None, auto_transition=False, **metadata):
        """
        Set context information for change tracking.
        This should be called before saving an instance to provide
        additional context to the signal handlers.
        """
        if user:
            instance._changed_by = user
        if reason:
            instance._transition_reason = reason
        if auto_transition:
            instance._auto_transition = True
        
        # Set any additional metadata
        for key, value in metadata.items():
            setattr(instance, f'_{key}', value)
    
    @staticmethod
    def clear_change_context(instance):
        """Clear change context from instance"""
        attrs_to_clear = [
            '_changed_by', '_transition_reason', '_auto_transition',
            '_archive_reason', '_failure_reason', '_error_details'
        ]
        for attr in attrs_to_clear:
            if hasattr(instance, attr):
                delattr(instance, attr)
