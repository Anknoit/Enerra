from django.apps import AppConfig


class TradeCaptureConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.trade_capture'
    label = 'trade_capture'

    def ready(self):
        import apps.trade_capture.signals  # noqa: F401
