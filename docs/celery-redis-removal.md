# Celery & Redis Removal

This documents the decision to strip Celery, Redis, and `django-celery-beat`
from the project, exactly what changed, and how to bring them back if a real
background job ever appears.

---

## Why they were removed

- Production deploys to a **cPanel Python web app**, where running a Redis
  broker plus a Celery worker and beat scheduler adds real operational
  complexity for zero payoff.
- The only task in the codebase was a **placeholder** (`scrape_task`) that did
  nothing but `print`. There is no feature to preserve.
- The stack pulled ~19 `requirements.txt` packages into the shared-hosting
  install (install time, disk, attack surface).
- Leaving the old migration in place would **break fresh deploys**: the old
  `events.0001_initial` depended on `django_celery_beat.0019`, so `migrate`
  failed on any database that never installed `django_celery_beat`.

## What was removed

| Piece | Change |
|---|---|
| `config/celery.py` | file deleted |
| `events/tasks.py` (stub `scrape_task`) | file deleted |
| `config/__init__.py` | dropped `from .celery import app as celery_app` |
| `config/settings.py` | removed `django_celery_beat` from `INSTALLED_APPS`; removed the `CELERY_*` block |
| `events/migrations/0001_initial.py` | rewritten as a no-op (no dependency, no `RunPython`) |
| `requirements.txt` | removed `celery`, `django-celery-beat`, `redis` + celery-only transitive deps (`amqp`, `billiard`, `click*`, `cron_descriptor`, `django-timezone-field`, `kombu`, `prompt_toolkit`, `python-crontab`, `python-dateutil`, `six`, `tzlocal`, `vine`, `wcwidth`) |
| `docker-compose.yml` | removed `celery`, `celery-beat`, `redis` services |
| `.env` / `example.env` | removed `CELERY_BROKER_URL` |
| docs | `AGENTS.md`, `README.md`, `docs/*` updated |

## State of existing databases

Django records which migrations have been applied in the `django_migrations`
table. Any database that already ran the old `django_celery_beat` migrations
(and created the `scrape-task-daily` row) keeps:

- the recorded `django_celery_beat` migration rows, and
- the `django_celery_beat_*` tables and the periodic-task row.

These are **orphaned but harmless** — nothing reads or writes them. `migrate`
won't touch them. If you ever want them gone from an existing database:

```sql
-- optional, manual cleanup of an old DB (not part of any migration)
DROP TABLE IF EXISTS django_celery_beat_periodictasks,
    django_celery_beat_periodictask,
    django_celery_beat_periodictask_executions,
    django_celery_beat_clockedschedule,
    django_celery_beat_solarschedule,
    django_celery_beat_crontabschedule,
    django_celery_beat_intervalschedule;
DELETE FROM django_migrations WHERE app = 'django_celery_beat';
```

Fresh databases never see any of this.

---

## How to re-enable Celery (reversal)

Re-adding the stack is straightforward and safe on **both** databases that
already have the old tables and fresh databases.

### 1. Dependencies + settings

```python
# requirements.txt
celery==5.6.1
django-celery-beat==2.8.1
redis==7.1.0
```

```python
# config/settings.py — INSTALLED_APPS
"django_celery_beat",

# config/settings.py — bottom of file
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
```

```env
# .env / example.env
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 2. App instance + task

Re-create `config/celery.py`:

```python
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

Add the import back to `config/__init__.py`:

```python
from .celery import app as celery_app
import pymysql

pymysql.install_as_MySQLdb()
__all__ = ("celery_app",)
```

Write your real task (e.g. `events/tasks.py`):

```python
from celery import shared_task


@shared_task
def scrape_task():
    ...
```

### 3. Re-create the schedule (the one thing a migration must do)

The old `events.0001_initial` created the periodic task, so that logic can't
just "come back". **Do not resurrect the old `0001`** — instead add a **new**
forward migration (e.g. `events/0006`) that recreates the task. It works on
every database: existing DBs already have `django_celery_beat` applied, fresh
DBs install it first (the new migration declares the dependency).

```python
from django.db import migrations


def create_scrape_task(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")

    crontab, _ = CrontabSchedule.objects.get_or_create(
        minute="0",
        hour="2",
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
        ("events", "0005_event_display_event_order"),
        ("django_celery_beat", "0019_alter_periodictasks_options"),
    ]

    operations = [
        migrations.RunPython(create_scrape_task),
    ]
```

Generate it as a normal migration in the app:

```sh
python manage.py makemigrations events --empty -n recreate_scrape_task
# then edit the generated file as above
```

### 4. Run it

```sh
docker compose up -d redis
python manage.py migrate
celery -A config worker -l info    # separate terminal/process
celery -A config beat -l info      # separate terminal/process
```

On cPanel you would need a persistent process for the worker and beat, which is
exactly the complexity this removal avoids — only add it back for a real job.

---

## Note

Only re-introduce this stack when there is an actual background job to run.
Until then, prefer synchronous work inside a request or a plain cron-managed
`manage.py` command.
