"""
app/api/v1/auth_router.py
─────────────────────────
HTTP router for authentication endpoints. Contains ONLY HTTP concerns:
- Parse request bodies
- Call application service
- Return HTTP responses with correct status codes

NO business logic lives here. The router delegates everything to AuthService.
"""

from fastapi import APIRouter, Depends, status

from app.application.services.auth_service import AuthService
from app.api.v1.dependencies import get_auth_service
from app.domain.dtos.auth_dto import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register with name, email, and password. Returns the created user."""
    return await auth_service.register(request)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Log in and receive a JWT",
)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticate with email and password. Returns a JWT access token."""
    return await auth_service.login(request)
