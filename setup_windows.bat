@echo off
echo ================================================
echo Django Grey Literature Review Application
echo Windows Setup and Verification Script
echo ================================================
echo.

REM Check if we're in the right directory
if not exist "manage.py" (
    echo ❌ Error: manage.py not found. Please run this from the project root directory.
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check Python version
echo 🐍 Checking Python version...
python --version

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Check for .env file
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your database settings before continuing.
    echo Press any key to continue once .env is configured...
    pause
)

echo.
echo 🔍 Running verification script...
python verify_setup.py
if errorlevel 1 (
    echo ❌ Verification failed. Please check the errors above.
    pause
    exit /b 1
)

echo.
echo 🧪 Running tests to verify fixes...
python manage.py test apps.review_manager.tests.SessionActivityTests -v 2
if errorlevel 1 (
    echo ❌ Critical tests failed. The field migration fixes may not be working.
    pause
    exit /b 1
)

echo.
echo 📊 Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ❌ Database migration failed
    pause
    exit /b 1
)

echo.
echo 👤 Checking if superuser exists...
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser found')"

echo.
echo ================================================
echo ✅ SETUP COMPLETE!
echo ================================================
echo.
echo Your Django Grey Literature Review Application is ready!
echo.
echo 🚀 To start development:
echo    python manage.py runserver
echo.
echo 🌐 Access points:
echo    Dashboard: http://localhost:8000/review/
echo    Admin:     http://localhost:8000/admin/
echo.
echo 🧪 To run all tests:
echo    python manage.py test apps.review_manager
echo.
echo 📊 To create sample data:
echo    python manage.py create_sample_sessions --count 10
echo.
pause
