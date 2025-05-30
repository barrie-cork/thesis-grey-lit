#!/bin/bash
# Script to clean up PostgreSQL connections and run tests properly

echo "🧹 Cleaning up PostgreSQL test database connections..."

# Kill any existing connections to the test database
sudo -u postgres psql -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'test_thesis_grey' AND pid <> pg_backend_pid();
"

# Drop the test database if it exists
sudo -u postgres psql -c "DROP DATABASE IF EXISTS test_thesis_grey;"

echo "✅ Database cleanup complete"
echo "🧪 Running tests..."

# Run tests with clean database
python manage.py test apps.review_manager --keepdb=False
