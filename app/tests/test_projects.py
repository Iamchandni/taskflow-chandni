"""
app/tests/test_projects.py
──────────────────────────
Integration tests for project endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, auth_headers: dict):
    """POST /projects → 201 with project data."""
    response = await client.post(
        "/projects",
        json={"name": "My Project", "description": "Test project"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Project"
    assert data["description"] == "Test project"
    assert "id" in data
    assert "owner_id" in data


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient, auth_headers: dict):
    """GET /projects → 200 with paginated list."""
    # Create a project first
    await client.post(
        "/projects",
        json={"name": "Listed Project"},
        headers=auth_headers,
    )

    response = await client.get("/projects", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert len(data["items"]) > 0


@pytest.mark.asyncio
async def test_get_project_detail(client: AsyncClient, auth_headers: dict):
    """GET /projects/:id → 200 with tasks."""
    # Create project
    create_resp = await client.post(
        "/projects",
        json={"name": "Detail Project"},
        headers=auth_headers,
    )
    project_id = create_resp.json()["id"]

    response = await client.get(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Detail Project"
    assert "tasks" in data


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, auth_headers: dict):
    """PATCH /projects/:id → 200 with updated data."""
    create_resp = await client.post(
        "/projects",
        json={"name": "Old Name"},
        headers=auth_headers,
    )
    project_id = create_resp.json()["id"]

    response = await client.patch(
        f"/projects/{project_id}",
        json={"name": "New Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient, auth_headers: dict):
    """DELETE /projects/:id → 200 with message."""
    create_resp = await client.post(
        "/projects",
        json={"name": "To Delete"},
        headers=auth_headers,
    )
    project_id = create_resp.json()["id"]

    response = await client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200

    # Verify it's gone
    get_resp = await client.get(f"/projects/{project_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_project_not_found(client: AsyncClient, auth_headers: dict):
    """GET /projects/:id with bad ID → 404."""
    response = await client.get(
        "/projects/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthenticated_access(client: AsyncClient):
    """GET /projects without token → 401."""
    response = await client.get("/projects")
    assert response.status_code == 401
