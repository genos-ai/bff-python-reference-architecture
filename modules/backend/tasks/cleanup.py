"""Scheduled cleanup tasks."""

from modules.backend.core.logging import get_logger
from modules.backend.tasks.broker import get_broker

logger = get_logger(__name__)

broker = get_broker()


@broker.task(schedule=[{"cron": "0 3 * * *"}])
async def cleanup_magic_links() -> dict:
    """Daily: delete expired magic links older than 24 hours."""
    from modules.backend.core.database import get_async_session
    from modules.backend.repositories.magic_link import MagicLinkRepository

    async with get_async_session() as session:
        repo = MagicLinkRepository(session)
        deleted = await repo.cleanup_expired()

    logger.info("Magic link cleanup completed", extra={"deleted": deleted})
    return {"deleted": deleted}
