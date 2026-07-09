## Summary
Provide integration test coverage that pins the existing unauthenticated `GET /health` endpoint to return HTTP 200 with the exact JSON body `{"status": "ok"}`.

## Source issues
- #1: Add health endpoint

## Files to create or modify
- `app/tests/test_health.py` — CREATE. Integration test module for the `/health` endpoint, using the existing session-scoped `client` async fixture from `app/tests/conftest.py`. This is the only file this group changes.
- `app/main.py` — REFERENCE ONLY, DO NOT MODIFY. The `GET /health` route already exists at `app/main.py:171-173`: `@app.get("/health", tags=["Health"])` / `async def health_check(): return {"status": "ok"}`. It already satisfies the functional acceptance criteria (200 + `{"status": "ok"}` + no auth). Do not add, move, duplicate, or edit this route.

## Test plan (write these first)
All tests live in `app/tests/test_health.py`. Use the `client: AsyncClient` fixture from `app/tests/conftest.py` (an `httpx.AsyncClient` over `ASGITransport(app=app)` with `base_url="http://test"`). `asyncio_mode = "auto"` is set in `pyproject.toml`, so `@pytest.mark.asyncio` is optional, but include it to match the style of `app/tests/test_auth.py`. Import `import pytest` and `from httpx import AsyncClient`.

1. Test `test_health_returns_200` — Valid request: `response = await client.get("/health")` → `assert response.status_code == 200`. Confirms the endpoint exists and responds OK.
2. Test `test_health_returns_status_ok_body` — Valid request: `response = await client.get("/health")` → `assert response.json() == {"status": "ok"}`. Asserts equality on the entire dict (not a substring or key-presence check), so the test fails if the payload contract drifts. This is the guard against an always-passing test — it pins the precise body the issue requires.
3. Test `test_health_requires_no_auth` — Authentication is out of scope for the endpoint: call `await client.get("/health")` with NO `Authorization` header → `assert response.status_code == 200`. Confirms the endpoint is publicly reachable and not gated behind auth (contrast with the 401/403 paths in `test_auth.py`).
4. Test `test_health_content_type_json` — Response shape: `response = await client.get("/health")` → `assert response.headers["content-type"].startswith("application/json")`. Confirms FastAPI serialized a JSON response.

## Implementation steps
1. Create `app/tests/test_health.py` with a module docstring describing it as integration tests for the `GET /health` endpoint (mirror the docstring style of `app/tests/test_auth.py`).
2. Add imports: `import pytest` and `from httpx import AsyncClient`.
3. Implement `async def test_health_returns_200(client: AsyncClient)` decorated with `@pytest.mark.asyncio`, asserting `response.status_code == 200` as in test-plan item 1.
4. Implement `async def test_health_returns_status_ok_body(client: AsyncClient)`, asserting `response.json() == {"status": "ok"}` as in test-plan item 2.
5. Implement `async def test_health_requires_no_auth(client: AsyncClient)`, calling `client.get("/health")` with no headers and asserting `status_code == 200` as in test-plan item 3.
6. Implement `async def test_health_content_type_json(client: AsyncClient)`, asserting the `content-type` header starts with `application/json` as in test-plan item 4.
7. Do NOT modify `app/main.py`. The production route already exists and meets the functional criteria; the deliverable for this group is the missing test coverage only.
8. Run `pytest app/tests/test_health.py -v` and confirm all four tests pass. They pass immediately because the endpoint already exists — this is expected. The acceptance criterion is "health endpoint test exists," and the assertions genuinely exercise the endpoint contract (exact status, exact body, no-auth, JSON content-type) rather than passing trivially.

## Error handling
- If `client.get("/health")` raises a connection/transport error, that indicates the test harness (`ASGITransport`/`app` import) is broken — let the exception propagate and fail the test. Do not swallow it or wrap it in a try/except that hides the failure.
- Tests must not log or print request/response internals containing tokens, credentials, or PII. The health endpoint returns no sensitive data, so no redaction is required — and do not add auth headers or user data to these tests.
- Do not add error-path production code. The endpoint has no error paths and none are in scope.

## Constraints
- Do NOT modify `app/main.py`, any router in `app/api/v1/`, `app/tests/conftest.py`, or any other existing test file — those are out of this group's scope.
- Ignore the `files_touched` paths supplied by the task group (`src/handlers/health.go`, `src/routes/routes.go`, `src/handlers/health_test.go`). They are Go paths from an incorrect triage; this repository is Python/FastAPI. The correct and only file to create is `app/tests/test_health.py`.
- No new external dependencies — `pytest==8.3.3`, `pytest-asyncio==0.24.0`, and `httpx==0.27.2` are already in `requirements.txt`.
- Authentication is explicitly out of scope for the endpoint; do not add auth to `/health` or test any auth behavior beyond confirming none is required.
- Reuse the existing `client` fixture from `conftest.py`; do not create a new `AsyncClient` or a second `app` instance.

## Risks
- Risk: The task group describes `.go` files, which could mislead a Coder into scaffolding a Go project. Mitigation: this plan pins the exact Python file (`app/tests/test_health.py`) and forbids touching production code.
- Risk: A test asserting only `status_code == 200` would pass trivially and be flagged as always-passing by the Validation agent. Mitigation: test-plan item 2 asserts the exact body `{"status": "ok"}`, tying the test to the real contract.
- Risk: Duplicating the route into a new health router while the `app/main.py` route remains would create two `/health` registrations. Mitigation: the constraints forbid adding, moving, or editing the route.

## Rollback
- The change is a single new test file with no production impact. To revert: `git rm app/tests/test_health.py` or revert the PR. No migrations, no config, no runtime behavior changes, so rollback is risk-free and requires no redeploy of application code.

## Acceptance criteria
- [ ] `app/tests/test_health.py` exists and contains the four tests above.
- [ ] `GET /health` returns HTTP 200 (verified by `test_health_returns_200`).
- [ ] `GET /health` returns exactly `{"status": "ok"}` (verified by `test_health_returns_status_ok_body`).
- [ ] Endpoint is reachable without authentication (verified by `test_health_requires_no_auth`).
- [ ] `pytest app/tests/test_health.py -v` passes with 4 passed, 0 failed.
- [ ] No changes to `app/main.py` or any existing file; no regressions in `app/tests/test_auth.py`, `test_projects.py`, or `test_tasks.py`.
