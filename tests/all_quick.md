# 🔧 Useful Commands for Ongoing Development

## Security monitoring
python manage.py verify_security          # Quick security check
python manage.py security_audit          # Comprehensive audit
python manage.py run_security_tests      # Full security test suite
python manage.py test_security_minimal  # Minimal security test run

## Development workflow
python manage.py test                    # Run all tests
python manage.py check                  # Check for common issues
python manage.py create_sample_sessions --count 10  # Create sample session data
python manage.py create_sample_sessions --clean  # Clean up test data
python manage.py shell               # Open Django shell for testing

## Data Management
python manage.py migrate                # Apply database changes


## App Management
python manage.py runserver              # Start the development server
python manage.py createsuperuser         # Create an admin user



