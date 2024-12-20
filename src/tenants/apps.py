from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tenants'
    verbose_name = 'Tenant Management'

    def ready(self):
        """
        Initialize app when it's ready.
        Import signals here to avoid circular imports.
        """
        try:
            import tenants.signals  # noqa
        except ImportError:
            pass
