from typing import Sequence, Type, TypeVar, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.database.database import async_session
from loggers import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class SQLAlchemyRepository:
    """Base repository with common SQLAlchemy operations using context-managed sessions."""

    def __init__(self, model: Type[T]):
        self.model = model

    async def create(self, data: dict) -> Optional[T]:
        """Create a new record with context-managed session and error handling."""
        async with async_session() as session:
            instance = self.model(**data)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            logger.info("%s created successfully.", self.model.__name__)
            return instance

    async def get_single(self, **filters) -> Optional[T]:
        """Retrieve a single record with context-managed session and error handling."""
        async with async_session() as session:
            query = select(self.model).filter_by(**filters)
            result = await session.execute(query)
            return result.scalars().first()

    async def get_list(self, **filters) -> Sequence[T]:
        """Retrieve a list of records with context-managed session and error handling."""
        async with async_session() as session:
            query = select(self.model).filter_by(**filters)
            result = await session.execute(query)
            return result.scalars().all()

    async def update(self, data: dict, **filters) -> Optional[T]:
        """Update a record with context-managed session and error handling."""
        async with async_session() as session:
            try:
                query = select(self.model).filter_by(**filters)
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
            except (IntegrityError, SQLAlchemyError):
                await session.rollback()
                raise

    async def delete(self, **filters) -> Optional[T]:
        """Delete a record with context-managed session and error handling."""
        async with async_session() as session:
            try:
                query = select(self.model).filter_by(**filters)
                result = await session.execute(query)
                instance = result.scalars().first()
                if instance:
                    await session.delete(instance)
                    await session.commit()
                    logger.info("%s deleted successfully.", self.model.__name__)
                    return instance
                return None

            except (IntegrityError, SQLAlchemyError):
                await session.rollback()
                raise


class SoftDeleteRepository(SQLAlchemyRepository):
    """Repository with soft delete support."""

    async def get_single(self, **filters) -> Optional[T]:
        filters.setdefault("is_deleted", False)
        return await super().get_single(**filters)

    async def get_list(self, **filters) -> Sequence[T]:
        filters.setdefault("is_deleted", False)
        return await super().get_list(**filters)

    async def update(self, data: dict, **filters) -> Optional[T]:
        filters.setdefault("is_deleted", False)
        return await super().update(data, **filters)

    async def delete(self, **filters) -> Optional[T]:
        filters.setdefault("is_deleted", False)
        async with async_session() as session:
            try:
                query = select(self.model).filter_by(**filters)
                result = await session.execute(query)
                instance = result.scalars().first()
                if instance:
                    instance.is_deleted = True
                    await session.commit()
                    await session.refresh(instance)
                    logger.info("%s soft deleted successfully.", self.model.__name__)
                    return instance
                return None
            except (IntegrityError, SQLAlchemyError):
                await session.rollback()
                raise
