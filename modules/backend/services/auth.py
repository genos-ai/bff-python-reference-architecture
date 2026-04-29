"""
Auth service — magic link authentication with JWT tokens.

Flow:
1. User requests magic link → we email a token
2. User clicks link → we verify token, issue JWT access + refresh + SSE tokens
3. Access token expires → client uses refresh token to get new tokens
4. Logout → blacklist refresh token JTI in Redis
"""

from datetime import timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from modules.backend.core.config import get_app_config
from modules.backend.core.logging import get_logger
from modules.backend.core.security import (
    create_access_token,
    create_refresh_token,
    create_sse_token,
    decode_token,
    generate_magic_link_token,
    hash_token,
)
from modules.backend.core.utils import utc_now
from modules.backend.repositories.magic_link import MagicLinkRepository
from modules.backend.repositories.user import UserRepository

logger = get_logger(__name__)


class AuthService:
    def __init__(self, session: AsyncSession, redis=None) -> None:
        self.session = session
        self.redis = redis
        self.user_repo = UserRepository(session)
        self.magic_link_repo = MagicLinkRepository(session)

    async def request_magic_link(self, email: str) -> tuple[str, str]:
        """
        Request a magic link for the given email.

        Always succeeds (prevents email enumeration).
        Returns (user_id, raw_token) for the email service to send.
        """
        user, _ = await self.user_repo.find_or_create_by_email(email)
        raw_token, token_hash = generate_magic_link_token()
        expires_at = utc_now() + timedelta(minutes=15)

        await self.magic_link_repo.create(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        await self.session.flush()

        logger.info(
            "Magic link created",
            extra={"user_id": str(user.id), "email": email},
        )
        return str(user.id), raw_token

    async def verify_magic_link(self, raw_token: str) -> dict:
        """
        Verify a magic link token and issue JWT tokens.

        Returns dict with access_token, sse_token, token_type, user.
        Refresh token is returned separately for cookie setting.
        """
        token_hash = hash_token(raw_token)
        magic_link = await self.magic_link_repo.get_valid_by_hash(token_hash)

        if not magic_link:
            from modules.backend.core.exceptions import AuthenticationError

            raise AuthenticationError("Invalid or expired magic link")

        await self.magic_link_repo.consume(magic_link.id)

        user = await self.user_repo.get_by_id(magic_link.user_id)

        jti = str(uuid4())
        token_data = {"sub": str(user.id), "email": user.email, "jti": jti}

        access_token = create_access_token(token_data)
        sse_token = create_sse_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id), "jti": jti})

        logger.info(
            "Magic link verified",
            extra={"user_id": str(user.id)},
        )

        return {
            "access_token": access_token,
            "sse_token": sse_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "display_name": user.display_name,
            },
        }

    async def refresh_tokens(self, refresh_token: str) -> dict:
        """Validate refresh token, rotate JTI, issue new token set."""
        payload = decode_token(refresh_token, expected_type="refresh")
        old_jti = payload.get("jti")

        # Check if JTI is blacklisted
        if self.redis and old_jti:
            blacklisted = await self.redis.get(f"blacklist:{old_jti}")
            if blacklisted:
                from modules.backend.core.exceptions import AuthenticationError

                raise AuthenticationError("Token has been revoked")

        user_id = payload["sub"]
        user = await self.user_repo.get_by_id(user_id)

        # Blacklist old JTI
        if self.redis and old_jti:
            jwt_config = get_app_config().security.jwt
            ttl = jwt_config.refresh_token_expire_days * 86400
            await self.redis.setex(f"blacklist:{old_jti}", ttl, "1")

        new_jti = str(uuid4())
        token_data = {"sub": str(user.id), "email": user.email, "jti": new_jti}

        access_token = create_access_token(token_data)
        sse_token = create_sse_token({"sub": str(user.id)})
        new_refresh = create_refresh_token({"sub": str(user.id), "jti": new_jti})

        return {
            "access_token": access_token,
            "sse_token": sse_token,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "display_name": user.display_name,
            },
        }

    async def logout(self, refresh_token: str) -> None:
        """Blacklist the refresh token's JTI."""
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
            jti = payload.get("jti")
            if self.redis and jti:
                jwt_config = get_app_config().security.jwt
                ttl = jwt_config.refresh_token_expire_days * 86400
                await self.redis.setex(f"blacklist:{jti}", ttl, "1")
        except Exception:
            pass  # Logout always succeeds
