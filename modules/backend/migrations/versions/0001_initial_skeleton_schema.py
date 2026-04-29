"""initial_skeleton_schema

Revision ID: 0001
Revises:
Create Date: 2026-04-29
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial skeleton tables: users and magic_links."""
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="user",
                   comment="One of: sysadmin, admin, user, viewer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.CheckConstraint(
            "role IN ('sysadmin', 'admin', 'user', 'viewer')",
            name="ck_user_role",
        ),
    )

    op.create_table(
        "magic_links",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "idx_magic_links_lookup",
        "magic_links",
        ["token_hash"],
        unique=False,
        postgresql_where=sa.text("consumed_at IS NULL"),
    )


def downgrade() -> None:
    """Drop skeleton tables."""
    op.drop_index(
        "idx_magic_links_lookup",
        table_name="magic_links",
        postgresql_where=sa.text("consumed_at IS NULL"),
    )
    op.drop_table("magic_links")
    op.drop_table("users")
