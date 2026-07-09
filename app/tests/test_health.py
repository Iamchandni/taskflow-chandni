"""
app/tests/test_health.py
────────────────────────
Integration tests for the GET /health endpoint.
Pins the endpoint's contract: HTTP 200, exact JSON body {"status": "ok"},
no authentication required, and a JSON content-type response header.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient):
    """GET /health → 200 OK."""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_returns_status_ok_body(client: AsyncClient):
    """GET /health → exact body {"status": "ok"}."""
    response = await client.get("/health")
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_requires_no_auth(client: AsyncClient):
    """GET /health without Authorization header → 200 (endpoint is public)."""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_content_type_json(client: AsyncClient):
    """GET /health → response Content-Type is application/json."""
    response = await client.get("/health")
    assert response.headers["content-type"].startswith("application/json")
