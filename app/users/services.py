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

    async def block_user(self, admin_login: str, user_id: UUID) -> bool:
        updated = await self.repository.update_user_status(user_id=user_id, is_blocked=True)
        if updated:
            await UserLogService.log(
                user_id=user_id,
                log_type=LogTypeEnum.PROFILE,
                action="blocked",
                data={"admin_login": admin_login}
            )

        return updated

    async def unblock_user(self, admin_login: str, user_id: UUID) -> bool:
        updated = await self.repository.update_user_status(user_id=user_id, is_blocked=False)
        if updated:
            await UserLogService.log(
                user_id=user_id,
                log_type=LogTypeEnum.PROFILE,
                action="unblocked",
                data={"admin_login": admin_login}
            )

        return updated

    async def get_users_by_language(self):
        return await self.repository.get_users_by_language()