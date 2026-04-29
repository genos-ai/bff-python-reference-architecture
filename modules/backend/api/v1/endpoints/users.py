"""
User profile endpoints.

GET    /users/me  -> Get current user profile
PATCH  /users/me  -> Update display name
DELETE /users/me  -> Deactivate account
"""

from fastapi import APIRouter

from modules.backend.core.dependencies import CurrentUser, DbSession
from modules.backend.schemas.auth import UpdateUserRequest, UserResponse
from modules.backend.schemas.base import ApiResponse
from modules.backend.services.user import UserService

router = APIRouter()


@router.get("/users/me")
async def get_profile(
    user: CurrentUser,
) -> ApiResponse[UserResponse]:
    """Get the current user's profile."""
    return ApiResponse(
        success=True,
        data=UserResponse(
            id=str(user.id),
            email=user.email,
            display_name=user.display_name,
            role=user.role,
        ),
    )


@router.patch("/users/me")
async def update_profile(
    body: UpdateUserRequest,
    user: CurrentUser,
    db: DbSession,
) -> ApiResponse[UserResponse]:
    """Update the current user's profile."""
    service = UserService(db)
    updated = await service.update_profile(user.id, body.display_name)
    await db.commit()

    return ApiResponse(
        success=True,
        data=UserResponse(
            id=str(updated.id),
            email=updated.email,
            display_name=updated.display_name,
            role=updated.role,
        ),
    )


@router.delete("/users/me", status_code=204)
async def deactivate_account(
    user: CurrentUser,
    db: DbSession,
) -> None:
    """Deactivate the current user's account (soft delete)."""
    service = UserService(db)
    await service.deactivate(user.id)
    await db.commit()
