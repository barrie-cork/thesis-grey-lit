#!/usr/bin/env python
"""
Verification script for Django Grey Literature Review Application
Checks that all critical fixes have been applied and the system is ready.
"""

import os
import sys
import django
from pathlib import Path

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thesis_grey_project.settings.local')
    django.setup()

def check_custom_user_model():
    """Verify custom User model is properly configured"""
    from django.conf import settings
    from django.contrib.auth import get_user_model
    
    print("🔍 Checking Custom User Model...")
    
    # Check AUTH_USER_MODEL setting
    if hasattr(settings, 'AUTH_USER_MODEL') and settings.AUTH_USER_MODEL == 'accounts.User':
        print("  ✅ AUTH_USER_MODEL correctly set to 'accounts.User'")
    else:
        print("  ❌ AUTH_USER_MODEL not set correctly")
        return False
    
    # Check User model is accessible
    try:
        User = get_user_model()
        print(f"  ✅ Custom User model loaded: {User}")
    except Exception as e:
        print(f"  ❌ Error loading User model: {e}")
        return False
    
    return True

def check_field_migration():
    """Verify field migration is complete in models"""
    print("🔍 Checking Field Migration...")
    
    try:
        from apps.review_manager.models import SessionActivity
        
        # Check if new field names exist
        activity_fields = [field.name for field in SessionActivity._meta.fields]
        
        required_fields = ['action', 'user', 'timestamp', 'details']
        old_fields = ['activity_type', 'performed_by', 'performed_at', 'metadata']
        
        missing_fields = [field for field in required_fields if field not in activity_fields]
        old_fields_present = [field for field in old_fields if field in activity_fields]
        
        if not missing_fields and not old_fields_present:
            print("  ✅ All field migrations completed successfully")
            print(f"  ✅ Current fields: {activity_fields}")
            return True
        else:
            if missing_fields:
                print(f"  ❌ Missing new fields: {missing_fields}")
            if old_fields_present:
                print(f"  ❌ Old fields still present: {old_fields_present}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error checking fields: {e}")
        return False

def check_model_functionality():
    """Test basic model functionality"""
    print("🔍 Testing Model Functionality...")
    
    try:
        from django.contrib.auth import get_user_model
        from apps.review_manager.models import SearchSession, SessionActivity
        
        User = get_user_model()
        
        # Test user creation
        test_user = User.objects.create_user(
            username='test_verification_user',
            email='test@example.com',
            password='testpass123'
        )
        print("  ✅ Test user created successfully")
        
        # Test session creation
        test_session = SearchSession.objects.create(
            title='Verification Test Session',
            description='Testing field migration',
            created_by=test_user
        )
        print("  ✅ Test session created successfully")
        
        # Test activity logging with new field names
        activity = SessionActivity.log_activity(
            session=test_session,
            action='CREATED',
            description='Session created during verification',
            user=test_user
        )
        print("  ✅ Activity logged with new field names successfully")
        
        # Test field access
        print(f"  ✅ Activity action: {activity.action}")
        print(f"  ✅ Activity user: {activity.user}")
        print(f"  ✅ Activity timestamp: {activity.timestamp}")
        
        # Cleanup
        test_session.delete()
        test_user.delete()
        print("  ✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error in model functionality test: {e}")
        return False

def check_app_structure():
    """Verify app structure and key files"""
    print("🔍 Checking Application Structure...")
    
    required_files = [
        'apps/accounts/models.py',
        'apps/review_manager/models.py',
        'apps/review_manager/views.py',
        'apps/review_manager/tests.py',
        'apps/review_manager/urls.py',
        'thesis_grey_project/settings/base.py',
        'manage.py',
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if not missing_files:
        print("  ✅ All required files present")
        return True
    else:
        print(f"  ❌ Missing files: {missing_files}")
        return False

def run_verification():
    """Run all verification checks"""
    print("🚀 Django Grey Literature Review Application - Setup Verification")
    print("=" * 70)
    
    checks = [
        ("Application Structure", check_app_structure),
        ("Custom User Model", check_custom_user_model),
        ("Field Migration", check_field_migration),
        ("Model Functionality", check_model_functionality),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        print(f"\n{check_name}")
        print("-" * 30)
        results[check_name] = check_func()
    
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{check_name:<25} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Your application is ready for development.")
        print("🚀 Next steps:")
        print("   1. Run: python manage.py runserver")
        print("   2. Access: http://localhost:8000/review/")
        print("   3. Test the dashboard and session creation")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        print("💡 Check the setup guide for troubleshooting steps.")
    
    return all_passed

if __name__ == "__main__":
    try:
        setup_django()
        success = run_verification()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Critical error during verification: {e}")
        print("💡 Make sure you're in the project root and virtual environment is activated")
        sys.exit(1)
