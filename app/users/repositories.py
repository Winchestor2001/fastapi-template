import time
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import exc
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.database.database import async_session
from app.database.repositories import SQLAlchemyRepository
from app.user.domain.repositories import AbstractUserRepository
from app.user.exceptions import FilteringError
from app.user.models import User
from loggers import get_logger

logger = get_logger(__name__)


class UserRepository(SQLAlchemyRepository, AbstractUserRepository):
    """
    User repository
    """

    def __init__(self):
        super().__init__(User)

    @staticmethod
    async def get_by_phone(phone_number: str) -> Optional[User]:
        """Fetch a users by phone number with avatar preloaded."""
        async with async_session() as session:
            try:
                result = await session.execute(
                    select(User)
                    .options(joinedload(User.avatar))
                    .where(User.phone_number == phone_number)
                    .limit(1)
                )
                user = result.scalars().first()
                return user
            except exc.CompileError as e:
                logger.error("Query compilation error get_by_phone from User: %s", e)
                raise FilteringError

    async def get_single(self, **filters) -> Optional[User]:
        """Retrieve a single record with context-managed session and error handling."""
        async with async_session() as session:
            try:
                query = select(self.model).options(
                    joinedload(User.avatar)
                ).filter_by(**filters)
                result = await session.execute(query)
                return result.scalars().first()
            except SQLAlchemyError as e:
                logger.error("SQLAlchemyError: Failed to retrieve single %s. Error: %s", self.model.__name__, e)
                return None

    async def update(self, data: dict, **filters) -> Optional[User]:
        async with async_session() as session:
            try:
                query = select(self.model).options(
                    joinedload(User.avatar)
                ).filter_by(**filters)
                result = await session.execute(query)
                instance = result.scalars().first()
                if instance:
                    for key, value in data.items():
                        setattr(instance, key, value)
                    await session.commit()
                    await session.refresh(instance)
                    logger.info("%s updated successfully.", self.model.__name__)
                    return instance
                return None
            except IntegrityError as e:
                await session.rollback()
                logger.error("IntegrityError: Failed to update %s. Error: %s", self.model.__name__, e)
                return None
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error("SQLAlchemyError: Failed to update %s. Error: %s", self.model.__name__, e)
                return None

    async def soft_delete_user(self, user_id: UUID) -> bool:
        """
        Soft delete a users by marking is_deleted=True and modifying the phone number.
        """
        async with async_session() as session:
            try:
                query = select(self.model).filter_by(id=user_id, is_deleted=False)
                result = await session.execute(query)
                user = result.scalars().first()

                if not user:
                    raise HTTPException(status_code=404, detail={"message": "User not found or already deleted."})

                # phone_number: +998913451175|1708401935
                deletion_datetime = int(time.time())
                user.phone_number = f"{user.phone_number}|{deletion_datetime}"
                user.username = f"{user.username}|{deletion_datetime}"
                user.is_deleted = True
                user.last_deleted_at = datetime.utcnow()

                await session.commit()
                logger.info("User %s soft deleted successfully.", user_id)
                return True

            except SQLAlchemyError as e:
                await session.rollback()
                logger.error("SQLAlchemyError: Failed to soft delete User. Error: %s", e)
                return False
