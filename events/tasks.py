from celery import shared_task
from datetime import datetime

@shared_task
def daily_task():
     print(f"Daily task ran at {datetime.now()}")
     return "Task complete"