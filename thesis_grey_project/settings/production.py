from .base import *

DEBUG = False
ALLOWED_HOSTS = ["yourdomain.com"]

# Make sure to set real secrets in production
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
