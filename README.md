# MedRelay (Python)

Medical event CAD dispatch system, built with FastAPI, Jinja2, SQLAlchemy, MySQL, and Server-Sent Events for realtime updates.

## Requirements

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Node.js 22+ (frontend assets)
- MySQL 8.x (production / local)

## Setup

```bash
cp .env.example .env
# Edit DATABASE_URL and SECRET_KEY

uv sync
uv run alembic upgrade head
uv run medrelay user-create

npm install
npm run build
```

## Development

```bash
uv run uvicorn web:app --reload --host 0.0.0.0 --port 8000
# In another terminal:
npm run dev
```

Open http://localhost:8000

## Tests

```bash
uv run pytest
```

Tests use SQLite in-memory (`APP_ENV=testing`).

## Docker (production)

```bash
docker compose -f docker-compose.prod.yml up --build
```

Set `SECRET_KEY`, `DB_PASSWORD`, and `MYSQL_ROOT_PASSWORD` in your environment.

Set **`REDIS_URL`** for realtime fan-out across workers (included in `docker-compose.prod.yml`). Without Redis, use a **single uvicorn worker** so SSE subscribers receive updates from the same process.

**Platform admin** (`/platform/...`, default-organisation admins only): manage tenant organisations and view system metrics (DB pool, realtime/Redis health). **Organisation admin** (`/admin/...`): users and audit logs for the logged-in organisation.

## Concurrent use (~10 operators)

MedRelay is designed for a small control-room team (on the order of 10 simultaneous users):

| Area | Behaviour |
|------|-----------|
| **MySQL pool** | Defaults to 10 connections + 10 overflow (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`). Tune if you add more app instances. |
| **Writes** | Incident reference numbers and assignment/status updates use row-level locks to avoid duplicate references or lost updates. |
| **SSE** | Bounded per-subscriber queues; subscriber cap per channel; publishes are scheduled on the app event loop (safe from sync route handlers). |
| **Sessions** | Signed cookie sessions; no server-side session store required. |
| **Health** | `GET /up` checks database connectivity (`database: ok` / `degraded`). |

For more than ~10 heavy users or horizontal scaling, increase pool settings and plan for Redis (or similar) for SSE fan-out before running multiple workers.

## Stack

| Layer | Technology |
|-------|------------|
| Web | FastAPI + Jinja2 |
| ORM | SQLAlchemy 2 + Alembic |
| DB | MySQL 8 |
| Realtime | SSE (native EventSource) |
| Frontend | Tailwind CSS 4, DaisyUI, Alpine.js, Vite |
| Tests | pytest |
