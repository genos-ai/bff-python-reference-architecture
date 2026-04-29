"""Database models."""

from modules.backend.models.base import Base, TimestampMixin, UUIDMixin
from modules.backend.models.magic_link import MagicLink
from modules.backend.models.user import User

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    "MagicLink",
    "User",
]
