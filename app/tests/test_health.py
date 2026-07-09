"""
app/tests/test_health.py
────────────────────────
Integration tests for the GET /health endpoint.
Verifies HTTP 200, exact JSON body, no-auth requirement, and JSON content-type.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_returns_status_ok_body(client: AsyncClient):
    response = await client.get("/health")
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_requires_no_auth(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_content_type_json(client: AsyncClient):
    response = await client.get("/health")
    assert response.headers["content-type"].startswith("application/json")
