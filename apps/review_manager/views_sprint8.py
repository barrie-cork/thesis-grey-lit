# apps/review_manager/views_sprint8.py
"""
Secure views for Review Manager app - Sprint 8 Implementation.
This module contains security-enhanced versions of views with:
- CSRF protection
- XSS prevention
- Ownership validation
- Audit logging
- Rate limiting
"""

import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, View
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.db.models import Q, Count, Case, When, IntegerField
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

# Import our security components
from .decorators import (
    owns_session, session_status_required, rate_limit,
    audit_action, secure_view, get_client_ip
)
from .permissions import (
    SessionOwnershipMixin, DraftSessionPermissionMixin,
    EditableSessionPermissionMixin, CompletedSessionPermissionMixin,
    SecurityAuditMixin, RateLimitMixin
)
from .forms import SessionCreateForm, SessionEditForm
from .models import SearchSession, SessionActivity, SessionStatusHistory

# Set up logging
security_logger = logging.getLogger('security')
audit_logger = logging.getLogger('audit')


# Secure Dashboard View
@method_decorator([
    login_required,
    csrf_protect,
    never_cache
], name='dispatch')
class SecureDashboardView(SessionOwnershipMixin, SecurityAuditMixin, ListView):
    """
    Security-enhanced dashboard view with XSS prevention and audit logging.
    Sprint 8: Security implementation.
    """
    model = SearchSession
    template_name = 'review_manager/dashboard.html'
    context_object_name = 'sessions'
    paginate_by = 12
    audit_action = 'VIEW_DASHBOARD'
    
    def get_queryset(self):
        # Only show sessions for the current user
        queryset = SearchSession.objects.filter(
            created_by=self.request.user
        ).select_related('created_by')
        
        # Sanitize and validate filter parameters
        status_filter = self.request.GET.get('status', '').strip()
        search_query = self.request.GET.get('q', '').strip()
        date_filter = self.request.GET.get('date_range', '').strip()
        sort_option = self.request.GET.get('sort', '').strip()
        
        # Validate status filter against allowed values
        valid_statuses = [choice[0] for choice in SearchSession.Status.choices] + ['all', 'active']
        if status_filter and status_filter not in valid_statuses:
            security_logger.warning(
                f"Invalid status filter attempted: {status_filter} by user {self.request.user.username}"
            )
            status_filter = 'all'
        
        # Apply status filter
        if status_filter and status_filter != 'all':
            if status_filter == 'active':
                queryset = queryset.exclude(
                    status__in=['completed', 'archived', 'failed']
                )
            else:
                queryset = queryset.filter(status=status_filter)
        
        # Apply search filter with XSS protection
        if search_query:
            # Escape the search query to prevent XSS
            escaped_query = escape(search_query)
            # Limit search query length
            if len(escaped_query) > 100:
                escaped_query = escaped_query[:100]
            
            queryset = queryset.filter(
                Q(title__icontains=escaped_query) | 
                Q(description__icontains=escaped_query)
            )
        
        # Apply date range filter with validation
        valid_date_filters = ['all', 'today', 'week', 'month', 'year']
        if date_filter and date_filter in valid_date_filters and date_filter != 'all':
            now = timezone.now()
            date_mappings = {
                'today': now.replace(hour=0, minute=0, second=0, microsecond=0),
                'week': now - timedelta(days=7),
                'month': now - timedelta(days=30),
                'year': now - timedelta(days=365)
            }
            if date_filter in date_mappings:
                queryset = queryset.filter(created_at__gte=date_mappings[date_filter])
        
        # Apply sorting with validation
        valid_sort_options = ['status', 'created', 'updated', 'title']
        if sort_option not in valid_sort_options:
            sort_option = 'status'
        
        if sort_option == 'created':
            return queryset.order_by('-created_at')
        elif sort_option == 'updated':
            return queryset.order_by('-updated_at')
        elif sort_option == 'title':
            return queryset.order_by('title')
        else:  # Default status-based sorting
            status_order = Case(
                When(status='in_review', then=1),
                When(status='ready_for_review', then=2),
                When(status='processing', then=3),
                When(status='executing', then=4),
                When(status='strategy_ready', then=5),
                When(status='draft', then=6),
                When(status='failed', then=7),
                When(status='completed', then=8),
                When(status='archived', then=9),
                default=10,
                output_field=IntegerField()
            )
            
            return queryset.annotate(
                status_order=status_order
            ).order_by('status_order', '-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_sessions = SearchSession.objects.filter(created_by=self.request.user)
        
        # Calculate stats with optimization
        active_sessions = all_sessions.exclude(
            status__in=['completed', 'archived', 'failed']
        )
        
        # Status counts for quick filter chips
        status_counts = {
            'draft_count': all_sessions.filter(status='draft').count(),
            'in_review_count': all_sessions.filter(status='in_review').count(),
            'completed_count': all_sessions.filter(status='completed').count(),
            'archived_count': all_sessions.filter(status='archived').count(),
        }
        
        # Sanitize filter values for template
        context.update({
            'total_sessions': all_sessions.count(),
            'active_sessions': active_sessions.count(),
            'completed_sessions': all_sessions.filter(status='completed').count(),
            'current_filter': escape(self.request.GET.get('status', 'all')),
            'search_query': escape(self.request.GET.get('q', '')),
            'current_date_filter': escape(self.request.GET.get('date_range', 'all')),
            'current_sort': escape(self.request.GET.get('sort', 'status')),
            'status_choices': SearchSession.Status.choices,
            **status_counts,
        })
        
        return context


# Secure Session Detail View
@method_decorator([
    login_required,
    csrf_protect,
    never_cache
], name='dispatch')
class SecureSessionDetailView(SessionOwnershipMixin, SecurityAuditMixin, DetailView):
    """Security-enhanced session detail view."""
    model = SearchSession
    template_name = 'review_manager/session_detail.html'
    context_object_name = 'session'
    pk_url_kwarg = 'session_id'
    audit_action = 'VIEW_SESSION_DETAIL'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        
        # Get recent activity with pagination
        recent_activities = SessionActivity.objects.filter(
            session=session
        ).order_by('-timestamp')[:10]  # Limit to prevent large queries
        
        # Get status history
        status_history = SessionStatusHistory.objects.filter(
            session=session
        ).order_by('-changed_at')[:5]
        
        context.update({
            'recent_activities': recent_activities,
            'status_history': status_history,
            'can_delete': session.status == 'draft',
            'can_archive': session.status == 'completed',
            'can_duplicate': session.status != 'draft',
            'can_edit': session.status in ['draft', 'strategy_ready'],
        })
        
        return context


# Secure Session Creation
@secure_view(require_csrf=True, never_cache_response=True, log_access=True)
@rate_limit(max_attempts=5, time_window=60)  # Limit session creation
@audit_action('SESSION_CREATED', lambda req, **kw: f"Created new session")
def secure_session_create_view(request):
    """
    Security-enhanced session creation with CSRF protection and rate limiting.
    """
    if request.method == 'POST':
        form = SessionCreateForm(request.POST)
        if form.is_valid():
            try:
                # Validate form data
                title = form.cleaned_data['title']
                description = form.cleaned_data.get('description', '')
                
                # Additional validation
                if len(title) > 200:
                    raise ValidationError("Title too long")
                if len(description) > 2000:
                    raise ValidationError("Description too long")
                
                # Create session
                new_session = form.save(user=request.user)
                
                # Log successful creation
                audit_logger.info(
                    f"Session created: {new_session.id} by user {request.user.username}"
                )
                
                messages.success(
                    request, 
                    f'Review session "{escape(new_session.title)}" created successfully.'
                )
                
                return redirect('review_manager:session_detail', session_id=new_session.id)
                
            except ValidationError as e:
                security_logger.warning(
                    f"Validation error in session creation: {str(e)} "
                    f"by user {request.user.username}"
                )
                messages.error(request, "Invalid input data.")
            except Exception as e:
                security_logger.error(
                    f"Error creating session: {str(e)} by user {request.user.username}"
                )
                messages.error(request, "An error occurred. Please try again.")
        else:
            # Log form validation errors
            security_logger.info(
                f"Form validation failed in session creation by user {request.user.username}: "
                f"{form.errors}"
            )
    else:
        form = SessionCreateForm()
    
    return render(request, 'review_manager/session_create.html', {'form': form})


# Secure Session Update
@method_decorator([
    login_required,
    csrf_protect,
    never_cache
], name='dispatch')
class SecureSessionUpdateView(EditableSessionPermissionMixin, SecurityAuditMixin, UpdateView):
    """Security-enhanced session update view."""
    model = SearchSession
    form_class = SessionEditForm
    template_name = 'review_manager/session_edit.html'
    pk_url_kwarg = 'session_id'
    audit_action = 'SESSION_UPDATED'
    
    def form_valid(self, form):
        # Log the update
        old_title = self.object.title
        old_description = self.object.description
        
        response = super().form_valid(form)
        
        # Log activity
        SessionActivity.log_activity(
            session=self.object,
            action='MODIFIED',
            description=f"Session updated by {self.request.user.username}",
            user=self.request.user,
            details={
                'old_title': old_title,
                'new_title': self.object.title,
                'old_description': old_description,
                'new_description': self.object.description,
                'ip_address': get_client_ip(self.request)
            }
        )
        
        messages.success(
            self.request, 
            f'Session "{escape(self.object.title)}" has been updated successfully.'
        )
        
        return response
    
    def get_success_url(self):
        return reverse('review_manager:session_detail', 
                      kwargs={'session_id': self.object.id})


# Secure Session Deletion
@method_decorator([
    login_required,
    csrf_protect,
    never_cache
], name='dispatch')
class SecureSessionDeleteView(DraftSessionPermissionMixin, SecurityAuditMixin, DeleteView):
    """Security-enhanced session deletion - only for draft sessions."""
    model = SearchSession
    template_name = 'review_manager/session_confirm_delete.html'
    pk_url_kwarg = 'session_id'
    success_url = reverse_lazy('review_manager:dashboard')
    audit_action = 'SESSION_DELETED'
    
    def delete(self, request, *args, **kwargs):
        session = self.get_object()
        session_title = session.title
        session_id = session.id
        
        # Log the deletion before it happens
        audit_logger.info(
            f"Session deletion: {session_id} titled '{session_title}' "
            f"deleted by user {request.user.username}"
        )
        
        response = super().delete(request, *args, **kwargs)
        
        messages.success(
            request, 
            f'Session "{escape(session_title)}" has been deleted.'
        )
        
        return response


# Secure AJAX Views
@login_required
@csrf_protect
@require_POST
@owns_session(log_attempts=True)
@rate_limit(max_attempts=20, time_window=60)
def secure_session_stats_ajax(request, session_id):
    """Security-enhanced AJAX endpoint for session statistics."""
    try:
        session = request.session_obj  # Set by owns_session decorator
        
        # Calculate basic stats
        stats = {
            'id': str(session.id),
            'status': session.status,
            'status_display': session.get_status_display(),
            'query_count': 0,  # Will be populated by other apps
            'execution_count': 0,
            'processed_results_count': 0,
            'reviewed_results_count': 0,
            'updated_at': session.updated_at.isoformat(),
            'can_edit': session.status in ['draft', 'strategy_ready'],
            'can_delete': session.status == 'draft',
            'can_archive': session.status == 'completed',
        }
        
        # Log API access
        audit_logger.debug(
            f"API access: session_stats for {session_id} by {request.user.username}"
        )
        
        return JsonResponse(stats)
        
    except Exception as e:
        security_logger.error(
            f"Error in session_stats_ajax: {str(e)} for user {request.user.username}"
        )
        return JsonResponse({
            'error': 'Internal error',
            'message': 'Unable to fetch session statistics'
        }, status=500)


@login_required
@csrf_protect
@require_POST
@owns_session(log_attempts=True)
@rate_limit(max_attempts=10, time_window=300)
@audit_action('SESSION_ARCHIVED', lambda req, session_id: f"Archived session {session_id}")
def secure_archive_session_ajax(request, session_id):
    """Security-enhanced AJAX endpoint for archiving sessions."""
    try:
        session = request.session_obj
        
        # Validate session can be archived
        if session.status != 'completed':
            return JsonResponse({
                'error': 'Invalid status',
                'message': 'Only completed sessions can be archived'
            }, status=400)
        
        # Archive the session
        old_status = session.status
        session.status = 'archived'
        session.save()
        
        # Log the action
        SessionActivity.log_activity(
            session=session,
            action='STATUS_CHANGED',
            user=request.user,
            description=f"Session archived by {request.user.username}",
            old_status=old_status,
            new_status='archived',
            details={'ip_address': get_client_ip(request)}
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Session "{escape(session.title)}" has been archived.',
            'new_status': 'archived',
            'new_status_display': 'Archived'
        })
        
    except Exception as e:
        security_logger.error(
            f"Error in archive_session_ajax: {str(e)} for user {request.user.username}"
        )
        return JsonResponse({
            'error': 'Internal error',
            'message': 'Unable to archive session'
        }, status=500)


@login_required
@csrf_protect
@require_POST
@owns_session(log_attempts=True)
@rate_limit(max_attempts=3, time_window=60)  # Strict limit for duplication
def secure_duplicate_session_ajax(request, session_id):
    """Security-enhanced AJAX endpoint for duplicating sessions."""
    try:
        original = request.session_obj
        
        # Validate session can be duplicated
        if original.status == 'draft':
            return JsonResponse({
                'error': 'Invalid status',
                'message': 'Draft sessions cannot be duplicated'
            }, status=400)
        
        # Create duplicate with validation
        duplicate_title = f"{original.title} (Copy)"
        if len(duplicate_title) > 200:
            duplicate_title = duplicate_title[:197] + "..."
        
        duplicate = SearchSession.objects.create(
            title=duplicate_title,
            description=original.description,
            created_by=request.user,
            status='draft'
        )
        
        # Log the duplication
        SessionActivity.log_activity(
            session=duplicate,
            action='CREATED',
            user=request.user,
            description=f"Session duplicated from '{original.title}' (ID: {original.id})",
            details={
                'original_session_id': str(original.id),
                'duplication_method': 'ajax',
                'ip_address': get_client_ip(request)
            }
        )
        
        audit_logger.info(
            f"Session duplicated: {original.id} -> {duplicate.id} "
            f"by user {request.user.username}"
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Session duplicated successfully.',
            'new_session_id': str(duplicate.id),
            'new_session_title': escape(duplicate.title),
            'edit_url': reverse('review_manager:edit_session', args=[duplicate.id])
        })
        
    except Exception as e:
        security_logger.error(
            f"Error in duplicate_session_ajax: {str(e)} for user {request.user.username}"
        )
        return JsonResponse({
            'error': 'Internal error',
            'message': 'Unable to duplicate session'
        }, status=500)


# Security monitoring endpoints
@login_required
@csrf_protect
@require_http_methods(['GET'])
@rate_limit(max_attempts=30, time_window=60)
def security_status_view(request):
    """
    Endpoint for monitoring security status and user session health.
    """
    try:
        user_sessions = SearchSession.objects.filter(created_by=request.user)
        
        # Calculate security-relevant statistics
        stats = {
            'total_sessions': user_sessions.count(),
            'active_sessions': user_sessions.exclude(
                status__in=['completed', 'archived', 'failed']
            ).count(),
            'failed_sessions': user_sessions.filter(status='failed').count(),
            'last_activity': None,
            'security_events': 0,  # Could be populated from logs
        }
        
        # Get last activity
        last_activity = SessionActivity.objects.filter(
            user=request.user
        ).order_by('-timestamp').first()
        
        if last_activity:
            stats['last_activity'] = last_activity.timestamp.isoformat()
        
        return JsonResponse(stats)
        
    except Exception as e:
        security_logger.error(
            f"Error in security_status_view: {str(e)} for user {request.user.username}"
        )
        return JsonResponse({
            'error': 'Unable to fetch security status'
        }, status=500)


# Content Security Policy header helper
def add_csp_headers(response):
    """Add Content Security Policy headers to prevent XSS."""
    response['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    response['X-Content-Type-Options'] = 'nosniff'
    response['X-Frame-Options'] = 'DENY'
    response['X-XSS-Protection'] = '1; mode=block'
    return response


# Middleware helper for security headers
class SecurityHeadersMiddleware:
    """Middleware to add security headers to all responses."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        if request.path.startswith('/review/'):
            response = add_csp_headers(response)
        
        return response
