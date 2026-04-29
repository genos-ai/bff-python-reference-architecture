"""
Base Repository.

Generic async CRUD operations for SQLAlchemy models with UUID primary keys.
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.backend.core.exceptions import NotFoundError
from modules.backend.core.logging import get_logger
from modules.backend.models.base import Base

logger = get_logger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations.

    Subclasses should set the model class:

        class UserRepository(BaseRepository[User]):
            model = User
    """

    model: type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id: UUID) -> ModelType:
        """Get a single record by ID. Raises NotFoundError if not found."""
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        instance = result.scalar_one_or_none()
        if instance is None:
            raise NotFoundError(self.model.__name__, str(id))
        return instance

    async def get_by_id_or_none(self, id: UUID) -> ModelType | None:
        """Get a single record by ID, returning None if not found."""
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def create(self, **kwargs: Any) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: UUID, **kwargs: Any) -> ModelType:
        """Update an existing record. Raises NotFoundError if not found."""
        instance = await self.get_by_id(id)
        for key, value in kwargs.items():
            if not hasattr(instance, key):
                raise ValueError(f"Unknown field: {key}")
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: UUID) -> None:
        """Delete a record by ID. Raises NotFoundError if not found."""
        instance = await self.get_by_id(id)
        await self.session.delete(instance)
        await self.session.flush()

    async def exists(self, id: UUID) -> bool:
        """Check if a record exists by ID."""
        result = await self.session.execute(select(self.model.id).where(self.model.id == id))
        return result.scalar_one_or_none() is not None

    async def count(self) -> int:
        """Get total count of records."""
        result = await self.session.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()
