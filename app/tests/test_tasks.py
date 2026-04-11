"""
app/tests/test_tasks.py
───────────────────────
Integration tests for task endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def project_id(client: AsyncClient, auth_headers: dict) -> str:
    """Create a project and return its ID for task tests."""
    response = await client.post(
        "/projects",
        json={"name": "Task Test Project"},
        headers=auth_headers,
    )
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, auth_headers: dict, project_id: str):
    """POST /projects/:id/tasks → 201 with task data."""
    response = await client.post(
        f"/projects/{project_id}/tasks",
        json={
            "title": "My Task",
            "description": "Task description",
            "priority": "high",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Task"
    assert data["priority"] == "high"
    assert data["status"] == "todo"  # default
    assert data["project_id"] == project_id


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient, auth_headers: dict, project_id: str):
    """GET /projects/:id/tasks → 200 with paginated list."""
    # Create a task
    await client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Listed Task"},
        headers=auth_headers,
    )

    response = await client.get(
        f"/projects/{project_id}/tasks",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0


@pytest.mark.asyncio
async def test_list_tasks_with_status_filter(
    client: AsyncClient, auth_headers: dict, project_id: str
):
    """GET /projects/:id/tasks?status=todo → only matching tasks."""
    # Create tasks with different statuses
    await client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Todo Task", "status": "todo"},
        headers=auth_headers,
    )
    await client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Done Task", "status": "done"},
        headers=auth_headers,
    )

    response = await client.get(
        f"/projects/{project_id}/tasks?status=todo",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["status"] == "todo"


@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, auth_headers: dict, project_id: str):
    """PATCH /tasks/:id → 200 with updated data."""
    create_resp = await client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Update Me"},
        headers=auth_headers,
    )
    task_id = create_resp.json()["id"]

    response = await client.patch(
        f"/tasks/{task_id}",
        json={"title": "Updated Title", "status": "in_progress"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_delete_task_by_creator(
    client: AsyncClient, auth_headers: dict, project_id: str
):
    """DELETE /tasks/:id by creator → 200."""
    create_resp = await client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Delete Me"},
        headers=auth_headers,
    )
    task_id = create_resp.json()["id"]

    response = await client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_task_unauthorized(client: AsyncClient, auth_headers: dict, project_id: str):
    """DELETE /tasks/:id by non-owner/non-creator → 403."""
    # Create task as original user
    create_resp = await client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Protected Task"},
        headers=auth_headers,
    )
    task_id = create_resp.json()["id"]

    # Register and login as a different user
    import uuid
    other = str(uuid.uuid4())[:8]
    await client.post(
        "/auth/register",
        json={
            "name": f"Other {other}",
            "email": f"other_{other}@test.com",
            "password": "otherpass123",
        },
    )
    login_resp = await client.post(
        "/auth/login",
        json={"email": f"other_{other}@test.com", "password": "otherpass123"},
    )
    other_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # Try to delete with different user
    response = await client.delete(f"/tasks/{task_id}", headers=other_headers)
    assert response.status_code == 403
