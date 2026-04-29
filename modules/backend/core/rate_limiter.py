"""
Rate limiter — Redis sorted set sliding window.

Per-user, per-endpoint rate limiting for auth endpoints.
"""

from modules.backend.core.logging import get_logger
from modules.backend.core.utils import utc_now

logger = get_logger(__name__)


class RateLimitExceeded(Exception):
    """Raised when a rate limit is exceeded."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        super().__init__(f"Rate limit exceeded: {limit} requests per {window_seconds}s")


async def check_rate_limit(
    redis,
    key: str,
    limit: int,
    window_seconds: int,
) -> None:
    """
    Check and enforce a sliding window rate limit.

    Args:
        redis: Redis client
        key: Rate limit key (e.g. "ratelimit:magic_link:user@example.com")
        limit: Maximum requests allowed in the window
        window_seconds: Window size in seconds

    Raises:
        RateLimitExceeded: If the limit is exceeded
    """
    now = utc_now().timestamp()
    window_start = now - window_seconds

    pipe = redis.pipeline()
    # Remove expired entries
    pipe.zremrangebyscore(key, 0, window_start)
    # Count current entries
    pipe.zcard(key)
    # Add current request
    pipe.zadd(key, {f"{now}": now})
    # Set expiry on the key
    pipe.expire(key, window_seconds)
    results = await pipe.execute()

    current_count = results[1]
    if current_count >= limit:
        logger.warning(
            "Rate limit exceeded",
            extra={"key": key, "limit": limit, "window": window_seconds},
        )
        raise RateLimitExceeded(limit, window_seconds)
