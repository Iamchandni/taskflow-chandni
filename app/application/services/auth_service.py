"""
app/application/services/auth_service.py
────────────────────────────────────────
Orchestrates authentication use cases: registration and login.

Key DDD rules enforced here:
- Receives repository interfaces (not concrete impls) via constructor injection.
- Never touches SQLAlchemy sessions — all DB access goes through IUserRepository.
- Uses core/security.py for hashing and JWT — pure functions, no framework deps.
- Raises domain exceptions (from core/exceptions.py), NOT HTTP exceptions.
"""

from uuid import uuid4

from app.core.exceptions import AuthenticationError, ConflictError, ValidationError
from app.core.logging import get_logger
from app.core.security import create_access_token, hash_password, verify_password
from app.domain.dtos.auth_dto import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.domain.entities.user import User
from app.domain.interfaces.user_repository import IUserRepository

logger = get_logger(__name__)


class AuthService:
    """Handles user registration and login."""

    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo

    async def register(self, request: RegisterRequest) -> UserResponse:
        """
        Register a new user.
        1. Check for duplicate email → ConflictError
        2. Hash password with bcrypt
        3. Persist via repository
        4. Return public user response (no password)
        """
        existing = await self._user_repo.get_by_email(request.email)
        if existing:
            raise ConflictError("email already registered")

        user = User(
            id=uuid4(),
            name=request.name,
            email=request.email,
            password=hash_password(request.password),
        )

        created = await self._user_repo.create(user)
        logger.info("user_registered", user_id=str(created.id), email=created.email)

        return UserResponse(
            id=created.id,
            name=created.name,
            email=created.email,
            created_at=created.created_at,
        )

    async def login(self, request: LoginRequest) -> TokenResponse:
        """
        Authenticate a user and return a JWT.
        1. Look up user by email
        2. Verify password → AuthenticationError
        3. Create and return signed JWT
        """
        user = await self._user_repo.get_by_email(request.email)
        if not user:
            raise AuthenticationError("invalid credentials")

        if not verify_password(request.password, user.password):
            raise AuthenticationError("invalid credentials")

        token = create_access_token(str(user.id), user.email)
        logger.info("user_logged_in", user_id=str(user.id))

        return TokenResponse(access_token=token)
