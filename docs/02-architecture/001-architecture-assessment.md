# 001 - Architecture Assessment

*Assessed: 2026-04-28*

## Summary

A **BFF (Backend-for-Frontend) Python reference architecture** skeleton. The core is production-capable: full auth flow, S3 storage, background tasks, event bus, and structured logging. The code is clean, strictly layered, and follows the reference architecture standards closely.

**Overall readiness: 72%** — working business logic with gaps in resilience, observability, frontend, and test coverage.

---

## System Architecture

```
                    ┌──────────────────────────┐
                    │   Frontend (React/Vite)   │  ← Boilerplate only
                    │   modules/frontend/       │
                    └────────────┬─────────────┘
                                 │ HTTP/REST + SSE
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                     FastAPI Application                          │
│                     modules/backend/                             │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │  API Layer  │──│  Services    │──│   Repositories          │ │
│  │  api/v1/    │  │  services/   │  │   repositories/         │ │
│  └──────┬──────┘  └──────┬───────┘  └────────────┬────────────┘ │
│         │                │                        │              │
│  ┌──────┴──────┐  ┌──────┴───────┐  ┌────────────┴────────────┐ │
│  │  Schemas    │  │  Events      │  │   Models (SQLAlchemy)   │ │
│  │  schemas/   │  │  events/     │  │   models/               │ │
│  └─────────────┘  └──────────────┘  └─────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Core Infrastructure                      │ │
│  │  config, logging, security, middleware, database,           │ │
│  │  concurrency, resilience, health, encryption                │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
         │              │                     │
         ▼              ▼                     ▼
┌──────────────┐ ┌──────────────┐  ┌────────────────────┐
│  PostgreSQL  │ │    Redis     │  │  S3 / MinIO        │
│  (Primary)   │ │  (Cache,     │  │  (File Storage)    │
│              │ │   Tasks,     │  │                    │
│              │ │   Events,    │  │                    │
│              │ │   Pub/Sub)   │  │                    │
└──────────────┘ └──────────────┘  └────────────────────┘
```

---

## Backend Layers

Strict layered architecture — no skipping allowed.

```
API Layer        →  HTTP endpoints, request validation, response envelope
     ↓
Service Layer    →  Business logic, orchestration, domain validation
     ↓
Repository Layer →  Data access, SQL queries, transactions
     ↓
Model Layer      →  SQLAlchemy ORM entities
```

| Layer | Directory | Files | Status |
|-------|-----------|-------|--------|
| API | `api/v1/endpoints/` | auth, users, connections, positions, notes, attachments, export, events, views | 95% — all endpoints have real logic |
| Services | `services/` | auth, user, connection, journal, views, sync, storage, email, exchange/, grouper/, indicators/ | 90% — full business logic |
| Repositories | `repositories/` | user, position, fill, connection, candle, magic_link, note, attachment | 95% — real queries, generic base |
| Models | `models/` | user, position, fill, candle, connection, magic_link, note, attachment | 95% — full schema with indexes |
| Schemas | `schemas/` | auth, position, connection, note, attachment, views, base | 95% — request/response types |
| Core | `core/` | config, logging, security, middleware, database, concurrency, resilience, health, encryption, rate_limiter | 85% — infrastructure solid, some not wired |

---

## Domain Architecture

### Exchange Integration

Port/adapter pattern with a factory registry.

```
ExchangeProtocol (interface)
    ├── BinanceFuturesAdapter   ← HMAC-SHA256 signing, cursor pagination
    └── BybitAdapter            ← Spot, Linear, Inverse products
```

- Read-only API key validation (rejects write permissions)
- AES-256-GCM encryption for stored API keys
- Configurable rate limits, timeouts, retries (in `exchange.yaml`)

### Sync Pipeline

Full end-to-end flow:

```
POST /connections/{id}/sync
    → Enqueue Taskiq task (202 Accepted)
        → SyncService.sync_connection()
            → Decrypt API keys
            → Get exchange adapter
            → Fetch fills page-by-page
            → Upsert fills, update cursor
            → group_fills() → 5-state machine (open/add/close/partial/flip)
            → Reconcile with existing positions
            → Persist positions + fill assignments
            → Enqueue indicator calculation tasks
            → Publish events to Redis
```

### Position Grouper

Pure function: fills -> positions. Five-state machine:

| State | Trigger | Result |
|-------|---------|--------|
| A | First fill, no open position | Open new position |
| B | Fill in same direction | Scale in (add to position) |
| C | Opposing fill closes exactly | Close position |
| D | Opposing fill partially closes | Reduce position |
| E | Opposing fill exceeds position | Flip direction (split commission) |

### Indicator Engine

Pure function: candles -> indicator snapshots. Registry-based.

| Indicator | Periods |
|-----------|---------|
| EMA | 9, 21, 50, 200 |
| RSI | 14 |
| MACD | 12/26/9 |
| Bollinger Bands | 20/2 |

Multi-timeframe: 1h, 4h, 1d. Graceful failure per indicator (no cascade).

---

## Infrastructure

### Authentication Flow

```
Magic Link Request → Email (Resend API) → Token (15-min expiry)
    → Verify Token → JWT access (30-min) + refresh (7-day HttpOnly cookie)
        → SSE token for event streaming
```

Dev-only: `POST /auth/dev-login` for instant JWT without email (debug=true only).

### Background Tasks

| Component | Technology | Status |
|-----------|-----------|--------|
| Task broker | Taskiq + Redis | Working |
| Task scheduler | LabelScheduleSource | Infrastructure ready, no tasks scheduled |
| Defined tasks | sync_trades, calculate_indicators, cleanup | Working (sync + indicators), cleanup is stub |

### Event Architecture

| Component | Technology | Status |
|-----------|-----------|--------|
| Event broker | FastStream + Redis Streams | Working |
| Publishers | `publish_event(stream, event)` | Working, feature-flag gated |
| Consumers | Subscriber handlers | Not implemented (stubs only) |
| SSE | Server-Sent Events to frontend | Working (Redis pub/sub) |

### Configuration

13 YAML config files, all validated by Pydantic schemas at startup:

| File | Purpose |
|------|---------|
| application.yaml | App name, server, CORS, pagination, timeouts |
| database.yaml | PostgreSQL, Redis connection settings |
| logging.yaml | Log level, format, file output path |
| features.yaml | 10 feature flags |
| security.yaml | JWT, rate limits, headers, secrets validation |
| observability.yaml | Tracing, metrics, health checks |
| concurrency.yaml | Thread/process pools, semaphores |
| events.yaml | Event broker, streams, consumer config |
| exchange.yaml | Binance/Bybit URLs, timeouts, retries |
| indicators.yaml | Timeframes, EMA periods, lookback |
| journal.yaml | Attachment limits, storage quota |
| candles.yaml | Retention, TimescaleDB toggle |
| sync.yaml | Lock TTL, lookback days |

### Database Schema

8 tables with proper indexes, constraints, and cascade deletes:

| Table | Purpose | Key Indexes |
|-------|---------|-------------|
| users | User accounts | email (unique) |
| exchange_connections | API key storage (encrypted) | user_id |
| positions | Grouped trades | timeline, status, strategy, tags (GIN) |
| fills | Raw trade data | connection_id, position_id |
| candles | OHLCV market data | composite PK (exchange, symbol, timeframe, open_time) |
| magic_links | Auth tokens | user_id, expires_at |
| position_notes | Journal notes | position_id |
| position_attachments | Screenshots/links | position_id |

---

## Production Readiness

### What Works End-to-End

| Flow | Status |
|------|--------|
| Magic link auth (request → email → verify → JWT) | Working |
| Exchange connection (create → validate → encrypt → store) | Working |
| Trade sync (enqueue → fetch → group → reconcile → indicators) | Working |
| Position views (dashboard, list, detail with computed fields) | Working |
| Journal (notes, attachments, S3 upload, storage quota) | Working |
| CSV export with filters | Working |
| SSE event streaming | Working |
| Health checks (liveness, readiness, detailed) | Working |

### Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| Core Framework | 95% | FastAPI, async DB, graceful shutdown |
| Authentication | 100% | Magic link, JWT, cookies, logout |
| Data Layer | 95% | Async SQLAlchemy, migrations, queries |
| API Endpoints | 85% | 25+ endpoints with real logic |
| Business Logic | 90% | Auth, sync, grouper, indicators, storage |
| Error Handling | 85% | Standard envelope, exception hierarchy |
| Security | 70% | Encryption, CORS, headers — rate limiting not wired |
| Observability | 40% | Logging done — tracing/metrics not instrumented |
| Resilience | 30% | Infrastructure ready — not wired to exchange calls |
| Testing | 50% | 239 tests pass — ~50% endpoint coverage gap |
| Frontend | 5% | Boilerplate only |
| **Overall** | **72%** | |

### Critical Gaps

| Gap | Impact | Effort |
|-----|--------|--------|
| No resilience on exchange calls | Sync hangs on flaky APIs | 2-3 hours |
| Rate limiting not wired | Auth endpoints can be brute-forced | 30 min |
| No event consumers | Events published but not processed | 4-6 hours |
| No observability instrumentation | Can't diagnose slow syncs | 4-6 hours |
| No scheduled tasks | No daily cleanup/reconciliation | 1-2 hours |
| No frontend | Can't use the system | 40-60 hours |
| Test coverage gaps | ~50% of endpoints untested | 8-12 hours |
| No domain error codes | Clients can't distinguish error types | 2-4 hours |

---

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Web framework | FastAPI | Async-native, Pydantic integration, OpenAPI docs |
| ORM | SQLAlchemy async | Mature, flexible, explicit query control |
| Auth | Magic link + JWT | Passwordless, no credential storage |
| Task queue | Taskiq + Redis | Lightweight, async-native, no Celery overhead |
| Event bus | FastStream + Redis Streams | Ordered, persistent, consumer groups |
| File storage | S3 (MinIO for dev) | Standard API, portable between providers |
| Logging | structlog (JSON) | Machine-parseable, filterable by source |
| Config | YAML + Pydantic validation | Typed, validated at startup, clear errors |

---

## Dependency Map

```
API Endpoints
    └── Services (injected via FastAPI Depends)
        ├── Repositories (initialized in service constructors)
        │   └── SQLAlchemy AsyncSession (from core/database.py)
        ├── Exchange Adapters (from factory)
        │   └── httpx.AsyncClient
        ├── Storage Service (S3/MinIO)
        │   └── boto3
        ├── Email Service (Resend)
        │   └── httpx
        └── Event Publishers (FastStream)
            └── Redis

Background Tasks (Taskiq)
    └── Services (instantiated per task)

Event Consumers (FastStream)
    └── Services (instantiated per event)

CLI (Click)
    └── FastAPI app factory / Taskiq broker / FastStream app
```

No circular dependencies. All cross-cutting concerns flow through `core/`.
