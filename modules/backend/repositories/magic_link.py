"""Magic link repository."""

from uuid import UUID

from sqlalchemy import select, update

from modules.backend.core.utils import utc_now
from modules.backend.models.magic_link import MagicLink
from modules.backend.repositories.base import BaseRepository


class MagicLinkRepository(BaseRepository[MagicLink]):
    model = MagicLink

    async def get_valid_by_hash(self, token_hash: str) -> MagicLink | None:
        """Find an unconsumed, unexpired magic link by token hash."""
        now = utc_now()
        result = await self.session.execute(
            select(MagicLink).where(
                MagicLink.token_hash == token_hash,
                MagicLink.consumed_at.is_(None),
                MagicLink.expires_at > now,
            )
        )
        return result.scalar_one_or_none()

    async def consume(self, id: UUID) -> None:
        """Mark a magic link as consumed."""
        await self.session.execute(
            update(MagicLink).where(MagicLink.id == id).values(consumed_at=utc_now())
        )
        await self.session.flush()

    async def cleanup_expired(self) -> int:
        """Delete expired magic links older than 24 hours. Returns count deleted."""
        from datetime import timedelta

        from sqlalchemy import delete

        cutoff = utc_now() - timedelta(hours=24)
        result = await self.session.execute(delete(MagicLink).where(MagicLink.expires_at < cutoff))
        await self.session.flush()
        return result.rowcount
