"""
Celery application configuration for background task processing.
This keeps the FastAPI server as a lightweight controller that delegates heavy work.
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "synthesize",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.generation",
        "app.tasks.notifications",
        "app.tasks.cleanup",
        "app.tasks.billing",
        "app.tasks.data_factory"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=900,  # 15 minutes
    task_soft_time_limit=840,  # 14 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,  # 1 hour
    # Queue routing
    task_routes={
        "app.tasks.generation.*": {"queue": "generation"},
        "app.tasks.notifications.*": {"queue": "notifications"},
        "app.tasks.cleanup.*": {"queue": "cleanup"},
        "app.tasks.billing.*": {"queue": "billing"},
        "app.tasks.data_factory.*": {"queue": "generation"},
    },
    # Priority queues
    task_default_priority=5,
    task_queue_max_priority=10,
)

# Periodic tasks (Celery Beat schedule)
celery_app.conf.beat_schedule = {
    # Cleanup tasks
    "cleanup-old-datasets": {
        "task": "app.tasks.cleanup.cleanup_old_datasets",
        "schedule": 3600.0,  # Every hour
    },
    "calculate-usage-stats": {
        "task": "app.tasks.cleanup.calculate_usage_stats",
        "schedule": 1800.0,  # Every 30 minutes
    },
    
    # Billing tasks
    "check-expiring-subscriptions": {
        "task": "app.tasks.billing.check_expiring_subscriptions",
        "schedule": crontab(hour=9, minute=0),  # Daily at 9 AM UTC
    },
    "process-grace-period-expirations": {
        "task": "app.tasks.billing.process_grace_period_expirations",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight UTC
    },
    "retry-failed-payments": {
        "task": "app.tasks.billing.retry_failed_payments",
        "schedule": crontab(hour=10, minute=0),  # Daily at 10 AM UTC
    },
    "generate-monthly-invoices": {
        "task": "app.tasks.billing.generate_monthly_invoices",
        "schedule": crontab(hour=0, minute=0, day_of_month=1),  # 1st of month
    },
    "reset-monthly-usage": {
        "task": "app.tasks.billing.reset_monthly_usage",
        "schedule": crontab(hour=0, minute=5, day_of_month=1),  # 1st of month
    },
}
