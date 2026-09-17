import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astro_planner.settings')

app = Celery('astro_planner')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'generate-report-every-minute': {
        'task': 'forecasts.tasks.generate_forecasts_report',
        'schedule': crontab(minute='*/1')
    },
    'generate-report-every-day': {
        'task': 'forecasts.tasks.generate_forecasts_report',
        'schedule': crontab(hour='11', minute='0')
    }
}
