"""
Security utilities — JWT tokens and magic link token hashing.

No password hashing — this app uses passwordless magic link auth.
"""

import hashlib
import secrets
from datetime import timedelta
from typing import Any

from jose import JWTError, jwt

from modules.backend.core.config import get_app_config, get_settings
from modules.backend.core.exceptions import AuthenticationError
from modules.backend.core.logging import get_logger
from modules.backend.core.utils import utc_now

logger = get_logger(__name__)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    settings = get_settings()
    jwt_config = get_app_config().security.jwt
    to_encode = data.copy()

    if expires_delta:
        expire = utc_now() + expires_delta
    else:
        expire = utc_now() + timedelta(minutes=jwt_config.access_token_expire_minutes)

    to_encode.update(
        {
            "exp": expire,
            "type": "access",
            "aud": jwt_config.audience,
        }
    )
    return jwt.encode(to_encode, settings.app_secret_key, algorithm=jwt_config.algorithm)


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    settings = get_settings()
    jwt_config = get_app_config().security.jwt
    to_encode = data.copy()
    expire = utc_now() + timedelta(days=jwt_config.refresh_token_expire_days)
    to_encode.update(
        {
            "exp": expire,
            "type": "refresh",
            "aud": jwt_config.audience,
        }
    )
    return jwt.encode(to_encode, settings.app_secret_key, algorithm=jwt_config.algorithm)


def create_sse_token(data: dict[str, Any]) -> str:
    """Create a short-lived JWT for SSE connections."""
    settings = get_settings()
    jwt_config = get_app_config().security.jwt
    to_encode = data.copy()
    expire = utc_now() + timedelta(minutes=30)
    to_encode.update(
        {
            "exp": expire,
            "type": "sse",
            "aud": jwt_config.audience,
        }
    )
    return jwt.encode(to_encode, settings.app_secret_key, algorithm=jwt_config.algorithm)


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string
        expected_type: If set, validates the token 'type' claim matches

    Raises:
        AuthenticationError: If token is invalid, expired, or wrong type
    """
    settings = get_settings()
    jwt_config = get_app_config().security.jwt
    try:
        payload = jwt.decode(
            token,
            settings.app_secret_key,
            algorithms=[jwt_config.algorithm],
            audience=jwt_config.audience,
        )
    except JWTError as e:
        logger.warning("Token decode failed", extra={"error": str(e)})
        raise AuthenticationError("Invalid or expired token")

    if expected_type and payload.get("type") != expected_type:
        raise AuthenticationError(f"Expected {expected_type} token, got {payload.get('type')}")

    return payload


def generate_magic_link_token() -> tuple[str, str]:
    """
    Generate a magic link token.

    Returns:
        Tuple of (raw_token, token_hash).
        raw_token is sent to the user; token_hash is stored in the database.
    """
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)
    return raw_token, token_hash


def hash_token(raw_token: str) -> str:
    """SHA-256 hash a token for secure storage."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
