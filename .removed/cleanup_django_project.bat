@echo off
echo Starting Django Grey Literature Project Cleanup...
echo ================================================

cd /d "D:\Python\Projects\thesis-grey-lit"

echo.
echo Removing temporary test files...
if exist "test_fixes.py" del "test_fixes.py" && echo   Removed: test_fixes.py
if exist "test_sprint6_timeline_history.py" del "test_sprint6_timeline_history.py" && echo   Removed: test_sprint6_timeline_history.py
if exist "test_sprint6_timeline_history_fixed.py" del "test_sprint6_timeline_history_fixed.py" && echo   Removed: test_sprint6_timeline_history_fixed.py
if exist "check_fixes.py" del "check_fixes.py" && echo   Removed: check_fixes.py
if exist "verify_setup.py" del "verify_setup.py" && echo   Removed: verify_setup.py

echo.
echo Removing shell command files...
if exist "shell_commands_sprint6.py" del "shell_commands_sprint6.py" && echo   Removed: shell_commands_sprint6.py
if exist "shell_commands_sprint6_fixed.py" del "shell_commands_sprint6_fixed.py" && echo   Removed: shell_commands_sprint6_fixed.py
if exist "cleanup_project.py" del "cleanup_project.py" && echo   Removed: cleanup_project.py

echo.
echo Removing fix and diagnostic files...
if exist "fix_verification.sh" del "fix_verification.sh" && echo   Removed: fix_verification.sh

echo.
echo Removing git artifacts...
if exist "commitmsg.txt" del "commitmsg.txt" && echo   Removed: commitmsg.txt

echo.
echo Removing coverage files...
if exist ".coverage" del ".coverage" && echo   Removed: .coverage
if exist "htmlcov" rmdir /s /q "htmlcov" && echo   Removed: htmlcov directory

echo.
echo Removing obsolete documentation...
if exist "CONFIGURATION_FIXES_APPLIED.md" del "CONFIGURATION_FIXES_APPLIED.md" && echo   Removed: CONFIGURATION_FIXES_APPLIED.md
if exist "SETUP_COMPLETE.md" del "SETUP_COMPLETE.md" && echo   Removed: SETUP_COMPLETE.md
if exist "TEAM_LEAD_ONBOARDING_OVERVIEW.md" del "TEAM_LEAD_ONBOARDING_OVERVIEW.md" && echo   Removed: TEAM_LEAD_ONBOARDING_OVERVIEW.md
if exist "ONBOARDING_INDEX.md" del "ONBOARDING_INDEX.md" && echo   Removed: ONBOARDING_INDEX.md
if exist "REMOVAL_APPROVAL.md" del "REMOVAL_APPROVAL.md" && echo   Removed: REMOVAL_APPROVAL.md

echo.
echo Removing IDE configuration files...
if exist ".cursor" rmdir /s /q ".cursor" && echo   Removed: .cursor directory
if exist ".roo" rmdir /s /q ".roo" && echo   Removed: .roo directory
if exist ".roomodes" del ".roomodes" && echo   Removed: .roomodes
if exist ".windsurfrules" del ".windsurfrules" && echo   Removed: .windsurfrules

echo.
echo Removing cleanup scripts (including this one)...
if exist "comprehensive_cleanup.py" del "comprehensive_cleanup.py" && echo   Removed: comprehensive_cleanup.py
if exist "quick_cleanup.py" del "quick_cleanup.py" && echo   Removed: quick_cleanup.py

echo.
echo Cleaning Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
for /r . %%f in (*.pyc) do @if exist "%%f" del "%%f" 2>nul

echo.
echo Verifying important files are preserved...
if exist "manage.py" echo   ✓ manage.py
if exist "requirements.txt" echo   ✓ requirements.txt  
if exist "README.md" echo   ✓ README.md
if exist "CUSTOM_USER_ALERT.md" echo   ✓ CUSTOM_USER_ALERT.md
if exist "DEVELOPER_ONBOARDING.md" echo   ✓ DEVELOPER_ONBOARDING.md
if exist "DEVELOPMENT_GUIDE.md" echo   ✓ DEVELOPMENT_GUIDE.md
if exist "TEAM_LEAD_CHECKLIST.md" echo   ✓ TEAM_LEAD_CHECKLIST.md
if exist "apps" echo   ✓ apps/ directory
if exist "templates" echo   ✓ templates/ directory
if exist "static" echo   ✓ static/ directory
if exist "thesis_grey_project" echo   ✓ thesis_grey_project/ directory

echo.
echo ================================================
echo Django Grey Literature Project Cleanup Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Run: python manage.py check
echo 2. Run: python manage.py migrate  
echo 3. Run: python manage.py test apps.review_manager
echo 4. Start server: python manage.py runserver
echo 5. Visit: http://localhost:8000/review/
echo.
echo Project structure is now clean and ready for development!

pause
