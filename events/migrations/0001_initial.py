from django.db import migrations


def create_scrape_task(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")

    crontab, _ = CrontabSchedule.objects.get_or_create(
        minute="0",
        hour="2",           # runs at 02:00 UTC
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
        timezone="UTC",
    )

    PeriodicTask.objects.update_or_create(
        name="scrape-task-daily",
        defaults={
            "task": "events.tasks.scrape_task",
            "crontab": crontab,
            "enabled": True,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("django_celery_beat", "0019_alter_periodictasks_options"),
    ]

    operations = [
        migrations.RunPython(create_scrape_task),
    ]
