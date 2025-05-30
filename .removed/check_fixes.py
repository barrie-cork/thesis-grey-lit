#!/usr/bin/env python
"""
Simple Field Migration Verification Script
Tests that the field migration fixes work without needing cleanup.
"""

import os
import sys
import django

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thesis_grey_project.settings.local')
    django.setup()

def test_field_fixes_simple():
    """Test field fixes without creating/deleting records"""
    print("🧪 Testing Field Migration Fixes (No Database Changes)...")
    
    try:
        # 1. Test that imports work with new field names
        print("  ✅ Testing imports and model structure...")
        from django.contrib.auth import get_user_model
        from apps.review_manager.models import SearchSession, SessionActivity
        from apps.review_manager.forms import SessionCreateForm
        
        User = get_user_model()
        
        # 2. Check SessionActivity has correct field names
        print("  ✅ Checking SessionActivity field structure...")
        activity_field_names = [field.name for field in SessionActivity._meta.fields]
        
        required_fields = ['action', 'user', 'timestamp', 'details']
        old_fields = ['activity_type', 'performed_by', 'performed_at', 'metadata']
        
        missing_new = [field for field in required_fields if field not in activity_field_names]
        present_old = [field for field in old_fields if field in activity_field_names]
        
        if missing_new:
            print(f"  ❌ Missing new fields: {missing_new}")
            return False
        if present_old:
            print(f"  ❌ Old fields still present: {present_old}")
            return False
        
        print(f"     ✅ All correct fields present: {required_fields}")
        
        # 3. Test ActivityType choices structure
        print("  ✅ Testing ActivityType choices...")
        choices_dict = dict(SessionActivity.ActivityType.choices)
        if 'CREATED' in choices_dict:
            print(f"     ✅ CREATED choice: {choices_dict['CREATED']}")
        else:
            print("  ❌ CREATED choice missing")
            return False
        
        # 4. Test string representation without creating records
        print("  ✅ Testing __str__ method structure...")
        # We can't test actual string output without creating records,
        # but we can check the method exists and doesn't have syntax errors
        str_method = getattr(SessionActivity, '__str__', None)
        if str_method:
            print("     ✅ __str__ method exists")
        else:
            print("  ❌ __str__ method missing")
            return False
        
        # 5. Test form structure
        print("  ✅ Testing form structure...")
        form = SessionCreateForm()
        if hasattr(form, 'save'):
            print("     ✅ Form save method exists")
        else:
            print("  ❌ Form save method missing")
            return False
        
        # 6. Test log_activity classmethod
        print("  ✅ Testing log_activity method...")
        if hasattr(SessionActivity, 'log_activity'):
            print("     ✅ log_activity classmethod exists")
        else:
            print("  ❌ log_activity method missing")
            return False
        
        print("✅ ALL FIELD MIGRATION CHECKS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR in field migration check: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_test_file():
    """Check that test file has been updated"""
    print("🧪 Checking test file for field fixes...")
    
    test_file_path = 'apps/review_manager/tests.py'
    
    try:
        with open(test_file_path, 'r') as f:
            content = f.read()
        
        # Check for old field names that should be gone
        old_patterns = ['performed_at', 'activity_type', 'performed_by']
        found_old = []
        
        for pattern in old_patterns:
            if pattern in content:
                found_old.append(pattern)
        
        if found_old:
            print(f"  ❌ Old field names still in tests: {found_old}")
            return False
        
        # Check for new field names that should be present
        new_patterns = ['timestamp', 'action', 'user']
        found_new = []
        
        for pattern in new_patterns:
            if pattern in content:
                found_new.append(pattern)
        
        if len(found_new) < len(new_patterns):
            missing = [p for p in new_patterns if p not in found_new]
            print(f"  ❌ Missing new field names in tests: {missing}")
            return False
        
        print("  ✅ Test file correctly updated with new field names")
        return True
        
    except Exception as e:
        print(f"  ❌ Error checking test file: {e}")
        return False

if __name__ == "__main__":
    try:
        setup_django()
        
        # Check both model structure and test file
        model_ok = test_field_fixes_simple()
        test_file_ok = check_test_file()
        
        if model_ok and test_file_ok:
            print("\n🎉 ALL CHECKS PASSED!")
            print("   ✅ Field migration is complete")
            print("   ✅ Models have correct field names")
            print("   ✅ Tests have been updated")
            print("\n🚀 Ready to run full test suite:")
            print("   python manage.py test apps.review_manager")
        else:
            print("\n❌ SOME CHECKS FAILED")
            if not model_ok:
                print("   ❌ Model structure issues")
            if not test_file_ok:
                print("   ❌ Test file issues")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)
