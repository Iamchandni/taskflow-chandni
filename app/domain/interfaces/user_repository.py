"""
app/domain/interfaces/user_repository.py
────────────────────────────────────────
Abstract repository contract for User persistence.
The domain defines WHAT operations are needed; infrastructure decides HOW.
This is the core of dependency inversion — application services depend on
this ABC, never on the concrete SQLAlchemy implementation.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.user import User


class IUserRepository(ABC):
    """Contract for user persistence operations."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Persist a new user and return it with generated fields filled."""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve a user by their UUID. Returns None if not found."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email address. Returns None if not found."""
        ...
