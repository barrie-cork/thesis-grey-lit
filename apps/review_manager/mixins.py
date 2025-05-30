# Sprint 5 Task 29: UserFeedbackMixin for consistent user feedback

from django.contrib import messages
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.utils import timezone


class UserFeedbackMixin:
    """Mixin for consistent user feedback across all Review Manager views"""
    
    # Success messages with context formatting
    success_messages = {
        'create': 'Your review session "{title}" has been created successfully.',
        'update': 'Session "{title}" has been updated.',
        'delete': 'Session "{title}" has been deleted.',
        'duplicate': 'Session duplicated successfully. You can now edit "{title}".',
        'archive': 'Session "{title}" has been archived.',
        'unarchive': 'Session "{title}" has been restored from archive.',
        'status_change': 'Session "{title}" status changed to {status}.',
        'search_complete': 'Found {count} sessions matching your criteria.',
        'filter_applied': 'Showing {count} sessions with current filters.',
    }
    
    # Error messages with recovery suggestions
    error_messages = {
        'permission': "You don't have permission to access this session. <a href='/review/'>Return to dashboard</a>.",
        'not_found': "The requested session could not be found. <a href='/review/'>View all sessions</a>.",
        'invalid_status': "This action cannot be performed on a session in {status} status. <a href='/help/'>View help</a>.",
        'delete_non_draft': "Only draft sessions can be deleted. Try <a href='#'>archiving completed sessions</a> instead.",
        'network_error': "A network error occurred. Please check your connection and try again.",
        'server_error': "A server error occurred. Our team has been notified. Please try again later.",
        'validation_error': "Please check the highlighted fields and try again.",
        'session_locked': "This session is currently being modified by another process. Please wait and try again.",
    }
    
    # Info messages for guidance
    info_messages = {
        'first_session': 'This is your first session! Check out our <a href="/help/getting-started/">getting started guide</a>.',
        'status_explanation': 'Need help understanding session statuses? <a href="/help/status-guide/">View our status guide</a>.',
        'empty_results': 'No sessions match your current filters. Try <a href="#" onclick="clearFilters()">clearing filters</a> or <a href="/review/create/">creating a new session</a>.',
        'archive_info': 'Archived sessions are hidden from the main view but can be accessed anytime.',
        'beta_feature': 'This feature is in beta. <a href="/feedback/">Share your feedback</a> to help us improve.',
    }
    
    # Warning messages for important notifications
    warning_messages = {
        'draft_reminder': 'This session is still in draft. <a href="{strategy_url}">Complete your search strategy</a> to proceed.',
        'failed_session': 'This session failed during execution. <a href="{detail_url}">View error details</a> to recover.',
        'old_session': 'This session was created over 6 months ago. Consider <a href="{duplicate_url}">creating a new session</a> with updated search terms.',
        'quota_warning': 'You are approaching your session limit. <a href="/account/upgrade/">Upgrade your account</a> for unlimited sessions.',
        'unsaved_changes': 'You have unsaved changes. Save your work before leaving this page.',
    }
    
    def add_success_message(self, action, **kwargs):
        """Add a success message with context"""
        message = self.success_messages.get(action, "Action completed successfully.")
        formatted_message = message.format(**kwargs)
        messages.success(self.request, mark_safe(formatted_message))
    
    def add_error_message(self, error_type, **kwargs):
        """Add an error message with recovery suggestions"""
        message = self.error_messages.get(error_type, "An error occurred. Please try again.")
        formatted_message = message.format(**kwargs)
        messages.error(self.request, mark_safe(formatted_message))
    
    def add_info_message(self, info_type, **kwargs):
        """Add an informational message"""
        message = self.info_messages.get(info_type, "Information updated.")
        formatted_message = message.format(**kwargs)
        messages.info(self.request, mark_safe(formatted_message))
    
    def add_warning_message(self, warning_type, **kwargs):
        """Add a warning message"""
        message = self.warning_messages.get(warning_type, "Please review the following.")
        formatted_message = message.format(**kwargs)
        messages.warning(self.request, mark_safe(formatted_message))
    
    def get_context_messages(self):
        """Get all current messages for context"""
        return {
            'has_messages': bool(messages.get_messages(self.request)),
            'message_count': len(messages.get_messages(self.request)),
        }
    
    def handle_ajax_response(self, success=True, message='', data=None, status=200):
        """Standard AJAX response format"""
        response_data = {
            'success': success,
            'message': message,
            'data': data or {},
            'timestamp': timezone.now().isoformat(),
        }
        
        if not success and status == 200:
            status = 400  # Default to 400 for errors
            
        return JsonResponse(response_data, status=status)
    
    def format_validation_errors(self, form):
        """Format form validation errors for user display"""
        error_list = []
        for field, errors in form.errors.items():
            field_label = form.fields[field].label or field.replace('_', ' ').title()
            for error in errors:
                error_list.append(f"{field_label}: {error}")
        
        if error_list:
            error_message = "Please correct the following issues:<br>" + "<br>".join([f"• {error}" for error in error_list])
            return mark_safe(error_message)
        
        return "Please check your input and try again."
    
    def add_contextual_help(self, context):
        """Add contextual help messages based on current state"""
        # Check if user has no sessions
        if context.get('total_sessions', 0) == 0:
            self.add_info_message('first_session')
        
        # Check for failed sessions
        if hasattr(self, 'object') and getattr(self.object, 'status', None) == 'failed':
            self.add_warning_message('failed_session', 
                detail_url=f"/review/{self.object.id}/")
        
        # Check for old draft sessions
        if (hasattr(self, 'object') and 
            getattr(self.object, 'status', None) == 'draft' and
            getattr(self.object, 'created_at', None)):
            
            from datetime import timedelta
            
            if self.object.created_at < timezone.now() - timedelta(days=180):
                self.add_warning_message('old_session',
                    duplicate_url=f"/review/{self.object.id}/duplicate/")
    
    def get_smart_redirect_message(self, action, object_name=''):
        """Get appropriate message based on where user is being redirected"""
        redirect_messages = {
            'dashboard': f"Returning to dashboard. {object_name} saved successfully.",
            'detail': f"Viewing {object_name} details.",
            'edit': f"You can now edit {object_name}.",
            'strategy': "Next step: Define your search strategy.",
            'execution': "Ready to execute your searches.",
            'review': "Time to review your results.",
            'report': "View your completed review report.",
        }
        
        return redirect_messages.get(action, "Navigation successful.")


class AjaxResponseMixin:
    """Mixin for handling AJAX requests with consistent response format"""
    
    def dispatch(self, request, *args, **kwargs):
        """Handle AJAX detection"""
        self.is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Handle successful form submission for AJAX and regular requests"""
        response = super().form_valid(form)
        
        if self.is_ajax:
            return JsonResponse({
                'success': True,
                'message': 'Form submitted successfully.',
                'redirect_url': self.get_success_url(),
                'object_id': getattr(self.object, 'id', None),
            })
        
        return response
    
    def form_invalid(self, form):
        """Handle form validation errors for AJAX and regular requests"""
        if self.is_ajax:
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below.',
                'errors': form.errors,
                'field_errors': {field: errors for field, errors in form.errors.items()},
            }, status=400)
        
        return super().form_invalid(form)


class ContextualHelpMixin:
    """Mixin for adding contextual help and guidance"""
    
    help_topics = {
        'dashboard': {
            'title': 'Dashboard Overview',
            'content': 'This is your control centre for managing literature review sessions.',
            'tips': [
                'Use filters to quickly find specific sessions',
                'Status badges show where each session is in the workflow',
                'Click the main action button to continue where you left off',
            ]
        },
        'create_session': {
            'title': 'Creating a New Session',
            'content': 'Give your review a descriptive title and optional description.',
            'tips': [
                'Choose a title that clearly describes your research topic',
                'The description helps you remember the scope later',
                'You will define search terms in the next step',
            ]
        },
        'session_detail': {
            'title': 'Session Details',
            'content': 'View comprehensive information about your review session.',
            'tips': [
                'Check the status explanation for next steps',
                'Use the action buttons to continue your workflow',
                'Recent activity shows what happened when',
            ]
        },
    }
    
    def get_help_context(self, topic=None):
        """Get contextual help for the current view"""
        if not topic:
            topic = getattr(self, 'help_topic', 'general')
        
        help_data = self.help_topics.get(topic, {
            'title': 'Help',
            'content': 'Get help and guidance for using this feature.',
            'tips': ['Contact support if you need assistance']
        })
        
        return {
            'help_available': True,
            'help_topic': topic,
            'help_title': help_data['title'],
            'help_content': help_data['content'],
            'help_tips': help_data['tips'],
        }
    
    def get_context_data(self, **kwargs):
        """Add help context to template context"""
        context = super().get_context_data(**kwargs)
        context.update(self.get_help_context())
        return context
