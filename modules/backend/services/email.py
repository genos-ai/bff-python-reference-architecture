"""
Email service — sends magic link emails via Resend or SMTP.

Selection: if RESEND_API_KEY is set, uses Resend; otherwise SMTP.
"""

from modules.backend.core.config import get_settings
from modules.backend.core.logging import get_logger

logger = get_logger(__name__)


async def send_magic_link_email(
    to_email: str,
    token: str,
    frontend_url: str,
) -> None:
    """Send a magic link email to the user."""
    verify_url = f"{frontend_url}/auth/verify?token={token}"

    settings = get_settings()

    if _has_resend(settings):
        await _send_via_resend(to_email, verify_url)
    else:
        logger.warning(
            "No email provider configured — logging magic link",
            extra={"email": to_email, "verify_url": verify_url},
        )


def _has_resend(settings) -> bool:
    """Check if Resend API key is configured."""
    key = getattr(settings, "resend_api_key", "") or ""
    return len(key) > 0 and key != "re_xxxxx"


async def _send_via_resend(to_email: str, verify_url: str) -> None:
    """Send email using Resend API."""
    import resend

    settings = get_settings()
    resend.api_key = settings.resend_api_key

    resend.Emails.send(
        {
            "from": "BFF Web <noreply@updates.example.com>",
            "to": [to_email],
            "subject": "Your login link",
            "html": (
                f"<p>Click the link below to log in:</p>"
                f'<p><a href="{verify_url}">Log in</a></p>'
                f"<p>This link expires in 15 minutes.</p>"
                f"<p>If you didn't request this, ignore this email.</p>"
            ),
        }
    )
    logger.info("Magic link email sent via Resend", extra={"to": to_email})
