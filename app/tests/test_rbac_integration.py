"""
app/tests/test_rbac_integration.py
────────────────────────────────────
Integration tests for RBAC enforcement at the HTTP layer.
Requires a live DB with migration 002_add_user_role applied.
"""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_can_update_any_project(client: AsyncClient, auth_headers: dict, admin_headers: dict):
    """Member creates project; admin PATCH /projects/{id} → 200 with updated name."""
    create_resp = await client.post("/projects", json={"name": "Member Project"}, headers=auth_headers)
    project_id = create_resp.json()["id"]

    response = await client.patch(
        f"/projects/{project_id}", json={"name": "Renamed by admin"}, headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed by admin"


@pytest.mark.asyncio
async def test_admin_can_delete_any_project(client: AsyncClient, auth_headers: dict, admin_headers: dict):
    """Member creates project; admin DELETE → 200; member GET → 404."""
    create_resp = await client.post("/projects", json={"name": "To Be Deleted"}, headers=auth_headers)
    project_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/projects/{project_id}", headers=admin_headers)
    assert delete_resp.status_code == 200

    get_resp = await client.get(f"/projects/{project_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_member_cannot_update_others_project(client: AsyncClient, auth_headers: dict):
    """Member A creates project; member B PATCH → 403 with error message."""
    create_resp = await client.post("/projects", json={"name": "A's Project"}, headers=auth_headers)
    project_id = create_resp.json()["id"]

    other = str(uuid.uuid4())[:8]
    await client.post(
        "/auth/register",
        json={"name": f"Other {other}", "email": f"other_{other}@test.com", "password": "otherpass123"},
    )
    login_resp = await client.post(
        "/auth/login", json={"email": f"other_{other}@test.com", "password": "otherpass123"}
    )
    other_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    response = await client.patch(f"/projects/{project_id}", json={"name": "Hijacked"}, headers=other_headers)
    assert response.status_code == 403
    assert response.json()["error"] == "permission denied"


@pytest.mark.asyncio
async def test_member_cannot_delete_others_project(client: AsyncClient, auth_headers: dict):
    """Member A creates project; member B DELETE → 403 with error message."""
    create_resp = await client.post("/projects", json={"name": "Protected Project"}, headers=auth_headers)
    project_id = create_resp.json()["id"]

    other = str(uuid.uuid4())[:8]
    await client.post(
        "/auth/register",
        json={"name": f"Other {other}", "email": f"other_{other}@test.com", "password": "otherpass123"},
    )
    login_resp = await client.post(
        "/auth/login", json={"email": f"other_{other}@test.com", "password": "otherpass123"}
    )
    other_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    response = await client.delete(f"/projects/{project_id}", headers=other_headers)
    assert response.status_code == 403
    assert response.json()["error"] == "permission denied"


@pytest.mark.asyncio
async def test_owner_can_still_manage_own_project(client: AsyncClient, auth_headers: dict):
    """Project owner PATCH their own project → 200 (ownership regression check)."""
    create_resp = await client.post("/projects", json={"name": "My Project"}, headers=auth_headers)
    project_id = create_resp.json()["id"]

    response = await client.patch(
        f"/projects/{project_id}", json={"name": "Updated by owner"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated by owner"


@pytest.mark.asyncio
async def test_admin_can_update_any_task(client: AsyncClient, auth_headers: dict, admin_headers: dict):
    """Member A creates project+task; admin PATCH /tasks/{id} with status → 200."""
    proj_resp = await client.post("/projects", json={"name": "Task Owner Project"}, headers=auth_headers)
    project_id = proj_resp.json()["id"]
    task_resp = await client.post(
        f"/projects/{project_id}/tasks", json={"title": "Member Task"}, headers=auth_headers
    )
    task_id = task_resp.json()["id"]

    response = await client.patch(f"/tasks/{task_id}", json={"status": "done"}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "done"


@pytest.mark.asyncio
async def test_admin_can_delete_any_task(client: AsyncClient, auth_headers: dict, admin_headers: dict):
    """Member A creates project+task; admin DELETE /tasks/{id} → 200."""
    proj_resp = await client.post("/projects", json={"name": "Task Delete Project"}, headers=auth_headers)
    project_id = proj_resp.json()["id"]
    task_resp = await client.post(
        f"/projects/{project_id}/tasks", json={"title": "Task to Delete"}, headers=auth_headers
    )
    task_id = task_resp.json()["id"]

    response = await client.delete(f"/tasks/{task_id}", headers=admin_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_member_cannot_update_others_task(client: AsyncClient, auth_headers: dict):
    """Member A creates project+task; member B PATCH /tasks/{id} → 403."""
    proj_resp = await client.post("/projects", json={"name": "Protected Task Project"}, headers=auth_headers)
    project_id = proj_resp.json()["id"]
    task_resp = await client.post(
        f"/projects/{project_id}/tasks", json={"title": "Protected Task"}, headers=auth_headers
    )
    task_id = task_resp.json()["id"]

    other = str(uuid.uuid4())[:8]
    await client.post(
        "/auth/register",
        json={"name": f"Other {other}", "email": f"other_{other}@test.com", "password": "otherpass123"},
    )
    login_resp = await client.post(
        "/auth/login", json={"email": f"other_{other}@test.com", "password": "otherpass123"}
    )
    other_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    response = await client.patch(f"/tasks/{task_id}", json={"status": "done"}, headers=other_headers)
    assert response.status_code == 403
    assert response.json()["error"] == "permission denied"


@pytest.mark.asyncio
async def test_registered_user_defaults_to_member(client: AsyncClient):
    """POST /auth/register → 201 with role == 'member'."""
    unique = str(uuid.uuid4())[:8]
    response = await client.post(
        "/auth/register",
        json={"name": f"New User {unique}", "email": f"new_{unique}@test.com", "password": "newpass123"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "member"


@pytest.mark.asyncio
async def test_register_cannot_self_assign_admin(client: AsyncClient):
    """POST /auth/register with extra role='admin' → 201 but role is still 'member'."""
    unique = str(uuid.uuid4())[:8]
    response = await client.post(
        "/auth/register",
        json={
            "name": f"Sneaky User {unique}",
            "email": f"sneaky_{unique}@test.com",
            "password": "sneakypass123",
            "role": "admin",
        },
    )
    assert response.status_code == 201
    assert response.json()["role"] == "member"
