"""
User profile integration tests.

PATCH /users/me — update display name
DELETE /users/me — deactivate account
"""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

# =============================================================================
# Helper — reuse auth flow from test_auth
# =============================================================================

_captured_token: str | None = None


async def _get_auth(client):
    """Get access token via magic link flow with a unique email per call."""
    global _captured_token
    email = f"profile-{uuid4().hex[:8]}@example.com"

    with patch(
        "modules.backend.services.email.send_magic_link_email",
        new_callable=AsyncMock,
    ) as mock_email:

        async def capture(email, token, frontend_url):
            global _captured_token
            _captured_token = token

        mock_email.side_effect = capture
        await client.post(
            "/api/v1/auth/magic-link",
            json={"email": email},
        )

    raw_token = _captured_token
    _captured_token = None

    r = await client.post("/api/v1/auth/verify", json={"token": raw_token})
    data = r.json()["data"]
    return data["access_token"], {"Authorization": f"Bearer {data['access_token']}"}


# =============================================================================
# PATCH /users/me
# =============================================================================


class TestUpdateProfile:
    async def test_set_display_name(self, client):
        _, headers = await _get_auth(client)

        r = await client.patch(
            "/api/v1/users/me",
            headers=headers,
            json={"display_name": "Trader Joe"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["display_name"] == "Trader Joe"

    async def test_clear_display_name(self, client):
        _, headers = await _get_auth(client)

        # Set it first
        await client.patch(
            "/api/v1/users/me",
            headers=headers,
            json={"display_name": "Temp Name"},
        )

        # Clear it
        r = await client.patch(
            "/api/v1/users/me",
            headers=headers,
            json={"display_name": None},
        )
        assert r.status_code == 200
        assert r.json()["data"]["display_name"] is None

    async def test_requires_auth(self, client):
        r = await client.patch(
            "/api/v1/users/me",
            json={"display_name": "Hacker"},
        )
        assert r.status_code == 401


# =============================================================================
# DELETE /users/me
# =============================================================================


class TestDeactivateAccount:
    async def test_deactivate_returns_204(self, client):
        _, headers = await _get_auth(client)

        r = await client.delete("/api/v1/users/me", headers=headers)
        assert r.status_code == 204

    async def test_deactivated_user_cannot_access(self, client):
        """After deactivation, the same token should be rejected."""
        _, headers = await _get_auth(client)

        # Deactivate
        r = await client.delete("/api/v1/users/me", headers=headers)
        assert r.status_code == 204

        # Try to access a protected endpoint
        r = await client.get("/api/v1/views/dashboard", headers=headers)
        assert r.status_code == 401

    async def test_requires_auth(self, client):
        r = await client.delete("/api/v1/users/me")
        assert r.status_code == 401
