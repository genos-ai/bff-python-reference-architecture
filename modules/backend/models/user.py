"""User model."""

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from modules.backend.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(sa.String(100))
    role: Mapped[str] = mapped_column(
        sa.String(20), default="user", nullable=False,
        comment="One of: sysadmin, admin, user, viewer",
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
