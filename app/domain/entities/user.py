"""
app/domain/entities/user.py
───────────────────────────
Pure domain entity for User. This is a plain Python dataclass with ZERO
dependencies on SQLAlchemy, FastAPI, or Pydantic. It represents the core
business concept of a user in the system.

The domain entity is mapped to/from the ORM model via infrastructure/mappers/.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.shared.constants import UserRole


@dataclass
class User:
    """A registered user in the system."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    email: str = ""
    password: str = ""  # bcrypt hash — never plain text
    created_at: datetime = field(default_factory=datetime.utcnow)
    role: str = UserRole.MEMBER.value
