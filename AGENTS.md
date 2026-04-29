# AGENTS.md — AI Assistant Instructions

This file tells AI coding assistants how to work with this codebase.
For full details, see `docs/99-reference-architecture/`.

## Project Overview

BFF (Backend-for-Frontend) Python web reference architecture skeleton.
FastAPI backend, React frontend, PostgreSQL, Redis, Taskiq, FastStream.

## Critical Rules

- **No hardcoded values.** All configuration from `config/settings/*.yaml`. All secrets from `config/.env`. No hardcoded fallbacks in code, ever.
- **Absolute imports only.** Always `from modules.backend.core.config import ...`. Never relative imports.
- **Centralized logging only.** Always `from modules.backend.core.logging import get_logger`. Never `import logging` directly.
- **Timezone-naive UTC datetimes.** Use `from modules.backend.core.utils import utc_now`. Never `datetime.utcnow()` (deprecated) or `datetime.now()` (local time).
- **`.project_root` marker** determines the project root. Use `find_project_root()` from `modules.backend.core.config`.
- **All CLI scripts must have `--verbose` and `--debug` options** with appropriate logging for each.
- **Files must not exceed 1000 lines.** Target ~400-500 lines. Split into focused submodules if larger.
- **`__init__.py` files must be minimal.** Docstring and necessary exports only. No business logic.
- **Secure by default (P8).** Deny-by-default for all interfaces. Empty allowlists = deny all.
- **No layer skipping.** API -> Service -> Repository -> Model. API must never import repositories.
- **Backend owns all business logic (P1).** Frontend renders only.

## Architecture

### Entry Points
- `run.py` — CLI entry point (Click). Commands: server, worker, scheduler, health, config, test, migrate, event-worker.
- `modules/backend/main.py` — FastAPI app factory.

### Backend Layers (in `modules/backend/`)
| Layer | Directory | Purpose |
|-------|-----------|---------|
| API | `api/` | HTTP endpoints, request validation, response formatting |
| Service | `services/` | Business logic, orchestration, validation rules |
| Repository | `repositories/` | Data access, SQL queries, transactions |
| Model | `models/` | SQLAlchemy ORM entities |
| Schema | `schemas/` | Pydantic request/response models |
| Core | `core/` | Config, logging, security, middleware, database, resilience, RBAC |
| Events | `events/` | FastStream broker, publishers, consumers |
| Tasks | `tasks/` | Taskiq background jobs |

### Roles (RBAC)
Four roles: `sysadmin`, `admin`, `user`, `viewer`.

```python
from modules.backend.core.dependencies import AdminUser, StandardUser, AuthenticatedUser

@router.get("/admin-only")
async def admin_endpoint(user: AdminUser): ...  # sysadmin, admin

@router.get("/write-access")
async def write_endpoint(user: StandardUser): ...  # sysadmin, admin, user

@router.get("/read-access")
async def read_endpoint(user: AuthenticatedUser): ...  # any authenticated role
```

### Configuration
- `config/settings/*.yaml` — All app settings (validated by Pydantic schemas in `core/config_schema.py`)
- `config/.env` — Secrets only (DB_PASSWORD, APP_SECRET_KEY, ENCRYPTION_KEY)
- `core/config.py` — Loads and caches both; `get_app_config()` for YAML, `get_settings()` for secrets

## Code Patterns

### Error Handling
```python
from modules.backend.core.exceptions import NotFoundError
raise NotFoundError("User", user_id)
```

### Logging
```python
from modules.backend.core.logging import get_logger
logger = get_logger(__name__)
logger.info("Operation completed", extra={"user_id": str(user.id)})
```

### Database Sessions
```python
from modules.backend.core.dependencies import DbSession

async def get_user(db: DbSession, user_id: UUID) -> User:
    ...
```

### Events
```python
from modules.backend.events.publishers import publish_event
await publish_event("domain:event-type", event)
```

## Governing Documents

1. **Reference Architecture** — `docs/99-reference-architecture/` (authoritative)

## What NOT To Do

- Don't use `os.getenv()` with fallback defaults — fail fast at startup
- Don't use `datetime.now()` or `datetime.utcnow()` — use `utc_now()`
- Don't import from `models/` or `repositories/` in API endpoints — go through services
- Don't compute fields in endpoints — all computation happens in services or repositories
- Don't add business logic in `__init__.py` files
- Don't use relative imports anywhere in `modules/`
- Don't hardcode URLs, timeouts, or rate limits — use `config/settings/*.yaml`
- Don't store timezone-aware datetimes — use naive UTC everywhere
