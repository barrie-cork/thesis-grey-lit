#!/bin/bash
# Complete Django setup script for PostgreSQL

echo "🚀 Setting up Django Grey Literature Project"
echo "=" * 50

# Make sure we're using the local settings (PostgreSQL)
export DJANGO_SETTINGS_MODULE=thesis_grey_project.settings.local

echo "📦 Step 1: Clean up any existing test databases..."
# Clean up PostgreSQL test databases
sudo -u postgres psql -c "DROP DATABASE IF EXISTS test_thesis_grey;" 2>/dev/null || echo "No test db to clean"

echo "🗃️ Step 2: Ensure main database exists..."
# Create main database if it doesn't exist
sudo -u postgres psql -c "CREATE DATABASE thesis_grey OWNER postgres;" 2>/dev/null || echo "Database may already exist"

echo "🔄 Step 3: Create and apply migrations..."
# Make migrations for all apps
python manage.py makemigrations accounts
python manage.py makemigrations review_manager
python manage.py makemigrations search_strategy
python manage.py makemigrations serp_execution
python manage.py makemigrations results_manager
python manage.py makemigrations review_results
python manage.py makemigrations reporting

# Apply all migrations
python manage.py migrate

echo "👤 Step 4: Create superuser (optional)..."
echo "Would you like to create a superuser now? (you can skip and do this later)"
read -p "Create superuser? (y/N): " create_user
if [[ $create_user =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

echo "🧪 Step 5: Run tests to verify everything works..."
python manage.py test apps.review_manager --keepdb

echo "📊 Step 6: Create sample data..."
python manage.py create_sample_sessions --count 5

echo "✅ Setup complete!"
echo "🚀 Start the server with: python manage.py runserver"
echo "🌐 Then visit: http://localhost:8000/review/"
