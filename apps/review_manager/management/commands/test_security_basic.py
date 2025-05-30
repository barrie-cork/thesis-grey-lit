# apps/review_manager/management/commands/test_security_basic.py
"""
Basic security test runner for Sprint 8.
"""

from django.core.management.base import BaseCommand, CommandError
from django.test.utils import get_runner
from django.conf import settings
import sys
import time


class Command(BaseCommand):
    help = 'Run basic security tests for Review Manager Sprint 8'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Run tests with verbose output',
        )
    
    def handle(self, *args, **options):
        """Run the basic security test suite."""
        self.stdout.write(
            self.style.SUCCESS('🔍 Starting Basic Security Tests...\n')
        )
        
        # Set up test runner
        test_runner_class = get_runner(settings)
        test_runner = test_runner_class(
            verbosity=2 if options['verbose'] else 1,
            interactive=False,
            keepdb=True
        )
        
        start_time = time.time()
        
        try:
            # Run basic security tests
            self.stdout.write('Running basic security tests...')
            result = test_runner.run_tests(['apps.review_manager.tests_sprint8_fixed.BasicSecurityTests'])
            if result:
                raise CommandError('Basic security tests failed')
            
            self.stdout.write('Running ownership decorator tests...')
            result = test_runner.run_tests(['apps.review_manager.tests_sprint8_fixed.OwnershipDecoratorTests'])
            if result:
                raise CommandError('Ownership decorator tests failed')
            
            self.stdout.write('Running permission tests...')
            result = test_runner.run_tests(['apps.review_manager.tests_sprint8_fixed.SessionPermissionTests'])
            if result:
                raise CommandError('Permission tests failed')
            
            self.stdout.write('Running integration tests...')
            result = test_runner.run_tests(['apps.review_manager.tests_sprint8_fixed.IntegrationSecurityTests'])
            if result:
                raise CommandError('Integration tests failed')
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Summary
            self.stdout.write('\\n' + '='*60)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Basic Security Tests Passed! '
                    f'({duration:.2f} seconds)'
                )
            )
            self.stdout.write('='*60)
            
            # Security checklist
            self.stdout.write('\\n📋 Security Features Verified:')
            security_features = [
                '✅ Session ownership validation',
                '✅ Permission-based access control',
                '✅ Cross-user data isolation',
                '✅ Status-based operation restrictions',
                '✅ Security decorator functionality',
                '✅ Basic audit capabilities'
            ]
            
            for feature in security_features:
                self.stdout.write(f'  {feature}')
            
            self.stdout.write('\\n🔒 Core Security Implementation Working!')
            
        except CommandError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Security tests failed: {e}')
            )
            sys.exit(1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Unexpected error: {e}')
            )
            import traceback
            traceback.print_exc()
            sys.exit(1)
