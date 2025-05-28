from .base import *

DEBUG = False
ALLOWED_HOSTS = ["yourdomain.com"]

# Make sure to set real secrets in production
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# Security settings for production
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_HSTS_SECONDS = 31536000  # Optional: Enable HSTS after confirming site works with HTTPS
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True # Optional
# SECURE_HSTS_PRELOAD = True # Optional
