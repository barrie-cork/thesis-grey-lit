# Sprint 6 Django Shell Test Commands
# Run these commands in Django shell: python manage.py shell

# Import required modules
from apps.review_manager.models import SearchSession, SessionActivity, UserSessionStats
from django.contrib.auth import get_user_model
from apps.review_manager.signals import SignalUtils
from django.utils import timezone

# Get user
User = get_user_model()
user = User.objects.first()  # Your admin user

# Create a test session
session1 = SearchSession.objects.create(
    title="Machine Learning in Healthcare Review",
    description="Systematic review of machine learning applications in healthcare diagnostics",
    created_by=user,
    status='draft'
)

print(f"✅ Created session with ID: {session1.id}")

# Simulate status progression with reasons
print("🔄 Simulating status progression...")

# Progress to strategy_ready
SignalUtils.set_change_context(
    session1,
    user=user,
    reason='Completed search strategy definition with PIC framework'
)
session1.status = 'strategy_ready'
session1.save()
print(f"   ✅ Progressed to strategy_ready")

# Progress to executing
SignalUtils.set_change_context(
    session1,
    user=user,
    reason='Search execution started across multiple databases'
)
session1.status = 'executing'
session1.save()
print(f"   ✅ Progressed to executing")

# Progress to processing
SignalUtils.set_change_context(
    session1,
    user=user,
    reason='Search execution completed, processing results'
)
session1.status = 'processing'
session1.save()
print(f"   ✅ Progressed to processing")

# Progress to completed
SignalUtils.set_change_context(
    session1,
    user=user,
    reason='Review process completed successfully'
)
session1.status = 'completed'
session1.save()
print(f"   ✅ Progressed to completed")

# Check what was created
print(f"\n📊 Session Progress Summary:")
print(f"   Session ID: {session1.id}")
print(f"   Current Status: {session1.get_status_display()}")
print(f"   Total Activities: {session1.activities.count()}")
print(f"   Status Changes: {session1.status_history.count()}")

# Update user stats
stats = UserSessionStats.update_user_stats(user)
print(f"\n📈 User Statistics:")
print(f"   Total Sessions: {stats.total_sessions}")
print(f"   Completed Sessions: {stats.completed_sessions}")
print(f"   Completion Rate: {stats.completion_rate:.1f}%")

# Display test URLs
print(f"\n🔗 Test these URLs (replace {session1.id} with your session ID):")
print(f"   Session Detail:    http://localhost:8000/review/{session1.id}/")
print(f"   Activity Timeline: http://localhost:8000/review/{session1.id}/timeline/")
print(f"   Status History:    http://localhost:8000/review/{session1.id}/history/")
print(f"   Main Dashboard:    http://localhost:8000/review/")

print(f"\n✨ Sprint 6 test session created! Session ID: {session1.id}")
