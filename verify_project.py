#!/usr/bin/env python3
"""
Django Grey Literature Project - Verification Script
Run this script to verify the project is properly set up after cleanup.
Works in both Windows and WSL environments.
"""

import os
import sys
from pathlib import Path

def get_project_root():
    """Get the project root directory, works in both Windows and WSL"""
    # Try to get from current working directory first
    current_dir = Path.cwd()
    
    # Check if we're already in the project directory
    if (current_dir / 'manage.py').exists():
        return current_dir
    
    # Try common paths
    possible_paths = [
        Path('/mnt/d/Python/Projects/thesis-grey-lit'),  # WSL
        Path('D:/Python/Projects/thesis-grey-lit'),      # Windows
        Path(__file__).parent,                           # Script directory
        current_dir,                                     # Current directory
    ]
    
    for path in possible_paths:
        if path.exists() and (path / 'manage.py').exists():
            return path
    
    # If none found, use current directory
    return current_dir

def verify_project_structure():
    """Verify the Django project structure is intact"""
    print("🔍 Verifying Django Project Structure...")
    print("=" * 50)
    
    project_root = get_project_root()
    print(f"📁 Project root: {project_root}")
    
    # Critical files that must exist
    critical_files = [
        'manage.py',
        'requirements.txt',
        'README.md',
        'CUSTOM_USER_ALERT.md',
        'DEVELOPER_ONBOARDING.md',
        'DEVELOPMENT_GUIDE.md',
        'TEAM_LEAD_CHECKLIST.md',
        '.env.example',
        '.gitignore'
    ]
    
    # Critical directories that must exist
    critical_dirs = [
        'apps',
        'thesis_grey_project',
        'templates',
        'static',
        'docs',
        'venv'
    ]
    
    # Django apps that must exist
    required_apps = [
        'accounts',
        'review_manager',
        'search_strategy',
        'serp_execution',
        'results_manager',
        'review_results',
        'reporting'
    ]
    
    missing_files = []
    missing_dirs = []
    missing_apps = []
    
    # Check critical files
    print("\n📄 Checking Critical Files...")
    for filename in critical_files:
        file_path = project_root / filename
        if file_path.exists():
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename}")
            missing_files.append(filename)
    
    # Check critical directories
    print("\n📁 Checking Critical Directories...")
    for dirname in critical_dirs:
        dir_path = project_root / dirname
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ {dirname}/")
        else:
            print(f"❌ {dirname}/")
            missing_dirs.append(dirname)
    
    # Check Django apps
    print("\n🏢 Checking Django Apps...")
    apps_dir = project_root / 'apps'
    if apps_dir.exists():
        for app_name in required_apps:
            app_path = apps_dir / app_name
            if app_path.exists() and app_path.is_dir():
                # Check for essential Django files
                models_file = app_path / 'models.py'
                views_file = app_path / 'views.py'
                tests_file = app_path / 'tests.py'
                
                if all(f.exists() for f in [models_file, views_file, tests_file]):
                    print(f"✅ {app_name} (complete)")
                else:
                    missing_files_list = []
                    if not models_file.exists():
                        missing_files_list.append('models.py')
                    if not views_file.exists():
                        missing_files_list.append('views.py')
                    if not tests_file.exists():
                        missing_files_list.append('tests.py')
                    print(f"⚠️  {app_name} (missing: {', '.join(missing_files_list)})")
            else:
                print(f"❌ {app_name}")
                missing_apps.append(app_name)
    else:
        print("❌ apps/ directory not found!")
        missing_dirs.append('apps')
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    if not missing_files and not missing_dirs and not missing_apps:
        print("✅ ALL CHECKS PASSED!")
        print("🎉 Project structure is complete and ready for development")
        return True
    else:
        print("❌ ISSUES FOUND:")
        if missing_files:
            print(f"   Missing files: {', '.join(missing_files)}")
        if missing_dirs:
            print(f"   Missing directories: {', '.join(missing_dirs)}")
        if missing_apps:
            print(f"   Missing apps: {', '.join(missing_apps)}")
        return False

def verify_custom_user_model():
    """Verify the custom User model is properly configured"""
    print("\n🧪 Verifying Custom User Model...")
    print("=" * 35)
    
    try:
        # Get project root and add to Python path
        project_root = get_project_root()
        sys.path.insert(0, str(project_root))
        
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thesis_grey_project.settings.local')
        
        import django
        django.setup()
        
        # Test custom User model
        from django.contrib.auth import get_user_model
        from django.conf import settings
        
        User = get_user_model()
        
        print(f"✅ AUTH_USER_MODEL: {settings.AUTH_USER_MODEL}")
        print(f"✅ User model class: {User.__name__}")
        print(f"✅ User model module: {User.__module__}")
        
        # Check if User model has UUID primary key
        pk_field = User._meta.pk
        if hasattr(pk_field, 'default') and 'uuid' in str(pk_field.default).lower():
            print("✅ User model uses UUID primary key")
        elif 'UUID' in str(type(pk_field)):
            print("✅ User model uses UUID primary key")
        else:
            print(f"⚠️  User model primary key type: {type(pk_field)}")
        
        print("✅ Custom User model verification passed!")
        return True
        
    except Exception as e:
        print(f"❌ Custom User model verification failed: {e}")
        return False

def verify_django_setup():
    """Verify Django can run basic commands"""
    print("\n⚙️  Verifying Django Setup...")
    print("=" * 30)
    
    project_root = get_project_root()
    original_cwd = os.getcwd()
    
    try:
        os.chdir(project_root)
        
        # Test Django check command
        import subprocess
        result = subprocess.run(
            ['python', 'manage.py', 'check'], 
            capture_output=True, 
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            print("✅ Django check passed")
        else:
            print(f"❌ Django check failed:")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
        # Test if we can import apps
        sys.path.insert(0, str(project_root))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thesis_grey_project.settings.local')
        
        import django
        django.setup()
        
        from apps.review_manager.models import SearchSession
        from apps.accounts.models import User
        
        print("✅ Django apps import successfully")
        print("✅ Models can be imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Django setup verification failed: {e}")
        return False
    finally:
        os.chdir(original_cwd)

def show_project_info():
    """Show basic project information"""
    print("\n📋 Project Information...")
    print("=" * 30)
    
    project_root = get_project_root()
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python version: {sys.version}")
    print(f"💻 Platform: {sys.platform}")
    print(f"📂 Current working directory: {os.getcwd()}")
    
    # Check if virtual environment is active
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is active")
    else:
        print("⚠️  Virtual environment may not be active")

def main():
    """Run all verification checks"""
    print("🚀 Django Grey Literature Project Verification")
    print("=" * 55)
    print("Verifying project setup after cleanup...")
    
    # Show project info first
    show_project_info()
    
    # Run all verification checks
    structure_ok = verify_project_structure()
    user_model_ok = verify_custom_user_model()
    django_ok = verify_django_setup()
    
    print("\n" + "=" * 55)
    print("🏁 FINAL VERIFICATION RESULTS")
    print("=" * 55)
    
    if structure_ok and user_model_ok and django_ok:
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("✅ Project is ready for development")
        print("\n📋 Next Steps:")
        print("1. Run: python manage.py migrate")
        print("2. Run: python manage.py createsuperuser")
        print("3. Run: python manage.py test apps.review_manager")
        print("4. Run: python manage.py create_sample_sessions --count 10")
        print("5. Run: python manage.py runserver")
        print("6. Visit: http://localhost:8000/review/")
    else:
        print("❌ VERIFICATION FAILED")
        print("Please address the issues above before continuing")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
