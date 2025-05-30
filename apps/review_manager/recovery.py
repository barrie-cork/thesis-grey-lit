# apps/review_manager/recovery.py

"""
Error Recovery Management System
Provides context-aware error recovery suggestions and handling
"""

from django.urls import reverse
from django.utils import timezone
from typing import Dict, List, Any, Optional


class ErrorRecoveryManager:
    """
    Manages error recovery strategies and suggestions for different error types
    """
    
    # Recovery strategy definitions
    RECOVERY_STRATEGIES = {
        'search_execution_failed': {
            'title': 'Search Execution Error',
            'message': 'Your search execution encountered an error and could not complete.',
            'description': 'This usually happens due to temporary connectivity issues or invalid search parameters.',
            'severity': 'error',
            'suggestions': [
                {
                    'text': 'Retry Search Execution',
                    'description': 'Attempt to run the search again with the same parameters',
                    'action': 'retry_execution',
                    'icon': 'refresh',
                    'button_class': 'btn-primary',
                    'primary': True,
                    'estimated_time': '2-5 minutes'
                },
                {
                    'text': 'Review Search Strategy',
                    'description': 'Check and modify your search terms and parameters',
                    'action': 'edit_strategy',
                    'icon': 'edit',
                    'button_class': 'btn-secondary',
                    'estimated_time': '5-10 minutes'
                },
                {
                    'text': 'Contact Support',
                    'description': 'Get help from our support team',
                    'action': 'contact_support',
                    'icon': 'help-circle',
                    'button_class': 'btn-outline-secondary',
                    'estimated_time': '1-2 hours'
                }
            ]
        },
        
        'processing_timeout': {
            'title': 'Processing Timeout',
            'message': 'Result processing took longer than expected and was stopped.',
            'description': 'This can happen with large result sets. You can resume processing or use batch mode.',
            'severity': 'warning',
            'suggestions': [
                {
                    'text': 'Resume Processing',
                    'description': 'Continue processing from where it left off',
                    'action': 'resume_processing',
                    'icon': 'play',
                    'button_class': 'btn-primary',
                    'primary': True,
                    'estimated_time': '5-15 minutes'
                },
                {
                    'text': 'Enable Batch Processing',
                    'description': 'Process results in smaller, more manageable chunks',
                    'action': 'batch_processing',
                    'icon': 'layers',
                    'button_class': 'btn-secondary',
                    'estimated_time': '10-30 minutes'
                },
                {
                    'text': 'Reduce Result Set',
                    'description': 'Modify search parameters to get fewer results',
                    'action': 'reduce_results',
                    'icon': 'filter',
                    'button_class': 'btn-outline-secondary',
                    'estimated_time': '5-10 minutes'
                }
            ]
        },
        
        'database_connection_error': {
            'title': 'Database Connection Error',
            'message': 'Unable to connect to the database.',
            'description': 'This is typically a temporary issue. Please wait a moment and try again.',
            'severity': 'error',
            'suggestions': [
                {
                    'text': 'Retry Operation',
                    'description': 'Wait a moment and try the operation again',
                    'action': 'retry_operation',
                    'icon': 'refresh',
                    'button_class': 'btn-primary',
                    'primary': True,
                    'estimated_time': '1-2 minutes'
                },
                {
                    'text': 'Check System Status',
                    'description': 'View current system status and known issues',
                    'action': 'check_status',
                    'icon': 'activity',
                    'button_class': 'btn-secondary',
                    'estimated_time': '1 minute'
                }
            ]
        },
        
        'permission_denied': {
            'title': 'Permission Denied',
            'message': 'You do not have permission to perform this action.',
            'description': 'Your account may not have the necessary permissions for this operation.',
            'severity': 'warning',
            'suggestions': [
                {
                    'text': 'Check Account Status',
                    'description': 'Review your account permissions and status',
                    'action': 'check_account',
                    'icon': 'user',
                    'button_class': 'btn-primary',
                    'primary': True,
                    'estimated_time': '2-3 minutes'
                },
                {
                    'text': 'Contact Administrator',
                    'description': 'Request permission from your system administrator',
                    'action': 'contact_admin',
                    'icon': 'shield',
                    'button_class': 'btn-secondary',
                    'estimated_time': '1-24 hours'
                }
            ]
        },
        
        'rate_limit_exceeded': {
            'title': 'Rate Limit Exceeded',
            'message': 'Too many requests have been made in a short time period.',
            'description': 'Please wait before trying again to avoid overloading the system.',
            'severity': 'warning',
            'suggestions': [
                {
                    'text': 'Wait and Retry',
                    'description': 'Wait a few minutes before attempting the operation again',
                    'action': 'wait_retry',
                    'icon': 'clock',
                    'button_class': 'btn-primary',
                    'primary': True,
                    'estimated_time': '5-10 minutes'
                },
                {
                    'text': 'Schedule for Later',
                    'description': 'Schedule the operation to run at a less busy time',
                    'action': 'schedule_later',
                    'icon': 'calendar',
                    'button_class': 'btn-secondary',
                    'estimated_time': '1-2 hours'
                }
            ]
        },
        
        'invalid_search_parameters': {
            'title': 'Invalid Search Parameters',
            'message': 'The search parameters provided are invalid or incomplete.',
            'description': 'Please review and correct your search strategy before proceeding.',
            'severity': 'warning',
            'suggestions': [
                {
                    'text': 'Edit Search Strategy',
                    'description': 'Review and modify your Population, Interest, and Context terms',
                    'action': 'edit_strategy',
                    'icon': 'edit',
                    'button_class': 'btn-primary',
                    'primary': True,
                    'estimated_time': '5-10 minutes'
                },
                {
                    'text': 'Use Template',
                    'description': 'Start with a proven search strategy template',
                    'action': 'use_template',
                    'icon': 'file-text',
                    'button_class': 'btn-secondary',
                    'estimated_time': '3-5 minutes'
                },
                {
                    'text': 'Get Help',
                    'description': 'View guidance on creating effective search strategies',
                    'action': 'view_help',
                    'icon': 'help-circle',
                    'button_class': 'btn-outline-secondary',
                    'estimated_time': '10-15 minutes'
                }
            ]
        },
        
        'session_expired': {
            'title': 'Session Expired',
            'message': 'Your session has expired due to inactivity.',
            'description': 'Please log in again to continue working on your review.',
            'severity': 'info',
            'suggestions': [
                {
                    'text': 'Log In Again',
                    'description': 'Sign in to continue where you left off',
                    'action': 'login_redirect',
                    'icon': 'log-in',
                    'button_class': 'btn-primary',
                    'primary': True,
                    'estimated_time': '1-2 minutes'
                },
                {
                    'text': 'Save Work Locally',
                    'description': 'Download any unsaved work before logging in',
                    'action': 'save_local',
                    'icon': 'download',
                    'button_class': 'btn-secondary',
                    'estimated_time': '1 minute'
                }
            ]
        },
        
        'unknown_error': {
            'title': 'Unexpected Error',
            'message': 'An unexpected error occurred.',
            'description': 'We\'re sorry for the inconvenience. Please try again or contact support if the problem persists.',
            'severity': 'error',
            'suggestions': [
                {
                    'text': 'Try Again',
                    'description': 'Attempt the operation again',
                    'action': 'retry_operation',
                    'icon': 'refresh',
                    'button_class': 'btn-primary',
                    'primary': True,
                    'estimated_time': '1-2 minutes'
                },
                {
                    'text': 'Go to Dashboard',
                    'description': 'Return to the main dashboard',
                    'action': 'go_dashboard',
                    'icon': 'home',
                    'button_class': 'btn-secondary',
                    'estimated_time': '1 minute'
                },
                {
                    'text': 'Report Issue',
                    'description': 'Report this error to help us improve the system',
                    'action': 'report_issue',
                    'icon': 'flag',
                    'button_class': 'btn-outline-secondary',
                    'estimated_time': '3-5 minutes'
                }
            ]
        }
    }
    
    @classmethod
    def get_recovery_options(cls, error_type: str, session=None) -> Dict[str, Any]:
        """
        Get recovery options for a specific error type
        
        Args:
            error_type: The type of error that occurred
            session: The SearchSession object (optional, for context)
        
        Returns:
            Dictionary containing recovery options and metadata
        """
        strategy = cls.RECOVERY_STRATEGIES.get(error_type, cls.RECOVERY_STRATEGIES['unknown_error'])
        
        # Create a copy to avoid modifying the original
        recovery_options = {
            'error_type': error_type,
            'title': strategy['title'],
            'message': strategy['message'],
            'description': strategy['description'],
            'severity': strategy['severity'],
            'suggestions': [],
            'session_id': session.id if session else None,
            'timestamp': timezone.now().isoformat(),
            'support_available': True
        }
        
        # Process suggestions and add context-specific information
        for suggestion in strategy['suggestions']:
            processed_suggestion = suggestion.copy()
            
            # Add session-specific context if available
            if session:
                processed_suggestion = cls._add_session_context(processed_suggestion, session, error_type)
            
            recovery_options['suggestions'].append(processed_suggestion)
        
        # Add contextual help based on session state
        if session:
            recovery_options['context'] = cls._get_session_context(session, error_type)
        
        return recovery_options
    
    @classmethod
    def _add_session_context(cls, suggestion: Dict[str, Any], session, error_type: str) -> Dict[str, Any]:
        """
        Add session-specific context to a recovery suggestion
        """
        action = suggestion['action']
        
        # Generate appropriate URLs based on the action
        # Use try-catch to handle missing URL patterns for future apps
        try:
            if action == 'edit_strategy':
                suggestion['url'] = reverse('search_strategy:define', kwargs={'session_id': session.id})
            elif action == 'retry_execution':
                suggestion['url'] = reverse('serp_execution:execute', kwargs={'session_id': session.id})
            elif action == 'go_dashboard':
                suggestion['url'] = reverse('review_manager:dashboard')
            elif action == 'contact_support':
                suggestion['url'] = '#'  # Placeholder for support system
            elif action == 'check_account':
                suggestion['url'] = '#'  # Placeholder for accounts app
        except:
            # Fallback to session detail for missing apps
            suggestion['url'] = reverse('review_manager:session_detail', kwargs={'session_id': session.id})
        
        # Add session-specific information to description
        if action in ['retry_execution', 'resume_processing']:
            suggestion['description'] += f' for "{session.title}"'
        
        return suggestion
    
    @classmethod
    def _get_session_context(cls, session, error_type: str) -> Dict[str, Any]:
        """
        Get additional context information about the session for recovery
        """
        context = {
            'session_title': session.title,
            'session_status': session.status,
            'session_created': session.created_at.isoformat(),
            'session_updated': session.updated_at.isoformat(),
            'has_strategy': False,  # Will be: bool(session.population_terms or session.interest_terms) when Search Strategy app is implemented
            'can_retry': session.status in ['failed', 'draft', 'strategy_ready'],
            'data_preservation': True  # Indicate that user data is safe
        }
        
        # Add error-specific context
        if error_type == 'search_execution_failed':
            context['last_execution_attempt'] = session.updated_at.isoformat()
            context['retry_safe'] = True
        elif error_type == 'processing_timeout':
            context['partial_results_available'] = True
            context['can_resume'] = True
        
        return context
    
    @classmethod
    def get_error_prevention_tips(cls, error_type: str) -> List[str]:
        """
        Get tips to prevent this type of error in the future
        """
        prevention_tips = {
            'search_execution_failed': [
                'Ensure your search terms are properly formatted',
                'Check your internet connection before starting searches',
                'Avoid using too many complex search operators',
                'Test with a smaller set of terms first'
            ],
            'processing_timeout': [
                'Consider using more specific search terms to reduce result sets',
                'Run searches during off-peak hours for better performance',
                'Enable batch processing for large result sets',
                'Break complex searches into multiple smaller searches'
            ],
            'rate_limit_exceeded': [
                'Space out your search executions',
                'Avoid running multiple searches simultaneously',
                'Schedule large operations during off-peak hours',
                'Use batch processing to reduce API calls'
            ],
            'invalid_search_parameters': [
                'Validate your search terms before execution',
                'Use the search strategy preview feature',
                'Start with simpler search terms and add complexity gradually',
                'Refer to the search strategy guide for best practices'
            ]
        }
        
        return prevention_tips.get(error_type, [
            'Save your work frequently',
            'Keep your browser and system up to date',
            'Report any recurring issues to support'
        ])
    
    @classmethod
    def log_recovery_attempt(cls, session, error_type: str, action: str, user, success: bool, details: str = None):
        """
        Log a recovery attempt for analytics and debugging
        """
        from .models import SessionActivity
        
        SessionActivity.objects.create(
            session=session,
            action='recovery_attempt',
            description=f'Recovery attempt: {action} for {error_type}',
            user=user,
            details={
                'error_type': error_type,
                'recovery_action': action,
                'success': success,
                'details': details or '',
                'timestamp': timezone.now().isoformat()
            }
        )
    
    @classmethod
    def get_recovery_success_rate(cls, error_type: str = None) -> Dict[str, Any]:
        """
        Get statistics on recovery success rates
        """
        from .models import SessionActivity
        from django.db.models import Count, Q
        
        query = SessionActivity.objects.filter(
            action='recovery_attempt'
        )
        
        if error_type:
            query = query.filter(details__error_type=error_type)
        
        total_attempts = query.count()
        successful_attempts = query.filter(details__success=True).count()
        
        success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'success_rate': round(success_rate, 1),
            'error_type': error_type or 'all'
        }
