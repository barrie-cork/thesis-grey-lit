#!/bin/bash
# Script to clean up PostgreSQL test database connections

echo "🧹 Cleaning PostgreSQL test database connections..."

# Function to kill PostgreSQL connections to test database
cleanup_postgres_connections() {
    echo "Terminating connections to test_thesis_grey database..."
    
    # Try to connect to PostgreSQL and terminate connections
    sudo -u postgres psql -c "
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = 'test_thesis_grey'
      AND pid <> pg_backend_pid();
    " 2>/dev/null || echo "PostgreSQL connection cleanup attempted"
    
    # Drop the test database if it exists
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS test_thesis_grey;" 2>/dev/null || echo "Test database cleanup attempted"
    
    echo "✅ PostgreSQL cleanup complete"
}

# Clean up connections
cleanup_postgres_connections

# Wait a moment for connections to close
sleep 2

echo "🧪 Running Django tests with clean database..."

# Set environment to use test settings
export DJANGO_SETTINGS_MODULE=thesis_grey_project.settings.test

# Run tests with SQLite (no connection issues)
python manage.py test apps.review_manager --verbosity=2

echo "✨ Test run complete!"
