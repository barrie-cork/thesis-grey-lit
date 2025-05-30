#!/usr/bin/env python3
"""
Comprehensive Project Cleanup Script for Django Grey Literature Review Application

This script removes all unnecessary test files, temporary files, and development artifacts
while preserving the core Django application structure and proper test files.

Usage:
    python comprehensive_cleanup.py
    python comprehensive_cleanup.py --dry-run  # Preview changes without making them
"""

import os
import sys
import shutil
from pathlib import Path
import argparse

class GreyLitCleanup:
    """Comprehensive cleanup manager for the Django project"""
    
    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.removed_files = []
        self.removed_dirs = []
        self.kept_files = []
        self.errors = []
        
    def log_action(self, action: str, path: str, success: bool = True):
        """Log cleanup actions"""
        status = "✅" if success else "❌"
        mode = "(DRY RUN) " if self.dry_run else ""
        print(f"{mode}{status} {action}: {path}")
        
    def remove_file(self, file_path: Path, reason: str = ""):
        """Safely remove a file"""
        try:
            if file_path.exists():
                if not self.dry_run:
                    file_path.unlink()
                self.removed_files.append(str(file_path.relative_to(self.project_root)))
                self.log_action("Removed file", str(file_path.relative_to(self.project_root)))
                if reason:
                    print(f"   Reason: {reason}")
            else:
                self.log_action("File not found", str(file_path.relative_to(self.project_root)), False)
        except Exception as e:
            self.errors.append(f"Could not remove {file_path}: {e}")
            self.log_action("Error removing", str(file_path.relative_to(self.project_root)), False)
            
    def remove_directory(self, dir_path: Path, reason: str = ""):
        """Safely remove a directory and its contents"""
        try:
            if dir_path.exists() and dir_path.is_dir():
                if not self.dry_run:
                    shutil.rmtree(dir_path)
                self.removed_dirs.append(str(dir_path.relative_to(self.project_root)))
                self.log_action("Removed directory", str(dir_path.relative_to(self.project_root)))
                if reason:
                    print(f"   Reason: {reason}")
            else:
                self.log_action("Directory not found", str(dir_path.relative_to(self.project_root)), False)
        except Exception as e:
            self.errors.append(f"Could not remove {dir_path}: {e}")
            self.log_action("Error removing", str(dir_path.relative_to(self.project_root)), False)
            
    def keep_file(self, file_path: Path, reason: str = ""):
        """Mark a file as kept (for informational purposes)"""
        self.kept_files.append(str(file_path.relative_to(self.project_root)))
        self.log_action("Keeping", str(file_path.relative_to(self.project_root)))
        if reason:
            print(f"   Reason: {reason}")

    def cleanup_test_files(self):
        """Remove temporary test files but keep proper Django tests"""
        print("\\n🧪 Cleaning up test files...")
        print("=" * 50)
        
        # Temporary test files to remove
        temp_test_files = [
            'test_fixes.py',
            'test_sprint6_timeline_history.py', 
            'test_sprint6_timeline_history_fixed.py',
            'test_imports.py',
            'test_sprint4.py',
            'test_sprint5.py',
            'setup_and_test.py',
            'verify_setup.py',
            'check_fixes.py'
        ]
        
        for filename in temp_test_files:
            file_path = self.project_root / filename
            self.remove_file(file_path, "Temporary diagnostic test file")
            
        # Check for any other test files in root (but keep proper Django tests in apps)
        for file_path in self.project_root.glob('test_*.py'):
            if file_path.name not in temp_test_files:
                self.remove_file(file_path, "Additional temporary test file")
                
        # Keep proper Django tests in apps
        for app_path in (self.project_root / 'apps').glob('*/tests.py'):
            if app_path.exists():
                self.keep_file(app_path, "Proper Django app test file")

    def cleanup_shell_scripts(self):
        """Remove temporary shell command scripts"""
        print("\\n📝 Cleaning up shell scripts...")
        print("=" * 30)
        
        shell_files = [
            'shell_commands_sprint6.py',
            'shell_commands_sprint6_fixed.py',
            'cleanup_project.py'  # Old cleanup script
        ]
        
        for filename in shell_files:
            file_path = self.project_root / filename
            self.remove_file(file_path, "Temporary shell command script")

    def cleanup_fix_files(self):
        """Remove diagnostic and fix files"""
        print("\\n🔧 Cleaning up fix and diagnostic files...")
        print("=" * 40)
        
        fix_files = [
            'sprint5_fix.py',
            'fix_mixins.py',
            'emergency_fix.py',
            'debug_django.py',
            'fix_sprint5.py',
            'diagnose_sprint5.py',
            'fix_verification.sh'
        ]
        
        for filename in fix_files:
            file_path = self.project_root / filename
            self.remove_file(file_path, "Diagnostic/fix file")
            
        # Remove batch files
        batch_files = [
            'run_debug.bat',
            'run_sprint5_fix.bat',
            'quick_fix.sh'
        ]
        
        for filename in batch_files:
            file_path = self.project_root / filename
            self.remove_file(file_path, "Temporary batch/shell file")

    def cleanup_backup_files(self):
        """Remove backup and corrupted files"""
        print("\\n💾 Cleaning up backup files...")
        print("=" * 30)
        
        # Find backup files
        for backup_file in self.project_root.rglob('*.backup'):
            self.remove_file(backup_file, "Backup file")
            
        for backup_file in self.project_root.rglob('*.corrupted'):
            self.remove_file(backup_file, "Corrupted file backup")
            
        # Specific backup files mentioned in the old cleanup script
        specific_backups = [
            'apps/review_manager/mixins.py.backup',
            'apps/review_manager/mixins.py.corrupted'
        ]
        
        for backup_path in specific_backups:
            file_path = self.project_root / backup_path
            self.remove_file(file_path, "Specific backup file")

    def cleanup_cache_files(self):
        """Remove cache files and compiled Python files"""
        print("\\n🗂️ Cleaning up cache files...")
        print("=" * 30)
        
        # Remove __pycache__ directories
        pycache_count = 0
        for pycache_dir in self.project_root.rglob('__pycache__'):
            if pycache_dir.is_dir() and 'venv' not in str(pycache_dir):
                self.remove_directory(pycache_dir, "Python cache directory")
                pycache_count += 1
                
        # Remove .pyc files
        pyc_count = 0
        for pyc_file in self.project_root.rglob('*.pyc'):
            if 'venv' not in str(pyc_file):
                if not self.dry_run:
                    pyc_file.unlink()
                pyc_count += 1
                
        if pyc_count > 0:
            self.log_action(f"Removed {pyc_count} .pyc files", "")

    def cleanup_coverage_files(self):
        """Remove coverage files"""
        print("\\n📊 Cleaning up coverage files...")
        print("=" * 30)
        
        coverage_files = [
            '.coverage',
            'htmlcov'
        ]
        
        for item in coverage_files:
            path = self.project_root / item
            if path.is_file():
                self.remove_file(path, "Coverage data file")
            elif path.is_dir():
                self.remove_directory(path, "Coverage HTML reports")

    def cleanup_git_artifacts(self):
        """Clean up git-related artifacts (but keep .git itself)"""
        print("\\n📦 Cleaning up Git artifacts...")
        print("=" * 30)
        
        git_artifacts = [
            'commitmsg.txt'
        ]
        
        for filename in git_artifacts:
            file_path = self.project_root / filename
            self.remove_file(file_path, "Git artifact file")

    def cleanup_ide_files(self):
        """Clean up IDE configuration files"""
        print("\\n💻 Cleaning up IDE files...")
        print("=" * 25)
        
        ide_dirs = [
            '.cursor',
            '.roo'
        ]
        
        for dirname in ide_dirs:
            dir_path = self.project_root / dirname
            if dir_path.is_dir():
                self.remove_directory(dir_path, "IDE configuration directory")
                
        ide_files = [
            '.roomodes',
            '.windsurfrules'
        ]
        
        for filename in ide_files:
            file_path = self.project_root / filename
            self.remove_file(file_path, "IDE configuration file")

    def cleanup_documentation_duplicates(self):
        """Remove duplicate or obsolete documentation"""
        print("\\n📚 Cleaning up documentation duplicates...")
        print("=" * 40)
        
        # Files that have been superseded or migrated
        obsolete_docs = [
            'CONFIGURATION_FIXES_APPLIED.md',
            'SETUP_COMPLETE.md',
            'TEAM_LEAD_ONBOARDING_OVERVIEW.md',
            'ONBOARDING_INDEX.md'
        ]
        
        for filename in obsolete_docs:
            file_path = self.project_root / filename
            self.remove_file(file_path, "Obsolete documentation file")

    def verify_important_files(self):
        """Verify that important files are still present"""
        print("\\n✅ Verifying important files are preserved...")
        print("=" * 45)
        
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
        
        critical_dirs = [
            'apps',
            'templates',
            'static',
            'thesis_grey_project',
            'docs'
        ]
        
        for filename in critical_files:
            file_path = self.project_root / filename
            if file_path.exists():
                self.log_action("✓ Preserved", filename)
            else:
                self.log_action("⚠ Missing", filename, False)
                
        for dirname in critical_dirs:
            dir_path = self.project_root / dirname
            if dir_path.exists() and dir_path.is_dir():
                self.log_action("✓ Preserved", f"{dirname}/")
            else:
                self.log_action("⚠ Missing", f"{dirname}/", False)

    def verify_app_structure(self):
        """Verify Django app structure is intact"""
        print("\\n🏗️ Verifying Django app structure...")
        print("=" * 35)
        
        expected_apps = [
            'accounts',
            'review_manager', 
            'search_strategy',
            'serp_execution',
            'results_manager',
            'review_results',
            'reporting'
        ]
        
        for app_name in expected_apps:
            app_path = self.project_root / 'apps' / app_name
            if app_path.exists():
                # Check for essential Django files
                essential_files = ['models.py', 'views.py', 'tests.py']
                missing_files = []
                
                for essential_file in essential_files:
                    file_path = app_path / essential_file
                    if not file_path.exists():
                        missing_files.append(essential_file)
                        
                if missing_files:
                    self.log_action(f"⚠ App {app_name} missing", f"{', '.join(missing_files)}", False)
                else:
                    self.log_action(f"✓ App {app_name}", "Complete")
            else:
                self.log_action(f"⚠ App {app_name}", "Directory missing", False)

    def generate_summary(self):
        """Generate cleanup summary"""
        print("\\n" + "=" * 60)
        print("🎉 CLEANUP SUMMARY")
        print("=" * 60)
        
        mode_msg = " (DRY RUN - NO CHANGES MADE)" if self.dry_run else ""
        print(f"📊 Cleanup Results{mode_msg}:")
        print(f"   📄 Files removed: {len(self.removed_files)}")
        print(f"   📁 Directories removed: {len(self.removed_dirs)}")
        print(f"   ✅ Files preserved: {len(self.kept_files)}")
        print(f"   ❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print("\\n❌ Errors encountered:")
            for error in self.errors:
                print(f"   {error}")
                
        if self.removed_files:
            print("\\n🗑️ Files removed:")
            for file_path in sorted(self.removed_files):
                print(f"   {file_path}")
                
        if self.removed_dirs:
            print("\\n📁 Directories removed:")
            for dir_path in sorted(self.removed_dirs):
                print(f"   {dir_path}")

    def run_cleanup(self):
        """Execute the full cleanup process"""
        print("🧹 Starting Comprehensive Django Project Cleanup")
        print("=" * 55)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be actually removed")
            print("=" * 50)
        
        # Execute cleanup steps
        self.cleanup_test_files()
        self.cleanup_shell_scripts()
        self.cleanup_fix_files()
        self.cleanup_backup_files()
        self.cleanup_cache_files()
        self.cleanup_coverage_files()
        self.cleanup_git_artifacts()
        self.cleanup_ide_files()
        self.cleanup_documentation_duplicates()
        
        # Verification steps
        self.verify_important_files()
        self.verify_app_structure()
        
        # Generate summary
        self.generate_summary()
        
        if not self.dry_run:
            print("\\n🚀 Next Steps:")
            print("1. Run: python manage.py check")
            print("2. Run: python manage.py migrate")
            print("3. Run: python manage.py test apps.review_manager")
            print("4. Start server: python manage.py runserver")
            print("5. Visit: http://localhost:8000/review/")
        else:
            print("\\n🔄 To actually perform cleanup:")
            print("   python comprehensive_cleanup.py")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Clean up Django grey literature project")
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview changes without making them')
    parser.add_argument('--project-root', type=str, 
                       default=str(Path(__file__).parent),
                       help='Project root directory')
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root)
    if not project_root.exists():
        print(f"❌ Project root does not exist: {project_root}")
        sys.exit(1)
        
    if not (project_root / 'manage.py').exists():
        print(f"❌ Not a Django project (no manage.py found): {project_root}")
        sys.exit(1)
    
    cleanup = GreyLitCleanup(project_root, args.dry_run)
    cleanup.run_cleanup()

if __name__ == "__main__":
    main()
