"""
app/tests/conftest.py
─────────────────────
Shared test fixtures for integration tests. Uses the real FastAPI app
with httpx.AsyncClient for end-to-end testing.

For testing, we use the same app but configure a test database via
environment variables.
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client that talks directly to the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """
    Register a test user and return auth headers with a valid JWT.
    Each test gets a unique user to avoid conflicts.
    """
    import uuid
    unique = str(uuid.uuid4())[:8]

    # Register
    await client.post(
        "/auth/register",
        json={
            "name": f"Test User {unique}",
            "email": f"test_{unique}@taskflow.com",
            "password": "testpassword123",
        },
    )

    # Login
    response = await client.post(
        "/auth/login",
        json={
            "email": f"test_{unique}@taskflow.com",
            "password": "testpassword123",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
