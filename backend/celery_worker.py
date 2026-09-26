import compat  # noqa: F401 – Python 3.12 pkg_resources shim (must be first)
import os
from app import create_app
from app.extensions import celery

app = create_app(os.getenv('FLASK_ENV', 'development'))
app.app_context().push()

# Import all celery tasks so they are registered with the worker
from app.tasks_celery import deadline, weekly, reports  # noqa: F401

# Celery Beat schedule (periodic tasks)
from celery.schedules import crontab

celery.conf.beat_schedule = {
    # Every day at 8:00 AM UTC — deadline reminder
    'check-deadlines-daily': {
        'task': 'app.tasks_celery.deadline.check_deadlines',
        'schedule': crontab(hour=8, minute=0),
    },
    # Every Monday at 9:00 AM UTC — weekly digest
    'send-weekly-digest-monday': {
        'task': 'app.tasks_celery.weekly.send_weekly_digest',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },
}

celery.conf.timezone = 'UTC'
