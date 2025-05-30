"""
Sprint 11 - Performance Benchmarking Tests
==========================================

This test suite provides comprehensive performance benchmarking for the review_manager app.

Benchmark Categories:
1. Database query performance
2. View response times
3. Memory usage analysis
4. Concurrent user simulation
5. Large dataset handling
6. API endpoint performance
"""

import time
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from django.db import transaction, connections, models
from django.db.models import Q, Count
from django.test.utils import override_settings
from unittest.mock import patch
import psutil
import os

from apps.review_manager.models import SearchSession, SessionActivity, UserSessionStats

User = get_user_model()


class DatabasePerformanceTests(TestCase):
    """Test database query performance and optimization."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test data
        self.sessions = []
        for i in range(100):
            session = SearchSession.objects.create(
                title=f"Performance Test Session {i+1}",
                description=f"Description for session {i+1}",
                created_by=self.user,
                status='draft' if i % 4 == 0 else 'executing'
            )
            self.sessions.append(session)
            
            # Create activities for each session
            for j in range(5):
                SessionActivity.objects.create(
                    session=session,
                    action='created' if j == 0 else 'updated',
                    user=self.user,
                    description=f"Activity {j+1} for session {i+1}"
                )
    
    def test_dashboard_query_performance(self):
        """Test dashboard query performance with large dataset."""
        start_time = time.time()
        
        # Simulate dashboard query (from DashboardView.get_queryset)
        queryset = SearchSession.objects.filter(
            created_by=self.user
        ).select_related('created_by').annotate(
            activity_count=Count('activities')
        ).order_by('-updated_at')[:12]
        
        # Force evaluation
        list(queryset)
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Should complete in under 100ms
        self.assertLess(query_time, 0.1, f"Dashboard query took {query_time:.3f}s (should be <0.1s)")
        
        # Verify query count efficiency
        with self.assertNumQueries(2):  # One for sessions, one for user select_related
            list(SearchSession.objects.filter(
                created_by=self.user
            ).select_related('created_by')[:12])
    
    def test_session_detail_query_optimization(self):
        """Test session detail view query optimization."""
        session = self.sessions[0]
        
        start_time = time.time()
        
        # Simulate session detail queries
        with self.assertNumQueries(3):  # Session, activities, stats
            retrieved_session = SearchSession.objects.select_related('created_by').get(id=session.id)
            activities = list(SessionActivity.objects.filter(session=session).order_by('-timestamp')[:5])
            activity_count = SessionActivity.objects.filter(session=session).count()
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Should complete in under 50ms
        self.assertLess(query_time, 0.05, f"Session detail queries took {query_time:.3f}s (should be <0.05s)")
    
    def test_bulk_operations_performance(self):
        """Test bulk operations performance."""
        # Test bulk creation
        start_time = time.time()
        
        new_sessions = []
        for i in range(50):
            new_sessions.append(SearchSession(
                title=f"Bulk Session {i+1}",
                description=f"Bulk description {i+1}",
                created_by=self.user,
                status='draft'
            ))
        
        SearchSession.objects.bulk_create(new_sessions)
        
        end_time = time.time()
        bulk_create_time = end_time - start_time
        
        # Should complete in under 100ms
        self.assertLess(bulk_create_time, 0.1, f"Bulk create took {bulk_create_time:.3f}s (should be <0.1s)")
        
        # Test bulk update
        start_time = time.time()
        
        SearchSession.objects.filter(
            title__startswith="Bulk Session"
        ).update(status='strategy_ready')
        
        end_time = time.time()
        bulk_update_time = end_time - start_time
        
        # Should complete in under 50ms
        self.assertLess(bulk_update_time, 0.05, f"Bulk update took {bulk_update_time:.3f}s (should be <0.05s)")
    
    def test_complex_filtering_performance(self):
        """Test complex filtering and search performance."""
        start_time = time.time()
        
        # Complex query with multiple filters and search
        complex_queryset = SearchSession.objects.filter(
            created_by=self.user,
            status__in=['draft', 'executing', 'strategy_ready']
        ).filter(
            Q(title__icontains='Performance') | 
            Q(description__icontains='session')
        ).select_related('created_by').prefetch_related('activities')
        
        # Force evaluation
        results = list(complex_queryset)
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Should complete in under 200ms
        self.assertLess(query_time, 0.2, f"Complex filtering took {query_time:.3f}s (should be <0.2s)")
        self.assertGreater(len(results), 0, "Complex query should return results")


class ViewPerformanceTests(TestCase):
    """Test view response time performance."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Create test sessions
        self.sessions = []
        for i in range(50):
            session = SearchSession.objects.create(
                title=f"Performance Session {i+1}",
                description=f"Test description {i+1}",
                created_by=self.user,
                status='draft'
            )
            self.sessions.append(session)
    
    def test_dashboard_response_time(self):
        """Test dashboard view response time."""
        start_time = time.time()
        
        response = self.client.get('/review/')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        # Should respond in under 200ms
        self.assertLess(response_time, 0.2, f"Dashboard response took {response_time:.3f}s (should be <0.2s)")
    
    def test_session_detail_response_time(self):
        """Test session detail view response time."""
        session = self.sessions[0]
        
        start_time = time.time()
        
        response = self.client.get(f'/review/session/{session.id}/')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        # Should respond in under 100ms
        self.assertLess(response_time, 0.1, f"Session detail response took {response_time:.3f}s (should be <0.1s)")
    
    def test_session_creation_performance(self):
        """Test session creation response time."""
        start_time = time.time()
        
        response = self.client.post('/review/create/', {
            'title': 'Performance Test Session',
            'description': 'Testing session creation performance'
        })
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        # Should respond in under 100ms
        self.assertLess(response_time, 0.1, f"Session creation took {response_time:.3f}s (should be <0.1s)")
    
    def test_ajax_endpoint_performance(self):
        """Test AJAX endpoint response times."""
        session = self.sessions[0]
        
        # Test stats endpoint
        start_time = time.time()
        response = self.client.get(f'/review/ajax/session/{session.id}/stats/')
        end_time = time.time()
        
        stats_response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        # AJAX should be very fast
        self.assertLess(stats_response_time, 0.05, f"AJAX stats took {stats_response_time:.3f}s (should be <0.05s)")
    
    def test_pagination_performance(self):
        """Test pagination performance with large datasets."""
        # Create more sessions to test pagination
        for i in range(50, 100):
            SearchSession.objects.create(
                title=f"Pagination Session {i+1}",
                description=f"Test description {i+1}",
                created_by=self.user,
                status='draft'
            )
        
        # Test first page
        start_time = time.time()
        response = self.client.get('/review/')
        end_time = time.time()
        
        first_page_time = end_time - start_time
        
        # Test second page
        start_time = time.time()
        response = self.client.get('/review/?page=2')
        end_time = time.time()
        
        second_page_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        # Pagination should be fast
        self.assertLess(first_page_time, 0.2, f"First page took {first_page_time:.3f}s")
        self.assertLess(second_page_time, 0.2, f"Second page took {second_page_time:.3f}s")
        
        # Pages should have similar performance
        time_difference = abs(first_page_time - second_page_time)
        self.assertLess(time_difference, 0.1, "Page response times should be consistent")


class MemoryUsageTests(TestCase):
    """Test memory usage and optimization."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def get_memory_usage(self):
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def test_large_dataset_memory_usage(self):
        """Test memory usage with large datasets."""
        initial_memory = self.get_memory_usage()
        
        # Create large dataset
        sessions = []
        for i in range(1000):
            sessions.append(SearchSession(
                title=f"Memory Test Session {i+1}",
                description=f"Memory test description {i+1}",
                created_by=self.user,
                status='draft'
            ))
        
        SearchSession.objects.bulk_create(sessions)
        
        # Test dashboard with large dataset
        response = self.client.get('/review/')
        self.assertEqual(response.status_code, 200)
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        self.assertLess(memory_increase, 100, f"Memory increased by {memory_increase:.2f}MB (should be <100MB)")
    
    def test_queryset_memory_efficiency(self):
        """Test QuerySet memory efficiency."""
        # Create sessions
        for i in range(500):
            SearchSession.objects.create(
                title=f"QuerySet Test Session {i+1}",
                description=f"Test description {i+1}",
                created_by=self.user,
                status='draft'
            )
        
        initial_memory = self.get_memory_usage()
        
        # Test iterator for large querysets
        session_count = 0
        for session in SearchSession.objects.filter(created_by=self.user).iterator():
            session_count += 1
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        self.assertEqual(session_count, 500)
        # Iterator should keep memory usage low
        self.assertLess(memory_increase, 50, f"Iterator memory increased by {memory_increase:.2f}MB (should be <50MB)")


class ConcurrentUserTests(TransactionTestCase):
    """Test concurrent user performance."""
    
    def setUp(self):
        self.users = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'user{i+1}',
                email=f'user{i+1}@example.com',
                password='testpass123'
            )
            self.users.append(user)
    
    def simulate_user_activity(self, user):
        """Simulate user activity (login, create session, view dashboard)."""
        client = Client()
        
        # Login
        login_success = client.login(username=user.username, password='testpass123')
        if not login_success:
            return {'error': 'Login failed'}
        
        start_time = time.time()
        
        # Create session
        response = client.post('/review/create/', {
            'title': f'Concurrent Session by {user.username}',
            'description': 'Testing concurrent user activity'
        })
        
        if response.status_code != 302:
            return {'error': 'Session creation failed'}
        
        # View dashboard
        response = client.get('/review/')
        
        if response.status_code != 200:
            return {'error': 'Dashboard access failed'}
        
        end_time = time.time()
        
        return {
            'user': user.username,
            'total_time': end_time - start_time,
            'success': True
        }
    
    def test_concurrent_user_performance(self):
        """Test performance with concurrent users."""
        start_time = time.time()
        
        # Simulate 10 concurrent users
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.simulate_user_activity, user) for user in self.users]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check results
        successful_users = [r for r in results if r.get('success')]
        failed_users = [r for r in results if not r.get('success')]
        
        self.assertEqual(len(successful_users), 10, f"All users should succeed, but {len(failed_users)} failed")
        
        # Average time per user should be reasonable
        avg_time = sum(r['total_time'] for r in successful_users) / len(successful_users)
        self.assertLess(avg_time, 1.0, f"Average user time was {avg_time:.3f}s (should be <1.0s)")
        
        # Total concurrent execution should be faster than sequential
        sequential_estimate = avg_time * 10
        efficiency = (sequential_estimate - total_time) / sequential_estimate
        self.assertGreater(efficiency, 0.5, f"Concurrent efficiency should be >50%, was {efficiency:.2%}")
    
    def test_database_connection_handling(self):
        """Test database connection handling under load."""
        def db_intensive_task():
            # Create sessions and activities
            user = User.objects.create_user(
                username=f'dbuser_{uuid.uuid4().hex[:8]}',
                email=f'dbuser_{uuid.uuid4().hex[:8]}@example.com',
                password='testpass123'
            )
            
            session = SearchSession.objects.create(
                title=f'DB Test Session {uuid.uuid4().hex[:8]}',
                description='Database intensive test',
                created_by=user,
                status='draft'
            )
            
            # Create multiple activities
            for i in range(5):
                SessionActivity.objects.create(
                    session=session,
                    action='updated',
                    user=user,
                    description=f'Activity {i+1}'
                )
            
            return session.id
        
        start_time = time.time()
        
        # Run 20 concurrent database operations
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(db_intensive_task) for _ in range(20)]
            session_ids = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All operations should succeed
        self.assertEqual(len(session_ids), 20, "All database operations should succeed")
        
        # Should complete in reasonable time
        self.assertLess(total_time, 5.0, f"Database operations took {total_time:.3f}s (should be <5.0s)")


class CachePerformanceTests(TestCase):
    """Test caching performance and optimization."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Clear cache
        cache.clear()
        
        # Create test data
        for i in range(20):
            SearchSession.objects.create(
                title=f"Cache Test Session {i+1}",
                description=f"Test description {i+1}",
                created_by=self.user,
                status='draft'
            )
    
    def test_cache_hit_performance(self):
        """Test cache hit vs miss performance."""
        cache_key = f"user_stats_{self.user.id}"
        
        # First request (cache miss)
        start_time = time.time()
        response = self.client.get('/review/')
        first_response_time = time.time() - start_time
        
        # Simulate caching stats
        stats_data = {
            'total_sessions': 20,
            'completed_sessions': 0,
            'active_sessions': 20
        }
        cache.set(cache_key, stats_data, 300)
        
        # Second request (cache hit)
        start_time = time.time()
        response = self.client.get('/review/')
        second_response_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        
        # Cache hit should be faster
        if first_response_time > 0.01:  # Only test if first response was measurable
            improvement = (first_response_time - second_response_time) / first_response_time
            self.assertGreater(improvement, 0, "Cache hit should be faster than cache miss")
    
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    })
    def test_performance_without_cache(self):
        """Test performance when cache is disabled."""
        start_time = time.time()
        
        response = self.client.get('/review/')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        # Should still perform reasonably without cache
        self.assertLess(response_time, 0.5, f"No-cache response took {response_time:.3f}s (should be <0.5s)")


class APIPerformanceTests(TestCase):
    """Test API endpoint performance."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Create test session
        self.session = SearchSession.objects.create(
            title="API Test Session",
            description="Test description",
            created_by=self.user,
            status='draft'
        )
    
    def test_json_response_performance(self):
        """Test JSON API response performance."""
        start_time = time.time()
        
        response = self.client.get(f'/review/ajax/session/{self.session.id}/stats/')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        
        # JSON responses should be very fast
        self.assertLess(response_time, 0.05, f"JSON response took {response_time:.3f}s (should be <0.05s)")
        
        # Verify JSON content
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('id', data)
    
    def test_post_request_performance(self):
        """Test POST request performance."""
        # Test archive endpoint
        self.session.status = 'completed'
        self.session.save()
        
        start_time = time.time()
        
        response = self.client.post(f'/review/ajax/session/{self.session.id}/archive/')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        
        # POST requests should be fast
        self.assertLess(response_time, 0.1, f"POST request took {response_time:.3f}s (should be <0.1s)")


class PerformanceBenchmarkReport:
    """Generate performance benchmark report."""
    
    @staticmethod
    def generate_report():
        """Generate comprehensive performance report."""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'benchmarks': {
                'database_queries': {
                    'dashboard_query_target': '<100ms',
                    'session_detail_target': '<50ms',
                    'bulk_operations_target': '<100ms',
                    'complex_filtering_target': '<200ms'
                },
                'view_responses': {
                    'dashboard_response_target': '<200ms',
                    'session_detail_target': '<100ms',
                    'session_creation_target': '<100ms',
                    'ajax_endpoints_target': '<50ms'
                },
                'memory_usage': {
                    'large_dataset_target': '<100MB increase',
                    'queryset_iterator_target': '<50MB increase'
                },
                'concurrent_users': {
                    'avg_user_time_target': '<1.0s',
                    'concurrent_efficiency_target': '>50%',
                    'database_operations_target': '<5.0s for 20 ops'
                },
                'cache_performance': {
                    'cache_hit_improvement': 'Should be faster than miss',
                    'no_cache_fallback_target': '<500ms'
                },
                'api_endpoints': {
                    'json_response_target': '<50ms',
                    'post_request_target': '<100ms'
                }
            },
            'recommendations': [
                'Monitor database query performance in production',
                'Implement database query optimization for slow queries',
                'Set up proper caching strategy for frequently accessed data',
                'Use database connection pooling for concurrent users',
                'Implement API response caching for read-heavy endpoints',
                'Monitor memory usage patterns under load',
                'Set up performance monitoring and alerting'
            ]
        }
        
        return report


# Performance test runner function
def run_performance_benchmarks():
    """Run all performance benchmarks and generate report."""
    print("Starting Performance Benchmarks...")
    print("=" * 50)
    
    # Import and run Django test runner
    from django.test.runner import DiscoverRunner
    
    test_runner = DiscoverRunner(verbosity=2, keepdb=True)
    
    # Run performance tests
    test_labels = [
        'apps.review_manager.tests_performance_benchmarks.DatabasePerformanceTests',
        'apps.review_manager.tests_performance_benchmarks.ViewPerformanceTests',
        'apps.review_manager.tests_performance_benchmarks.MemoryUsageTests',
        'apps.review_manager.tests_performance_benchmarks.ConcurrentUserTests',
        'apps.review_manager.tests_performance_benchmarks.CachePerformanceTests',
        'apps.review_manager.tests_performance_benchmarks.APIPerformanceTests'
    ]
    
    failures = test_runner.run_tests(test_labels)
    
    # Generate report
    report = PerformanceBenchmarkReport.generate_report()
    
    print("\nPerformance Benchmark Report")
    print("=" * 50)
    print(f"Generated: {report['timestamp']}")
    print("\nBenchmark Targets:")
    for category, targets in report['benchmarks'].items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for metric, target in targets.items():
            print(f"  - {metric.replace('_', ' ').title()}: {target}")
    
    print("\nRecommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print(f"\nTest Result: {'PASS' if failures == 0 else 'FAIL'}")
    print(f"Failed Tests: {failures}")
    
    return failures == 0