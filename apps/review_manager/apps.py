from django.apps import AppConfig


class ReviewManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.review_manager'
    verbose_name = 'Review Manager'
    
    def ready(self):
        """Import signal handlers when the app is ready"""
        import apps.review_manager.signals  # noqa
