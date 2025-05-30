# apps/review_manager/views_sprint6.py
"""
Sprint 6: Advanced Features Views

This module contains the advanced views for Sprint 6 implementation:
- Archive Management System
- Statistics Analytics Dashboard  
- Status History Tracking
- Enhanced AJAX endpoints
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, View
from django.db.models import Q, Count, Case, When, IntegerField
from django.db.models.functions import TruncDate, TruncMonth, Extract
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator

from .models import (
    SearchSession, SessionActivity, SessionStatusHistory, 
    SessionArchive, UserSessionStats
)
from .mixins import UserFeedbackMixin
from .signals import SignalUtils


class ActivityTimelineView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Sprint 6 Task 34: Interactive activity timeline for a session.
    Displays comprehensive activity history with filtering and search.
    """
    model = SearchSession
    template_name = 'review_manager/activity_timeline.html'
    context_object_name = 'session'
    pk_url_kwarg = 'session_id'
    
    def test_func(self):
        return self.get_object().created_by == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        
        # Get activities with filtering
        activities_queryset = session.activities.select_related('user').all()
        
        # Apply activity type filter
        activity_filter = self.request.GET.get('activity_type', 'all')
        if activity_filter != 'all':
            activities_queryset = activities_queryset.filter(action=activity_filter)
        
        # Apply date range filter
        date_filter = self.request.GET.get('date_range', 'all')
        if date_filter != 'all':
            now = timezone.now()
            if date_filter == 'today':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                activities_queryset = activities_queryset.filter(timestamp__gte=start_date)
            elif date_filter == 'week':
                start_date = now - timedelta(days=7)
                activities_queryset = activities_queryset.filter(timestamp__gte=start_date)
            elif date_filter == 'month':
                start_date = now - timedelta(days=30)
                activities_queryset = activities_queryset.filter(timestamp__gte=start_date)
        
        # Get paginated activities
        paginator = Paginator(activities_queryset, 20)
        page_number = self.request.GET.get('page')
        activities = paginator.get_page(page_number)
        
        # Get status history for timeline
        status_history = session.status_history.all()[:10]
        
        # Activity statistics
        activity_stats = {
            'total_activities': session.activities.count(),
            'status_changes': session.status_history.count(),
            'recent_activity': session.activities.first(),
            'activity_types_count': dict(
                session.activities.values('action')
                .annotate(count=Count('id'))
                .values_list('action', 'count')
            )
        }
        
        context.update({
            'activities': activities,
            'status_history': status_history,
            'activity_stats': activity_stats,
            'activity_types': [('SYSTEM', 'System'), ('CREATED', 'Created'), ('MODIFIED', 'Modified')],  # Simplified choices
            'current_activity_filter': activity_filter,
            'current_date_filter': date_filter,
        })
        
        return context


class ArchiveManagementView(LoginRequiredMixin, UserFeedbackMixin, ListView):
    """
    Sprint 6 Task 33: Comprehensive archive management view.
    Shows all archived sessions with bulk operations and statistics.
    """
    model = SearchSession
    template_name = 'review_manager/archive_management.html'
    context_object_name = 'archived_sessions'
    paginate_by = 15
    
    def get_queryset(self):
        # Only show archived sessions for the current user
        queryset = SearchSession.objects.filter(
            created_by=self.request.user,
            status='archived'
        ).select_related('created_by').prefetch_related('archive_info')
        
        # Apply search filter
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        # Apply date range filter for archive date
        date_filter = self.request.GET.get('archived_date', 'all')
        if date_filter != 'all':
            now = timezone.now()
            if date_filter == 'week':
                start_date = now - timedelta(days=7)
                queryset = queryset.filter(archive_info__archived_at__gte=start_date)
            elif date_filter == 'month':
                start_date = now - timedelta(days=30)
                queryset = queryset.filter(archive_info__archived_at__gte=start_date)
            elif date_filter == 'year':
                start_date = now - timedelta(days=365)
                queryset = queryset.filter(archive_info__archived_at__gte=start_date)
        
        # Sorting
        sort_option = self.request.GET.get('sort', 'archived_date')
        if sort_option == 'title':
            queryset = queryset.order_by('title')
        elif sort_option == 'completed_date':
            queryset = queryset.order_by('-completed_date')
        else:  # Default: archive date
            queryset = queryset.order_by('-archive_info__archived_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Archive statistics
        all_archived = SearchSession.objects.filter(
            created_by=self.request.user,
            status='archived'
        )
        
        archive_stats = {
            'total_archived': all_archived.count(),
            'archived_this_month': all_archived.filter(
                archive_info__archived_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
            'oldest_archive': all_archived.order_by('archive_info__archived_at').first(),
            'newest_archive': all_archived.order_by('-archive_info__archived_at').first(),
        }
        
        context.update({
            'archive_stats': archive_stats,
            'search_query': self.request.GET.get('q', ''),
            'current_date_filter': self.request.GET.get('archived_date', 'all'),
            'current_sort': self.request.GET.get('sort', 'archived_date'),
        })
        
        return context


class ArchiveSessionView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Sprint 6 Task 33: Archive a completed session with optional reason.
    """
    
    def get_object(self):
        return get_object_or_404(SearchSession, pk=self.kwargs['session_id'])
    
    def test_func(self):
        session = self.get_object()
        return (session.created_by == self.request.user and 
                session.status == 'completed')
    
    def post(self, request, session_id):
        session = self.get_object()
        archive_reason = request.POST.get('reason', '').strip()
        
        # Set context for signal handlers
        SignalUtils.set_change_context(
            session,
            user=request.user,
            reason=f'Manual archive: {archive_reason}' if archive_reason else 'Manual archive',
            archive_reason=archive_reason
        )
        
        # Change status to archived
        session.status = SearchSession.Status.ARCHIVED
        session.save()
        
        messages.success(
            request,
            f'Session "{session.title}" has been archived successfully.'
        )
        
        return redirect('review_manager:dashboard')


class UnarchiveSessionView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Sprint 6 Task 33: Restore a session from archive.
    """
    
    def get_object(self):
        return get_object_or_404(SearchSession, pk=self.kwargs['session_id'])
    
    def test_func(self):
        session = self.get_object()
        return (session.created_by == self.request.user and 
                session.status == 'archived')
    
    def post(self, request, session_id):
        session = self.get_object()
        
        # Set context for signal handlers
        SignalUtils.set_change_context(
            session,
            user=request.user,
            reason='Manual restore from archive'
        )
        
        # Restore to completed status
        session.status = SearchSession.Status.COMPLETED
        session.save()
        
        messages.success(
            request,
            f'Session "{session.title}" has been restored from archive.'
        )
        
        return redirect('review_manager:session_detail', session_id=session.id)


class BulkArchiveView(LoginRequiredMixin, View):
    """
    Sprint 6 Task 33: Bulk archive multiple completed sessions.
    """
    
    def post(self, request):
        session_ids = request.POST.getlist('session_ids')
        if not session_ids:
            messages.error(request, 'No sessions selected for archiving.')
            return redirect('review_manager:dashboard')
        
        # Get sessions that can be archived
        sessions = SearchSession.objects.filter(
            id__in=session_ids,
            created_by=request.user,
            status='completed'
        )
        
        if not sessions.exists():
            messages.error(request, 'No valid sessions found for archiving.')
            return redirect('review_manager:dashboard')
        
        # Archive each session
        archived_count = 0
        for session in sessions:
            SignalUtils.set_change_context(
                session,
                user=request.user,
                reason='Bulk archive operation'
            )
            session.status = SearchSession.Status.ARCHIVED
            session.save()
            archived_count += 1
        
        messages.success(
            request,
            f'Successfully archived {archived_count} session{"s" if archived_count != 1 else ""}.' 
        )
        
        return redirect('review_manager:dashboard')


class StatsAnalyticsView(LoginRequiredMixin, UserFeedbackMixin, ListView):
    """
    Sprint 6 Task 35: Comprehensive statistics and analytics dashboard.
    Provides detailed insights into user productivity and session patterns.
    """
    model = SearchSession
    template_name = 'review_manager/stats_analytics.html'
    context_object_name = 'sessions'
    
    def get_queryset(self):
        return SearchSession.objects.filter(created_by=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        sessions = self.get_queryset()
        
        # Update user statistics
        user_stats = UserSessionStats.update_user_stats(user)
        
        # Session status distribution
        status_distribution = dict(
            sessions.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        
        # Monthly session creation trends (last 12 months)
        monthly_trends = list(
            sessions.filter(
                created_at__gte=timezone.now() - timedelta(days=365)
            )
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        
        # Completion time analysis
        completed_sessions = sessions.filter(
            status__in=['completed', 'archived'],
            completed_date__isnull=False,
            start_date__isnull=False
        )
        
        completion_times = []
        for session in completed_sessions:
            duration = session.completed_date - session.start_date
            completion_times.append({
                'session': session,
                'duration': duration,
                'days': duration.days
            })
        
        # Activity patterns
        activity_by_hour = dict(
            user.session_activities.annotate(
                hour=Extract('timestamp', 'hour')
            )
            .values('hour')
            .annotate(count=Count('id'))
            .values_list('hour', 'count')
        )
        
        activity_by_day = dict(
            user.session_activities.annotate(
                day=Extract('timestamp', 'week_day')
            )
            .values('day')
            .annotate(count=Count('id'))
            .values_list('day', 'count')
        )
        
        # Recent achievements and milestones
        achievements = []
        
        # Check for milestones
        if user_stats.total_sessions >= 10:
            achievements.append({
                'title': 'Session Creator',
                'description': f'Created {user_stats.total_sessions} sessions',
                'icon': 'icon-star',
                'class': 'achievement-bronze'
            })
        
        if user_stats.completed_sessions >= 5:
            achievements.append({
                'title': 'Review Expert',
                'description': f'Completed {user_stats.completed_sessions} reviews',
                'icon': 'icon-trophy',
                'class': 'achievement-gold'
            })
        
        if user_stats.completion_rate >= 80:
            achievements.append({
                'title': 'High Achiever',
                'description': f'{user_stats.completion_rate:.1f}% completion rate',
                'icon': 'icon-medal',
                'class': 'achievement-silver'
            })
        
        # Recommendations for improvement
        recommendations = []
        
        if user_stats.completion_rate < 50:
            recommendations.append({
                'title': 'Improve Completion Rate',
                'description': 'Focus on completing your draft sessions.',
                'action': 'Review your draft sessions',
                'url': reverse('review_manager:dashboard') + '?status=draft'
            })
        
        if user_stats.failed_sessions > 0:
            recommendations.append({
                'title': 'Review Failed Sessions',
                'description': 'Investigate and recover from failed sessions.',
                'action': 'Check failed sessions',
                'url': reverse('review_manager:dashboard') + '?status=failed'
            })
        
        # Time periods for chart filters
        time_periods = [
            ('7', 'Last 7 days'),
            ('30', 'Last 30 days'),
            ('90', 'Last 3 months'),
            ('365', 'Last year'),
            ('all', 'All time')
        ]
        
        context.update({
            'user_stats': user_stats,
            'status_distribution': status_distribution,
            'monthly_trends': monthly_trends,
            'completion_times': completion_times,
            'activity_by_hour': activity_by_hour,
            'activity_by_day': activity_by_day,
            'achievements': achievements,
            'recommendations': recommendations,
            'time_periods': time_periods,
            'current_period': self.request.GET.get('period', '30'),
        })
        
        return context


class StatusHistoryView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Sprint 6 Task 32: Detailed status history for a session.
    Shows comprehensive audit trail of all status changes.
    """
    model = SearchSession
    template_name = 'review_manager/status_history.html'
    context_object_name = 'session'
    pk_url_kwarg = 'session_id'
    
    def test_func(self):
        return self.get_object().created_by == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        
        # Get complete status history
        status_history = session.status_history.select_related('changed_by').all()
        
        # Calculate transition statistics
        transition_stats = {
            'total_changes': status_history.count(),
            'progressions': sum(1 for h in status_history if h.is_progression),
            'regressions': sum(1 for h in status_history if h.is_regression),
            'error_recoveries': sum(1 for h in status_history if h.is_error_recovery),
        }
        
        # Time spent in each status
        time_in_status = {}
        max_duration_seconds = 0
        for history in status_history:
            if history.duration_in_previous_status and history.from_status:
                status = history.from_status
                if status not in time_in_status:
                    time_in_status[status] = timezone.timedelta()
                time_in_status[status] += history.duration_in_previous_status
                max_duration_seconds = max(max_duration_seconds, time_in_status[status].total_seconds())
        
        # Current status duration
        if status_history.exists():
            latest_change = status_history.first()
            current_status_start_time = latest_change.changed_at
            current_status_duration = timezone.now() - latest_change.changed_at
        else:
            current_status_start_time = session.created_at
            current_status_duration = timezone.now() - session.created_at
        
        context.update({
            'status_history': status_history,
            'transition_stats': transition_stats,
            'time_in_status': time_in_status,
            'max_duration_seconds': max_duration_seconds,
            'current_status_duration': current_status_duration,
            'current_status_start_time': current_status_start_time,
        })
        
        return context


# Sprint 6: Enhanced AJAX Views

@login_required
def activity_timeline_ajax(request, session_id):
    """
    Sprint 6: Return activity timeline data as JSON for dynamic updates.
    """
    session = get_object_or_404(SearchSession, pk=session_id, created_by=request.user)
    
    # Get recent activities
    activities = session.activities.select_related('user').all()[:20]
    
    activity_data = []
    for activity in activities:
        activity_data.append({
            'id': activity.id,
            'type': activity.action,
            'type_display': activity.action.replace('_', ' ').title(),
            'description': activity.description,
            'user': activity.user.username,
            'performed_at': activity.timestamp.isoformat(),
            'metadata': activity.details,
        })
    
    return JsonResponse({
        'activities': activity_data,
        'total_count': session.activities.count(),
    })


@require_POST
@login_required
def delete_activity_ajax(request, activity_id):
    """
    Sprint 6: Delete an activity record (admin only or for corrections).
    """
    activity = get_object_or_404(SessionActivity, pk=activity_id)
    session = activity.session
    
    # Check permissions
    if session.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Only allow deletion of certain activity types
    if activity.action not in ['COMMENT', 'MODIFIED']:
        return JsonResponse(
            {'error': 'This activity type cannot be deleted'}, 
            status=400
        )
    
    activity_description = activity.description
    activity.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'Activity "{activity_description}" was deleted.'
    })


@login_required
def user_stats_ajax(request):
    """
    Sprint 6: Return user statistics as JSON for dashboard widgets.
    """
    # Get or update user stats
    user_stats = UserSessionStats.update_user_stats(request.user)
    
    # Get additional real-time stats
    sessions = SearchSession.objects.filter(created_by=request.user)
    
    stats_data = {
        'user_stats': {
            'total_sessions': user_stats.total_sessions,
            'completed_sessions': user_stats.completed_sessions,
            'archived_sessions': user_stats.archived_sessions,
            'failed_sessions': user_stats.failed_sessions,
            'completion_rate': user_stats.completion_rate,
            'productivity_score': user_stats.productivity_score,
            'total_activities': user_stats.total_activities,
        },
        'real_time_stats': {
            'active_sessions': sessions.exclude(
                status__in=['completed', 'archived', 'failed']
            ).count(),
            'sessions_needing_attention': sessions.filter(
                status__in=['draft', 'failed']
            ).count(),
            'sessions_in_review': sessions.filter(
                status='in_review'
            ).count(),
        },
        'updated_at': timezone.now().isoformat(),
    }
    
    return JsonResponse(stats_data)


@require_POST
@login_required
def export_session_data_ajax(request, session_id):
    """
    Sprint 6: Export session data including activity history and statistics.
    """
    session = get_object_or_404(SearchSession, pk=session_id, created_by=request.user)
    
    # Prepare export data
    export_data = {
        'session': {
            'id': session.id,
            'title': session.title,
            'description': session.description,
            'status': session.status,
            'status_display': session.get_status_display(),
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat(),
            'completed_date': session.completed_date.isoformat() if session.completed_date else None,
        },
        'activities': [
            {
                'type': activity.action,
                'type_display': activity.action.replace('_', ' ').title(),
                'description': activity.description,
                'performed_by': activity.user.username,
                'performed_at': activity.timestamp.isoformat(),
                'metadata': activity.details,
            }
            for activity in session.activities.select_related('user').all()
        ],
        'status_history': [
            {
                'from_status': history.from_status,
                'to_status': history.to_status,
                'transition_display': history.get_transition_display(),
                'changed_by': history.changed_by.username,
                'changed_at': history.changed_at.isoformat(),
                'duration_in_previous_status': str(history.duration_in_previous_status) if history.duration_in_previous_status else None,
                'reason': history.reason,
                'is_progression': history.is_progression,
                'is_regression': history.is_regression,
                'is_error_recovery': history.is_error_recovery,
            }
            for history in session.status_history.select_related('changed_by').all()
        ],
        'statistics': session.stats,
        'exported_at': timezone.now().isoformat(),
        'exported_by': request.user.username,
    }
    
    # Log the export activity
    SessionActivity.log_activity(
        session=session,
        action='SYSTEM',
        description=f'Session data exported by {request.user.username}',
        user=request.user,
        details={'export_type': 'full_data'}
    )
    
    return JsonResponse({
        'success': True,
        'data': export_data,
        'filename': f'session_{session.id}_{session.title[:20]}_export.json'
    })


@login_required
def productivity_chart_data_ajax(request):
    """
    Sprint 6: Return productivity chart data for analytics dashboard.
    """
    period_days = int(request.GET.get('period', 30))
    start_date = timezone.now() - timedelta(days=period_days)
    
    sessions = SearchSession.objects.filter(
        created_by=request.user,
        created_at__gte=start_date
    )
    
    # Daily session creation
    daily_sessions = list(
        sessions.annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    
    # Status distribution over time
    status_over_time = {}
    for status, label in SearchSession.Status.choices:
        status_data = list(
            sessions.filter(status=status)
            .annotate(date=TruncDate('updated_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        status_over_time[status] = {
            'label': label,
            'data': status_data
        }
    
    # Completion rate trend
    completion_trend = []
    for i in range(period_days, 0, -1):
        date = timezone.now() - timedelta(days=i)
        total_sessions = sessions.filter(created_at__lte=date).count()
        completed_sessions = sessions.filter(
            created_at__lte=date,
            status__in=['completed', 'archived']
        ).count()
        
        rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        completion_trend.append({
            'date': date.date().isoformat(),
            'rate': round(rate, 1)
        })
    
    return JsonResponse({
        'daily_sessions': daily_sessions,
        'status_over_time': status_over_time,
        'completion_trend': completion_trend,
        'period_days': period_days,
        'generated_at': timezone.now().isoformat(),
    })
