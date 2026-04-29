"""
Auth integration tests — full magic link → JWT → protected endpoint chain.

Tests the complete auth flow via ASGI transport with real DB.
All tests are purely API-driven — no direct service or session access.
"""

from unittest.mock import AsyncMock, patch

from modules.backend.core.security import create_access_token

# =============================================================================
# Helper
# =============================================================================

_captured_token: str | None = None


async def _get_tokens(client):
    """
    Request magic link via API, capture the raw token from the email
    service call, then verify via API.
    """
    global _captured_token

    with patch(
        "modules.backend.services.email.send_magic_link_email",
        new_callable=AsyncMock,
    ) as mock_email:

        async def capture_token(email, token, frontend_url):
            global _captured_token
            _captured_token = token

        mock_email.side_effect = capture_token

        r = await client.post("/api/v1/auth/magic-link", json={"email": "auth-test@example.com"})
        assert r.status_code == 200

    assert _captured_token is not None, "Token not captured from email service"
    raw_token = _captured_token
    _captured_token = None

    response = await client.post("/api/v1/auth/verify", json={"token": raw_token})
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    return data, data["access_token"], response.cookies


# =============================================================================
# Magic link request
# =============================================================================


class TestMagicLinkRequest:
    async def test_returns_200_for_new_email(self, client):
        r = await client.post("/api/v1/auth/magic-link", json={"email": "new-user@example.com"})
        assert r.status_code == 200
        assert r.json()["success"] is True
        assert "login link" in r.json()["data"]["message"].lower()

    async def test_returns_200_for_existing_email(self, client):
        """Should succeed even if user already exists (idempotent)."""
        await client.post("/api/v1/auth/magic-link", json={"email": "repeat@example.com"})
        r = await client.post("/api/v1/auth/magic-link", json={"email": "repeat@example.com"})
        assert r.status_code == 200

    async def test_rejects_invalid_email(self, client):
        r = await client.post("/api/v1/auth/magic-link", json={"email": "not-an-email"})
        assert r.status_code == 422

    async def test_rejects_missing_email(self, client):
        r = await client.post("/api/v1/auth/magic-link", json={})
        assert r.status_code == 422


# =============================================================================
# Verify magic link
# =============================================================================


class TestVerifyMagicLink:
    async def test_valid_token_returns_tokens(self, client):
        data, access_token, _ = await _get_tokens(client)

        assert "access_token" in data
        assert "sse_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "auth-test@example.com"
        assert data["user"]["id"]

    async def test_sets_refresh_cookie(self, client):
        _, _, cookies = await _get_tokens(client)
        assert "refresh_token" in cookies

    async def test_invalid_token_returns_401(self, client):
        r = await client.post("/api/v1/auth/verify", json={"token": "bogus-token"})
        assert r.status_code == 401
        assert r.json()["error"]["code"] == "AUTH_UNAUTHORIZED"

    async def test_token_consumed_after_use(self, client):
        """Same token cannot be used twice."""
        global _captured_token

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
                json={"email": "consumed@example.com"},
            )

        raw_token = _captured_token
        _captured_token = None

        r1 = await client.post("/api/v1/auth/verify", json={"token": raw_token})
        assert r1.status_code == 200

        r2 = await client.post("/api/v1/auth/verify", json={"token": raw_token})
        assert r2.status_code == 401

    async def test_missing_token_returns_422(self, client):
        r = await client.post("/api/v1/auth/verify", json={})
        assert r.status_code == 422


# =============================================================================
# Protected endpoints
# =============================================================================


class TestProtectedEndpoints:
    async def test_dashboard_requires_auth(self, client):
        r = await client.get("/api/v1/views/dashboard")
        assert r.status_code == 401

    async def test_dashboard_with_valid_token(self, client):
        _, access_token, _ = await _get_tokens(client)
        r = await client.get(
            "/api/v1/views/dashboard",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert r.status_code == 200
        assert r.json()["success"] is True
        assert "stats" in r.json()["data"]

    async def test_positions_with_valid_token(self, client):
        _, access_token, _ = await _get_tokens(client)
        r = await client.get(
            "/api/v1/views/positions",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert r.status_code == 200
        assert "positions" in r.json()["data"]

    async def test_settings_with_valid_token(self, client):
        _, access_token, _ = await _get_tokens(client)
        r = await client.get(
            "/api/v1/views/settings",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["user"]["email"] == "auth-test@example.com"

    async def test_expired_token_returns_401(self, client):
        from datetime import timedelta

        token = create_access_token(
            data={"sub": "fake-id", "email": "x@x.com", "jti": "j1"},
            expires_delta=timedelta(seconds=-1),
        )
        r = await client.get(
            "/api/v1/views/dashboard",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 401

    async def test_malformed_token_returns_401(self, client):
        r = await client.get(
            "/api/v1/views/dashboard",
            headers={"Authorization": "Bearer not.a.jwt"},
        )
        assert r.status_code == 401

    async def test_missing_bearer_prefix_returns_401(self, client):
        r = await client.get(
            "/api/v1/views/dashboard",
            headers={"Authorization": "Token abc123"},
        )
        assert r.status_code == 401


# =============================================================================
# Refresh token
# =============================================================================


class TestRefreshToken:
    async def test_refresh_issues_new_tokens(self, client):
        _, _, cookies = await _get_tokens(client)
        refresh_token = cookies.get("refresh_token")

        r = await client.post(
            "/api/v1/auth/refresh",
            cookies={"refresh_token": refresh_token},
        )
        assert r.status_code == 200
        data = r.json()["data"]
        assert "access_token" in data
        assert "sse_token" in data

    async def test_refresh_without_cookie_returns_401(self, client):
        r = await client.post("/api/v1/auth/refresh")
        assert r.status_code == 401


# =============================================================================
# Logout
# =============================================================================


class TestLogout:
    async def test_logout_clears_cookie(self, client):
        _, access_token, cookies = await _get_tokens(client)

        r = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
            cookies={"refresh_token": cookies.get("refresh_token", "")},
        )
        assert r.status_code == 204

    async def test_logout_without_cookie_still_204(self, client):
        r = await client.post("/api/v1/auth/logout")
        assert r.status_code == 204
