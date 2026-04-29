"""User repository."""

from sqlalchemy import select

from modules.backend.models.user import User
from modules.backend.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        """Find user by email (case-insensitive)."""
        result = await self.session.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def find_or_create_by_email(self, email: str) -> tuple[User, bool]:
        """Find existing user or create new one. Returns (user, created)."""
        normalized = email.lower().strip()
        existing = await self.get_by_email(normalized)
        if existing:
            return existing, False
        user = await self.create(email=normalized)
        return user, True
