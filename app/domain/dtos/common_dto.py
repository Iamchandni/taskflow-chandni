"""
app/domain/dtos/common_dto.py
─────────────────────────────
Shared DTOs used across multiple endpoints — pagination wrapper and
error response schemas.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Wraps any list response with pagination metadata."""

    items: list[T]
    total: int
    page: int
    limit: int
    pages: int


class ErrorResponse(BaseModel):
    """Standard error response body."""

    error: str


class ValidationErrorResponse(BaseModel):
    """Structured validation error with per-field messages."""

    error: str = "validation failed"
    fields: dict[str, str]


class MessageResponse(BaseModel):
    """Simple success message."""

    message: str
