from celery.schedules import crontab
from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


CELERY_BEAT_SCHEDULE = {
    "scrape-task": {
        "task": "events.tasks.scrape_task",
        #"schedule": crontab(hour=0, minute=0), 
        "schedule": crontab(minute='*'), # TO run every minute to test
    },
}
