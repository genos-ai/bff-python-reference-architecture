"""
Health Check Utilities.

Shared health check functions for database and Redis connectivity.
Used by both the health API endpoints and scheduled background tasks.
"""

from typing import Any

from modules.backend.core.logging import get_logger
from modules.backend.core.utils import utc_now

logger = get_logger(__name__)


async def check_database() -> dict[str, Any]:
    """
    Check database connectivity.

    Returns:
        Dict with status, latency, and optional error message
    """
    try:
        from modules.backend.core.config import get_app_config
        from modules.backend.core.database import get_db_session

        db_config = get_app_config().database

        if not db_config.host or not db_config.name:
            return {"status": "not_configured"}

        start = utc_now()
        async for session in get_db_session():
            from sqlalchemy import text

            await session.execute(text("SELECT 1"))
            break

        latency_ms = int((utc_now() - start).total_seconds() * 1000)

        return {
            "status": "healthy",
            "latency_ms": latency_ms,
        }

    except ImportError:
        return {"status": "not_configured"}
    except Exception as e:
        logger.warning("Database health check failed", extra={"error": str(e)})
        return {
            "status": "unhealthy",
            "error": str(e),
        }


async def check_redis() -> dict[str, Any]:
    """
    Check Redis connectivity.

    Returns:
        Dict with status, latency, and optional error message
    """
    try:
        import redis.asyncio as redis

        from modules.backend.core.config import get_redis_url

        redis_url = get_redis_url()

        start = utc_now()
        client = redis.from_url(redis_url)
        await client.ping()
        await client.aclose()

        latency_ms = int((utc_now() - start).total_seconds() * 1000)

        return {
            "status": "healthy",
            "latency_ms": latency_ms,
        }

    except ImportError:
        return {"status": "not_configured"}
    except Exception as e:
        logger.warning("Redis health check failed", extra={"error": str(e)})
        return {
            "status": "unhealthy",
            "error": str(e),
        }
