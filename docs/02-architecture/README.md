# Architecture

System design documents, diagrams, and architecture decision records (ADRs).

## Naming Convention

```
001-system-overview.md
002-data-model.md
003-adr-choice-of-framework.md
```

## System Architecture

```
+-----------------------------------------------------------------+
|                       Frontend (React)                          |
|                    modules/frontend/                             |
+-----------------------------------------------------------------+
                             |
                             | HTTP/REST
                             v
+-----------------------------------------------------------------+
|                     BFF Layer (FastAPI)                          |
|                    modules/backend/                              |
|  +-------------+  +-------------+  +-------------------------+  |
|  |  API Layer  |--|  Services   |--|     Repositories        |  |
|  +-------------+  +-------------+  +-------------------------+  |
+-----------------------------------------------------------------+
                             |
            +----------------+----------------+
            v                                 v
+-------------------------+     +-------------------------+
|      PostgreSQL         |     |         Redis           |
|    (Primary Store)      |     |   (Cache/Tasks/Queue)   |
+-------------------------+     +-------------------------+
```

## Backend Layers

| Layer | Responsibility | Location |
|-------|----------------|----------|
| API | HTTP handlers, request/response | `modules/backend/api/` |
| Services | Business logic, orchestration | `modules/backend/services/` |
| Repositories | Data access, queries | `modules/backend/repositories/` |
| Models | Database entities | `modules/backend/models/` |
| Schemas | Pydantic models | `modules/backend/schemas/` |

## Key Principles

1. **Backend owns all business logic** - Frontend is presentation only
2. **Layered architecture** - Each layer only calls the layer below
3. **Absolute imports** - No relative imports
4. **No hardcoded values** - All config from YAML/env files
5. **Fail fast** - Missing config fails at startup

## Architecture Standards

See [99-reference-architecture/](../99-reference-architecture/) for complete standards.
