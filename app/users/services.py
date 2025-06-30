from uuid import UUID


from app.core.services import BaseService
from app.user_logs.models import LogTypeEnum
from app.user_logs.services import UserLogService
from celery_tasks.main import celery_app  # noqa: F401
from loggers import get_logger

logger = get_logger(__name__)


class UserService(BaseService):
    def __init__(self, repository):
        super().__init__(repository)
