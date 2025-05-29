from django.urls import path
from . import views

app_name = 'review_manager'

urlpatterns = [
    # Dashboard - Main entry point
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Session CRUD operations
    path('create/', views.session_create_view, name='create_session'),
    path('<int:session_id>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('<int:session_id>/edit/', views.SessionUpdateView.as_view(), name='edit_session'),
    path('<int:session_id>/delete/', views.SessionDeleteView.as_view(), name='delete_session'),
    
    # Session management actions
    path('<int:session_id>/duplicate/', views.DuplicateSessionView.as_view(), name='duplicate_session'),
    path('<int:session_id>/click/', views.SessionClickView.as_view(), name='session_click'),
    
    # AJAX endpoints
    path('api/sessions/<int:session_id>/stats/', views.session_stats_ajax, name='session_stats_ajax'),
    path('api/sessions/<int:session_id>/archive/', views.archive_session_ajax, name='archive_session_ajax'),
]
