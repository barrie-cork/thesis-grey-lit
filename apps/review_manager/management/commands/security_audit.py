# apps/review_manager/management/commands/security_audit.py
"""
Management command to perform a comprehensive security audit of the Review Manager app.
Sprint 8: Security & Testing implementation.
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings
from apps.review_manager.models import SearchSession, SessionActivity, SessionStatusHistory

User = get_user_model()


class Command(BaseCommand):
    help = 'Perform comprehensive security audit of Review Manager app'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='security_audit.json',
            help='Output file for audit results'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to analyze (default: 30)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output'
        )
    
    def handle(self, *args, **options):
        """Perform the security audit."""
        self.stdout.write(
            self.style.SUCCESS('🔍 Starting Security Audit...\n')
        )
        
        audit_results = {
            'audit_timestamp': datetime.now().isoformat(),
            'audit_period_days': options['days'],
            'security_checks': {},
            'recommendations': [],
            'risk_level': 'LOW'
        }
        
        # Perform various security checks
        try:
            # 1. Check user access patterns
            self._check_user_access_patterns(audit_results, options['days'])
            
            # 2. Check session security
            self._check_session_security(audit_results, options['days'])
            
            # 3. Check activity anomalies
            self._check_activity_anomalies(audit_results, options['days'])
            
            # 4. Check permission violations
            self._check_permission_violations(audit_results, options['days'])
            
            # 5. Check system configuration
            self._check_system_configuration(audit_results)
            
            # 6. Check file permissions
            self._check_file_permissions(audit_results)
            
            # 7. Check database security
            self._check_database_security(audit_results)
            
            # 8. Analyze logs for security events
            self._analyze_security_logs(audit_results, options['days'])
            
            # Calculate overall risk level
            self._calculate_risk_level(audit_results)
            
            # Generate recommendations
            self._generate_recommendations(audit_results)
            
            # Output results
            self._output_results(audit_results, options)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Security audit failed: {str(e)}')
            )
            raise
    
    def _check_user_access_patterns(self, audit_results, days):
        """Check for unusual user access patterns."""
        self.stdout.write('Checking user access patterns...')
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Check for users with unusual activity
        users_with_activity = User.objects.filter(
            session_activities__timestamp__gte=cutoff_date
        ).annotate(
            activity_count=Count('session_activities')
        )
        
        high_activity_users = users_with_activity.filter(
            activity_count__gt=1000  # More than 1000 activities
        )
        
        # Check for users accessing many sessions
        users_session_access = User.objects.filter(
            created_sessions__created_at__gte=cutoff_date
        ).annotate(
            session_count=Count('created_sessions')
        )
        
        high_session_users = users_session_access.filter(
            session_count__gt=100  # More than 100 sessions
        )
        
        audit_results['security_checks']['user_access_patterns'] = {
            'high_activity_users': list(high_activity_users.values('username', 'activity_count')),
            'high_session_users': list(high_session_users.values('username', 'session_count')),
            'total_active_users': users_with_activity.count(),
            'risk_level': 'HIGH' if high_activity_users.exists() else 'LOW'
        }
    
    def _check_session_security(self, audit_results, days):
        """Check session security metrics."""
        self.stdout.write('Checking session security...')
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Check for failed sessions
        failed_sessions = SearchSession.objects.filter(
            status='failed',
            updated_at__gte=cutoff_date
        )
        
        # Check for sessions with many status changes
        sessions_with_many_changes = SearchSession.objects.filter(
            updated_at__gte=cutoff_date
        ).annotate(
            status_changes=Count('status_history')
        ).filter(status_changes__gt=10)
        
        # Check for rapid session creation
        rapid_creation = SearchSession.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        audit_results['security_checks']['session_security'] = {
            'failed_sessions_count': failed_sessions.count(),
            'sessions_with_many_changes': sessions_with_many_changes.count(),
            'rapid_creation_last_hour': rapid_creation,
            'total_sessions_period': SearchSession.objects.filter(
                created_at__gte=cutoff_date
            ).count(),
            'risk_level': 'HIGH' if rapid_creation > 50 or failed_sessions.count() > 100 else 'MEDIUM' if failed_sessions.count() > 10 else 'LOW'
        }
    
    def _check_activity_anomalies(self, audit_results, days):
        """Check for unusual activity patterns."""
        self.stdout.write('Checking activity anomalies...')
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Check for unusual activity types
        activity_counts = SessionActivity.objects.filter(
            timestamp__gte=cutoff_date
        ).values('action').annotate(count=Count('action')).order_by('-count')
        
        # Check for error activities
        error_activities = SessionActivity.objects.filter(
            timestamp__gte=cutoff_date,
            action__in=['ERROR', 'error_recovery', 'FAILED']
        )
        
        # Check for activities outside normal hours
        night_activities = SessionActivity.objects.filter(
            timestamp__gte=cutoff_date,
            timestamp__hour__lt=6  # Before 6 AM
        )
        
        audit_results['security_checks']['activity_anomalies'] = {
            'activity_distribution': list(activity_counts),
            'error_activities_count': error_activities.count(),
            'night_activities_count': night_activities.count(),
            'total_activities': SessionActivity.objects.filter(
                timestamp__gte=cutoff_date
            ).count(),
            'risk_level': 'HIGH' if error_activities.count() > 100 else 'MEDIUM' if error_activities.count() > 10 else 'LOW'
        }
    
    def _check_permission_violations(self, audit_results, days):
        """Check for potential permission violations."""
        self.stdout.write('Checking permission violations...')
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # This would be populated by security middleware logs
        # For now, we'll check for suspicious patterns
        
        # Check for users trying to access others' sessions
        # (This would come from security logs in a real implementation)
        
        audit_results['security_checks']['permission_violations'] = {
            'unauthorized_access_attempts': 0,  # Would be from logs
            'permission_denied_count': 0,       # Would be from logs
            'suspicious_patterns': [],          # Would be from log analysis
            'risk_level': 'LOW'
        }
    
    def _check_system_configuration(self, audit_results):
        """Check system configuration for security issues."""
        self.stdout.write('Checking system configuration...')
        
        config_issues = []
        
        # Check DEBUG setting
        if settings.DEBUG:
            config_issues.append('DEBUG is enabled in production')
        
        # Check ALLOWED_HOSTS
        if not settings.ALLOWED_HOSTS or '*' in settings.ALLOWED_HOSTS:
            config_issues.append('ALLOWED_HOSTS not properly configured')
        
        # Check SECRET_KEY
        if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 50:
            config_issues.append('SECRET_KEY is weak or missing')
        
        # Check CSRF settings
        if not getattr(settings, 'CSRF_COOKIE_SECURE', False) and not settings.DEBUG:
            config_issues.append('CSRF_COOKIE_SECURE should be True in production')
        
        # Check session settings
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False) and not settings.DEBUG:
            config_issues.append('SESSION_COOKIE_SECURE should be True in production')
        
        audit_results['security_checks']['system_configuration'] = {
            'issues': config_issues,
            'debug_enabled': settings.DEBUG,
            'allowed_hosts_configured': bool(settings.ALLOWED_HOSTS and '*' not in settings.ALLOWED_HOSTS),
            'risk_level': 'HIGH' if config_issues else 'LOW'
        }
    
    def _check_file_permissions(self, audit_results):
        """Check file system permissions."""
        self.stdout.write('Checking file permissions...')
        
        permission_issues = []
        
        # Check key directories
        key_paths = [
            settings.BASE_DIR,
            os.path.join(settings.BASE_DIR, 'apps'),
            os.path.join(settings.BASE_DIR, 'logs') if os.path.exists(os.path.join(settings.BASE_DIR, 'logs')) else None
        ]
        
        for path in key_paths:
            if path and os.path.exists(path):
                stat_info = os.stat(path)
                permissions = oct(stat_info.st_mode)[-3:]
                
                # Check if permissions are too open
                if permissions in ['777', '776', '775']:
                    permission_issues.append(f'{path} has overly permissive permissions: {permissions}')
        
        audit_results['security_checks']['file_permissions'] = {
            'issues': permission_issues,
            'risk_level': 'HIGH' if permission_issues else 'LOW'
        }
    
    def _check_database_security(self, audit_results):
        """Check database security configuration."""
        self.stdout.write('Checking database security...')
        
        db_config = settings.DATABASES['default']
        security_issues = []
        
        # Check if using SQLite in production
        if db_config['ENGINE'].endswith('sqlite3') and not settings.DEBUG:
            security_issues.append('Using SQLite in production environment')
        
        # Check for default passwords
        if db_config.get('PASSWORD') in ['', 'password', 'admin', '123456']:
            security_issues.append('Database using weak or default password')
        
        # Check SSL configuration
        if not db_config.get('OPTIONS', {}).get('sslmode') and not settings.DEBUG:
            security_issues.append('Database connection not using SSL')
        
        audit_results['security_checks']['database_security'] = {
            'engine': db_config['ENGINE'],
            'issues': security_issues,
            'risk_level': 'HIGH' if security_issues else 'LOW'
        }
    
    def _analyze_security_logs(self, audit_results, days):
        """Analyze security logs for suspicious activity."""
        self.stdout.write('Analyzing security logs...')
        
        log_analysis = {
            'security_events': 0,
            'error_events': 0,
            'suspicious_patterns': [],
            'log_files_found': False
        }
        
        # Check if log files exist
        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        if os.path.exists(logs_dir):
            log_analysis['log_files_found'] = True
            
            security_log = os.path.join(logs_dir, 'security.log')
            if os.path.exists(security_log):
                try:
                    with open(security_log, 'r') as f:
                        lines = f.readlines()
                        log_analysis['security_events'] = len(lines)
                        
                        # Look for suspicious patterns
                        for line in lines[-100:]:  # Last 100 lines
                            if 'CRITICAL' in line or 'unauthorized' in line.lower():
                                log_analysis['suspicious_patterns'].append(line.strip())
                except Exception as e:
                    log_analysis['error'] = str(e)
        
        audit_results['security_checks']['log_analysis'] = log_analysis
        audit_results['security_checks']['log_analysis']['risk_level'] = (
            'HIGH' if log_analysis['suspicious_patterns'] else 'LOW'
        )
    
    def _calculate_risk_level(self, audit_results):
        """Calculate overall risk level based on all checks."""
        risk_scores = []
        
        for check_name, check_data in audit_results['security_checks'].items():
            risk_level = check_data.get('risk_level', 'LOW')
            if risk_level == 'HIGH':
                risk_scores.append(3)
            elif risk_level == 'MEDIUM':
                risk_scores.append(2)
            else:
                risk_scores.append(1)
        
        if not risk_scores:
            overall_risk = 'LOW'
        else:
            avg_risk = sum(risk_scores) / len(risk_scores)
            if avg_risk >= 2.5:
                overall_risk = 'HIGH'
            elif avg_risk >= 1.5:
                overall_risk = 'MEDIUM'
            else:
                overall_risk = 'LOW'
        
        audit_results['risk_level'] = overall_risk
    
    def _generate_recommendations(self, audit_results):
        """Generate security recommendations based on audit results."""
        recommendations = []
        
        for check_name, check_data in audit_results['security_checks'].items():
            risk_level = check_data.get('risk_level', 'LOW')
            
            if check_name == 'system_configuration' and risk_level in ['HIGH', 'MEDIUM']:
                recommendations.extend([
                    'Review Django security settings',
                    'Ensure DEBUG=False in production',
                    'Configure ALLOWED_HOSTS properly',
                    'Enable secure cookie settings'
                ])
            
            elif check_name == 'user_access_patterns' and risk_level == 'HIGH':
                recommendations.extend([
                    'Review users with unusually high activity',
                    'Implement additional monitoring for power users',
                    'Consider rate limiting per user'
                ])
            
            elif check_name == 'session_security' and risk_level in ['HIGH', 'MEDIUM']:
                recommendations.extend([
                    'Investigate failed sessions',
                    'Review rapid session creation patterns',
                    'Implement stricter session validation'
                ])
            
            elif check_name == 'file_permissions' and risk_level == 'HIGH':
                recommendations.extend([
                    'Fix overly permissive file permissions',
                    'Review directory access controls',
                    'Implement proper file security'
                ])
        
        # Add general recommendations
        recommendations.extend([
            'Enable comprehensive security logging',
            'Implement real-time security monitoring',
            'Regular security audits and reviews',
            'Keep dependencies updated',
            'Implement backup and recovery procedures'
        ])
        
        audit_results['recommendations'] = list(set(recommendations))  # Remove duplicates
    
    def _output_results(self, audit_results, options):
        """Output audit results."""
        # Save to file
        output_file = options['output']
        with open(output_file, 'w') as f:
            json.dump(audit_results, f, indent=2, default=str)
        
        # Display summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS('🔒 Security Audit Complete')
        )
        self.stdout.write('='*60)
        
        # Risk level with color coding
        risk_level = audit_results['risk_level']
        if risk_level == 'HIGH':
            risk_style = self.style.ERROR
        elif risk_level == 'MEDIUM':
            risk_style = self.style.WARNING
        else:
            risk_style = self.style.SUCCESS
        
        self.stdout.write(f'\n📊 Overall Risk Level: {risk_style(risk_level)}')
        
        # Show check results
        self.stdout.write('\n📋 Security Check Results:')
        for check_name, check_data in audit_results['security_checks'].items():
            risk = check_data.get('risk_level', 'LOW')
            if risk == 'HIGH':
                icon = '❌'
                style = self.style.ERROR
            elif risk == 'MEDIUM':
                icon = '⚠️'
                style = self.style.WARNING
            else:
                icon = '✅'
                style = self.style.SUCCESS
            
            self.stdout.write(f'  {icon} {check_name.replace("_", " ").title()}: {style(risk)}')
        
        # Show top recommendations
        self.stdout.write('\n💡 Top Recommendations:')
        for i, rec in enumerate(audit_results['recommendations'][:5], 1):
            self.stdout.write(f'  {i}. {rec}')
        
        if len(audit_results['recommendations']) > 5:
            self.stdout.write(f'  ... and {len(audit_results["recommendations"]) - 5} more')
        
        self.stdout.write(f'\n📄 Detailed results saved to: {output_file}')
        
        if options['verbose']:
            self.stdout.write('\n📝 Detailed Results:')
            self.stdout.write(json.dumps(audit_results, indent=2, default=str))
