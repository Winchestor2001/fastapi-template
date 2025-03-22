from typing import Sequence, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")
R = TypeVar("R", bound=BaseModel)


class BaseService:
    """Base service with common CRUD operations using Pydantic models."""

    def __init__(self, repository):
        self.repository = repository

    async def create(self, data: R) -> Optional[T]:
        return await self.repository.create(data.model_dump())

    async def get_single(self, **filters) -> Optional[T]:
        return await self.repository.get_single(**filters)

    async def get_list(self, **filters) -> Sequence[T]:
        return await self.repository.get_list(**filters)

    async def update(self, data: R, **filters) -> Optional[T]:
        return await self.repository.update(data.model_dump(exclude_unset=True), **filters)

    async def delete(self, **filters) -> Optional[T]:
        return await self.repository.delete(**filters)