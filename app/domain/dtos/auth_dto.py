"""
app/domain/dtos/auth_dto.py
───────────────────────────
DTOs (Data Transfer Objects) for authentication endpoints.
These are Pydantic models used STRICTLY for request validation and response
serialization. They do NOT contain business logic.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Requests ────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    """POST /auth/register request body."""

    name: str = Field(..., min_length=1, max_length=255, description="User's display name")
    email: EmailStr = Field(..., description="Unique email address")
    password: str = Field(..., min_length=6, max_length=128, description="Plain-text password")


class LoginRequest(BaseModel):
    """POST /auth/login request body."""

    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., min_length=1, description="Plain-text password")


# ── Responses ───────────────────────────────────────────────────


class TokenResponse(BaseModel):
    """Returned on successful login."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public user representation, returned on registration and in other contexts."""

    id: UUID
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
