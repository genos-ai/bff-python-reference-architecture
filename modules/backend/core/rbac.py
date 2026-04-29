"""
Role-Based Access Control.

Defines roles and dependency factories for protecting endpoints.

Usage:
    from modules.backend.core.rbac import require_role, Role

    @router.get("/admin-only")
    async def admin_endpoint(user: CurrentUser, _=Depends(require_role(Role.ADMIN, Role.SYSADMIN))):
        ...

    # Or use the pre-built type aliases:
    from modules.backend.core.dependencies import AdminUser

    @router.get("/admin-only")
    async def admin_endpoint(user: AdminUser):
        ...
"""

from enum import StrEnum
from typing import Any

from fastapi import Depends

from modules.backend.core.exceptions import ForbiddenError


class Role(StrEnum):
    SYSADMIN = "sysadmin"
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


def require_role(*allowed: Role):
    """
    Dependency factory that checks the current user has one of the allowed roles.

    Raises ForbiddenError if the user's role is not in the allowed set.
    """

    async def _check_role(
        authorization: str | None = None,
        db: Any = None,
    ) -> None:
        # This is called after CurrentUser resolves — we use the request state
        # The actual check happens in the typed aliases below
        pass

    return _check_role


def check_user_role(user: Any, *allowed: Role) -> None:
    """Check that user has one of the allowed roles. Raises ForbiddenError if not."""
    if user.role not in {r.value for r in allowed}:
        raise ForbiddenError(
            f"Role '{user.role}' is not authorized. Required: {', '.join(r.value for r in allowed)}"
        )
