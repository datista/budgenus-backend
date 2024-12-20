from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        """
        Initialize app when it's ready.
        Import signals here to avoid circular imports.
        """
        try:
            import core.signals  # noqa
        except ImportError:
            pass
