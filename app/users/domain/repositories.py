from abc import ABC, abstractmethod


class AbstractUserRepository(ABC):
    @abstractmethod
    async def create(self, data: dict) -> None:
        """Create a new users."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, data: dict, **filters) -> None:
        """Update an existing users."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, data: dict, **filters) -> None:
        """Get all users."""
        raise NotImplementedError