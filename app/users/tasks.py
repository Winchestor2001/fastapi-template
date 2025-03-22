from celery import shared_task

from loggers import get_logger

logger = get_logger(__name__)


@shared_task(name="task_name",
             autoretry_for=(Exception,),
             retry_kwargs={'max_retries': 3, 'countdown': 15})
def some_task_task() -> None:
    try:
        # logic here
        pass
    except Exception as e:
        logger.error("Error", exc_info=True)
        raise e  # Re-raise the exception for autoretry to work