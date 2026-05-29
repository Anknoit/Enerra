from django.apps import AppConfig


class MarketDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.market_data'
    label = 'market_data'

    def ready(self):
        import apps.market_data.signals  # noqa: F401
