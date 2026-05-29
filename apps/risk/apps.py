from django.apps import AppConfig


class RiskConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.risk'
    label = 'risk'

    def ready(self):
        import apps.risk.signals  # noqa: F401
