#!/usr/bin/env python
"""
Sprint 6 Testing Script: Timeline and History Features

This script creates comprehensive test data for testing the Sprint 6 advanced features:
- Status change tracking with signals
- Activity timeline
- Status history
- User statistics

Run this script from the Django shell or as a management command.
"""

import os
import sys
import django
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thesis_grey_lit.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.review_manager.models import (
    SearchSession, SessionActivity, SessionStatusHistory, 
    SessionArchive, UserSessionStats
)
from apps.review_manager.signals import SignalUtils

User = get_user_model()

def create_comprehensive_test_data():
    """Create comprehensive test data for Sprint 6 features"""
    
    print("🚀 Creating Sprint 6 Test Data...")
    print("=" * 50)
    
    # Get or create test user
    user = User.objects.first()
    if not user:
        print("❌ No users found! Please create a superuser first:")
        print("   python manage.py createsuperuser")
        return
    
    print(f"📤 Using user: {user.username}")
    
    # Create multiple test sessions with different scenarios
    test_sessions = []
    
    # Session 1: Complete workflow progression
    print("\n1. Creating session with complete workflow progression...")
    session1 = SearchSession.objects.create(
        title="Machine Learning in Healthcare Review",
        description="Systematic review of machine learning applications in healthcare diagnostics and treatment outcomes",
        created_by=user,
        status='draft'
    )
    test_sessions.append(('Complete Workflow', session1))
    
    # Simulate time-based progression with detailed reasons
    statuses_with_delays = [
        ('strategy_ready', 2, 'Completed comprehensive search strategy definition with PIC framework'),
        ('executing', 1, 'Initiated search execution across 5 databases (PubMed, Scopus, Web of Science, IEEE, ACM)'),
        ('processing', 3, 'Search execution completed successfully, processing 2,847 results'),
        ('ready_for_review', 1, 'Results processed and deduplicated, 1,234 unique articles ready for screening'),
        ('in_review', 5, 'Started systematic review process, completed title/abstract screening'),
        ('completed', 2, 'Review completed with 89 included studies, ready for report generation'),
    ]
    
    base_time = timezone.now() - timedelta(days=15)
    
    for i, (status, delay_hours, reason) in enumerate(statuses_with_delays):
        # Set the creation time to simulate progression over time
        session1.created_at = base_time + timedelta(hours=sum(d for _, d, _ in statuses_with_delays[:i]))
        
        # Set change context with detailed information
        SignalUtils.set_change_context(
            session1,
            user=user,
            reason=reason,
            auto_transition=False,
            workflow_step=i+1,
            total_steps=len(statuses_with_delays)
        )
        
        # Update status
        session1.status = status
        session1.save()
        
        # Add artificial delay to last update time
        session1.updated_at = base_time + timedelta(hours=sum(d for _, d, _ in statuses_with_delays[:i+1]))
        session1.save(update_fields=['updated_at'])
        
        print(f"   ✅ Progressed to {status}: {reason}")
    
    # Set completion date
    session1.completed_date = session1.updated_at
    session1.save(update_fields=['completed_date'])
    
    # Session 2: Session with error and recovery
    print("\n2. Creating session with error and recovery...")
    session2 = SearchSession.objects.create(
        title="AI Ethics in Clinical Decision Making",
        description="Comprehensive review of ethical considerations in AI-powered clinical decision support systems",
        created_by=user,
        status='draft',
        created_at=timezone.now() - timedelta(days=8)
    )
    test_sessions.append(('Error Recovery', session2))
    
    # Progress to executing, then fail, then recover
    error_progression = [
        ('strategy_ready', 'Search strategy defined for AI ethics literature'),
        ('executing', 'Started search execution across medical and ethics databases'),
        ('failed', 'Database timeout error during large query execution on PubMed'),
        ('executing', 'Resumed search execution with optimized query parameters'),
        ('processing', 'Search completed successfully after query optimization'),
        ('ready_for_review', 'Results processed, 567 articles ready for ethical analysis'),
    ]
    
    for i, (status, reason) in enumerate(error_progression):
        SignalUtils.set_change_context(
            session2,
            user=user,
            reason=reason,
            error_details={'database': 'PubMed', 'error_code': 'TIMEOUT'} if status == 'failed' else {}
        )
        session2.status = status
        session2.save()
        print(f"   ✅ {status}: {reason}")
    
    # Session 3: Archived session
    print("\n3. Creating archived session...")
    session3 = SearchSession.objects.create(
        title="Telemedicine Adoption During COVID-19",
        description="Rapid review of telemedicine adoption patterns and effectiveness during the COVID-19 pandemic",
        created_by=user,
        status='completed',
        created_at=timezone.now() - timedelta(days=30),
        completed_date=timezone.now() - timedelta(days=5)
    )
    test_sessions.append(('Archived', session3))
    
    # Archive the session
    SignalUtils.set_change_context(
        session3,
        user=user,
        reason='Archiving completed review after successful publication',
        archive_reason='Study published in Journal of Medical Internet Research'
    )
    session3.status = 'archived'
    session3.save()
    print(f"   ✅ Archived session: {session3.title}")
    
    # Session 4: Recently created draft (minimal activity)
    print("\n4. Creating recent draft session...")
    session4 = SearchSession.objects.create(
        title="Virtual Reality in Pain Management",
        description="Systematic review of VR applications for chronic pain management and patient outcomes",
        created_by=user,
        status='draft',
        created_at=timezone.now() - timedelta(hours=2)
    )
    test_sessions.append(('Recent Draft', session4))
    print(f"   ✅ Created recent draft: {session4.title}")
    
    # Session 5: Long-running in-review session
    print("\n5. Creating long-running review session...")
    session5 = SearchSession.objects.create(
        title="Blockchain in Healthcare Data Security",
        description="Comprehensive analysis of blockchain technology applications for healthcare data security and privacy",
        created_by=user,
        status='in_review',
        created_at=timezone.now() - timedelta(days=45),
        start_date=timezone.now() - timedelta(days=40)
    )
    test_sessions.append(('Long Review', session5))
    
    # Add some manual activities to show extended review process
    activities = [
        ('REVIEW_STARTED', 'Began systematic screening of 892 blockchain healthcare articles'),
        ('COMMENT', 'Note: Focus on privacy-preserving techniques and HIPAA compliance'),
        ('MODIFIED', 'Updated inclusion criteria to focus on peer-reviewed publications only'),
        ('COMMENT', 'Progress update: Completed screening of 445/892 articles (50%)'),
        ('COMMENT', 'Identified 67 relevant studies for full-text review'),
    ]
    
    for i, (activity_type, description) in enumerate(activities):
        activity_time = timezone.now() - timedelta(days=35-i*3)
        SessionActivity.objects.create(
            session=session5,
            activity_type=activity_type,
            description=description,
            performed_by=user,
            performed_at=activity_time,
            metadata={
                'review_progress': (i+1) / len(activities) * 100,
                'manual_entry': True
            }
        )
    
    print(f"   ✅ Created in-review session with {len(activities)} activities")
    
    # Update user statistics
    print("\n6. Updating user statistics...")
    user_stats = UserSessionStats.update_user_stats(user)
    print(f"   ✅ User stats updated:")
    print(f"      - Total sessions: {user_stats.total_sessions}")
    print(f"      - Completed sessions: {user_stats.completed_sessions}")
    print(f"      - Completion rate: {user_stats.completion_rate:.1f}%")
    print(f"      - Productivity score: {user_stats.productivity_score:.1f}")
    
    # Display summary and URLs
    print("\n" + "=" * 50)
    print("🎉 Sprint 6 Test Data Created Successfully!")
    print("=" * 50)
    
    print("\n📊 Test Sessions Created:")
    for session_type, session in test_sessions:
        print(f"   {session_type}: {session.title}")
        print(f"   - ID: {session.id}")
        print(f"   - Status: {session.get_status_display()}")
        print(f"   - Activities: {session.activities.count()}")
        print(f"   - Status Changes: {session.status_history.count()}")
        print()
    
    print("🔗 Test URLs to Visit:")
    print("=" * 30)
    
    for session_type, session in test_sessions:
        print(f"\n{session_type} Session (ID: {session.id}):")
        print(f"   📄 Session Detail:     http://localhost:8000/review/{session.id}/")
        print(f"   📋 Activity Timeline:  http://localhost:8000/review/{session.id}/timeline/")
        print(f"   📈 Status History:     http://localhost:8000/review/{session.id}/history/")
    
    print(f"\n🌟 Main Dashboard:        http://localhost:8000/review/")
    print(f"📊 Analytics Dashboard:   http://localhost:8000/review/analytics/")
    print(f"📦 Archive Management:    http://localhost:8000/review/archives/")
    
    print("\n🧪 Recommended Testing Sequence:")
    print("1. Visit the main dashboard to see all sessions")
    print("2. Test the complete workflow session timeline (lots of activities)")
    print("3. Check the error recovery session history (shows failures and recovery)")
    print("4. Visit analytics dashboard to see user statistics")
    print("5. Test archive management to see archived sessions")
    print("6. Try the export functionality on timeline/history pages")
    
    print(f"\n✨ Ready to test Sprint 6 advanced features!")
    
    return test_sessions

def clean_test_data():
    """Clean up test data if needed"""
    print("🧹 Cleaning up existing test data...")
    
    # Delete test sessions (this will cascade to activities and history)
    test_titles = [
        "Machine Learning in Healthcare Review",
        "AI Ethics in Clinical Decision Making", 
        "Telemedicine Adoption During COVID-19",
        "Virtual Reality in Pain Management",
        "Blockchain in Healthcare Data Security"
    ]
    
    deleted_count = 0
    for title in test_titles:
        sessions = SearchSession.objects.filter(title=title)
        count = sessions.count()
        sessions.delete()
        deleted_count += count
    
    print(f"   ✅ Deleted {deleted_count} test sessions")

if __name__ == "__main__":
    print("Sprint 6 Testing: Timeline and History Features")
    print("=" * 50)
    
    # Ask user what to do
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_test_data()
    else:
        # Clean existing test data first
        clean_test_data()
        
        # Create new test data
        test_sessions = create_comprehensive_test_data()
        
        print("\n🚀 Test data creation complete!")
        print("   Start your Django server: python manage.py runserver")
        print("   Then visit the URLs listed above to test Sprint 6 features.")
