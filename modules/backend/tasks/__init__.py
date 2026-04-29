"""
Background Tasks Package.

Taskiq-based background task processing with Redis backend.

Submodules:
    broker    — Taskiq broker configuration (modules.backend.tasks.broker)
    scheduler — Taskiq scheduler configuration (modules.backend.tasks.scheduler)

Import from submodules directly:
    from modules.backend.tasks.broker import get_broker
    from modules.backend.tasks.scheduler import get_scheduler
"""


def __getattr__(name: str):
    """Lazy attribute access for taskiq CLI compatibility."""
    if name == "broker":
        from modules.backend.tasks.broker import get_broker

        return get_broker()
    if name == "scheduler":
        from modules.backend.tasks.scheduler import get_scheduler

        return get_scheduler()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
