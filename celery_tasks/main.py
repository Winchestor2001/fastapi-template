from celery import Celery
from celery.schedules import crontab

from app.core.settings import settings
from loggers import get_logger

logger = get_logger(__name__)

redis_url = settings.build_redis_dsn()
rabbitmq_url = settings.build_rabbitmq_dsn()

celery_app = Celery(__name__, broker=rabbitmq_url, backend=redis_url)

celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.worker_state_db = "/data/celery-worker-state"
# turn on async conf
celery_app.conf.update(
    task_create_missing_queues=True,
    task_acks_late=True,
    task_send_sent_event=True,
    task_track_started=True,
    task_time_limit=1800,
    task_always_eager=False,  # Set to False for async task execution
    task_execution_timeout=3600,
)

celery_app.conf.update(
    include=[
        # tasks
        # "app.users.tasks",
    ],
)

celery_app.conf.beat_schedule = {
    "beat-task-title": {
        "task": "beat-task-function-name",
        "schedule": crontab(minute="*/1"),
    }
}