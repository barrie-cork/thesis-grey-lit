# apps/review_manager/tests_security_minimal.py
"""
Minimal security tests that avoid signal issues.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import SearchSession
from .permissions import SessionPermission
from .decorators import owns_session
from .middleware import SecurityHeadersMiddleware

User = get_user_model()


class MinimalSecurityTests(TestCase):
    """Minimal tests focusing only on core security functionality."""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            password='testpass123'
        )
        
        # Create session directly without triggering signals
        self.session = SearchSession.objects.create(
            title='Test Session',
            created_by=self.user1,
            status='draft'
        )
    
    def test_security_imports(self):
        """Test that security components can be imported."""
        from .decorators import owns_session, rate_limit, audit_action
        from .permissions import SessionPermission, SessionOwnershipMixin
        from .middleware import SecurityHeadersMiddleware
        
        # Verify callables
        self.assertTrue(callable(owns_session))
        self.assertTrue(callable(rate_limit))
        self.assertTrue(callable(audit_action))
        self.assertTrue(callable(SecurityHeadersMiddleware))
        
        # Verify classes have required methods
        self.assertTrue(hasattr(SessionPermission, 'can_view'))
        self.assertTrue(hasattr(SessionPermission, 'can_edit'))
        self.assertTrue(hasattr(SessionPermission, 'can_delete'))
    
    def test_session_ownership_permissions(self):
        """Test basic ownership permissions."""
        # Owner permissions
        self.assertTrue(SessionPermission.can_view(self.user1, self.session))
        self.assertTrue(SessionPermission.can_edit(self.user1, self.session))
        self.assertTrue(SessionPermission.can_delete(self.user1, self.session))
        
        # Non-owner permissions
        self.assertFalse(SessionPermission.can_view(self.user2, self.session))
        self.assertFalse(SessionPermission.can_edit(self.user2, self.session))
        self.assertFalse(SessionPermission.can_delete(self.user2, self.session))
    
    def test_status_based_permissions(self):
        """Test status-based permission logic."""
        # Draft session permissions
        self.assertTrue(SessionPermission.can_edit(self.user1, self.session))
        self.assertTrue(SessionPermission.can_delete(self.user1, self.session))
        self.assertFalse(SessionPermission.can_archive(self.user1, self.session))
        
        # Manually change status to test different states
        # Use update to avoid signals
        SearchSession.objects.filter(pk=self.session.pk).update(status='completed')
        self.session.refresh_from_db()
        
        # Completed session permissions
        self.assertFalse(SessionPermission.can_edit(self.user1, self.session))
        self.assertFalse(SessionPermission.can_delete(self.user1, self.session))
        self.assertTrue(SessionPermission.can_archive(self.user1, self.session))
    
    def test_middleware_initialization(self):
        """Test middleware can be initialized."""
        middleware = SecurityHeadersMiddleware(lambda r: None)
        self.assertIsNotNone(middleware)
        
        # Test that it has the required callable interface
        self.assertTrue(hasattr(middleware, 'process_response'))
    
    def test_decorator_can_be_applied(self):
        """Test that decorators can be applied to functions."""
        @owns_session
        def test_function(request, session_id):
            return "success"
        
        # Verify decorator was applied
        self.assertTrue(hasattr(test_function, '__wrapped__'))
        self.assertIsNotNone(test_function)
    
    def test_cross_user_isolation(self):
        """Test that users are properly isolated."""
        # User1's sessions
        user1_sessions = SearchSession.objects.filter(created_by=self.user1)
        self.assertIn(self.session, user1_sessions)
        
        # User2's sessions (should be empty)
        user2_sessions = SearchSession.objects.filter(created_by=self.user2)
        self.assertNotIn(self.session, user2_sessions)
        self.assertEqual(user2_sessions.count(), 0)
        
        # Direct permission checks
        self.assertTrue(self.session.created_by == self.user1)
        self.assertFalse(self.session.created_by == self.user2)


class ComponentTests(TestCase):
    """Test individual security components work correctly."""
    
    def test_permission_utility_methods(self):
        """Test SessionPermission utility methods."""
        user = User.objects.create_user(username='test', password='pass')
        session = SearchSession.objects.create(
            title='Test',
            created_by=user,
            status='draft'
        )
        
        # Test get_allowed_actions
        actions = SessionPermission.get_allowed_actions(user, session)
        self.assertIn('view', actions)
        self.assertIn('edit', actions)
        self.assertIn('delete', actions)
        
        # Should not include actions not available for draft
        self.assertNotIn('archive', actions)
    
    def test_security_middleware_response_processing(self):
        """Test that security middleware can process responses."""
        from django.http import HttpResponse
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/review/')
        response = HttpResponse('test')
        
        middleware = SecurityHeadersMiddleware(lambda r: response)
        processed_response = middleware.process_response(request, response)
        
        # Should return a response object
        self.assertIsNotNone(processed_response)
    
    def test_basic_model_functionality(self):
        """Test that models work without signal complications."""
        user = User.objects.create_user(username='modeltest', password='pass')
        
        # Create session
        session = SearchSession.objects.create(
            title='Model Test Session',
            description='Testing basic model functionality',
            created_by=user,
            status='draft'
        )
        
        # Test basic properties
        self.assertEqual(session.title, 'Model Test Session')
        self.assertEqual(session.created_by, user)
        self.assertEqual(session.status, 'draft')
        
        # Test status checking methods
        self.assertTrue(session.can_be_deleted())
        self.assertFalse(session.can_be_archived())
