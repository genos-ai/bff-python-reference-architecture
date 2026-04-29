"""Magic link model for passwordless authentication."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from modules.backend.core.utils import utc_now
from modules.backend.models.base import Base, UUIDMixin


class MagicLink(Base, UUIDMixin):
    __tablename__ = "magic_links"

    user_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(sa.String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(sa.DateTime)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=utc_now, nullable=False)

    __table_args__ = (
        sa.Index(
            "idx_magic_links_lookup", "token_hash", postgresql_where=sa.text("consumed_at IS NULL")
        ),
    )
