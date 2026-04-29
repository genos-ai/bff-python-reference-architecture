# 001 - Project Overview

## What Is This?

A **BFF (Backend-for-Frontend) Python reference architecture** — a production-ready skeleton for building web applications with a Python backend and React frontend.

This repo serves as the standard starting point for new projects. It implements the patterns, rules, and infrastructure documented in `docs/99-reference-architecture/` so that teams start with a working, compliant codebase rather than building from scratch.

## Who Is This For?

- **Developers** starting a new BFF web project — clone it and build on top
- **AI coding assistants** working in this codebase — read `AGENTS.md` for rules and patterns
- **Architects** evaluating or extending the reference architecture standards

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | FastAPI | Async Python web framework |
| Frontend | React + Vite + Tailwind | Single-page application |
| Database | PostgreSQL | Primary data store |
| Cache/Queue | Redis | Caching, task queue, event streams |
| Background Tasks | Taskiq | Async job execution |
| Event Bus | FastStream (Redis Streams) | Event-driven communication |
| ORM | SQLAlchemy (async) | Database access |
| Validation | Pydantic | Request/response schemas, config validation |
| Logging | structlog | Structured JSON logging |
| Observability | OpenTelemetry | Distributed tracing and metrics |

## Project Structure

```
.
├── modules/
│   ├── backend/               # FastAPI application
│   │   ├── api/               # HTTP endpoints (v1 versioned)
│   │   ├── core/              # Config, logging, security, middleware, database
│   │   ├── models/            # SQLAlchemy ORM entities
│   │   ├── repositories/      # Data access layer
│   │   ├── schemas/           # Pydantic request/response models
│   │   ├── services/          # Business logic and orchestration
│   │   ├── events/            # Event broker, publishers, consumers
│   │   ├── tasks/             # Background jobs
│   │   ├── migrations/        # Alembic database migrations
│   │   └── main.py            # App factory
│   └── frontend/              # React + Vite SPA
│
├── config/
│   ├── settings/              # YAML configuration (validated by Pydantic schemas)
│   └── .env                   # Secrets (never committed)
│
├── tests/
│   ├── unit/                  # Fast, isolated tests
│   ├── integration/           # Real database tests
│   └── e2e/                   # Full stack tests
│
├── docs/                      # All documentation
│   ├── 01-getting-started/    # Setup guides (you are here)
│   ├── 02-architecture/       # System design, ADRs
│   ├── 03-principles/         # Design principles
│   ├── 04-rules/              # Machine-readable compliance rules
│   ├── 05-plans/              # Implementation plans
│   ├── 98-research/           # Research and deep dives
│   └── 99-reference-architecture/  # Authoritative standards
│
├── scripts/                   # Development and analysis tools
├── var/                       # Runtime data (logs, cache, data, tmp)
├── AGENTS.md                  # AI assistant instructions
└── docker-compose.yml         # Local dev infrastructure
```

## Backend Architecture

Strict layered architecture — no skipping layers:

```
API Layer       →  HTTP handlers, request validation, response formatting
    ↓
Service Layer   →  Business logic, orchestration, validation rules
    ↓
Repository Layer →  Data access, SQL queries, transactions
    ↓
Model Layer     →  SQLAlchemy ORM entities
```

All business logic lives in the backend. The frontend is a thin presentation layer only.

## Configuration

- **Application settings**: `config/settings/*.yaml` — validated at startup by Pydantic schemas in `core/config_schema.py`
- **Secrets**: `config/.env` — loaded via Pydantic Settings, never hardcoded
- **Access in code**: `get_app_config()` for YAML settings, `get_settings()` for secrets

## Key Design Decisions

1. **Backend-first** — all logic in the backend, clients are presentation only
2. **Config-driven** — no hardcoded values, everything from YAML or env
3. **Fail fast** — missing config or secrets cause startup failure, not runtime errors
4. **Structured logging** — single JSONL log file (`var/logs/system.jsonl`), filter by `source` field
5. **Resilience built-in** — circuit breakers, retries, semaphores, timeouts for all external calls
6. **Event-driven option** — FastStream + Redis Streams for async communication (feature-flagged)

## Getting Started

See the [setup instructions](README.md) in this directory, or jump straight to `AGENTS.md` at the project root for the full rules and patterns reference.

## Reference Architecture

The authoritative standards are in `docs/99-reference-architecture/`:

- **01-18** (`*-core-*`) — Core standards that apply to all projects
- **20-27** (`*-opt-*`) — Optional modules adopted per project need
