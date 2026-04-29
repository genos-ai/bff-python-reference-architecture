"""
SQLAlchemy Base Model.

Base class for all database models with common mixins.
"""

from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from modules.backend.core.utils import utc_now


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class UUIDMixin:
    """Mixin that adds a UUID primary key."""

    id: Mapped[UUID] = mapped_column(
        sa.Uuid,
        primary_key=True,
        default=uuid4,
    )


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps (naive UTC)."""

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
