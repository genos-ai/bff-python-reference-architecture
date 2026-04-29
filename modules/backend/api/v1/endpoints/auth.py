"""
Auth endpoints — magic link authentication.

POST /auth/magic-link  → Request a login link
POST /auth/verify      → Verify token, get JWT
POST /auth/refresh     → Refresh tokens (cookie)
POST /auth/logout      → Blacklist refresh token
"""

from fastapi import APIRouter, Response

from modules.backend.core.dependencies import DbSession, RefreshToken
from modules.backend.core.logging import get_logger
from modules.backend.schemas.auth import AuthResponse, MagicLinkRequest, VerifyRequest
from modules.backend.schemas.base import ApiResponse
from modules.backend.services.auth import AuthService

logger = get_logger(__name__)

router = APIRouter()


@router.post("/auth/magic-link")
async def request_magic_link(
    body: MagicLinkRequest,
    db: DbSession,
) -> ApiResponse:
    """Request a magic link. Always returns 200 (prevents email enumeration)."""
    service = AuthService(db)
    user_id, raw_token = await service.request_magic_link(body.email)

    # Send email (non-blocking — failures don't block the response)
    try:
        from modules.backend.core.config import get_settings
        from modules.backend.services.email import send_magic_link_email

        settings = get_settings()
        frontend_url = getattr(settings, "frontend_url", "http://localhost:5173")
        await send_magic_link_email(body.email, raw_token, frontend_url)
    except Exception as e:
        logger.error(
            "Failed to send magic link email",
            extra={"email": body.email, "error": str(e)},
        )

    return ApiResponse(
        success=True, data={"message": "If that email exists, a login link was sent."}
    )


@router.post("/auth/verify")
async def verify_magic_link(
    body: VerifyRequest,
    db: DbSession,
    response: Response,
) -> ApiResponse[AuthResponse]:
    """Verify a magic link token and issue JWT tokens."""
    service = AuthService(db)
    result = await service.verify_magic_link(body.token)

    # Set refresh token as HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 86400,
        path="/api/v1/auth",
    )

    return ApiResponse(
        success=True,
        data=AuthResponse(
            access_token=result["access_token"],
            sse_token=result["sse_token"],
            token_type=result["token_type"],
            user=result["user"],
        ),
    )


@router.post("/auth/refresh")
async def refresh_tokens(
    db: DbSession,
    refresh_token: RefreshToken,
    response: Response,
) -> ApiResponse[AuthResponse]:
    """Refresh access token using refresh token from cookie."""
    if not refresh_token:
        from modules.backend.core.exceptions import AuthenticationError

        raise AuthenticationError("No refresh token provided")

    service = AuthService(db)
    result = await service.refresh_tokens(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 86400,
        path="/api/v1/auth",
    )

    return ApiResponse(
        success=True,
        data=AuthResponse(
            access_token=result["access_token"],
            sse_token=result["sse_token"],
            token_type=result["token_type"],
            user=result["user"],
        ),
    )


@router.post("/auth/dev-login")
async def dev_login(
    body: MagicLinkRequest,
    db: DbSession,
    response: Response,
) -> ApiResponse[AuthResponse]:
    """
    Dev-only: skip email, instantly log in. Only available when debug=True.
    """
    from modules.backend.core.config import get_app_config

    if not get_app_config().application.debug:
        from modules.backend.core.exceptions import AuthenticationError

        raise AuthenticationError("Dev login is only available in debug mode")

    service = AuthService(db)
    _, raw_token = await service.request_magic_link(body.email)
    await db.flush()
    result = await service.verify_magic_link(raw_token)

    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 86400,
        path="/api/v1/auth",
    )

    return ApiResponse(
        success=True,
        data=AuthResponse(
            access_token=result["access_token"],
            sse_token=result["sse_token"],
            token_type=result["token_type"],
            user=result["user"],
        ),
    )


@router.post("/auth/logout", status_code=204)
async def logout(
    db: DbSession,
    refresh_token: RefreshToken,
    response: Response,
) -> None:
    """Logout — blacklist refresh token and clear cookie."""
    if refresh_token:
        service = AuthService(db)
        await service.logout(refresh_token)

    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
    )
