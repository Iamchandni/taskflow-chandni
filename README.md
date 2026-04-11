# TaskFlow — Task Management API

A production-grade task management REST API built with **FastAPI**, **PostgreSQL**, and **Docker**, following **Domain-Driven Design (DDD)** architecture.

## Features

- **User Authentication** — Register, login with JWT (bcrypt, 24h expiry)
- **Projects** — CRUD with owner-based authorization
- **Tasks** — Full CRUD with status/priority enums, filters, pagination
- **Project Stats** — Task counts by status and assignee
- **DDD Architecture** — Clean layer separation with dependency inversion
- **Docker** — Single `docker compose up` for the full stack
- **Migrations** — Alembic with up/down migration support
- **Structured Logging** — JSON logs via structlog
- **Integration Tests** — 19+ tests with pytest + httpx

---

## Quick Start

### 1. Clone & Configure

```bash
cp .env.example .env
# Edit .env if needed (defaults work for local dev)
```

### 2. Start with Docker

```bash
docker compose up --build
```

This will:
- Start PostgreSQL 16
- Run Alembic migrations automatically
- Seed the database with test data
- Start the API on http://localhost:8000

### 3. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@test.com", "password": "secret123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@test.com", "password": "secret123"}'

# Use the token for authenticated endpoints
export TOKEN="<access_token from login>"
curl http://localhost:8000/projects -H "Authorization: Bearer $TOKEN"
```

### Pre-seeded Test User

| Field    | Value              |
|----------|--------------------|
| Email    | test@taskflow.com  |
| Password | password123        |

---

## API Documentation

Interactive docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

| Method | Endpoint                    | Description                          | Auth |
|--------|-----------------------------|--------------------------------------|------|
| POST   | `/auth/register`            | Register a new user                  | No   |
| POST   | `/auth/login`               | Login, get JWT                       | No   |
| GET    | `/projects`                 | List user's projects (paginated)     | Yes  |
| POST   | `/projects`                 | Create a project                     | Yes  |
| GET    | `/projects/:id`             | Project detail + tasks               | Yes  |
| PATCH  | `/projects/:id`             | Update project (owner only)          | Yes  |
| DELETE | `/projects/:id`             | Delete project + tasks (owner only)  | Yes  |
| GET    | `/projects/:id/stats`       | Task counts by status/assignee       | Yes  |
| GET    | `/projects/:id/tasks`       | List tasks (filterable, paginated)   | Yes  |
| POST   | `/projects/:id/tasks`       | Create a task                        | Yes  |
| PATCH  | `/tasks/:id`                | Update a task                        | Yes  |
| DELETE | `/tasks/:id`                | Delete (owner or creator only)       | Yes  |

### Query Parameters

- `?page=1&limit=20` — Pagination (all list endpoints)
- `?status=todo|in_progress|done` — Filter tasks by status
- `?assignee=<uuid>` — Filter tasks by assignee

---

## Architecture (DDD)

```
app/
├── api/v1/          → HTTP routers only (no business logic)
├── application/
│   ├── services/    → Use-case orchestration (auth, project, task)
│   └── processors/  → Metric computation (stats)
├── domain/
│   ├── entities/    → Pure dataclasses (no framework deps)
│   ├── interfaces/  → Repository contracts (ABCs)
│   └── dtos/        → Request/response Pydantic schemas
├── infrastructure/
│   ├── persistence/ → SQLAlchemy engine, ORM models, repo implementations
│   ├── mappers/     → Entity ↔ ORM model converters
│   └── schedulers/  → (placeholder)
├── core/            → Config, security, exceptions, logging
└── shared/          → Constants, enums, SQL fragments
```

### Key Rules

1. **Domain layer has zero framework dependencies** — entities are plain dataclasses
2. **Dependency inversion** — domain defines interfaces, infrastructure implements
3. **Application services never touch SQLAlchemy** — they receive repo interfaces
4. **API layer is HTTP-only** — delegates all logic to services
5. **Mappers bridge the gap** — converting between domain entities and ORM models

---

## Running Tests

Tests require a running PostgreSQL instance:

```bash
# With Docker (recommended)
docker compose up db -d
POSTGRES_HOST=localhost pytest app/tests/ -v

# Or run tests inside the API container
docker compose exec api pytest app/tests/ -v
```

---

## Environment Variables

| Variable           | Default             | Description            |
|--------------------|---------------------|------------------------|
| POSTGRES_USER      | taskflow            | DB username            |
| POSTGRES_PASSWORD  | taskflow_secret     | DB password            |
| POSTGRES_DB        | taskflow            | DB name                |
| POSTGRES_HOST      | db                  | DB host                |
| POSTGRES_PORT      | 5432                | DB port                |
| JWT_SECRET         | change-me-...       | JWT signing key        |
| JWT_EXPIRY_HOURS   | 24                  | Token lifetime (hours) |
| BCRYPT_ROUNDS      | 12                  | bcrypt cost factor     |

---

## Migrations

```bash
# Run migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description"

# Rollback one step
alembic downgrade -1
```

---

## License

MIT
