"""
Unit Tests for Security Module.

Black box tests against the public interface of security.py.
JWT operations execute for real. Only the config boundary is stubbed.
"""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from modules.backend.core.config_schema import JwtSchema
from modules.backend.core.exceptions import AuthenticationError
from modules.backend.core.security import (
    create_access_token,
    create_refresh_token,
    create_sse_token,
    decode_token,
    generate_magic_link_token,
    hash_token,
)

TEST_JWT_SECRET = "test-secret-key-that-is-long-enough-for-testing-purposes"


@pytest.fixture
def jwt_config():
    """Real Pydantic JwtSchema with test values."""
    return JwtSchema(
        algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_days=7,
        audience="test-api",
    )


@pytest.fixture
def _stub_config(jwt_config):
    """Stub the config boundary so security functions can resolve settings."""
    settings = SimpleNamespace(app_secret_key=TEST_JWT_SECRET)
    app_config = SimpleNamespace(security=SimpleNamespace(jwt=jwt_config))
    with (
        patch(
            "modules.backend.core.security.get_settings",
            return_value=settings,
        ),
        patch(
            "modules.backend.core.security.get_app_config",
            return_value=app_config,
        ),
    ):
        yield


# =============================================================================
# JWT Access Tokens
# =============================================================================


@pytest.mark.usefixtures("_stub_config")
class TestCreateAccessToken:
    """Tests for JWT access token creation and decoding."""

    def test_round_trip_preserves_payload(self):
        token = create_access_token({"sub": "user-42", "role": "admin"})
        payload = decode_token(token)
        assert payload["sub"] == "user-42"
        assert payload["role"] == "admin"

    def test_token_includes_access_type(self):
        token = create_access_token({"sub": "user-1"})
        payload = decode_token(token)
        assert payload["type"] == "access"

    def test_token_includes_expiration(self):
        token = create_access_token({"sub": "user-1"})
        payload = decode_token(token)
        assert "exp" in payload

    def test_custom_expiration_delta(self):
        short = create_access_token({"sub": "u"}, expires_delta=timedelta(minutes=5))
        long = create_access_token({"sub": "u"}, expires_delta=timedelta(hours=24))
        short_exp = decode_token(short)["exp"]
        long_exp = decode_token(long)["exp"]
        assert long_exp > short_exp

    def test_does_not_mutate_input_data(self):
        data = {"sub": "user-1"}
        create_access_token(data)
        assert data == {"sub": "user-1"}


# =============================================================================
# JWT Refresh Tokens
# =============================================================================


@pytest.mark.usefixtures("_stub_config")
class TestCreateRefreshToken:
    """Tests for JWT refresh token creation."""

    def test_round_trip_preserves_payload(self):
        token = create_refresh_token({"sub": "user-99"})
        payload = decode_token(token)
        assert payload["sub"] == "user-99"

    def test_token_includes_refresh_type(self):
        token = create_refresh_token({"sub": "user-1"})
        payload = decode_token(token)
        assert payload["type"] == "refresh"

    def test_refresh_expires_later_than_access(self):
        access = create_access_token({"sub": "u"})
        refresh = create_refresh_token({"sub": "u"})
        access_exp = decode_token(access)["exp"]
        refresh_exp = decode_token(refresh)["exp"]
        assert refresh_exp > access_exp


# =============================================================================
# JWT SSE Tokens
# =============================================================================


@pytest.mark.usefixtures("_stub_config")
class TestCreateSseToken:
    """Tests for SSE token creation."""

    def test_round_trip_preserves_payload(self):
        token = create_sse_token({"sub": "user-1"})
        payload = decode_token(token)
        assert payload["sub"] == "user-1"

    def test_token_includes_sse_type(self):
        token = create_sse_token({"sub": "user-1"})
        payload = decode_token(token)
        assert payload["type"] == "sse"


# =============================================================================
# Token Type Validation
# =============================================================================


@pytest.mark.usefixtures("_stub_config")
class TestDecodeTokenTypeValidation:
    """Tests for expected_type enforcement on decode."""

    def test_access_token_passes_access_check(self):
        token = create_access_token({"sub": "u"})
        payload = decode_token(token, expected_type="access")
        assert payload["type"] == "access"

    def test_access_token_fails_refresh_check(self):
        token = create_access_token({"sub": "u"})
        with pytest.raises(AuthenticationError, match="Expected refresh"):
            decode_token(token, expected_type="refresh")

    def test_refresh_token_fails_access_check(self):
        token = create_refresh_token({"sub": "u"})
        with pytest.raises(AuthenticationError, match="Expected access"):
            decode_token(token, expected_type="access")


# =============================================================================
# Token Decoding — Failure Cases
# =============================================================================


@pytest.mark.usefixtures("_stub_config")
class TestDecodeTokenFailures:
    """Tests for token decoding failures."""

    def test_garbage_token_raises_authentication_error(self):
        with pytest.raises(AuthenticationError):
            decode_token("not-a-jwt-token")

    def test_empty_token_raises_authentication_error(self):
        with pytest.raises(AuthenticationError):
            decode_token("")

    def test_tampered_token_raises_authentication_error(self):
        token = create_access_token({"sub": "user-1"})
        tampered = token[:-4] + "XXXX"
        with pytest.raises(AuthenticationError):
            decode_token(tampered)

    def test_expired_token_raises_authentication_error(self):
        token = create_access_token(
            {"sub": "user-1"},
            expires_delta=timedelta(seconds=-1),
        )
        with pytest.raises(AuthenticationError):
            decode_token(token)


# =============================================================================
# Magic Link Token Hashing
# =============================================================================


class TestMagicLinkTokens:
    """Tests for magic link token generation and hashing."""

    def test_generate_returns_raw_and_hash(self):
        raw, hashed = generate_magic_link_token()
        assert isinstance(raw, str)
        assert isinstance(hashed, str)
        assert raw != hashed

    def test_hash_is_deterministic(self):
        assert hash_token("hello") == hash_token("hello")

    def test_hash_is_sha256_hex(self):
        result = hash_token("test")
        assert len(result) == 64  # SHA-256 hex digest

    def test_generated_token_hashes_to_stored_hash(self):
        raw, stored_hash = generate_magic_link_token()
        assert hash_token(raw) == stored_hash

    def test_each_call_produces_unique_token(self):
        raw_a, _ = generate_magic_link_token()
        raw_b, _ = generate_magic_link_token()
        assert raw_a != raw_b
