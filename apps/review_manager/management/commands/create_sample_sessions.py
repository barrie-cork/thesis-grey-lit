from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.review_manager.models import SearchSession, SessionActivity
from django.utils import timezone
import random

# Use the custom User model
User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample review sessions for testing the dashboard'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of sessions to create')
        parser.add_argument('--username', type=str, default='testuser', help='Username for session owner')

    def handle(self, *args, **options):
        username = options['username']
        count = options['count']
        
        # Get or create user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='testpass123'
            )
            self.stdout.write(f'Created user: {username}')

        # Sample data
        titles = [
            'Diabetes Management Guidelines Review',
            'COVID-19 Treatment Protocols',
            'Mental Health Interventions Study',
            'Cancer Screening Best Practices',
            'Hypertension Management Guidelines',
            'Pediatric Nutrition Guidelines',
            'Elderly Care Protocol Review',
            'Emergency Medicine Procedures',
            'Chronic Pain Management',
            'Vaccination Schedule Guidelines',
            'Wound Care Best Practices',
            'Surgical Safety Protocols',
            'Patient Safety Measures',
            'Quality Improvement Methods',
            'Clinical Decision Support Tools'
        ]
        
        descriptions = [
            'Systematic review of current guidelines for managing diabetes in primary care settings.',
            'Comprehensive analysis of treatment protocols developed during the COVID-19 pandemic.',
            'Review of evidence-based mental health interventions for adult populations.',
            'Analysis of cancer screening recommendations from major health organizations.',
            'Review of hypertension management guidelines across different populations.',
            'Systematic review of pediatric nutrition guidelines and recommendations.',
            'Analysis of care protocols for elderly patients in various healthcare settings.',
            'Review of emergency medicine procedures and their effectiveness.',
            'Systematic review of chronic pain management approaches and guidelines.',
            'Analysis of vaccination schedule recommendations from health authorities.',
            'Review of wound care best practices across different clinical settings.',
            'Systematic review of surgical safety protocols and their implementation.',
            'Analysis of patient safety measures in healthcare organizations.',
            'Review of quality improvement methodologies in healthcare delivery.',
            'Analysis of clinical decision support tools and their effectiveness.'
        ]
        
        statuses = [
            'draft', 'strategy_ready', 'executing', 'processing', 
            'ready_for_review', 'in_review', 'completed', 'failed', 'archived'
        ]
        
        created_sessions = []
        
        for i in range(count):
            title = random.choice(titles)
            if SearchSession.objects.filter(title=title, created_by=user).exists():
                title = f"{title} ({i+1})"
            
            session = SearchSession.objects.create(
                title=title,
                description=random.choice(descriptions),
                status=random.choice(statuses),
                created_by=user,
                # Removed PIC framework fields - these belong in Search Strategy app
            )
            
            # Create activity log
            SessionActivity.objects.create(
                session=session,
                activity_type=SessionActivity.ActivityType.CREATED,
                description=f'Session "{session.title}" created by {user.username}',
                performed_by=user
            )
            
            # Add some additional activities for non-draft sessions
            if session.status != 'draft':
                SessionActivity.objects.create(
                    session=session,
                    activity_type=SessionActivity.ActivityType.STATUS_CHANGED,
                    description=f'Status changed from draft to {session.get_status_display()}',
                    old_status='draft',
                    new_status=session.status,
                    performed_by=user
                )
            
            created_sessions.append(session)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(created_sessions)} sample sessions for user "{username}"'
            )
        )
        
        # Display summary
        status_counts = {}
        for session in created_sessions:
            status_counts[session.get_status_display()] = status_counts.get(session.get_status_display(), 0) + 1
        
        self.stdout.write('\nStatus distribution:')
        for status, count in status_counts.items():
            self.stdout.write(f'  {status}: {count}')
