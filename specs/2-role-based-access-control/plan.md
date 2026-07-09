## Summary
Add a global `role` (`admin` | `member`) to users and a pure RBAC policy module so that admins may manage any project/task while members retain the existing per-resource ownership permissions.

## Source issues
- #2: Role based Access Control

> Note: no `specs/2-*/spec.md` exists, and the issue body is thin ("admin and owner access", with a stray "Admin vs Manager" mention). This plan commits to a concrete, testable interpretation (below) so the Coder does not guess. The Spec Edge Case agent (stage 2.5) may harden it further, but implementation must not deviate without an updated plan.

**Committed interpretation of RBAC for this group:**
- A user has exactly one *global* role: `admin` or `member` (default `member`).
- **`owner` is NOT a global role.** Ownership stays per-resource (`project.owner_id`, `task.creator_id`). RBAC layers a global `admin` role *on top of* the existing ownership model.
- **admin** — may update/delete ANY project and update/delete ANY task, bypassing ownership.
- **member** — unchanged ownership rules: may manage projects they own; may update/delete a task if they are the task creator or the owner of the task's project.
- Roles are assigned out-of-band (DB/migration/seed). Self-service registration can NEVER grant `admin`.

## Files to create or modify

**Create**
- `app/core/rbac.py` — CREATE. Pure, framework-free RBAC policy: `is_admin`, `can_manage_project`, `can_manage_task`. Imports only domain entities + `UserRole`. No SQLAlchemy/FastAPI. (This is the Python equivalent of the group's fictional `src/rbac/roles.go` + `src/rbac/permissions.go`; a single module is used, matching the repo's `core/security.py` convention.)
- `alembic/versions/002_add_user_role.py` — CREATE. Migration adding a `user_role` Postgres enum and a `role` column to `users` (NOT NULL, `server_default='member'`). `down_revision = "001_initial"`.
- `app/tests/test_rbac.py` — CREATE (TDD Writer). Unit tests for `app/core/rbac.py`. No DB required.
- `app/tests/test_rbac_integration.py` — CREATE (TDD Writer). Integration tests for admin bypass + member enforcement + no privilege escalation via register. Requires DB.

**Modify**
- `app/shared/constants.py` — add `UserRole(str, Enum)` with `ADMIN = "admin"`, `MEMBER = "member"` (mirrors the existing `TaskStatus`/`TaskPriority` pattern).
- `app/domain/entities/user.py` — add `role: str = UserRole.MEMBER.value` field (import `UserRole` from `app.shared.constants`; constants.py is pure stdlib, so the entity stays framework-free).
- `app/infrastructure/persistence/models/user_model.py` — add `role` column mapped to the `user_role` enum, `nullable=False`, `server_default="member"`.
- `app/infrastructure/mappers/user_mapper.py` — map `role` in both `to_entity` and `to_model`.
- `app/domain/dtos/auth_dto.py` — add `role: str` to `UserResponse` (additive; clients need to know their role).
- `app/application/services/auth_service.py` — set `role=UserRole.MEMBER.value` explicitly when building the `User` on register; return `role=created.role` in the `UserResponse`.
- `app/application/services/project_service.py` — change `update_project` and `delete_project` to accept `current_user: User` (instead of `user_id: UUID`) and gate on `can_manage_project(current_user, project)`.
- `app/application/services/task_service.py` — change `update_task` to accept `current_user: User` and gate on `can_manage_task` (NEW check — currently unguarded); change `delete_task` to accept `current_user: User` and gate on `can_manage_task`.
- `app/api/v1/project_router.py` — pass `current_user` (not `current_user.id`) to `update_project`/`delete_project`.
- `app/api/v1/task_router.py` — pass `current_user` (not `current_user.id`) to `update_task`/`delete_task`.
- `app/tests/conftest.py` — add an `admin_headers` fixture (TDD Writer scope) that registers a user, promotes it to `admin` via a direct DB write, then logs in.

## Test plan (write these first)

`pyproject.toml` sets `asyncio_mode = "auto"`; keep `@pytest.mark.asyncio` on async tests to match existing style. Unit tests in `test_rbac.py` are synchronous and need no DB.

### A. Unit tests — `app/tests/test_rbac.py` (no DB, deterministic; primary evidence)
Construct `User`, `Project`, `Task` dataclasses directly with explicit `id`/`owner_id`/`creator_id` UUIDs. Import `from app.core.rbac import is_admin, can_manage_project, can_manage_task` and `from app.shared.constants import UserRole`.

1. Test `test_is_admin_true_for_admin` → `is_admin(User(role="admin"))` returns `True`.
2. Test `test_is_admin_false_for_member` → `is_admin(User(role="member"))` returns `False`.
3. Test `test_can_manage_project_member_owner` → member user whose `id == project.owner_id` → `True`.
4. Test `test_can_manage_project_member_non_owner` → member user whose `id != project.owner_id` → `False`.
5. Test `test_can_manage_project_admin_non_owner` → admin user whose `id != project.owner_id` → `True` (admin bypass).
6. Test `test_can_manage_task_member_creator` → member user is `task.creator_id`, project owned by a third party → `True`.
7. Test `test_can_manage_task_member_project_owner` → member user is `project.owner_id`, task created by a third party → `True`.
8. Test `test_can_manage_task_member_unrelated` → member user is neither creator nor project owner → `False`.
9. Test `test_can_manage_task_admin_unrelated` → admin user, neither creator nor project owner → `True`.
10. Test `test_can_manage_task_project_none_creator` → `project=None`, member user is the creator → `True`.
11. Test `test_can_manage_task_project_none_non_creator` → `project=None`, member user is NOT the creator (and not admin) → `False` (edge: orphaned/deleted parent project must not silently grant access).

### B. Integration tests — `app/tests/test_rbac_integration.py` (needs DB + migration 002 applied)
Use the existing `client` and `auth_headers` fixtures plus the new `admin_headers` fixture. For a "second member", inline-register/login like `test_delete_task_unauthorized` in `test_tasks.py` does.

1. Test `test_admin_can_update_any_project` → member (`auth_headers`) `POST /projects`; admin (`admin_headers`) `PATCH /projects/{id}` with `{"name":"Renamed by admin"}` → `200`, body `name == "Renamed by admin"`.
2. Test `test_admin_can_delete_any_project` → member creates project; admin `DELETE /projects/{id}` → `200`; subsequent member `GET /projects/{id}` → `404`.
3. Test `test_member_cannot_update_others_project` → member A creates project; member B (inline-registered) `PATCH /projects/{id}` → `403`, body `{"error":"permission denied"}`.
4. Test `test_member_cannot_delete_others_project` → member A creates; member B `DELETE /projects/{id}` → `403`.
5. Test `test_owner_can_still_manage_own_project` → member A creates project, then A `PATCH`es it → `200` (regression guard: ownership preserved for members).
6. Test `test_admin_can_update_any_task` → member A creates project + task; admin `PATCH /tasks/{task_id}` with `{"status":"done"}` → `200`, body `status == "done"`.
7. Test `test_admin_can_delete_any_task` → member A creates project + task; admin `DELETE /tasks/{task_id}` → `200`.
8. Test `test_member_cannot_update_others_task` → member A creates project + task; member B `PATCH /tasks/{task_id}` → `403` (NEW enforcement — `update_task` was previously unguarded).
9. Test `test_registered_user_defaults_to_member` → `POST /auth/register` (valid body) → `201`, response `role == "member"`.
10. Test `test_register_cannot_self_assign_admin` → `POST /auth/register` with an extra `"role":"admin"` field in the JSON body → `201` and response `role == "member"` (Pydantic ignores unknown fields; asserts no privilege escalation).

## Implementation steps

1. **`app/shared/constants.py`** — after the `TaskPriority` enum, add:
   ```python
   class UserRole(str, Enum):
       ADMIN = "admin"
       MEMBER = "member"
   ```

2. **`app/domain/entities/user.py`** — add `from app.shared.constants import UserRole` and a new dataclass field AFTER `created_at`:
   ```python
   role: str = UserRole.MEMBER.value
   ```
   Keep the entity a plain dataclass (no SQLAlchemy/Pydantic import).

3. **`app/infrastructure/persistence/models/user_model.py`** — import the SQLAlchemy enum type (`from sqlalchemy import String, DateTime, Enum as SAEnum`) and add, after the `password` column:
   ```python
   role: Mapped[str] = mapped_column(
       SAEnum("admin", "member", name="user_role"),
       nullable=False,
       server_default="member",
   )
   ```
   The enum `name="user_role"` MUST match the migration's enum name.

4. **`app/infrastructure/mappers/user_mapper.py`** — add `role=model.role` to the `User(...)` build in `to_entity`, and `role=entity.role` to the `UserModel(...)` build in `to_model`.

5. **`alembic/versions/002_add_user_role.py`** — create with:
   ```python
   from typing import Sequence, Union
   from alembic import op
   import sqlalchemy as sa

   revision: str = "002_add_user_role"
   down_revision: Union[str, None] = "001_initial"
   branch_labels: Union[str, Sequence[str], None] = None
   depends_on: Union[str, Sequence[str], None] = None


   def upgrade() -> None:
       user_role = sa.Enum("admin", "member", name="user_role")
       user_role.create(op.get_bind(), checkfirst=True)
       op.add_column(
           "users",
           sa.Column("role", user_role, nullable=False, server_default="member"),
       )


   def downgrade() -> None:
       op.drop_column("users", "role")
       sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
   ```
   Existing user rows receive `member` via the server default. Do not backfill any admin here.

6. **`app/domain/dtos/auth_dto.py`** — add `role: str` to `UserResponse` (place after `email`).

7. **`app/application/services/auth_service.py`** — import `UserRole`; in `register`, build the `User` with an explicit `role=UserRole.MEMBER.value`; and construct the returned `UserResponse` with `role=created.role`. Registration must never read a role from the request.

8. **`app/core/rbac.py`** — create the pure policy module:
   ```python
   from typing import Optional

   from app.domain.entities.project import Project
   from app.domain.entities.task import Task
   from app.domain.entities.user import User
   from app.shared.constants import UserRole


   def is_admin(user: User) -> bool:
       """True if the user holds the global admin role."""
       return user.role == UserRole.ADMIN.value


   def can_manage_project(user: User, project: Project) -> bool:
       """Admins may manage any project; members only projects they own."""
       return is_admin(user) or project.owner_id == user.id


   def can_manage_task(user: User, task: Task, project: Optional[Project]) -> bool:
       """
       Allowed for: admins, the task's creator, or the owner of the task's
       project. `project` may be None (parent deleted) — then only admins and
       the creator qualify.
       """
       if is_admin(user):
           return True
       if task.creator_id == user.id:
           return True
       return project is not None and project.owner_id == user.id
   ```

9. **`app/application/services/project_service.py`** — add imports `from app.core.rbac import can_manage_project` and `from app.domain.entities.user import User`. Change `update_project` signature to `(self, project_id: UUID, request: ProjectUpdateRequest, current_user: User)` and replace `if project.owner_id != user_id: raise AuthorizationError(...)` with `if not can_manage_project(current_user, project): raise AuthorizationError("permission denied")`. Change `delete_project` signature to `(self, project_id: UUID, current_user: User)` and apply the same `can_manage_project` gate. Leave `create_project`/`list_projects`/`get_project_detail` unchanged.

10. **`app/application/services/task_service.py`** — add imports `from app.core.rbac import can_manage_task` and `from app.domain.entities.user import User`. Change `update_task` signature to `(self, task_id: UUID, request: TaskUpdateRequest, current_user: User)`: after loading the task (404 if missing), load `project = await self._project_repo.get_by_id(task.project_id)`, then `if not can_manage_task(current_user, task, project): raise AuthorizationError("permission denied")` BEFORE applying field updates. Change `delete_task` signature to `(self, task_id: UUID, current_user: User)`: after loading the task (404 if missing), load the project, gate on `can_manage_task`, then delete; remove the old inline creator/owner branch logic and its `by=` log detail — log `logger.info("task_deleted", task_id=str(task_id))`.

11. **`app/api/v1/project_router.py`** — in `update_project` call `await project_service.update_project(project_id, request, current_user)`; in `delete_project` call `await project_service.delete_project(project_id, current_user)`.

12. **`app/api/v1/task_router.py`** — in `update_task` call `await task_service.update_task(task_id, request, current_user)`; in `delete_task` call `await task_service.delete_task(task_id, current_user)`.

13. **`app/tests/conftest.py`** (TDD Writer) — add the `admin_headers` fixture:
    ```python
    import pytest_asyncio
    from sqlalchemy import update
    from app.infrastructure.persistence.database import async_session_factory
    from app.infrastructure.persistence.models.user_model import UserModel

    @pytest_asyncio.fixture
    async def admin_headers(client: AsyncClient) -> dict[str, str]:
        import uuid
        unique = str(uuid.uuid4())[:8]
        email = f"admin_{unique}@taskflow.com"
        await client.post("/auth/register", json={
            "name": f"Admin {unique}", "email": email, "password": "adminpass123",
        })
        async with async_session_factory() as session:
            await session.execute(
                update(UserModel).where(UserModel.email == email).values(role="admin")
            )
            await session.commit()
        login = await client.post("/auth/login", json={
            "email": email, "password": "adminpass123",
        })
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    ```

14. **Write `app/tests/test_rbac.py`** with the 11 unit tests from section A, constructing entities directly.

15. **Write `app/tests/test_rbac_integration.py`** with the 10 integration tests from section B.

16. **Apply the migration and run the suite**: `alembic upgrade head`, then `pytest app/tests -v`. All new tests plus all existing tests in `test_auth.py`, `test_projects.py`, `test_tasks.py`, `test_health.py` must pass.

## Error handling
- **Unauthorized mutation** (member acting on a resource they neither own nor created, non-admin): services raise `AuthorizationError("permission denied")`, mapped to HTTP **403** with body `{"error":"permission denied"}` by the existing handler in `app/main.py`.
- **Missing resource**: services raise `NotFoundError("not found")` → HTTP **404**. Order matters — check existence (404) BEFORE the permission gate, matching the existing `project_service`/`task_service` behavior.
- **Missing/invalid token**: unchanged — `get_current_user` raises `AuthenticationError` → **401**.
- **Register with a `role` field in the body**: Pydantic (`RegisterRequest`) silently ignores the unknown field; the user is created as `member`. No error, no escalation.
- **Logging**: keep the existing structured `logger.info` calls (`project_updated`, `project_deleted`, `task_updated`, `task_deleted`). Do NOT log tokens, password hashes, request bodies, or email addresses beyond what the code already logs. Do not add a role value to logs unless it is non-sensitive (role is non-sensitive, but not required).

## Constraints
- **Ignore the task group's `files_touched`** (`src/middleware/auth.go`, `src/models/user.go`, `src/rbac/roles.go`, etc.). They are fictional Go paths from an incorrect triage. This repository is Python/FastAPI; the real files are listed above.
- **Do not touch `app/tests/test_health.py`** or any file owned by group-2 (the health-endpoint group).
- **Do not modify `app/core/security.py` or the JWT payload.** Role is intentionally NOT stored in the JWT; `get_current_user` reloads the `User` (and thus current role) from the DB on every request, so revoking/changing a role takes effect immediately and old tokens cannot carry a stale elevated role.
- **Do not add a role field to `RegisterRequest`** or any self-service endpoint. Admin is granted only out-of-band (DB/migration/seed).
- **Do not modify `seed.sql`.** The demo user remains `member` (server default); admin seeding is out of scope.
- **No read-side restrictions.** `GET /projects/{id}` and list endpoints keep their current visibility behavior; this group only governs mutations (update/delete project, update/delete task).
- **Services stay framework-free**: no SQLAlchemy or FastAPI imports in services or in `app/core/rbac.py`. RBAC decisions raise domain exceptions, never `HTTPException`.
- **No new external dependencies.** Everything uses the existing SQLAlchemy, Alembic, Pydantic, pytest, httpx stack.
- **Coder must not edit test files** (`conftest.py`, `test_rbac.py`, `test_rbac_integration.py`) — those are the TDD Writer's deliverable per the Constitution's role boundaries.

## Risks
- **Ambiguous spec ("Admin vs Manager")**: mitigated by committing to `admin` + `member` (with per-resource ownership) here and flagging it for the Spec Edge Case agent. If the human checkpoint wants a distinct `manager` tier, the plan must be revised before coding — do not invent one silently.
- **Behavior change on `update_task`**: it was previously unguarded (any authenticated user could edit any task). Adding `can_manage_task` returns **403** for unrelated members. This is intentional (it is the exact gap the issue calls out) but is a behavior change — documented in test B8 and here. Existing `test_update_task` still passes because it updates as the creator.
- **Migration ordering**: integration tests and the app itself will fail if `role` is missing from the DB, because `UserModel` now selects it. Mitigation: `alembic upgrade head` MUST run before any test/app start; the migration adds the column with a server default so existing rows are valid.
- **Enum type collision**: creating the `user_role` Postgres enum twice fails. Mitigation: `checkfirst=True` on create and drop in the migration.
- **Integration tests require Postgres**: the unit tests in `test_rbac.py` (DB-free) are the deterministic core evidence; integration tests need the compose DB with migration 002 applied (the Validation agent's environment).

## Rollback
- Code is additive and revertible via `git revert` of the PR. Because `get_current_user` reloads role from the DB, reverting the app code immediately restores the pure-ownership behavior.
- Schema: run `alembic downgrade -1` (executes `002_add_user_role.downgrade`) to drop the `role` column and the `user_role` enum. Safe because no other table references `role` and the column has a default. Revert app code and DB together to avoid the ORM selecting a dropped column.

## Acceptance criteria
- [ ] `UserRole` enum exists (`admin`, `member`); `User` entity, `UserModel`, and `UserMapper` all carry `role`, defaulting to `member`.
- [ ] Migration `002_add_user_role` adds the `role` column (NOT NULL, default `member`) and is reversible.
- [ ] `app/core/rbac.py` exists with pure `is_admin`, `can_manage_project`, `can_manage_task` and all 11 unit tests in `test_rbac.py` pass.
- [ ] Admin can update/delete any project and any task (integration tests B1, B2, B6, B7 pass → 200).
- [ ] Members retain ownership permissions (B5 passes) and are denied on others' resources with 403 (B3, B4, B8 pass).
- [ ] New users default to `member` and cannot self-assign `admin` via register (B9, B10 pass).
- [ ] Error paths return the defined status codes: 403 `{"error":"permission denied"}`, 404 `{"error":"not found"}`, 401 unchanged.
- [ ] No regressions: `pytest app/tests -v` passes for `test_auth.py`, `test_projects.py`, `test_tasks.py`, `test_health.py`.
- [ ] No secrets, tokens, password hashes, or PII added to logs.
