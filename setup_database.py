#!/usr/bin/env python3
"""
Django Project Setup Script
Sets up the database and runs initial migrations
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thesis_grey_project.settings.local')

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print(f"   STDOUT: {e.stdout}")
        if e.stderr:
            print(f"   STDERR: {e.stderr}")
        return False

def setup_database():
    """Set up the database and run migrations"""
    print("🚀 Django Grey Literature Project Setup")
    print("=" * 45)
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: No virtual environment detected")
        print("   Consider activating your virtual environment first")
    
    print("📊 Creating migrations for all apps...")
    
    # Create migrations for each app
    apps = ['accounts', 'review_manager', 'search_strategy', 'serp_execution', 
            'results_manager', 'review_results', 'reporting']
    
    for app in apps:
        run_command(f"python manage.py makemigrations {app}", f"Creating migrations for {app}")
    
    print("\n🗃️ Applying migrations...")
    if run_command("python manage.py migrate", "Applying all migrations"):
        print("✅ Database setup complete!")
        
        print("\n🧪 Testing the setup...")
        if run_command("python manage.py check", "Running Django system check"):
            print("✅ Django system check passed!")
            
            print("\n📊 Creating sample data...")
            run_command("python manage.py create_sample_sessions --count 3", "Creating sample sessions")
            
            print("\n" + "=" * 45)
            print("🎉 Setup Complete!")
            print("=" * 45)
            print("✅ Database is ready")
            print("✅ Migrations applied")
            print("✅ Sample data created")
            print("\n🚀 Next steps:")
            print("1. Create superuser: python manage.py createsuperuser")
            print("2. Start server: python manage.py runserver") 
            print("3. Visit: http://localhost:8000/review/")
            
            return True
    
    return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
