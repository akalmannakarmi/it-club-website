from celery import shared_task
from django.utils import timezone


@shared_task
def scrape_task():
    print("Daily scrape task ran at", timezone.now())
