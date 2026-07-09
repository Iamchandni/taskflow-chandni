"""
app/infrastructure/mappers/user_mapper.py
─────────────────────────────────────────
Bidirectional mapper between the pure domain User entity and the SQLAlchemy
UserModel. This keeps the domain layer clean — the entity never knows about
SQLAlchemy, and the ORM model never leaks into application services.
"""

from app.domain.entities.user import User
from app.infrastructure.persistence.models.user_model import UserModel


class UserMapper:
    """Converts between User (domain) ↔ UserModel (ORM)."""

    @staticmethod
    def to_entity(model: UserModel) -> User:
        """ORM model → domain entity."""
        return User(
            id=model.id,
            name=model.name,
            email=model.email,
            password=model.password,
            created_at=model.created_at,
            role=model.role,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        """Domain entity → ORM model (for inserts)."""
        return UserModel(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            password=entity.password,
            created_at=entity.created_at,
            role=entity.role,
        )
