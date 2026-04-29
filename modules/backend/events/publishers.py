"""
Event Publishers.

Base publisher with feature-flag gating. Domain-specific publishers
will be added as modules are built (e.g. SyncEventPublisher).
"""

from modules.backend.core.logging import get_logger

logger = get_logger(__name__)


def _get_trace_id() -> str | None:
    """Extract current OpenTelemetry trace ID if available."""
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        if span and span.is_recording():
            return format(span.get_span_context().trace_id, "032x")
    except ImportError:
        pass
    return None


async def publish_event(stream: str, event) -> None:
    """Publish an event if the feature flag is enabled."""
    from modules.backend.core.config import get_app_config

    if not get_app_config().features.events_publish_enabled:
        return

    from modules.backend.events.broker import get_event_broker

    broker = get_event_broker()
    await broker.publish(event.model_dump(), channel=stream)
    logger.debug(
        "Event published",
        extra={
            "stream": stream,
            "event_type": event.event_type,
            "event_id": event.event_id,
        },
    )
