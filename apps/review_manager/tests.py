from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import SearchSession, SessionActivity
import time

# Use the custom User model
User = get_user_model()

class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create test sessions
        self.session1 = SearchSession.objects.create(
            title='Test Review 1',
            description='First test review',
            status='draft',
            created_by=self.user
        )
        self.session2 = SearchSession.objects.create(
            title='Test Review 2',
            description='Second test review',
            status='strategy_ready',
            created_by=self.user
        )

    def test_dashboard_loads_successfully(self):
        """Test that dashboard loads without errors"""
        response = self.client.get(reverse('review_manager:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your Literature Reviews')
        self.assertContains(response, 'Test Review 1')
        self.assertContains(response, 'Test Review 2')

    def test_dashboard_shows_correct_stats(self):
        """Test that dashboard shows correct statistics"""
        response = self.client.get(reverse('review_manager:dashboard'))
        # Updated to match current template structure with id attributes
        self.assertContains(response, 'id="total-sessions">2<')
        self.assertContains(response, 'id="active-sessions">2<')
        self.assertContains(response, 'id="completed-sessions">0<')

    def test_dashboard_search_functionality(self):
        """Test dashboard search works correctly"""
        response = self.client.get(reverse('review_manager:dashboard'), {'q': 'First'})
        self.assertContains(response, 'Test Review 1')
        self.assertNotContains(response, 'Test Review 2')

    def test_dashboard_status_filter(self):
        """Test dashboard status filtering works"""
        response = self.client.get(reverse('review_manager:dashboard'), {'status': 'draft'})
        self.assertContains(response, 'Test Review 1')
        self.assertNotContains(response, 'Test Review 2')

    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('review_manager:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/review/')


class SessionCreateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_session_creation_success(self):
        """Test successful session creation"""
        response = self.client.post(reverse('review_manager:create_session'), {
            'title': 'New Test Review',
            'description': 'This is a test review session'
        })
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check session was created
        session = SearchSession.objects.get(title='New Test Review')
        self.assertEqual(session.description, 'This is a test review session')
        self.assertEqual(session.status, 'draft')
        self.assertEqual(session.created_by, self.user)

    def test_session_creation_creates_activity_log(self):
        """Test that session creation logs activity"""
        initial_activity_count = SessionActivity.objects.count()
        
        self.client.post(reverse('review_manager:create_session'), {
            'title': 'New Test Review',
            'description': 'This is a test review session'
        })
        
        # Check activity was logged
        self.assertTrue(SessionActivity.objects.count() >= initial_activity_count + 1)
        activity = SessionActivity.objects.latest('timestamp')
        self.assertEqual(activity.action, SessionActivity.ActivityType.CREATED)
        self.assertEqual(activity.user, self.user)

    def test_session_creation_performance(self):
        """Test UC-2.1.4: Session creation under 30 seconds (should be much faster)"""
        start_time = time.time()
        response = self.client.post(reverse('review_manager:create_session'), {
            'title': 'Performance Test Review',
            'description': 'Testing creation performance'
        })
        end_time = time.time()
        
        self.assertLess(end_time - start_time, 1.0)  # Should be well under 30s
        self.assertEqual(response.status_code, 302)

    def test_session_creation_with_empty_title_fails(self):
        """Test that sessions cannot be created with empty titles"""
        response = self.client.post(reverse('review_manager:create_session'), {
            'title': '',
            'description': 'This should fail'
        })
        
        # Should not redirect (form should have errors)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'This field is required.')


class SessionNavigationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_session_navigation_by_status(self):
        """Test UC-1.2 smart navigation by status"""
        statuses_and_expected = [
            ('draft', 'Define Strategy'),
            ('strategy_ready', 'Execute Searches'),
            ('ready_for_review', 'Start Review'),
            ('completed', 'View Report'),
        ]
        
        for status, expected_text in statuses_and_expected:
            with self.subTest(status=status):
                session = SearchSession.objects.create(
                    title=f'Test {status}',
                    status=status,
                    created_by=self.user
                )
                
                response = self.client.get(reverse('review_manager:dashboard'))
                self.assertContains(response, expected_text)


class SessionPermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123',
            email='user1@example.com'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123',
            email='user2@example.com'
        )
        
        self.session = SearchSession.objects.create(
            title='User1 Session',
            description='This belongs to user1',
            created_by=self.user1
        )

    def test_users_can_only_see_own_sessions(self):
        """Test SEC-1: Users can only access their own sessions"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('review_manager:dashboard'))
        self.assertContains(response, 'User1 Session')
        
        # Login as user2
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('review_manager:dashboard'))
        self.assertNotContains(response, 'User1 Session')

    def test_session_detail_access_control(self):
        """Test that users cannot access other users' session details"""
        # User2 tries to access User1's session
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(
            reverse('review_manager:session_detail', kwargs={'session_id': self.session.id})
        )
        self.assertEqual(response.status_code, 403)

    def test_session_edit_access_control(self):
        """Test that users cannot edit other users' sessions"""
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(
            reverse('review_manager:edit_session', kwargs={'session_id': self.session.id})
        )
        self.assertEqual(response.status_code, 403)


class SessionStatusWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
    def test_status_transition_validation(self):
        """Test that status transitions follow the defined workflow"""
        session = SearchSession.objects.create(
            title='Test Session',
            status='draft',
            created_by=self.user
        )
        
        # Valid transitions
        self.assertTrue(session.can_transition_to('strategy_ready'))
        
        # Invalid transitions
        self.assertFalse(session.can_transition_to('completed'))
        self.assertFalse(session.can_transition_to('executing'))

    def test_status_manager_logic(self):
        """Test the SessionStatusManager class"""
        from .models import SessionStatusManager
        manager = SessionStatusManager()
        
        # Test valid transitions
        self.assertTrue(manager.can_transition('draft', 'strategy_ready'))
        self.assertTrue(manager.can_transition('strategy_ready', 'executing'))
        self.assertTrue(manager.can_transition('completed', 'archived'))
        
        # Test invalid transitions
        self.assertFalse(manager.can_transition('draft', 'completed'))
        self.assertFalse(manager.can_transition('executing', 'draft'))

    def test_session_helper_methods(self):
        """Test the session helper methods"""
        draft_session = SearchSession.objects.create(
            title='Draft Session',
            status='draft',
            created_by=self.user
        )
        
        completed_session = SearchSession.objects.create(
            title='Completed Session',
            status='completed',
            created_by=self.user
        )
        
        # Test can_be_deleted
        self.assertTrue(draft_session.can_be_deleted())
        self.assertFalse(completed_session.can_be_deleted())
        
        # Test can_be_archived
        self.assertFalse(draft_session.can_be_archived())
        self.assertTrue(completed_session.can_be_archived())
        
        # Test can_be_duplicated
        self.assertFalse(draft_session.can_be_duplicated())
        self.assertTrue(completed_session.can_be_duplicated())


class SessionManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_delete_draft_session(self):
        """Test UC-3.2: Can delete draft sessions"""
        session = SearchSession.objects.create(
            title='Draft Session',
            status='draft',
            created_by=self.user
        )
        
        response = self.client.post(
            reverse('review_manager:delete_session', kwargs={'session_id': session.id})
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SearchSession.objects.filter(id=session.id).exists())

    def test_cannot_delete_non_draft_session(self):
        """Test UC-3.2.4: Cannot delete non-draft sessions"""
        session = SearchSession.objects.create(
            title='Active Session',
            status='strategy_ready',
            created_by=self.user
        )
        
        response = self.client.post(
            reverse('review_manager:delete_session', kwargs={'session_id': session.id})
        )
        
        self.assertEqual(response.status_code, 403)
        self.assertTrue(SearchSession.objects.filter(id=session.id).exists())

    def test_duplicate_session(self):
        """Test UC-3.4: Session duplication"""
        original = SearchSession.objects.create(
            title='Original Session',
            description='Original description',
            status='completed',
            created_by=self.user
        )
        
        response = self.client.post(
            reverse('review_manager:duplicate_session', kwargs={'session_id': original.id})
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Check duplicate was created
        duplicate = SearchSession.objects.get(title='Original Session (Copy)')
        self.assertEqual(duplicate.description, 'Original description')
        self.assertEqual(duplicate.status, 'draft')
        self.assertEqual(duplicate.created_by, self.user)


class PerformanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create many sessions to test performance
        for i in range(50):
            SearchSession.objects.create(
                title=f'Session {i}',
                description=f'Description for session {i}',
                status='draft' if i % 2 == 0 else 'strategy_ready',
                created_by=self.user
            )

    def test_dashboard_performance_with_many_sessions(self):
        """Test PERF-1: Dashboard loads in reasonable time with many sessions"""
        start_time = time.time()
        response = self.client.get(reverse('review_manager:dashboard'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 2.0)  # Should load in under 2 seconds

    def test_search_performance(self):
        """Test PERF-2: Search returns results quickly"""
        start_time = time.time()
        response = self.client.get(
            reverse('review_manager:dashboard'), 
            {'q': 'Session 25'}
        )
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 0.5)  # Should return in under 500ms
        self.assertContains(response, 'Session 25')


class SessionActivityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.session = SearchSession.objects.create(
            title='Test Session',
            description='Test description',
            created_by=self.user
        )

    def test_activity_logging_convenience_method(self):
        """Test the SessionActivity.log_activity convenience method"""
        SessionActivity.log_activity(
            session=self.session,
            action=SessionActivity.ActivityType.STATUS_CHANGED,
            description='Status changed from draft to strategy_ready',
            user=self.user,
            old_status='draft',
            new_status='strategy_ready'
        )
        
        activity = SessionActivity.objects.latest('timestamp')
        self.assertEqual(activity.session, self.session)
        self.assertEqual(activity.action, SessionActivity.ActivityType.STATUS_CHANGED)
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.old_status, 'draft')
        self.assertEqual(activity.new_status, 'strategy_ready')

    def test_activity_string_representation(self):
        """Test that activity string representation is meaningful"""
        activity = SessionActivity.objects.create(
            session=self.session,
            action=SessionActivity.ActivityType.CREATED,
            description='Session created',
            user=self.user
        )
        
        expected = f"Session Created on {self.session.title} at {activity.timestamp}"
        self.assertEqual(str(activity), expected)


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_session_string_representation(self):
        """Test that session string representation is meaningful"""
        session = SearchSession.objects.create(
            title='Test Session',
            status='draft',
            created_by=self.user
        )
        
        expected = f"Test Session (Draft)"
        self.assertEqual(str(session), expected)

    def test_session_absolute_url(self):
        """Test that get_absolute_url returns correct URL"""
        session = SearchSession.objects.create(
            title='Test Session',
            created_by=self.user
        )
        
        expected_url = reverse('review_manager:session_detail', kwargs={'session_id': session.pk})
        self.assertEqual(session.get_absolute_url(), expected_url)

    def test_session_stats_property(self):
        """Test the session stats property"""
        session = SearchSession.objects.create(
            title='Test Session',
            created_by=self.user
        )
        
        stats = session.stats
        self.assertIn('session_id', stats)
        self.assertIn('status', stats)
        self.assertIn('created_days_ago', stats)
        self.assertEqual(stats['session_id'], session.pk)
        self.assertEqual(stats['status'], session.status)
