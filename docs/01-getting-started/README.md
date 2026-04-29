# Getting Started

Setup guides, installation instructions, and quickstart walkthroughs.

## Naming Convention

```
001-environment-setup.md
002-first-run.md
003-development-workflow.md
```

## Prerequisites

- Python 3.14+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-name>
```

### 2. Backend Setup

**Option A: uv (Recommended for BFF/Web)**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Option B: conda (For data-heavy projects)**

```bash
conda create -n project python=3.14
conda activate project
pip install -r requirements.txt
```

```bash
cp config/.env.example config/.env
# Edit config/.env with your settings
```

### 3. Frontend Setup

```bash
cd modules/frontend
npm install
```

### 4. Database Setup

```bash
createdb <database-name>
cd modules/backend
alembic upgrade head
```

## Running the Application

```bash
# Backend (from project root)
uvicorn modules.backend.main:app --reload --port 8000

# Frontend (in separate terminal)
cd modules/frontend
npm run dev
```

### Access Points

- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend: http://localhost:5173

## Running Tests

```bash
pytest tests/unit                    # Fast, isolated tests
pytest tests/integration             # Tests with real database
pytest tests/e2e                     # Full stack tests
pytest tests/unit --cov=modules/backend  # With coverage
```

## Code Quality

```bash
black modules/backend tests
isort modules/backend tests
flake8 modules/backend tests
mypy modules/backend
```
