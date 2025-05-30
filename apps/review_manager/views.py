from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, View
from django.db.models import Q, Count, Case, When, IntegerField
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import SessionCreateForm, SessionEditForm
from .models import SearchSession, SessionActivity
# Import UserFeedbackMixin after we ensure it's working
try:
    from .mixins import UserFeedbackMixin  # Sprint 5 Task 29
except ImportError:
    # Fallback if mixins aren't ready yet
    class UserFeedbackMixin:
        pass

# Create your views here.

class SessionNavigationMixin:
    """Mixin for smart session navigation"""
    
    def get_session_next_url(self, session):
        """Determine where to send user when they click on a session"""
        # Helper function to safely reverse URLs
        def safe_reverse(url_name, kwargs=None, fallback_url=None, fallback_text="View Details"):
            try:
                from django.urls import reverse
                return reverse(url_name, kwargs=kwargs or {})
            except:
                # If the app doesn't exist yet, return a fallback
                return fallback_url or reverse('review_manager:session_detail', kwargs={'session_id': session.id})
        
        navigation_map = {
            'draft': {
                'url': safe_reverse(
                    'search_strategy:define', 
                    {'session_id': session.id},
                    fallback_url=reverse('review_manager:session_detail', kwargs={'session_id': session.id})
                ),
                'text': 'Complete Search Strategy',
                'icon': 'icon-strategy',
                'help': 'Define your Population, Interest, and Context terms',
                'class': 'btn-primary'
            },
            'strategy_ready': {
                'url': safe_reverse(
                    'serp_execution:execute', 
                    {'session_id': session.id},
                    fallback_url=reverse('review_manager:session_detail', kwargs={'session_id': session.id})
                ),
                'text': 'Execute Searches',
                'icon': 'icon-search',
                'help': 'Run searches across selected databases',
                'class': 'btn-primary'
            },
            'executing': {
                'url': safe_reverse(
                    'serp_execution:status', 
                    {'session_id': session.id},
                    fallback_url=reverse('review_manager:session_detail', kwargs={'session_id': session.id})
                ),
                'text': 'View Progress',
                'icon': 'icon-progress',
                'help': 'Monitor search execution progress',
                'class': 'btn-outline-secondary'
            },
            'processing': {
                'url': safe_reverse(
                    'serp_execution:status', 
                    {'session_id': session.id},
                    fallback_url=reverse('review_manager:session_detail', kwargs={'session_id': session.id})
                ),
                'text': 'Processing Results',
                'icon': 'icon-processing',
                'help': 'Results are being processed',
                'class': 'btn-outline-secondary'
            },
            'ready_for_review': {
                'url': safe_reverse(
                    'review_results:overview', 
                    {'session_id': session.id},
                    fallback_url=reverse('review_manager:session_detail', kwargs={'session_id': session.id})
                ),
                'text': 'Start Review',
                'icon': 'icon-review',
                'help': f'{self.get_session_stats(session).get("processed_results_count", 0)} results ready for review',
                'class': 'btn-primary'
            },
            'in_review': {
                'url': safe_reverse(
                    'review_results:overview', 
                    {'session_id': session.id},
                    fallback_url=reverse('review_manager:session_detail', kwargs={'session_id': session.id})
                ),
                'text': 'Continue Review',
                'icon': 'icon-continue',
                'help': f'{self.get_session_stats(session).get("reviewed_results_count", 0)} of {self.get_session_stats(session).get("processed_results_count", 0)} reviewed',
                'class': 'btn-primary'
            },
            'completed': {
                'url': safe_reverse(
                    'reporting:summary', 
                    {'session_id': session.id},
                    fallback_url=reverse('review_manager:session_detail', kwargs={'session_id': session.id})
                ),
                'text': 'View Report',
                'icon': 'icon-report',
                'help': 'Access final report and export options',
                'class': 'btn-outline-secondary'
            },
            'failed': {
                'url': reverse('review_manager:session_detail', kwargs={'session_id': session.id}),
                'text': 'View Error Details',
                'icon': 'icon-error',
                'help': 'See what went wrong and recovery options',
                'class': 'btn-outline-danger'
            },
            'archived': {
                'url': safe_reverse(
                    'reporting:summary', 
                    {'session_id': session.id},
                    fallback_url=reverse('review_manager:session_detail', kwargs={'session_id': session.id})
                ),
                'text': 'View Archived Report',
                'icon': 'icon-archive',
                'help': 'Access archived review report',
                'class': 'btn-outline-secondary'
            },
        }
        
        return navigation_map.get(
            session.status, 
            {
                'url': reverse('review_manager:session_detail', kwargs={'session_id': session.id}),
                'text': 'View Details',
                'icon': 'icon-info',
                'help': 'View session information',
                'class': 'btn-outline-secondary'
            }
        )
    
    def get_session_stats(self, session):
        """Get basic stats for a session - placeholder for now"""
        # This would be expanded when other apps are implemented
        return {
            'query_count': 0,
            'execution_count': 0,
            'processed_results_count': 0,
            'reviewed_results_count': 0,
        }


class DashboardView(LoginRequiredMixin, SessionNavigationMixin, UserFeedbackMixin, ListView):
    """Enhanced dashboard view with advanced filtering - Sprint 5 Task 25"""
    model = SearchSession
    template_name = 'review_manager/dashboard.html'
    context_object_name = 'sessions'
    paginate_by = 12  # 4x3 grid on desktop
    
    def get_queryset(self):
        # Only show sessions for the current user
        queryset = SearchSession.objects.filter(
            created_by=self.request.user
        ).select_related('created_by')
        
        # Apply status filter
        status_filter = self.request.GET.get('status', 'all')
        if status_filter != 'all':
            if status_filter == 'active':
                queryset = queryset.exclude(
                    status__in=['completed', 'archived', 'failed']
                )
            else:
                queryset = queryset.filter(status=status_filter)
        
        # Apply search filter
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        # Apply date range filter - Sprint 5 Enhancement
        date_filter = self.request.GET.get('date_range', 'all')
        if date_filter != 'all':
            now = timezone.now()
            if date_filter == 'today':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(created_at__gte=start_date)
            elif date_filter == 'week':
                start_date = now - timedelta(days=7)
                queryset = queryset.filter(created_at__gte=start_date)
            elif date_filter == 'month':
                start_date = now - timedelta(days=30)
                queryset = queryset.filter(created_at__gte=start_date)
            elif date_filter == 'year':
                start_date = now - timedelta(days=365)
                queryset = queryset.filter(created_at__gte=start_date)
        
        # Apply sorting - Sprint 5 Enhancement
        sort_option = self.request.GET.get('sort', 'status')
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
        
        # Calculate enhanced stats - Sprint 5
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
        
        context.update({
            'total_sessions': all_sessions.count(),
            'active_sessions': active_sessions.count(),
            'completed_sessions': all_sessions.filter(status='completed').count(),
            'current_filter': self.request.GET.get('status', 'all'),
            'search_query': self.request.GET.get('q', ''),
            'current_date_filter': self.request.GET.get('date_range', 'all'),
            'current_sort': self.request.GET.get('sort', 'status'),
            'status_choices': SearchSession.Status.choices,
            **status_counts,
        })
        
        # Add navigation info for each session
        for session in context['sessions']:
            session.nav_info = self.get_session_next_url(session)
        
        return context


class SessionDetailView(LoginRequiredMixin, UserPassesTestMixin, SessionNavigationMixin, DetailView):
    """Detailed view of a single session"""
    model = SearchSession
    template_name = 'review_manager/session_detail.html'
    context_object_name = 'session'
    pk_url_kwarg = 'session_id'
    
    def test_func(self):
        return self.get_object().created_by == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        
        # Get navigation info
        nav_info = self.get_session_next_url(session)
        
        # Get recent activity
        recent_activities = SessionActivity.objects.filter(
            session=session
        ).order_by('-timestamp')[:5]
        
        # Get detailed statistics
        stats = self.get_session_stats(session)
        
        # Status explanation
        status_explanations = {
            'draft': 'Your session is created but needs a search strategy.',
            'strategy_ready': 'Your search strategy is defined. Ready to execute searches.',
            'executing': 'Searches are currently running across selected databases.',
            'processing': 'Search results are being processed and deduplicated.',
            'ready_for_review': f'{stats["processed_results_count"]} results are ready for your review.',
            'in_review': f'You have reviewed {stats["reviewed_results_count"]} of {stats["processed_results_count"]} results.',
            'completed': 'Your review is complete and ready for reporting.',
            'failed': 'An error occurred. Check the error details for recovery options.',
            'archived': 'This session has been archived but remains accessible.',
        }
        
        context.update({
            'nav_info': nav_info,
            'recent_activities': recent_activities,
            'stats': stats,
            'status_explanation': status_explanations.get(session.status, ''),
            'can_delete': session.status == 'draft',
            'can_archive': session.status == 'completed',
            'can_duplicate': session.status != 'draft',
        })
        
        return context


class SessionClickView(LoginRequiredMixin, UserPassesTestMixin, SessionNavigationMixin, View):
    """Handle session card clicks for smart navigation"""
    
    def get_object(self):
        return get_object_or_404(SearchSession, pk=self.kwargs['session_id'])
    
    def test_func(self):
        return self.get_object().created_by == self.request.user
    
    def get(self, request, session_id):
        session = self.get_object()
        nav_info = self.get_session_next_url(session)
        return redirect(nav_info['url'])


@login_required
def session_create_view(request):
    """Create a new session with two-step workflow"""
    if request.method == 'POST':
        form = SessionCreateForm(request.POST)
        if form.is_valid():
            new_session = form.save(user=request.user)
            messages.success(
                request, 
                f'Review session "{new_session.title}" created successfully. Please define your search strategy.'
            )
            # Try to redirect to search strategy definition, fallback to session detail
            try:
                return redirect(reverse('search_strategy:define', kwargs={'session_id': new_session.id}))
            except:
                # Fallback to session detail if search_strategy app not ready
                messages.info(
                    request,
                    'Search Strategy app not yet available. You can view your session details for now.'
                )
                return redirect(reverse('review_manager:session_detail', kwargs={'session_id': new_session.id}))
    else:
        form = SessionCreateForm()
    return render(request, 'review_manager/session_create.html', {'form': form})


class SessionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit session title and description only"""
    model = SearchSession
    form_class = SessionEditForm
    template_name = 'review_manager/session_edit.html'
    pk_url_kwarg = 'session_id'
    
    def test_func(self):
        session = self.get_object()
        return session.created_by == self.request.user
    
    def form_valid(self, form):
        # Pass user to the form for activity logging
        form.save(user=self.request.user)
        messages.success(
            self.request, 
            f'Session "{self.object.title}" has been updated successfully.'
        )
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('review_manager:session_detail', 
                      kwargs={'session_id': self.object.id})


class SessionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete draft sessions only"""
    model = SearchSession
    template_name = 'review_manager/session_confirm_delete.html'
    pk_url_kwarg = 'session_id'
    success_url = reverse_lazy('review_manager:dashboard')
    
    def test_func(self):
        session = self.get_object()
        return (session.created_by == self.request.user and 
                session.status == 'draft')
    
    def delete(self, request, *args, **kwargs):
        session_title = self.get_object().title
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request, 
            f'Session "{session_title}" has been deleted.'
        )
        return response


class DuplicateSessionView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Create a copy of an existing session"""
    
    def get_object(self):
        return get_object_or_404(SearchSession, pk=self.kwargs['session_id'])
    
    def test_func(self):
        session = self.get_object()
        return session.created_by == self.request.user
    
    def post(self, request, session_id):
        original = self.get_object()
        
        # Create duplicate
        duplicate = SearchSession.objects.create(
            title=f"{original.title} (Copy)",
            description=original.description,
            created_by=request.user,
            status='draft'
        )
        
        # Log the duplication
        SessionActivity.objects.create(
            session=duplicate,
            action=SessionActivity.ActivityType.CREATED,
            user=request.user,
            description=f"Session duplicated from '{original.title}'"
        )
        
        messages.success(
            request,
            f'Session duplicated successfully. You can now edit "{duplicate.title}".'
        )
        
        # Redirect to edit the duplicate
        return redirect('review_manager:edit_session', session_id=duplicate.id)


# AJAX Views for enhanced interactivity

@login_required
def session_stats_ajax(request, session_id):
    """Return session statistics as JSON"""
    session = get_object_or_404(SearchSession, pk=session_id, created_by=request.user)
    
    # This will be expanded when other apps are implemented
    stats = {
        'id': session.id,
        'status': session.status,
        'status_display': session.get_status_display(),
        'query_count': 0,
        'execution_count': 0,
        'processed_results_count': 0,
        'reviewed_results_count': 0,
        'updated_at': session.updated_at.isoformat(),
    }
    
    return JsonResponse(stats)


@require_POST
@login_required
def archive_session_ajax(request, session_id):
    """Archive a completed session via AJAX"""
    session = get_object_or_404(SearchSession, pk=session_id, created_by=request.user)
    
    if session.status != 'completed':
        return JsonResponse({'error': 'Only completed sessions can be archived'}, status=400)
    
    session.status = 'archived'
    session.save()
    
    # Log the action
    SessionActivity.objects.create(
        session=session,
        action=SessionActivity.ActivityType.STATUS_CHANGED,
        user=request.user,
        description=f"Session archived by {request.user.username}",
        old_status='completed',
        new_status='archived'
    )
    
    return JsonResponse({
        'success': True,
        'message': f'Session "{session.title}" has been archived.',
        'new_status': 'archived',
        'new_status_display': 'Archived'
    })
