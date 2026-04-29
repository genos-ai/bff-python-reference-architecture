"""
Event Schemas.

Standardized event envelope and domain event types.

Naming convention for event_type: domain.entity.action (dot notation)
Stream naming convention: {domain}:{event-type} (colon-separated)
"""

from uuid import uuid4

from pydantic import BaseModel, Field

from modules.backend.core.utils import utc_now


class EventEnvelope(BaseModel):
    """Base event envelope — all events inherit from this."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    event_version: int = 1
    timestamp: str = Field(default_factory=lambda: utc_now().isoformat())
    source: str
    correlation_id: str
    trace_id: str | None = None
    payload: dict
