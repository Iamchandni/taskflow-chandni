"""
app/infrastructure/persistence/repositories/user_repository.py
──────────────────────────────────────────────────────────────
Concrete implementation of IUserRepository using SQLAlchemy async sessions.
This is the ONLY place where user-related SQL queries live.
Implements the contract defined in domain/interfaces/user_repository.py.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.interfaces.user_repository import IUserRepository
from app.infrastructure.mappers.user_mapper import UserMapper
from app.infrastructure.persistence.models.user_model import UserModel


class UserRepository(IUserRepository):
    """SQLAlchemy-backed user repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user: User) -> User:
        model = UserMapper.to_model(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return UserMapper.to_entity(model)

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None
