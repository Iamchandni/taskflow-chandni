"""
app/tests/test_auth.py
──────────────────────
Integration tests for the authentication endpoints.
Tests register, login, duplicate email, and wrong password scenarios.
"""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """POST /auth/register → 201 with user data (no password in response)."""
    unique = str(uuid.uuid4())[:8]
    response = await client.post(
        "/auth/register",
        json={
            "name": "Alice",
            "email": f"alice_{unique}@test.com",
            "password": "securepass123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == f"alice_{unique}@test.com"
    assert "id" in data
    assert "password" not in data  # never leak the hash


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """POST /auth/register with existing email → 409."""
    unique = str(uuid.uuid4())[:8]
    email = f"dup_{unique}@test.com"

    # First registration
    await client.post(
        "/auth/register",
        json={"name": "First", "email": email, "password": "pass123456"},
    )

    # Duplicate registration
    response = await client.post(
        "/auth/register",
        json={"name": "Second", "email": email, "password": "pass123456"},
    )
    assert response.status_code == 409
    assert response.json()["error"] == "email already registered"


@pytest.mark.asyncio
async def test_register_missing_fields(client: AsyncClient):
    """POST /auth/register with missing fields → 400 with structured errors."""
    response = await client.post(
        "/auth/register",
        json={},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "validation failed"
    assert "fields" in data


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """POST /auth/login with valid credentials → 200 with token."""
    unique = str(uuid.uuid4())[:8]
    email = f"login_{unique}@test.com"

    # Register first
    await client.post(
        "/auth/register",
        json={"name": "Bob", "email": email, "password": "mypassword123"},
    )

    # Login
    response = await client.post(
        "/auth/login",
        json={"email": email, "password": "mypassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """POST /auth/login with wrong password → 401."""
    unique = str(uuid.uuid4())[:8]
    email = f"wrong_{unique}@test.com"

    # Register
    await client.post(
        "/auth/register",
        json={"name": "Charlie", "email": email, "password": "rightpass123"},
    )

    # Login with wrong password
    response = await client.post(
        "/auth/login",
        json={"email": email, "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "invalid credentials"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """POST /auth/login with unknown email → 401."""
    response = await client.post(
        "/auth/login",
        json={"email": "nobody@nowhere.com", "password": "whatever123"},
    )
    assert response.status_code == 401
