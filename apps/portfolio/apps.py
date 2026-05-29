from django.apps import AppConfig


class PortfolioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.portfolio'
    label = 'portfolio'

    def ready(self):
        import apps.portfolio.signals  # noqa: F401
