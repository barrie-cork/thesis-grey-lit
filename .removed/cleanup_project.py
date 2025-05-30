#!/usr/bin/env python3
"""
Project Cleanup Script - Remove temporary diagnostic and fix files
"""

import os
from pathlib import Path
import shutil

def cleanup_project():
    """Clean up temporary files created during Sprint 5 debugging"""
    
    project_root = Path('/mnt/d/Python/Projects/thesis-grey-lit')
    
    print("🧹 Cleaning up Sprint 5 diagnostic files...")
    print("=" * 50)
    
    # Files to remove
    cleanup_files = [
        'sprint5_fix.py',
        'fix_mixins.py', 
        'emergency_fix.py',
        'debug_django.py',
        'run_debug.bat',
        'run_sprint5_fix.bat',
        'quick_fix.sh',
        'fix_sprint5.py',
        'diagnose_sprint5.py',
        'test_imports.py',
        'test_sprint4.py',
        'test_sprint5.py',
        'setup_and_test.py'
    ]
    
    # Backup files to remove
    backup_files = [
        'apps/review_manager/mixins.py.backup',
        'apps/review_manager/mixins.py.corrupted'
    ]
    
    removed_count = 0
    kept_files = []
    
    # Remove main cleanup files
    for filename in cleanup_files:
        file_path = project_root / filename
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"🗑️  Removed: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"⚠️  Could not remove {filename}: {e}")
        else:
            print(f"📄 Not found: {filename}")
    
    # Remove backup files
    for backup_file in backup_files:
        file_path = project_root / backup_file
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"🗑️  Removed backup: {backup_file}")
                removed_count += 1
            except Exception as e:
                print(f"⚠️  Could not remove {backup_file}: {e}")
    
    # Check for any remaining diagnostic files
    diagnostic_patterns = [
        '*fix*.py',
        '*diagnostic*.py', 
        '*debug*.py',
        '*test*.py'
    ]
    
    print(f"\n🔍 Checking for other diagnostic files...")
    
    for pattern in diagnostic_patterns:
        for file_path in project_root.glob(pattern):
            # Skip important files
            if file_path.name in ['manage.py', 'setup.py']:
                continue
            
            # Skip files in apps directories (these are real app files)
            if 'apps' in file_path.parts:
                continue
                
            if file_path.is_file():
                keep_file = input(f"❓ Found {file_path.name} - Remove it? (y/N): ").lower()
                if keep_file == 'y':
                    try:
                        file_path.unlink()
                        print(f"🗑️  Removed: {file_path.name}")
                        removed_count += 1
                    except Exception as e:
                        print(f"⚠️  Could not remove {file_path.name}: {e}")
                else:
                    kept_files.append(file_path.name)
    
    # Clean up __pycache__ directories
    print(f"\n🧹 Cleaning __pycache__ directories...")
    
    pycache_count = 0
    for pycache_dir in project_root.rglob('__pycache__'):
        if pycache_dir.is_dir():
            try:
                shutil.rmtree(pycache_dir)
                print(f"🗑️  Removed: {pycache_dir.relative_to(project_root)}")
                pycache_count += 1
            except Exception as e:
                print(f"⚠️  Could not remove {pycache_dir}: {e}")
    
    # Clean up .pyc files
    print(f"\n🧹 Cleaning .pyc files...")
    
    pyc_count = 0
    for pyc_file in project_root.rglob('*.pyc'):
        try:
            pyc_file.unlink()
            pyc_count += 1
        except Exception as e:
            print(f"⚠️  Could not remove {pyc_file}: {e}")
    
    if pyc_count > 0:
        print(f"🗑️  Removed {pyc_count} .pyc files")
    
    # Summary
    print(f"\n✨ Cleanup Summary:")
    print(f"📄 Files removed: {removed_count}")
    print(f"📁 __pycache__ dirs removed: {pycache_count}")
    print(f"🐍 .pyc files removed: {pyc_count}")
    
    if kept_files:
        print(f"📄 Files kept: {', '.join(kept_files)}")
    
    # Show remaining project structure
    print(f"\n📁 Clean Project Structure:")
    
    important_files = [
        'manage.py',
        'requirements.txt',
        'README.md',
        '.env',
        '.gitignore'
    ]
    
    important_dirs = [
        'apps/',
        'templates/',
        'static/',
        'thesis_grey_project/',
        'docs/'
    ]
    
    for item in important_files:
        file_path = project_root / item
        if file_path.exists():
            print(f"✅ {item}")
        else:
            print(f"❓ {item} (not found)")
    
    for item in important_dirs:
        dir_path = project_root / item.rstrip('/')
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ {item}")
        else:
            print(f"❓ {item} (not found)")
    
    # Final Sprint 5 verification
    print(f"\n🎯 Sprint 5 Verification:")
    
    sprint5_files = [
        'apps/review_manager/mixins.py',
        'apps/review_manager/templates/review_manager/dashboard.html',
        'apps/review_manager/static/review_manager/css/dashboard.css',
        'apps/review_manager/static/review_manager/js/dashboard.js'
    ]
    
    for file_path_str in sprint5_files:
        file_path = project_root / file_path_str
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {file_path_str} ({size:,} bytes)")
        else:
            print(f"❌ {file_path_str} (missing)")
    
    print(f"\n🎉 Project cleanup complete!")
    print(f"💡 You can now run: python manage.py runserver")
    print(f"🌐 Then visit: http://localhost:8000/review/")

if __name__ == '__main__':
    cleanup_project()
