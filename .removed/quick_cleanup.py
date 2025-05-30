#!/usr/bin/env python3
"""
Quick cleanup script for Django Grey Literature project
Removes the most obvious unnecessary files
"""

import os
from pathlib import Path

def quick_cleanup():
    """Remove the most obvious unnecessary files"""
    project_root = Path('D:/Python/Projects/thesis-grey-lit')
    
    print("🧹 Starting Quick Cleanup...")
    print("=" * 40)
    
    # Files to remove
    files_to_remove = [
        'test_fixes.py',
        'test_sprint6_timeline_history.py', 
        'test_sprint6_timeline_history_fixed.py',
        'check_fixes.py',
        'cleanup_project.py',
        'shell_commands_sprint6.py',
        'shell_commands_sprint6_fixed.py',
        'fix_verification.sh',
        'verify_setup.py',
        'commitmsg.txt',
        '.coverage',
        'CONFIGURATION_FIXES_APPLIED.md',
        'SETUP_COMPLETE.md',
        'TEAM_LEAD_ONBOARDING_OVERVIEW.md',
        'ONBOARDING_INDEX.md',
        'REMOVAL_APPROVAL.md'
    ]
    
    # Directories to remove  
    dirs_to_remove = [
        '.cursor',
        '.roo',
        'htmlcov'
    ]
    
    # Remove files
    removed_files = 0
    for filename in files_to_remove:
        file_path = project_root / filename
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"✅ Removed: {filename}")
                removed_files += 1
            except Exception as e:
                print(f"❌ Error removing {filename}: {e}")
        else:
            print(f"📄 Not found: {filename}")
    
    # Remove directories
    removed_dirs = 0
    for dirname in dirs_to_remove:
        dir_path = project_root / dirname
        if dir_path.exists() and dir_path.is_dir():
            try:
                import shutil
                shutil.rmtree(dir_path)
                print(f"✅ Removed directory: {dirname}")
                removed_dirs += 1
            except Exception as e:
                print(f"❌ Error removing {dirname}: {e}")
        else:
            print(f"📁 Not found: {dirname}")
    
    # Clean __pycache__ directories (excluding venv)
    pycache_count = 0
    for pycache_dir in project_root.rglob('__pycache__'):
        if 'venv' not in str(pycache_dir):
            try:
                import shutil
                shutil.rmtree(pycache_dir)
                pycache_count += 1
            except Exception as e:
                print(f"❌ Error removing __pycache__: {e}")
    
    if pycache_count > 0:
        print(f"✅ Removed {pycache_count} __pycache__ directories")
    
    # Clean .pyc files (excluding venv)
    pyc_count = 0
    for pyc_file in project_root.rglob('*.pyc'):
        if 'venv' not in str(pyc_file):
            try:
                pyc_file.unlink()
                pyc_count += 1
            except Exception:
                pass
    
    if pyc_count > 0:
        print(f"✅ Removed {pyc_count} .pyc files")
    
    print(f"\\n📊 Summary:")
    print(f"   Files removed: {removed_files}")
    print(f"   Directories removed: {removed_dirs}")
    print(f"   Cache files cleaned: {pycache_count + pyc_count}")
    
    print(f"\\n✨ Quick cleanup complete!")
    
    # Show important files that remain
    print(f"\\n✅ Important files preserved:")
    important_files = [
        'manage.py',
        'requirements.txt',
        'README.md',
        'CUSTOM_USER_ALERT.md',
        'DEVELOPER_ONBOARDING.md',
        'DEVELOPMENT_GUIDE.md',
        'TEAM_LEAD_CHECKLIST.md'
    ]
    
    for filename in important_files:
        file_path = project_root / filename
        if file_path.exists():
            print(f"   ✓ {filename}")
        else:
            print(f"   ⚠ {filename} (missing)")

if __name__ == '__main__':
    quick_cleanup()
