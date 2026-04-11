"""
app/api/v1/dependencies.py
──────────────────────────
FastAPI dependency injection wiring. This is the ONLY place where:
1. The SQLAlchemy session is obtained (via get_db_session)
2. Concrete repositories are instantiated and injected into services
3. JWT tokens are extracted and validated to get the current user

This module is the "composition root" — it wires infrastructure implementations
to domain interfaces, ensuring all other layers remain decoupled.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.processors.stats_processor import StatsProcessor
from app.application.services.auth_service import AuthService
from app.application.services.project_service import ProjectService
from app.application.services.task_service import TaskService
from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.domain.entities.user import User
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories.project_repository import ProjectRepository
from app.infrastructure.persistence.repositories.task_repository import TaskRepository
from app.infrastructure.persistence.repositories.user_repository import UserRepository


# ── Database session ────────────────────────────────────────────

async def get_db(session: AsyncSession = Depends(get_db_session)) -> AsyncSession:
    """Yields an async DB session — used only in this file to build repos."""
    return session


# ── Repository factories ───────────────────────────────────────

def get_user_repo(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


def get_project_repo(session: AsyncSession = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(session)


def get_task_repo(session: AsyncSession = Depends(get_db)) -> TaskRepository:
    return TaskRepository(session)


# ── Service factories ──────────────────────────────────────────

def get_auth_service(user_repo: UserRepository = Depends(get_user_repo)) -> AuthService:
    return AuthService(user_repo)


def get_project_service(
    project_repo: ProjectRepository = Depends(get_project_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
) -> ProjectService:
    return ProjectService(project_repo, task_repo)


def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repo),
    project_repo: ProjectRepository = Depends(get_project_repo),
) -> TaskService:
    return TaskService(task_repo, project_repo)


def get_stats_processor(
    project_repo: ProjectRepository = Depends(get_project_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
) -> StatsProcessor:
    return StatsProcessor(project_repo, task_repo)


# ── Authentication dependency ──────────────────────────────────

async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    user_repo: UserRepository = Depends(get_user_repo),
) -> User:
    """
    Extract and validate the Bearer JWT from the Authorization header.
    Returns the authenticated User domain entity.
    Raises AuthenticationError (→ 401) on any failure.
    """
    if not authorization:
        raise AuthenticationError("missing authorization header")

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("invalid authorization header format")

    token = parts[1]
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise AuthenticationError("invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("invalid token payload")

    user = await user_repo.get_by_id(UUID(user_id))
    if not user:
        raise AuthenticationError("user not found")

    return user
