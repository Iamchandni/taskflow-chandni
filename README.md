# TaskFlow — Task Management API

## 1. Overview
TaskFlow is a production-grade task management REST API. It allows users to securely register, manage projects, and oversee tasks with statuses and priorities.

**Tech Stack**:
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL 16
- **Containerization**: Docker & Docker Compose (featuring Multi-stage builds)
- **Migrations**: Alembic
- **ORM**: SQLAlchemy 2.0
- **Auth**: JWT via bcrypt

## 2. Architecture Decisions
The project strictly follows **Domain-Driven Design (DDD)**.
- **Why this structure?** It ensures a clean separation of concerns. Layers are strictly split into `api` (HTTP delivery), `application` (use-case orchestration), `domain` (pure business rules & entities), and `infrastructure` (database, ORM, implementation of interfaces).
- **Tradeoffs**: DDD mapping introduces boilerplate (e.g., transforming ORM models to Domain Entities to DTO schemas). For a simple CRUD app, a basic MVC architecture would be faster to write. However, DDD ensures TaskFlow remains robust, testable, and strictly decoupled as it scales. 
- **What was left out and why?** 
  - A Frontend (React). Focus was deliberately aimed 100% on building a flawless, heavily structured backend API.
  - Complex Role-Based Access Control (RBAC). A simple "ownership" model was used instead of complex hierarchical permissions (Admin vs Manager) to keep the logic focused on the core DDD principles without muddying the domain logic too early.

## 3. Running Locally
The environment is entirely containerized. Assuming you have Docker installed, there are zero manual service dependencies to configure on your machine.

```bash
# 1. Clone the repository
git clone https://github.com/your-name/taskflow
cd taskflow

# 2. Setup your environment variables
cp .env.example .env

# 3. Spin up the Database and the API
docker compose up --build
```
*The API is now running and available at [http://localhost:8000](http://localhost:8000)*
*Interactive API Documentation (Swagger UI) is available at [http://localhost:8000/docs](http://localhost:8000/docs)*

## 4. Running Migrations
Migrations are configured to run **automatically** on container start natively via the `scripts/start.sh` entrypoint wrapper (`alembic upgrade head`). **No manual intervention is needed**.

If you ever uniquely need to revert migrations manually against the running container:
```bash
# Enter the API container
docker compose exec api bash

# Rollback one step
alembic downgrade -1
```

## 5. Test Credentials
The database securely seeds a test user, a "Demo Project", and several tasks sequentially on startup. Once the container is running, you can log in immediately:

**Email**: `test@taskflow.com`
**Password**: `password123`

*(Note: The seed password is automatically hashed via `$2b$12$...` bcrypt rounds during insertion).*

## 6. API Reference
All endpoints, schemas, validation errors, and `401 Unauthorized` states are documented interactively via OpenAPI.

Go to **[http://localhost:8000/docs](http://localhost:8000/docs)** to test via the UI.

### Endpoint Summary
- `POST /auth/register` - Create a new user
- `POST /auth/login` - Login, receive JWT Bearer token
- `GET /projects` - List user's projects (Paginated)
- `POST /projects` - Create a project
- `GET /projects/{id}` - Get project details along with its tasks
- `PATCH /projects/{id}` - Update project structure
- `DELETE /projects/{id}` - Delete project
- `GET /projects/{id}/stats` - Get metric counts by task status and assignee
- `GET /projects/{project_id}/tasks` - List tasks (Filtered by `?status=` and `?assignee=`)
- `POST /projects/{project_id}/tasks` - Create a scoped task
- `PATCH /tasks/{id}` - Update a task
- `DELETE /tasks/{id}` - Delete a task

## 7. What You'd Do With More Time
**Honest Reflection:**
- **Shortcuts Taken**: My test suite heavily focuses on robust HTTP-level integration testing rather than deeply parsing isolated Domain Entity unit tests.
- **Improvements via More Time**:
  - **Caching**: I would implement an in-memory Redis cache for the `GET /projects/{id}/stats` metrics. Aggregations can become incredibly database-expensive once millions of tasks exist.
  - **Authentication Flow**: Currently, there are only short-lived access tokens. I would implement standard short-lived Access + long-lived Refresh Token rotation to tighten operational security.

