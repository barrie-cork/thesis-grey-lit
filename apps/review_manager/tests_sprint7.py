# apps/review_manager/tests_sprint7.py

"""
Sprint 7 Testing: Polish & Performance Tests
Real-time status monitoring, notifications, and error recovery testing
"""

import json
import time
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from threading import Thread
import asyncio

from .models import SearchSession, SessionActivity, UserSessionStats
from .recovery import ErrorRecoveryManager

User = get_user_model()


class RealTimeStatusTestCase(TestCase):
    """Test real-time status monitoring functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Create test sessions
        self.session_executing = SearchSession.objects.create(
            title='Executing Session',
            description='Test executing session',
            created_by=self.user,
            status='executing'
        )
        
        self.session_processing = SearchSession.objects.create(
            title='Processing Session',
            description='Test processing session',
            created_by=self.user,
            status='processing'
        )
        
        self.session_completed = SearchSession.objects.create(
            title='Completed Session',
            description='Test completed session',
            created_by=self.user,
            status='completed'
        )
    
    def test_status_check_api_basic_functionality(self):
        """Test basic status check API functionality"""
        url = reverse('review_manager:status_check_api')
        
        data = {
            'session_ids': [
                str(self.session_executing.id),
                str(self.session_processing.id),
                str(self.session_completed.id)
            ]
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        self.assertIn('sessions', response_data)
        self.assertIn('timestamp', response_data)
        self.assertIn('poll_interval', response_data)
        
        # Check that all sessions are included
        sessions = response_data['sessions']
        self.assertEqual(len(sessions), 3)
        
        # Verify session data structure
        for session_id, session_data in sessions.items():
            self.assertIn('status', session_data)
            self.assertIn('status_display', session_data)
            self.assertIn('updated_at', session_data)
            self.assertIn('title', session_data)
    
    def test_status_check_api_performance(self):
        """Test status check API performance with many sessions"""
        # Create 50 test sessions
        sessions = []
        for i in range(50):
            session = SearchSession.objects.create(
                title=f'Test Session {i}',
                description=f'Test session {i}',
                created_by=self.user,
                status='executing'
            )
            sessions.append(session)
        
        session_ids = [str(s.id) for s in sessions]
        
        url = reverse('review_manager:status_check_api')
        data = {'session_ids': session_ids}
        
        start_time = time.time()
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        end_time = time.time()
        
        # Should respond within 500ms even with 50 sessions
        self.assertLess(end_time - start_time, 0.5)
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(len(response_data['sessions']), 50)
    
    def test_status_check_api_invalid_data(self):
        """Test status check API with invalid data"""
        url = reverse('review_manager:status_check_api')
        
        # Test with no session IDs
        response = self.client.post(
            url,
            json.dumps({'session_ids': []}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test with invalid JSON
        response = self.client.post(
            url,
            'invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test with too many session IDs
        too_many_ids = [f'id-{i}' for i in range(101)]
        response = self.client.post(
            url,
            json.dumps({'session_ids': too_many_ids}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_status_check_api_unauthorized_sessions(self):
        """Test that users can only access their own sessions"""
        # Create another user and session
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        other_session = SearchSession.objects.create(
            title='Other User Session',
            created_by=other_user,
            status='draft'
        )
        
        url = reverse('review_manager:status_check_api')
        data = {
            'session_ids': [
                str(self.session_executing.id),
                str(other_session.id)  # Should not be accessible
            ]
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Should only return the user's own session
        self.assertEqual(len(response_data['sessions']), 1)
        self.assertIn(str(self.session_executing.id), response_data['sessions'])
        self.assertNotIn(str(other_session.id), response_data['sessions'])
    
    def test_progress_simulation(self):
        """Test progress simulation endpoint"""
        url = reverse('review_manager:simulate_progress_update')
        
        data = {
            'session_id': str(self.session_executing.id),
            'type': 'execution',
            'progress': 65
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['progress'], 65)
        
        # Verify progress is cached
        cache_key = f'execution_progress_{self.session_executing.id}'
        cached_progress = cache.get(cache_key)
        self.assertEqual(cached_progress, 65)
    
    def test_system_health_check(self):
        """Test system health check endpoint"""
        url = reverse('review_manager:system_health_check')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        self.assertIn('health', response_data)
        
        health = response_data['health']
        self.assertIn('status', health)
        self.assertIn('timestamp', health)
        self.assertIn('checks', health)
        self.assertIn('performance', health)
        
        # Check database health
        self.assertIn('database', health['checks'])
        self.assertEqual(health['checks']['database']['status'], 'ok')
        
        # Check cache health
        self.assertIn('cache', health['checks'])
        self.assertEqual(health['checks']['cache']['status'], 'ok')


class NotificationTestCase(TestCase):
    """Test notification management functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_notification_preferences_get(self):
        """Test getting notification preferences"""
        url = reverse('review_manager:notification_preferences_get')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        self.assertIn('preferences', response_data)
        
        prefs = response_data['preferences']
        expected_keys = [
            'auto_dismiss_duration',
            'show_status_changes',
            'show_error_notifications',
            'show_success_notifications',
            'notification_position',
            'sound_enabled'
        ]
        
        for key in expected_keys:
            self.assertIn(key, prefs)
    
    def test_notification_preferences_save(self):
        """Test saving notification preferences"""
        url = reverse('review_manager:notification_preferences_api')
        
        preferences = {
            'auto_dismiss_duration': 3000,
            'show_status_changes': False,
            'show_error_notifications': True,
            'show_success_notifications': False,
            'notification_position': 'bottom-left',
            'sound_enabled': True
        }
        
        data = {'preferences': preferences}
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        self.assertIn('preferences', response_data)
        
        # Verify preferences were saved
        user_stats = UserSessionStats.objects.get(user=self.user)
        saved_prefs = user_stats.notification_preferences
        
        self.assertEqual(saved_prefs['auto_dismiss_duration'], 3000)
        self.assertFalse(saved_prefs['show_status_changes'])
        self.assertTrue(saved_prefs['show_error_notifications'])
        self.assertFalse(saved_prefs['show_success_notifications'])
        self.assertEqual(saved_prefs['notification_position'], 'bottom-left')
        self.assertTrue(saved_prefs['sound_enabled'])
    
    def test_notification_preferences_validation(self):
        """Test notification preferences validation"""
        url = reverse('review_manager:notification_preferences_api')
        
        # Test invalid duration (too short)
        data = {
            'preferences': {
                'auto_dismiss_duration': 500  # Below minimum
            }
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Should clamp to minimum value
        self.assertEqual(response_data['preferences']['auto_dismiss_duration'], 1000)
        
        # Test invalid duration (too long)
        data = {
            'preferences': {
                'auto_dismiss_duration': 50000  # Above maximum
            }
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Should clamp to maximum value
        self.assertEqual(response_data['preferences']['auto_dismiss_duration'], 30000)
        
        # Test invalid position
        data = {
            'preferences': {
                'notification_position': 'invalid-position'
            }
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Should default to top-right
        self.assertEqual(response_data['preferences']['notification_position'], 'top-right')


class ErrorRecoveryTestCase(TestCase):
    """Test error recovery functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        self.failed_session = SearchSession.objects.create(
            title='Failed Session',
            description='Test failed session',
            created_by=self.user,
            status='failed'
        )
    
    def test_get_recovery_options(self):
        """Test getting recovery options for failed session"""
        url = reverse('review_manager:get_error_recovery_options', 
                     kwargs={'session_id': self.failed_session.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        self.assertIn('recovery_options', response_data)
        
        options = response_data['recovery_options']
        self.assertIn('error_type', options)
        self.assertIn('title', options)
        self.assertIn('message', options)
        self.assertIn('suggestions', options)
        
        # Should have at least one suggestion
        self.assertGreater(len(options['suggestions']), 0)
    
    def test_get_recovery_options_non_failed_session(self):
        """Test getting recovery options for non-failed session"""
        normal_session = SearchSession.objects.create(
            title='Normal Session',
            created_by=self.user,
            status='draft'
        )
        
        url = reverse('review_manager:get_error_recovery_options', 
                     kwargs={'session_id': normal_session.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)
    
    def test_execute_recovery_action(self):
        """Test executing recovery actions"""
        url = reverse('review_manager:error_recovery_api')
        
        data = {
            'session_id': str(self.failed_session.id),
            'error_type': 'search_execution_failed',
            'action': 'retry_execution'
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        self.assertIn('message', response_data)
        
        # Verify session status was updated
        self.failed_session.refresh_from_db()
        self.assertEqual(self.failed_session.status, 'strategy_ready')
        
        # Verify activity was logged
        activity = SessionActivity.objects.filter(
            session=self.failed_session,
            action='error_recovery'
        ).first()
        
        self.assertIsNotNone(activity)
        self.assertEqual(activity.user, self.user)
    
    def test_execute_recovery_action_unauthorized(self):
        """Test executing recovery action on unauthorized session"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        other_session = SearchSession.objects.create(
            title='Other Session',
            created_by=other_user,
            status='failed'
        )
        
        url = reverse('review_manager:error_recovery_api')
        
        data = {
            'session_id': str(other_session.id),
            'error_type': 'search_execution_failed',
            'action': 'retry_execution'
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)


class ErrorRecoveryManagerTestCase(TestCase):
    """Test ErrorRecoveryManager utility class"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.session = SearchSession.objects.create(
            title='Test Session',
            created_by=self.user,
            status='failed'
        )
    
    def test_get_recovery_options_search_execution_failed(self):
        """Test recovery options for search execution failure"""
        options = ErrorRecoveryManager.get_recovery_options(
            'search_execution_failed', 
            self.session
        )
        
        self.assertEqual(options['error_type'], 'search_execution_failed')
        self.assertEqual(options['title'], 'Search Execution Error')
        self.assertIn('Search execution encountered an error', options['message'])
        self.assertEqual(options['severity'], 'error')
        self.assertEqual(options['session_id'], self.session.id)
        
        # Should have retry, edit, and support suggestions
        suggestions = options['suggestions']
        self.assertEqual(len(suggestions), 3)
        
        action_types = [s['action'] for s in suggestions]
        self.assertIn('retry_execution', action_types)
        self.assertIn('edit_strategy', action_types)
        self.assertIn('contact_support', action_types)
    
    def test_get_recovery_options_processing_timeout(self):
        """Test recovery options for processing timeout"""
        options = ErrorRecoveryManager.get_recovery_options(
            'processing_timeout', 
            self.session
        )
        
        self.assertEqual(options['error_type'], 'processing_timeout')
        self.assertEqual(options['title'], 'Processing Timeout')
        self.assertEqual(options['severity'], 'warning')
        
        suggestions = options['suggestions']
        action_types = [s['action'] for s in suggestions]
        self.assertIn('resume_processing', action_types)
        self.assertIn('batch_processing', action_types)
    
    def test_get_recovery_options_unknown_error(self):
        """Test recovery options for unknown error type"""
        options = ErrorRecoveryManager.get_recovery_options(
            'unknown_error_type', 
            self.session
        )
        
        # Should fall back to unknown error strategy
        self.assertEqual(options['error_type'], 'unknown_error_type')
        self.assertEqual(options['title'], 'Unexpected Error')
        self.assertEqual(options['severity'], 'error')
        
        suggestions = options['suggestions']
        action_types = [s['action'] for s in suggestions]
        self.assertIn('retry_operation', action_types)
        self.assertIn('go_dashboard', action_types)
        self.assertIn('report_issue', action_types)
    
    def test_get_error_prevention_tips(self):
        """Test error prevention tips"""
        tips = ErrorRecoveryManager.get_error_prevention_tips('search_execution_failed')
        
        self.assertIsInstance(tips, list)
        self.assertGreater(len(tips), 0)
        
        # Should contain helpful advice
        tips_text = ' '.join(tips).lower()
        self.assertIn('search', tips_text)
        
        # Test with unknown error type
        default_tips = ErrorRecoveryManager.get_error_prevention_tips('unknown_type')
        self.assertIsInstance(default_tips, list)
        self.assertGreater(len(default_tips), 0)
    
    def test_recovery_success_rate_calculation(self):
        """Test recovery success rate calculation"""
        # Create some test recovery attempts
        SessionActivity.objects.create(
            session=self.session,
            action='recovery_attempt',
            user=self.user,
            details={
                'error_type': 'search_execution_failed',
                'recovery_action': 'retry_execution',
                'success': True
            }
        )
        
        SessionActivity.objects.create(
            session=self.session,
            action='recovery_attempt',
            user=self.user,
            details={
                'error_type': 'search_execution_failed',
                'recovery_action': 'retry_execution',
                'success': False
            }
        )
        
        stats = ErrorRecoveryManager.get_recovery_success_rate('search_execution_failed')
        
        self.assertEqual(stats['total_attempts'], 2)
        self.assertEqual(stats['successful_attempts'], 1)
        self.assertEqual(stats['success_rate'], 50.0)
        self.assertEqual(stats['error_type'], 'search_execution_failed')
        
        # Test all error types
        all_stats = ErrorRecoveryManager.get_recovery_success_rate()
        self.assertEqual(all_stats['total_attempts'], 2)
        self.assertEqual(all_stats['error_type'], 'all')


class PerformanceTestCase(TransactionTestCase):
    """Test performance-related functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_concurrent_status_checks(self):
        """Test concurrent status check requests"""
        # Create test sessions
        sessions = []
        for i in range(10):
            session = SearchSession.objects.create(
                title=f'Test Session {i}',
                created_by=self.user,
                status='executing'
            )
            sessions.append(session)
        
        session_ids = [str(s.id) for s in sessions]
        url = reverse('review_manager:status_check_api')
        
        def make_request():
            response = self.client.post(
                url,
                json.dumps({'session_ids': session_ids}),
                content_type='application/json'
            )
            return response.status_code == 200
        
        # Run 5 concurrent requests
        threads = []
        results = []
        
        for _ in range(5):
            thread = Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))
    
    def test_cache_performance(self):
        """Test caching performance for status updates"""
        session = SearchSession.objects.create(
            title='Cache Test Session',
            created_by=self.user,
            status='executing'
        )
        
        # Set progress in cache
        cache_key = f'execution_progress_{session.id}'
        cache.set(cache_key, 75, timeout=300)
        
        url = reverse('review_manager:status_check_api')
        data = {'session_ids': [str(session.id)]}
        
        # Measure response time with cached data
        start_time = time.time()
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        
        # Should be very fast with cached data
        self.assertLess(end_time - start_time, 0.1)
        
        response_data = response.json()
        session_data = response_data['sessions'][str(session.id)]
        self.assertEqual(session_data['progress'], 75)


class IntegrationTestCase(TestCase):
    """Integration tests for Sprint 7 features"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_complete_status_monitoring_workflow(self):
        """Test complete status monitoring workflow"""
        # 1. Create a session
        session = SearchSession.objects.create(
            title='Integration Test Session',
            created_by=self.user,
            status='draft'
        )
        
        # 2. Check initial status
        url = reverse('review_manager:status_check_api')
        data = {'session_ids': [str(session.id)]}
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        session_data = response_data['sessions'][str(session.id)]
        self.assertEqual(session_data['status'], 'draft')
        
        # 3. Update session status
        session.status = 'executing'
        session.save()
        
        # 4. Simulate progress
        progress_url = reverse('review_manager:simulate_progress_update')
        progress_data = {
            'session_id': str(session.id),
            'type': 'execution',
            'progress': 50
        }
        
        response = self.client.post(
            progress_url,
            json.dumps(progress_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # 5. Check updated status with progress
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        session_data = response_data['sessions'][str(session.id)]
        self.assertEqual(session_data['status'], 'executing')
        self.assertEqual(session_data['progress'], 50)
    
    def test_error_recovery_workflow(self):
        """Test complete error recovery workflow"""
        # 1. Create a failed session
        session = SearchSession.objects.create(
            title='Error Recovery Test',
            created_by=self.user,
            status='failed'
        )
        
        # 2. Log an error activity
        SessionActivity.objects.create(
            session=session,
            action='failed',
            user=self.user,
            details={
                'error_type': 'search_execution_failed',
                'error_message': 'Connection timeout'
            }
        )
        
        # 3. Get recovery options
        options_url = reverse('review_manager:get_error_recovery_options', 
                            kwargs={'session_id': session.id})
        
        response = self.client.get(options_url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        self.assertIn('recovery_options', response_data)
        
        # 4. Execute recovery action
        recovery_url = reverse('review_manager:error_recovery_api')
        recovery_data = {
            'session_id': str(session.id),
            'error_type': 'search_execution_failed',
            'action': 'retry_execution'
        }
        
        response = self.client.post(
            recovery_url,
            json.dumps(recovery_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        
        # 5. Verify session was recovered
        session.refresh_from_db()
        self.assertEqual(session.status, 'strategy_ready')
        
        # 6. Verify recovery was logged
        recovery_activity = SessionActivity.objects.filter(
            session=session,
            action='error_recovery'
        ).first()
        
        self.assertIsNotNone(recovery_activity)
        self.assertEqual(recovery_activity.user, self.user)
    
    def test_notification_preferences_persistence(self):
        """Test notification preferences are persistent across requests"""
        # 1. Set initial preferences
        prefs_url = reverse('review_manager:notification_preferences_api')
        
        preferences = {
            'auto_dismiss_duration': 8000,
            'show_status_changes': False,
            'notification_position': 'bottom-right'
        }
        
        response = self.client.post(
            prefs_url,
            json.dumps({'preferences': preferences}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # 2. Get preferences in new request
        get_url = reverse('review_manager:notification_preferences_get')
        
        response = self.client.get(get_url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        saved_prefs = response_data['preferences']
        self.assertEqual(saved_prefs['auto_dismiss_duration'], 8000)
        self.assertFalse(saved_prefs['show_status_changes'])
        self.assertEqual(saved_prefs['notification_position'], 'bottom-right')
        
        # 3. Verify persistence in database
        user_stats = UserSessionStats.objects.get(user=self.user)
        db_prefs = user_stats.notification_preferences
        
        self.assertEqual(db_prefs['auto_dismiss_duration'], 8000)
        self.assertFalse(db_prefs['show_status_changes'])
        self.assertEqual(db_prefs['notification_position'], 'bottom-right')


if __name__ == '__main__':
    import django
    django.setup()
    
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["apps.review_manager.tests_sprint7"])
