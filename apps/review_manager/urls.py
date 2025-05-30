# apps/review_manager/urls.py

"""
URL Configuration for Review Manager App - Sprint 7 Enhanced
Includes real-time status monitoring, notifications, and error recovery endpoints
"""

from django.urls import path
from . import views, views_sprint6, views_sprint7, views_sprint8

app_name = 'review_manager'

urlpatterns = [
    # Core dashboard and session management views
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('create/', views.session_create_view, name='create_session'),
    path('session/<uuid:session_id>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('session/<uuid:session_id>/edit/', views.SessionUpdateView.as_view(), name='edit_session'),
    path('session/<uuid:session_id>/delete/', views.SessionDeleteView.as_view(), name='delete_session'),
    path('session/<uuid:session_id>/duplicate/', views.DuplicateSessionView.as_view(), name='duplicate_session'),
    
    # Sprint 6 Advanced Features
    path('session/<uuid:session_id>/activity-timeline/', views_sprint6.ActivityTimelineView.as_view(), name='activity_timeline'),
    path('session/<uuid:session_id>/status-history/', views_sprint6.StatusHistoryView.as_view(), name='status_history'),
    path('archive-management/', views_sprint6.ArchiveManagementView.as_view(), name='archive_management'),
    path('analytics/', views_sprint6.StatsAnalyticsView.as_view(), name='stats_analytics'),
    path('session/<uuid:session_id>/archive/', views_sprint6.ArchiveSessionView.as_view(), name='archive_session'),
    path('session/<uuid:session_id>/unarchive/', views_sprint6.UnarchiveSessionView.as_view(), name='unarchive_session'),
    path('bulk-archive/', views_sprint6.BulkArchiveView.as_view(), name='bulk_archive'),
    
    # Sprint 6 AJAX Endpoints
    path('ajax/activity-timeline/<uuid:session_id>/', views_sprint6.activity_timeline_ajax, name='activity_timeline_ajax'),
    path('ajax/delete-activity/<uuid:activity_id>/', views_sprint6.delete_activity_ajax, name='delete_activity_ajax'),
    path('ajax/user-stats/', views_sprint6.user_stats_ajax, name='user_stats_ajax'),
    path('ajax/export-session-data/<uuid:session_id>/', views_sprint6.export_session_data_ajax, name='export_session_data_ajax'),
    path('ajax/productivity-chart-data/', views_sprint6.productivity_chart_data_ajax, name='productivity_chart_data_ajax'),
    
    # Sprint 7 Real-time Status Monitoring
    path('api/status-check/', views_sprint7.status_check_api, name='status_check_api'),
    path('api/system-health/', views_sprint7.system_health_check, name='system_health_check'),
    path('api/simulate-progress/', views_sprint7.simulate_progress_update, name='simulate_progress_update'),
    
    # Sprint 7 Notification Management
    path('api/notification-preferences/', views_sprint7.notification_preferences_api, name='notification_preferences_api'),
    path('api/notification-preferences/get/', views_sprint7.notification_preferences_get, name='notification_preferences_get'),
    
    # Sprint 7 Error Recovery
    path('api/error-recovery/', views_sprint7.error_recovery_api, name='error_recovery_api'),
    path('session/<uuid:session_id>/recovery-options/', views_sprint7.get_error_recovery_options, name='get_error_recovery_options'),
    
    # Sprint 8 Secure Views
    path('secure/', views_sprint8.SecureDashboardView.as_view(), name='secure_dashboard'),
    path('secure/create/', views_sprint8.secure_session_create_view, name='secure_create_session'),
    path('secure/session/<uuid:session_id>/', views_sprint8.SecureSessionDetailView.as_view(), name='secure_session_detail'),
    path('secure/session/<uuid:session_id>/edit/', views_sprint8.SecureSessionUpdateView.as_view(), name='secure_edit_session'),
    path('secure/session/<uuid:session_id>/delete/', views_sprint8.SecureSessionDeleteView.as_view(), name='secure_delete_session'),
    
    # Sprint 8 Secure AJAX Endpoints
    path('secure/ajax/session-stats/<uuid:session_id>/', views_sprint8.secure_session_stats_ajax, name='session_stats_ajax'),
    path('secure/ajax/archive-session/<uuid:session_id>/', views_sprint8.secure_archive_session_ajax, name='archive_session_ajax'),
    path('secure/ajax/duplicate-session/<uuid:session_id>/', views_sprint8.secure_duplicate_session_ajax, name='duplicate_session_ajax'),
    path('secure/api/security-status/', views_sprint8.security_status_view, name='security_status'),
]
