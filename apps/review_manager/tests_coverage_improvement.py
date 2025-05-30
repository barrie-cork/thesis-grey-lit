"""
Sprint 11 - Coverage Improvement Tests
=====================================

This test suite addresses coverage gaps and fixes failing tests to achieve >95% coverage
for the review_manager app core functionality.

Test Categories:
1. Template tag coverage
2. Middleware coverage
3. Signals coverage
4. Permissions coverage
5. Management commands coverage
6. Missing view edge cases
7. Error handling coverage
"""

import json
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from io import StringIO

from apps.review_manager.models import SearchSession, SessionActivity, UserSessionStats
from apps.review_manager.templatetags.review_manager_extras import (
    duration_display, duration_short, status_class, activity_icon,
    transition_arrow, get_item, multiply, format_number, percentage
)
from apps.review_manager.signals import StatusChangeSignalHandler, SignalUtils
from apps.review_manager.middleware import SecurityHeadersMiddleware, SessionChangeTrackingMiddleware
from apps.review_manager.permissions import (
    SessionOwnershipMixin, SessionStatusPermissionMixin,
    SessionPermission, RateLimitMixin
)

User = get_user_model()


class TemplateTagCoverageTests(TestCase):
    """Test template tag functionality comprehensively."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.session = SearchSession.objects.create(
            title="Test Session",
            description="Test description",
            created_by=self.user
        )
    
    def test_duration_display_edge_cases(self):
        """Test duration formatting with various edge cases."""
        # Test invalid input
        self.assertEqual(duration_display("invalid"), "invalid")
        
        # Test zero duration
        self.assertEqual(duration_display(timedelta(0)), "Less than a minute")
        
        # Test seconds only
        self.assertEqual(duration_display(timedelta(seconds=30)), "Less than a minute")
        
        # Test exactly 1 minute
        self.assertEqual(duration_display(timedelta(minutes=1)), "1 minute")
        
        # Test multiple minutes
        self.assertEqual(duration_display(timedelta(minutes=5)), "5 minutes")
        
        # Test exactly 1 hour
        self.assertEqual(duration_display(timedelta(hours=1)), "1 hour")
        
        # Test hours and minutes
        self.assertEqual(duration_display(timedelta(hours=2, minutes=30)), "2 hours and 30 minutes")
        
        # Test exactly 1 day
        self.assertEqual(duration_display(timedelta(days=1)), "1 day")
        
        # Test days and hours
        self.assertEqual(duration_display(timedelta(days=3, hours=4)), "3 days and 4 hours")
    
    def test_duration_short_edge_cases(self):
        """Test short duration formatting."""
        # Test invalid input
        self.assertEqual(duration_short("invalid"), "invalid")
        
        # Test zero duration
        self.assertEqual(duration_short(timedelta(0)), "0s")
        
        # Test seconds only
        self.assertEqual(duration_short(timedelta(seconds=30)), "30s")
        
        # Test minutes only
        self.assertEqual(duration_short(timedelta(minutes=5)), "5m")
        
        # Test hours only
        self.assertEqual(duration_short(timedelta(hours=2)), "2h")
        
        # Test hours and minutes
        self.assertEqual(duration_short(timedelta(hours=2, minutes=30)), "2h 30m")
        
        # Test days only
        self.assertEqual(duration_short(timedelta(days=3)), "3d")
        
        # Test days and hours
        self.assertEqual(duration_short(timedelta(days=3, hours=4)), "3d 4h")
    
    def test_status_class_formatting(self):
        """Test status class formatting."""
        # Test basic status
        self.assertEqual(status_class('draft'), 'status-draft')
        
        # Test status with spaces
        self.assertEqual(status_class('strategy ready'), 'status-strategy_ready')
        
        # Test status with mixed case
        self.assertEqual(status_class('In Review'), 'status-in_review')
    
    def test_activity_icon_all_types(self):
        """Test activity icons for all activity types."""
        test_cases = {
            'CREATED': 'fa-plus-circle',
            'STATUS_CHANGED': 'fa-exchange-alt',
            'MODIFIED': 'fa-edit',
            'STRATEGY_DEFINED': 'fa-strategy',
            'SEARCH_EXECUTED': 'fa-search',
            'RESULTS_PROCESSED': 'fa-cogs',
            'REVIEW_STARTED': 'fa-play',
            'REVIEW_COMPLETED': 'fa-check-circle',
            'COMMENT': 'fa-comment',
            'ERROR': 'fa-exclamation-triangle',
            'SYSTEM': 'fa-robot',
            'unknown_type': 'fa-circle'  # Default case
        }
        
        for activity_type, expected_icon in test_cases.items():
            self.assertEqual(activity_icon(activity_type), expected_icon)
    
    def test_percentage_calculation(self):
        """Test percentage calculation."""
        # Test normal calculation
        self.assertEqual(percentage(25, 100), "25.0%")
        
        # Test zero total
        self.assertEqual(percentage(10, 0), "0.0%")
        
        # Test zero value
        self.assertEqual(percentage(0, 100), "0.0%")
        
        # Test invalid inputs
        self.assertEqual(percentage("invalid", 100), "0.0%")
        self.assertEqual(percentage(25, "invalid"), "0.0%")
    
    def test_get_item_dictionary_access(self):
        """Test dictionary item access."""
        test_dict = {'key1': 'value1', 'key2': 'value2'}
        
        # Test existing key
        self.assertEqual(get_item(test_dict, 'key1'), 'value1')
        
        # Test non-existing key
        self.assertEqual(get_item(test_dict, 'nonexistent'), '')
        
        # Test invalid dictionary
        self.assertEqual(get_item("not_dict", 'key'), '')
    
    def test_multiply_values(self):
        """Test value multiplication."""
        # Test normal multiplication
        self.assertEqual(multiply(5, 3), 15.0)
        
        # Test float multiplication
        self.assertEqual(multiply(2.5, 4), 10.0)
        
        # Test invalid inputs
        self.assertEqual(multiply("invalid", 3), 0)
        self.assertEqual(multiply(5, "invalid"), 0)
    
    def test_format_number_display(self):
        """Test number formatting."""
        # Test integer
        self.assertEqual(format_number(1000), "1,000")
        
        # Test float that's an integer
        self.assertEqual(format_number(1000.0), "1,000")
        
        # Test float with decimal
        self.assertEqual(format_number(1000.5), "1,000.5")
        
        # Test invalid input
        self.assertEqual(format_number("invalid"), "invalid")
    
    def test_transition_arrow_generation(self):
        """Test transition arrow generation."""
        from django.template import Context, Template
        
        # Test creation (no from_status)
        template = Template("{% load review_manager_extras %}{% transition_arrow None 'draft' %}")
        result = template.render(Context())
        self.assertIn('fa-plus', result)
        self.assertIn('text-success', result)
        
        # Test progression
        template = Template("{% load review_manager_extras %}{% transition_arrow 'draft' 'strategy_ready' %}")
        result = template.render(Context())
        self.assertIn('fa-arrow-up', result)
        self.assertIn('text-success', result)
        
        # Test failure
        template = Template("{% load review_manager_extras %}{% transition_arrow 'executing' 'failed' %}")
        result = template.render(Context())
        self.assertIn('fa-times', result)
        self.assertIn('text-danger', result)


class MiddlewareCoverageTests(TestCase):
    """Test middleware components comprehensively."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_security_headers_middleware(self):
        """Test security headers are properly set."""
        request = MagicMock()
        response = MagicMock()
        response.get.return_value = None
        
        middleware = SecurityHeadersMiddleware(lambda r: response)
        result = middleware(request)
        
        # Verify security headers are set
        expected_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Referrer-Policy'
        ]
        
        for header in expected_headers:
            response.__setitem__.assert_any_call(header, MagicMock())
    
    @patch('apps.review_manager.middleware.get_client_ip')
    def test_session_change_tracking_middleware(self, mock_get_ip):
        """Test session change tracking middleware."""
        mock_get_ip.return_value = '127.0.0.1'
        
        session = SearchSession.objects.create(
            title="Test Session",
            created_by=self.user
        )
        
        # Test GET request (should not create activity)
        response = self.client.get(f'/review/session/{session.id}/')
        initial_activity_count = SessionActivity.objects.filter(session=session).count()
        
        # Test POST request with session modification
        data = {
            'title': 'Updated Title',
            'description': 'Updated description'
        }
        response = self.client.post(f'/review/session/{session.id}/edit/', data)
        
        # Should create activity log entry
        new_activity_count = SessionActivity.objects.filter(session=session).count()
        self.assertGreater(new_activity_count, initial_activity_count)
    
    def test_middleware_process_exception(self):
        """Test middleware exception handling."""
        request = MagicMock()
        request.user = self.user
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        middleware = SessionChangeTrackingMiddleware(lambda r: None)
        
        # Test with exception
        exception = Exception("Test exception")
        result = middleware.process_exception(request, exception)
        
        # Should return None (let Django handle the exception)
        self.assertIsNone(result)


class SignalsCoverageTests(TestCase):
    """Test signal handling comprehensively."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_signal_utils_context_management(self):
        """Test SignalUtils context management."""
        session = SearchSession.objects.create(
            title="Test Session",
            created_by=self.user
        )
        
        # Test setting and getting change context
        context_data = {
            'reason': 'Test reason',
            'source': 'unit_test'
        }
        
        SignalUtils.set_change_context(session, user=self.user, **context_data)
        retrieved_context = SignalUtils.get_change_context(session)
        
        self.assertEqual(retrieved_context['user'], self.user)
        self.assertEqual(retrieved_context['reason'], 'Test reason')
        self.assertEqual(retrieved_context['source'], 'unit_test')
        
        # Test clearing context
        SignalUtils.clear_change_context(session)
        cleared_context = SignalUtils.get_change_context(session)
        self.assertEqual(cleared_context, {})
    
    def test_status_change_signal_handler_edge_cases(self):
        """Test status change handling with edge cases."""
        session = SearchSession.objects.create(
            title="Test Session",
            created_by=self.user,
            status='draft'
        )
        
        # Test status change with context
        SignalUtils.set_change_context(
            session,
            user=self.user,
            reason='Manual status change'
        )
        
        session.status = 'strategy_ready'
        session.save()
        
        # Verify activity was logged
        activities = SessionActivity.objects.filter(
            session=session,
            action='status_changed'
        )
        self.assertTrue(activities.exists())
        
        activity = activities.first()
        self.assertEqual(activity.user, self.user)
        self.assertIn('Manual status change', activity.description)
    
    def test_signal_handler_with_no_user_context(self):
        """Test signal handling when no user context is available."""
        session = SearchSession.objects.create(
            title="Test Session",
            created_by=self.user,
            status='draft'
        )
        
        # Don't set any context, just change status
        session.status = 'strategy_ready'
        session.save()
        
        # Should still create activity log
        activities = SessionActivity.objects.filter(session=session)
        self.assertTrue(activities.exists())
    
    def test_signal_handler_error_recovery(self):
        """Test signal handler error recovery scenarios."""
        session = SearchSession.objects.create(
            title="Test Session",
            created_by=self.user,
            status='executing'
        )
        
        # Simulate error recovery
        SignalUtils.set_change_context(
            session,
            user=self.user,
            reason='Error recovery - resetting to previous state'
        )
        
        session.status = 'failed'
        session.save()
        
        # Check for error activity
        error_activities = SessionActivity.objects.filter(
            session=session,
            action='status_changed'
        )
        self.assertTrue(error_activities.exists())


class PermissionsCoverageTests(TestCase):
    """Test permission system comprehensively."""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.session = SearchSession.objects.create(
            title="User1's Session",
            created_by=self.user1
        )
    
    def test_session_ownership_mixin(self):
        """Test session ownership validation."""
        mixin = SessionOwnershipMixin()
        
        # Mock request with user1
        request = MagicMock()
        request.user = self.user1
        mixin.request = request
        
        # Test get_queryset filters to user's sessions
        base_queryset = SearchSession.objects.all()
        mixin.model = SearchSession
        filtered_queryset = mixin.get_queryset()
        
        # Should only include user1's sessions
        self.assertIn(self.session, filtered_queryset)
        
        # Create session for user2
        user2_session = SearchSession.objects.create(
            title="User2's Session",
            created_by=self.user2
        )
        
        # Should not include user2's session in user1's queryset
        self.assertNotIn(user2_session, filtered_queryset)
    
    def test_session_status_permission_mixin(self):
        """Test status-based permission validation."""
        mixin = SessionStatusPermissionMixin()
        mixin.required_statuses = ['draft', 'strategy_ready']
        
        # Test with allowed status
        draft_session = SearchSession.objects.create(
            title="Draft Session",
            created_by=self.user1,
            status='draft'
        )
        self.assertTrue(mixin.check_status_permission(draft_session))
        
        # Test with disallowed status
        executing_session = SearchSession.objects.create(
            title="Executing Session",
            created_by=self.user1,
            status='executing'
        )
        self.assertFalse(mixin.check_status_permission(executing_session))
    
    def test_session_permission_utility(self):
        """Test SessionPermission utility class."""
        # Test ownership check
        self.assertTrue(SessionPermission.can_view(self.session, self.user1))
        self.assertFalse(SessionPermission.can_view(self.session, self.user2))
        
        # Test edit permission (draft status)
        draft_session = SearchSession.objects.create(
            title="Draft Session",
            created_by=self.user1,
            status='draft'
        )
        self.assertTrue(SessionPermission.can_edit(draft_session, self.user1))
        
        # Test edit permission (executing status - should be false)
        executing_session = SearchSession.objects.create(
            title="Executing Session",
            created_by=self.user1,
            status='executing'
        )
        self.assertFalse(SessionPermission.can_edit(executing_session, self.user1))
        
        # Test delete permission (only draft)
        self.assertTrue(SessionPermission.can_delete(draft_session, self.user1))
        self.assertFalse(SessionPermission.can_delete(executing_session, self.user1))
    
    def test_rate_limit_mixin(self):
        """Test rate limiting functionality."""
        mixin = RateLimitMixin()
        mixin.rate_limit_key = 'test_action'
        mixin.rate_limit_requests = 5
        mixin.rate_limit_window = 60
        
        # Mock request
        request = MagicMock()
        request.user = self.user1
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        # Test rate limit check (should pass initially)
        self.assertTrue(mixin.check_rate_limit(request))
        
        # Simulate multiple requests
        for _ in range(6):  # Exceed the limit
            mixin.check_rate_limit(request)
        
        # Should now be rate limited
        self.assertFalse(mixin.check_rate_limit(request))


class ManagementCommandsCoverageTests(TestCase):
    """Test management commands comprehensively."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_sample_sessions_command(self):
        """Test the create_sample_sessions management command."""
        # Test creating sessions
        out = StringIO()
        call_command('create_sample_sessions', '--count=3', '--username=testuser', stdout=out)
        
        # Verify sessions were created
        sessions = SearchSession.objects.filter(created_by=self.user)
        self.assertEqual(sessions.count(), 3)
        
        # Verify output
        output = out.getvalue()
        self.assertIn('3 sample sessions created', output)
    
    def test_create_sample_sessions_cleanup(self):
        """Test the cleanup functionality."""
        # Create some test sessions
        for i in range(3):
            SearchSession.objects.create(
                title=f"Sample Session {i+1}",
                description="Sample description",
                created_by=self.user
            )
        
        # Test cleanup
        out = StringIO()
        call_command('create_sample_sessions', '--clean', stdout=out)
        
        # Verify sessions were removed
        sessions = SearchSession.objects.filter(created_by=self.user)
        self.assertEqual(sessions.count(), 0)
        
        # Verify output
        output = out.getvalue()
        self.assertIn('sample sessions cleaned up', output)


class ViewEdgeCasesCoverageTests(TestCase):
    """Test view edge cases and error conditions."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_session_stats_ajax_unauthorized(self):
        """Test AJAX stats view with unauthorized access."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        session = SearchSession.objects.create(
            title="Other User's Session",
            created_by=other_user
        )
        
        # Try to access stats for other user's session
        response = self.client.get(f'/review/ajax/session/{session.id}/stats/')
        self.assertEqual(response.status_code, 404)
    
    def test_archive_session_ajax_invalid_status(self):
        """Test archiving session with invalid status."""
        session = SearchSession.objects.create(
            title="Draft Session",
            created_by=self.user,
            status='draft'  # Not completed, can't archive
        )
        
        response = self.client.post(f'/review/ajax/session/{session.id}/archive/')
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('Only completed sessions can be archived', data['error'])
    
    def test_duplicate_session_post_method_required(self):
        """Test duplicate session requires POST method."""
        session = SearchSession.objects.create(
            title="Original Session",
            created_by=self.user
        )
        
        # Try GET request (should not be allowed)
        response = self.client.get(f'/review/session/{session.id}/duplicate/')
        self.assertEqual(response.status_code, 405)  # Method not allowed
    
    def test_session_navigation_fallback(self):
        """Test session navigation fallback for missing apps."""
        session = SearchSession.objects.create(
            title="Test Session",
            created_by=self.user,
            status='strategy_ready'
        )
        
        # Access session detail to trigger navigation
        response = self.client.get(f'/review/session/{session.id}/')
        self.assertEqual(response.status_code, 200)
        
        # Check that navigation info is present in context
        self.assertIn('nav_info', response.context)
        nav_info = response.context['nav_info']
        self.assertIn('url', nav_info)
        self.assertIn('text', nav_info)
    
    def test_dashboard_pagination_edge_cases(self):
        """Test dashboard pagination with edge cases."""
        # Create more sessions than page size
        for i in range(15):  # More than paginate_by = 12
            SearchSession.objects.create(
                title=f"Session {i+1}",
                created_by=self.user
            )
        
        # Test first page
        response = self.client.get('/review/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['sessions']), 12)
        
        # Test second page
        response = self.client.get('/review/?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['sessions']), 3)
        
        # Test invalid page
        response = self.client.get('/review/?page=999')
        self.assertEqual(response.status_code, 200)  # Should show last page
    
    def test_dashboard_search_edge_cases(self):
        """Test dashboard search with edge cases."""
        # Create sessions with special characters
        special_session = SearchSession.objects.create(
            title="Session with 'quotes' and \"double quotes\"",
            description="Description with <script>alert('xss')</script>",
            created_by=self.user
        )
        
        # Test search with special characters
        response = self.client.get('/review/?q=quotes')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, special_session.title)
        
        # Test search with HTML (should be escaped)
        response = self.client.get('/review/?q=script')
        self.assertEqual(response.status_code, 200)
        # Should contain the session but HTML should be escaped
        self.assertContains(response, special_session.title)
        self.assertNotContains(response, '<script>')
    
    def test_form_validation_edge_cases(self):
        """Test form validation with edge cases."""
        # Test title at exact limit
        long_title = 'A' * 200  # Exact limit
        response = self.client.post('/review/create/', {
            'title': long_title,
            'description': 'Valid description'
        })
        self.assertEqual(response.status_code, 302)  # Should succeed
        
        # Test title over limit
        too_long_title = 'A' * 201  # Over limit
        response = self.client.post('/review/create/', {
            'title': too_long_title,
            'description': 'Valid description'
        })
        self.assertEqual(response.status_code, 200)  # Should stay on form with errors
        self.assertFormError(response, 'form', 'title', 'Ensure this value has at most 200 characters (it has 201).')
        
        # Test description at exact limit
        long_description = 'B' * 1000  # Exact limit
        response = self.client.post('/review/create/', {
            'title': 'Valid title',
            'description': long_description
        })
        self.assertEqual(response.status_code, 302)  # Should succeed
        
        # Test description over limit
        too_long_description = 'B' * 1001  # Over limit
        response = self.client.post('/review/create/', {
            'title': 'Valid title',
            'description': too_long_description
        })
        self.assertEqual(response.status_code, 200)  # Should stay on form with errors
        self.assertFormError(response, 'form', 'description', 'Description cannot be longer than 1000 characters.')


class ErrorHandlingCoverageTests(TestCase):
    """Test error handling and recovery scenarios."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_session_not_found_error(self):
        """Test handling of non-existent session IDs."""
        fake_uuid = str(uuid.uuid4())
        
        response = self.client.get(f'/review/session/{fake_uuid}/')
        self.assertEqual(response.status_code, 404)
    
    def test_unauthorized_session_access(self):
        """Test unauthorized access to other user's sessions."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        other_session = SearchSession.objects.create(
            title="Other User's Session",
            created_by=other_user
        )
        
        # Try to access other user's session
        response = self.client.get(f'/review/session/{other_session.id}/')
        self.assertEqual(response.status_code, 403)
    
    def test_invalid_status_transition(self):
        """Test invalid status transitions."""
        session = SearchSession.objects.create(
            title="Test Session",
            created_by=self.user,
            status='draft'
        )
        
        # Try to delete a non-draft session
        session.status = 'executing'
        session.save()
        
        response = self.client.post(f'/review/session/{session.id}/delete/')
        self.assertEqual(response.status_code, 403)  # Should be forbidden
    
    @patch('apps.review_manager.views.reverse')
    def test_view_url_resolution_failure(self, mock_reverse):
        """Test handling of URL resolution failures."""
        mock_reverse.side_effect = Exception("URL resolution failed")
        
        # Should still work and use fallback
        response = self.client.post('/review/create/', {
            'title': 'Test Session',
            'description': 'Test description'
        })
        
        # Should still create session but with fallback navigation
        self.assertEqual(response.status_code, 302)
    
    def test_database_error_handling(self):
        """Test database error scenarios."""
        # Test creating session with invalid user reference
        with self.assertRaises(Exception):
            SearchSession.objects.create(
                title="Invalid Session",
                created_by=None  # This should fail
            )
    
    def test_cache_failure_handling(self):
        """Test cache failure scenarios."""
        # Clear cache to ensure clean state
        cache.clear()
        
        # Create session
        session = SearchSession.objects.create(
            title="Test Session",
            created_by=self.user
        )
        
        # Access session stats (should work even if cache fails)
        response = self.client.get(f'/review/ajax/session/{session.id}/stats/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'draft')


class UserSessionStatsCoverageTests(TestCase):
    """Test UserSessionStats model and related functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_session_stats_creation(self):
        """Test automatic creation of user session stats."""
        # Create a session
        session = SearchSession.objects.create(
            title="Test Session",
            created_by=self.user
        )
        
        # Check if stats were created/updated
        stats, created = UserSessionStats.objects.get_or_create(user=self.user)
        self.assertIsNotNone(stats)
        
        # Test stats calculation
        self.assertEqual(stats.user, self.user)
    
    def test_stats_model_methods(self):
        """Test UserSessionStats model methods."""
        stats = UserSessionStats.objects.create(
            user=self.user,
            total_sessions=10,
            completed_sessions=7,
            average_completion_days=5.5
        )
        
        # Test completion rate calculation
        completion_rate = stats.completion_rate
        self.assertEqual(completion_rate, 70.0)  # 7/10 * 100
        
        # Test with zero sessions
        zero_stats = UserSessionStats.objects.create(
            user=self.user,
            total_sessions=0,
            completed_sessions=0
        )
        self.assertEqual(zero_stats.completion_rate, 0.0)


class IntegrationWorkflowTests(TestCase):
    """Test complete workflow integration scenarios."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_complete_session_lifecycle(self):
        """Test complete session lifecycle from creation to archival."""
        # 1. Create session
        response = self.client.post('/review/create/', {
            'title': 'Complete Lifecycle Test',
            'description': 'Testing full lifecycle'
        })
        self.assertEqual(response.status_code, 302)
        
        # Get the created session
        session = SearchSession.objects.filter(created_by=self.user).first()
        self.assertIsNotNone(session)
        self.assertEqual(session.status, 'draft')
        
        # 2. View session detail
        response = self.client.get(f'/review/session/{session.id}/')
        self.assertEqual(response.status_code, 200)
        
        # 3. Edit session
        response = self.client.post(f'/review/session/{session.id}/edit/', {
            'title': 'Updated Lifecycle Test',
            'description': 'Updated description'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify update
        session.refresh_from_db()
        self.assertEqual(session.title, 'Updated Lifecycle Test')
        
        # 4. Simulate status progression
        session.status = 'completed'
        session.save()
        
        # 5. Archive session
        response = self.client.post(f'/review/ajax/session/{session.id}/archive/')
        self.assertEqual(response.status_code, 200)
        
        # Verify archival
        session.refresh_from_db()
        self.assertEqual(session.status, 'archived')
        
        # 6. Check activity log
        activities = SessionActivity.objects.filter(session=session)
        self.assertGreater(activities.count(), 0)
        
        # Should have creation, update, and status change activities
        activity_types = list(activities.values_list('action', flat=True))
        self.assertIn('created', activity_types)
        self.assertIn('updated', activity_types)
        self.assertIn('status_changed', activity_types)
    
    def test_workflow_with_errors_and_recovery(self):
        """Test workflow with error conditions and recovery."""
        # Create session
        session = SearchSession.objects.create(
            title="Error Recovery Test",
            created_by=self.user
        )
        
        # Simulate error condition
        session.status = 'failed'
        session.save()
        
        # Test error recovery
        SignalUtils.set_change_context(
            session,
            user=self.user,
            reason='Manual recovery attempt'
        )
        
        session.status = 'draft'  # Reset to working state
        session.save()
        
        # Verify recovery was logged
        recovery_activities = SessionActivity.objects.filter(
            session=session,
            action='status_changed'
        )
        self.assertTrue(recovery_activities.exists())
        
        # Check that recovery context was captured
        recovery_activity = recovery_activities.last()
        self.assertIn('recovery', recovery_activity.description.lower())