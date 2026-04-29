"""
Integration Test Fixtures.

Fixtures for integration tests - uses real database and services.
These fixtures build on the root conftest.py database fixtures.
"""

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from modules.backend.core.database import get_db_session

# =============================================================================
# API Client Fixtures
# =============================================================================


def _create_test_app(
    session_factory=None,
):
    """
    Build a lightweight test app with routers and exception handlers
    but WITHOUT BaseHTTPMiddleware (which breaks async DB sessions
    by running handlers in a different task context).
    """
    from fastapi import FastAPI

    from modules.backend.api.health import router as health_router
    from modules.backend.api.v1 import router as api_v1_router
    from modules.backend.core.exception_handlers import register_exception_handlers

    app = FastAPI(title="Test App")
    register_exception_handlers(app)
    app.include_router(health_router, tags=["health"])
    app.include_router(api_v1_router, prefix="/api/v1")

    if session_factory is not None:

        async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
            async with session_factory() as session:
                yield session
                await session.commit()

        app.dependency_overrides[get_db_session] = override_get_db_session

    return app


@pytest.fixture
async def client(
    db_session_factory,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client with database session override.

    Each API request gets its own session from the factory.
    Sessions are rolled back after each request for isolation.
    """
    with (
        patch("modules.backend.core.config.get_settings") as mock_secrets,
        patch("modules.backend.core.config.get_app_config") as mock_config,
        patch("modules.backend.core.security.get_settings") as mock_security_settings,
        patch("modules.backend.core.security.get_app_config") as mock_security_config,
    ):
        mock_secrets.return_value = _create_mock_settings()
        mock_security_settings.return_value = _create_mock_settings()
        mock_app_config = _create_mock_app_config()
        mock_config.return_value = mock_app_config
        mock_security_config.return_value = mock_app_config

        app = _create_test_app(db_session_factory)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as test_client:
            yield test_client

        app.dependency_overrides.clear()


@pytest.fixture
async def client_no_db() -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client without database dependency override.

    Use this for testing endpoints that don't require database access
    (e.g., health checks, static responses).
    """
    with (
        patch("modules.backend.core.config.get_settings") as mock_secrets,
        patch("modules.backend.core.config.get_app_config") as mock_config,
        patch("modules.backend.core.security.get_settings") as mock_security_settings,
        patch("modules.backend.core.security.get_app_config") as mock_security_config,
    ):
        mock_secrets.return_value = _create_mock_settings()
        mock_security_settings.return_value = _create_mock_settings()
        mock_app_config = _create_mock_app_config()
        mock_config.return_value = mock_app_config
        mock_security_config.return_value = mock_app_config

        app = _create_test_app()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as test_client:
            yield test_client


# =============================================================================
# Mock Settings Helper
# =============================================================================


def _create_mock_settings() -> Any:
    """Create a real Settings-like object for testing with typed fields."""
    from unittest.mock import MagicMock

    settings = MagicMock()
    settings.db_password = "test_pass"
    settings.redis_password = ""
    settings.app_secret_key = "test-secret-key-that-is-long-enough-for-validation"
    settings.encryption_key = ""
    settings.anthropic_api_key = ""
    return settings


def _create_mock_app_config() -> Any:
    """
    Create a test AppConfig using real Pydantic schema instances.

    Uses the actual schema classes from config_schema.py so that
    integration tests exercise the same attribute access paths as
    production code.
    """
    from modules.backend.core.config_schema import (
        ApplicationSchema,
        ConcurrencySchema,
        DatabaseSchema,
        EventsSchema,
        FeaturesSchema,
        LoggingSchema,
        ObservabilitySchema,
        SecuritySchema,
    )

    class TestAppConfig:
        """Test-specific AppConfig with real schema instances."""

        def __init__(self) -> None:
            self.application = ApplicationSchema(
                name="Test Application",
                version="1.0.0",
                description="Test application",
                environment="test",
                debug=True,
                api_prefix="/api",
                docs_enabled=True,
                server={"host": "127.0.0.1", "port": 8000},
                cors={"origins": ["http://localhost:3000"]},
                pagination={"default_limit": 50, "max_limit": 100},
                timeouts={"database": 10, "external_api": 30, "background": 120},
            )
            self.database = DatabaseSchema(
                host="localhost",
                port=5432,
                name="test_db",
                user="test_user",
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                echo=False,
                echo_pool=False,
                redis={
                    "host": "localhost",
                    "port": 6379,
                    "db": 0,
                    "broker": {
                        "queue_name": "test_tasks",
                        "result_expiry_seconds": 3600,
                    },
                },
            )
            self.logging = LoggingSchema(
                level="WARNING",
                format="console",
                handlers={
                    "console": {"enabled": True},
                    "file": {
                        "enabled": False,
                        "path": "var/logs/test.jsonl",
                        "max_bytes": 10485760,
                        "backup_count": 5,
                    },
                },
            )
            self.features = FeaturesSchema(
                auth_magic_link_enabled=True,
                auth_rate_limit_enabled=False,
                api_detailed_errors=True,
                api_request_logging=False,
                security_headers_enabled=False,
                security_cors_enforce_production=False,
                background_tasks_enabled=False,
                events_enabled=False,
                events_publish_enabled=False,
                observability_tracing_enabled=False,
                observability_metrics_enabled=False,
            )
            self.security = SecuritySchema(
                jwt={
                    "algorithm": "HS256",
                    "access_token_expire_minutes": 30,
                    "refresh_token_expire_days": 7,
                    "audience": "bff-web-api",
                },
                rate_limiting={
                    "api": {
                        "requests_per_minute": 60,
                        "requests_per_hour": 1000,
                    },
                },
                request_limits={
                    "max_body_size_bytes": 5242880,
                    "max_header_size_bytes": 8192,
                },
                headers={
                    "x_content_type_options": "nosniff",
                    "x_frame_options": "DENY",
                    "referrer_policy": "strict-origin-when-cross-origin",
                    "hsts_enabled": False,
                    "hsts_max_age": 31536000,
                },
                secrets_validation={
                    "app_secret_min_length": 32,
                },
                cors={
                    "enforce_in_production": False,
                    "allow_methods": [
                        "GET",
                        "POST",
                        "PATCH",
                        "DELETE",
                        "OPTIONS",
                    ],
                    "allow_headers": ["Authorization", "Content-Type"],
                },
            )
            self.observability = ObservabilitySchema(
                tracing={
                    "enabled": False,
                    "service_name": "bff-test",
                    "exporter": "otlp",
                    "otlp_endpoint": "http://localhost:4317",
                    "sample_rate": 1.0,
                },
                metrics={"enabled": False},
                health_checks={
                    "ready_timeout_seconds": 5,
                    "detailed_auth_required": False,
                },
            )
            self.concurrency = ConcurrencySchema(
                thread_pool={"max_workers": 2},
                process_pool={"max_workers": 1},
                semaphores={
                    "database": 10,
                    "redis": 20,
                    "external_api": 5,
                    "llm": 2,
                },
                shutdown={"drain_seconds": 5},
            )
            self.events = EventsSchema(
                broker={"type": "redis"},
                streams={"default_maxlen": 1000},
                consumers={},
                dlq={"enabled": True, "stream_prefix": "dlq"},
            )

    return TestAppConfig()


# =============================================================================
# API Response Assertion Helpers
# =============================================================================


class ApiAssertions:
    """Helper class for API response assertions."""

    @staticmethod
    def assert_success(response: Any, expected_status: int = 200) -> dict[str, Any]:
        """Assert API response is successful."""
        assert response.status_code == expected_status, (
            f"Expected status {expected_status}, got {response.status_code}: " f"{response.text}"
        )
        data = response.json()
        assert data.get("success") is True, f"Response not successful: {data}"
        return data

    @staticmethod
    def assert_error(
        response: Any,
        expected_status: int,
        expected_code: str | None = None,
    ) -> dict[str, Any]:
        """Assert API response is an error."""
        assert response.status_code == expected_status, (
            f"Expected status {expected_status}, got {response.status_code}: " f"{response.text}"
        )
        data = response.json()
        assert data.get("success") is False, f"Response should be error: {data}"
        assert data.get("error") is not None, f"Missing error details: {data}"

        if expected_code:
            actual_code = data["error"].get("code")
            assert (
                actual_code == expected_code
            ), f"Expected error code {expected_code}, got {actual_code}"

        return data

    @staticmethod
    def assert_validation_error(
        response: Any,
        field: str | None = None,
    ) -> dict[str, Any]:
        """Assert API response is a validation error (422)."""
        data = ApiAssertions.assert_error(response, 422, "VAL_REQUEST_INVALID")

        if field:
            errors = data["error"].get("details", {}).get("validation_errors", [])
            fields = [e.get("field", "") for e in errors]
            assert any(field in f for f in fields), (
                f"Expected validation error for field '{field}', " f"got errors for: {fields}"
            )

        return data


@pytest.fixture
def api() -> ApiAssertions:
    """Provide API assertion helpers."""
    return ApiAssertions()


# =============================================================================
# Authentication Fixtures
# =============================================================================


@pytest.fixture
def auth_headers(test_settings: dict[str, Any]) -> dict[str, str]:
    """Provide authentication headers for API requests."""
    from modules.backend.core.security import create_access_token

    token = create_access_token(
        data={"sub": "test-user-id", "email": "test@example.com"},
    )
    return {"Authorization": f"Bearer {token}"}
