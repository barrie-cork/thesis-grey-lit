# apps/review_manager/logging_config.py
"""
Logging configuration for security events - Sprint 8
"""

import os
from django.conf import settings

# Security logging configuration
SECURITY_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'security_detailed': {
            'format': '[{asctime}] {levelname} {name} - {message}',
            'style': '{',
        },
        'audit_detailed': {
            'format': '[{asctime}] AUDIT {name} - User: {user} Action: {action} Details: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(settings.BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 10*1024*1024,  # 10MB
            'backupCount': 5,
            'formatter': 'security_detailed',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(settings.BASE_DIR, 'logs', 'audit.log'),
            'maxBytes': 10*1024*1024,  # 10MB
            'backupCount': 10,
            'formatter': 'audit_detailed',
        },
        'security_console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'security_detailed',
        },
        'security_mail_admins': {
            'level': 'CRITICAL',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'formatter': 'security_detailed',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_file', 'security_console', 'security_mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'permissions': {
            'handlers': ['security_file', 'security_console'],
            'level': 'INFO',
            'propagate': False,
        },
        'audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

def setup_security_logging():
    """
    Set up security logging configuration.
    Call this from Django settings.
    """
    import logging.config
    
    # Ensure logs directory exists
    logs_dir = os.path.join(settings.BASE_DIR, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logging
    logging.config.dictConfig(SECURITY_LOGGING)
    
    # Test logging setup
    security_logger = logging.getLogger('security')
    security_logger.info("Security logging initialized")
