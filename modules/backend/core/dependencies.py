"""
FastAPI Dependencies.

Shared dependencies for request handling and authentication.
"""

from typing import Annotated

from fastapi import Cookie, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from modules.backend.core.database import get_db_session
from modules.backend.core.logging import get_logger

logger = get_logger(__name__)

# Type alias for database session dependency
DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_request_id(x_request_id: str | None = Header(None)) -> str:
    """Extract or generate request ID from headers."""
    import uuid

    return x_request_id or str(uuid.uuid4())


RequestId = Annotated[str, Depends(get_request_id)]


async def get_current_user(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get the current authenticated user from the Bearer token.

    Raises 401 if no token or token is invalid.
    """
    from modules.backend.core.exceptions import AuthenticationError
    from modules.backend.core.security import decode_token
    from modules.backend.repositories.user import UserRepository

    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("Missing or invalid authorization header")

    token = authorization.removeprefix("Bearer ")
    payload = decode_token(token, expected_type="access")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")

    repo = UserRepository(db)
    user = await repo.get_by_id_or_none(user_id)
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")

    return user


async def get_current_user_optional(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db_session),
):
    """Get current user or None if not authenticated."""
    if not authorization:
        return None
    try:
        return await get_current_user(authorization=authorization, db=db)
    except Exception:
        return None


async def get_refresh_token(
    refresh_token: str | None = Cookie(None),
) -> str | None:
    """Extract refresh token from cookie."""
    return refresh_token


# ---------------------------------------------------------------------------
# Base auth aliases
# ---------------------------------------------------------------------------
CurrentUser = Annotated[object, Depends(get_current_user)]
OptionalUser = Annotated[object | None, Depends(get_current_user_optional)]
RefreshToken = Annotated[str | None, Depends(get_refresh_token)]


# ---------------------------------------------------------------------------
# Role-checked auth aliases
# ---------------------------------------------------------------------------

async def _get_admin_user(user=Depends(get_current_user)):
    """Require admin or sysadmin role."""
    from modules.backend.core.rbac import Role, check_user_role
    check_user_role(user, Role.ADMIN, Role.SYSADMIN)
    return user


async def _get_standard_user(user=Depends(get_current_user)):
    """Require user, admin, or sysadmin role (not viewer)."""
    from modules.backend.core.rbac import Role, check_user_role
    check_user_role(user, Role.USER, Role.ADMIN, Role.SYSADMIN)
    return user


async def _get_any_authenticated_user(user=Depends(get_current_user)):
    """Any authenticated user including viewer."""
    return user


AdminUser = Annotated[object, Depends(_get_admin_user)]
StandardUser = Annotated[object, Depends(_get_standard_user)]
AuthenticatedUser = Annotated[object, Depends(_get_any_authenticated_user)]
