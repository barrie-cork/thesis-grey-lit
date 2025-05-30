#!/usr/bin/env python3
"""
Clean __pycache__ directories from Django project
"""

import os
import shutil
from pathlib import Path

def clean_pycache():
    project_root = Path('D:/Python/Projects/thesis-grey-lit')
    removed_count = 0
    
    print("🧹 Cleaning __pycache__ directories...")
    
    # Find all __pycache__ directories (excluding venv)
    for pycache_dir in project_root.rglob('__pycache__'):
        if 'venv' not in str(pycache_dir):
            try:
                shutil.rmtree(pycache_dir)
                print(f"✅ Removed: {pycache_dir.relative_to(project_root)}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {pycache_dir}: {e}")
    
    print(f"\\n📊 Removed {removed_count} __pycache__ directories")
    
    # Also clean .pyc files
    pyc_count = 0
    for pyc_file in project_root.rglob('*.pyc'):
        if 'venv' not in str(pyc_file):
            try:
                pyc_file.unlink()
                pyc_count += 1
            except Exception:
                pass
    
    if pyc_count > 0:
        print(f"📊 Removed {pyc_count} .pyc files")
    
    print("✨ Cache cleanup complete!")

if __name__ == '__main__':
    clean_pycache()
