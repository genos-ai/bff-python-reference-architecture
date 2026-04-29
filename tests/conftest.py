"""
Root Pytest Fixtures.

Shared fixtures available to all test types.

Test Database Configuration:
    Set TEST_DATABASE_URL to your PostgreSQL test database:

        export TEST_DATABASE_URL="postgresql+asyncpg://bff_app:localdev@localhost/bff_web"  # noqa: E501

    Schema is managed by Alembic migrations — run them before tests.
"""

import os
from collections.abc import AsyncGenerator
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from modules.backend.models.base import Base  # noqa: F401

# =============================================================================
# Database Configuration
# =============================================================================

_DEFAULT_DB_URL = "postgresql+asyncpg://bff_app:localdev@localhost:5432/bff_web"


def get_test_database_url() -> str:
    """Get the PostgreSQL test database URL."""
    return os.environ.get("TEST_DATABASE_URL", _DEFAULT_DB_URL)


# =============================================================================
# Database Engine Fixtures
# =============================================================================


@pytest.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create the test database engine (PostgreSQL).

    Schema is managed by Alembic — tables are NOT created/dropped here.
    Scope is session to avoid recreating the engine for each test.
    """
    engine = create_async_engine(
        get_test_database_url(),
        echo=False,
        pool_size=5,
        max_overflow=10,
    )

    yield engine

    await engine.dispose()


@pytest.fixture(scope="session")
def db_session_factory(db_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Create a session factory bound to the test engine.

    Scope is session to reuse the factory across tests.
    """
    return async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


# =============================================================================
# Database Session Fixtures
# =============================================================================


@pytest.fixture
async def db_session(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session for a single test.

    Each test gets its own session. Changes are rolled back after the test
    to ensure test isolation.
    """
    async with db_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def db_session_committed(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session that commits changes.

    Use when you need committed data (e.g., testing unique constraints).
    WARNING: Data persists — use unique values to avoid cross-test conflicts.
    """
    async with db_session_factory() as session:
        yield session
        await session.commit()


# =============================================================================
# Test Settings Fixtures
# =============================================================================


@pytest.fixture
def test_settings() -> dict[str, Any]:
    """Provide test-specific settings."""
    return {
        "app_name": "Test Application",
        "app_env": "test",
        "app_debug": True,
        "app_log_level": "DEBUG",
        "app_secret_key": "test-secret-key-for-testing-only",
        "jwt_algorithm": "HS256",
        "jwt_access_token_expire_minutes": 5,
    }


# =============================================================================
# Utility Fixtures
# =============================================================================


@pytest.fixture
def anyio_backend() -> str:
    """Specify the async backend for anyio."""
    return "asyncio"
