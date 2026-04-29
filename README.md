# BFF Python Web Skeleton

Production-ready Backend-for-Frontend reference architecture for Python web applications.

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy (async), Pydantic |
| Frontend | React, Vite, TypeScript, Tailwind CSS |
| Database | PostgreSQL 16+ |
| Cache/Queue | Redis 7+ |
| Tasks | Taskiq (Redis backend) |
| Events | FastStream (Redis Streams) |
| Storage | S3-compatible (MinIO for dev) |
| Logging | structlog (JSON → `var/logs/system.jsonl`) |
| Observability | OpenTelemetry, Prometheus (optional) |

## Quick Start

```bash
# Infrastructure
docker compose up -d

# Backend
cp config/.env.example config/.env
pip install -r requirements.txt
python run.py --service server

# Frontend
cd modules/frontend && npm install && npm run dev
```

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Frontend | http://localhost:5173 |

## Project Structure

```
.
├── modules/
│   ├── backend/                # FastAPI application
│   │   ├── api/                # HTTP endpoints (v1 versioned)
│   │   ├── services/           # Business logic
│   │   ├── repositories/       # Data access
│   │   ├── models/             # SQLAlchemy entities
│   │   ├── schemas/            # Pydantic models
│   │   ├── core/               # Config, logging, security, middleware
│   │   ├── events/             # Event bus (FastStream)
│   │   ├── tasks/              # Background jobs (Taskiq)
│   │   └── main.py             # App factory
│   └── frontend/               # React SPA
├── config/
│   ├── settings/               # 13 YAML config files (Pydantic-validated)
│   └── .env                    # Secrets (never committed)
├── tests/
│   ├── unit/                   # 239 tests passing
│   ├── integration/            # Real database tests
│   └── e2e/                    # Full stack tests
├── docs/                       # Documentation and standards
│   └── 99-reference-architecture/  # 18 core + 8 optional standards
├── var/                        # Runtime (logs, cache, data, tmp)
├── AGENTS.md                   # AI assistant instructions
├── docker-compose.yml          # PostgreSQL, Redis, MinIO
└── run.py                      # CLI entry point
```

## Architecture

Strict layered backend — no skipping layers:

```
API → Service → Repository → Model
```

All business logic in the backend. Frontend is presentation only.

See [docs/02-architecture/001-architecture-assessment.md](docs/02-architecture/001-architecture-assessment.md) for the full assessment.

## Configuration

- **Settings**: `config/settings/*.yaml` — validated by Pydantic schemas at startup
- **Secrets**: `config/.env` — loaded via Pydantic Settings
- **No hardcoded values** — missing config fails at startup, not at runtime

## Testing

```bash
pytest tests/unit -v            # Unit tests
pytest tests/integration -v     # Integration tests
pytest --cov=modules/backend    # Coverage report
```

## Reference Architecture

Standards in `docs/99-reference-architecture/`:

- **01–18** Core standards (backend, auth, security, observability, testing, deployment)
- **20–27** Optional modules (data layer, events, frontend, Telegram, TUI, gateway)

## Development

```bash
black modules/backend tests     # Format
isort modules/backend tests     # Sort imports
flake8 modules/backend tests    # Lint
mypy modules/backend            # Type check
```
