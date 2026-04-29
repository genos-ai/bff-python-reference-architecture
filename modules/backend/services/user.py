"""User service — profile management."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.backend.repositories.user import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)

    async def update_profile(self, user_id: UUID, display_name: str | None) -> object:
        """Update user's display name."""
        return await self.repo.update(user_id, display_name=display_name)

    async def deactivate(self, user_id: UUID) -> None:
        """Soft-delete user by setting is_active=False."""
        await self.repo.update(user_id, is_active=False)
