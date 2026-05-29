import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('enerra')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.task_routes = {
    'apps.market_data.tasks.*': {'queue': 'market_data'},
    'apps.risk.tasks.*': {'queue': 'risk'},
    'apps.settlements.tasks.*': {'queue': 'settlements'},
    'apps.credit.tasks.*': {'queue': 'credit'},
    'apps.reporting.tasks.*': {'queue': 'reporting'},
    'apps.scheduling.tasks.*': {'queue': 'scheduling'},
    'integrations.*': {'queue': 'integrations'},
}
