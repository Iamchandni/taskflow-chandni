"""
app/infrastructure/persistence/models/user_model.py
───────────────────────────────────────────────────
SQLAlchemy ORM model for the users table.
This is an INFRASTRUCTURE concern — it maps the domain User entity to a
relational table. The domain entity itself (app/domain/entities/user.py) is
a pure dataclass with no SQLAlchemy dependency.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    role: Mapped[str] = mapped_column(
        SAEnum("admin", "member", name="user_role"),
        nullable=False,
        server_default="member",
    )

    # Relationships
    owned_projects = relationship("ProjectModel", back_populates="owner", cascade="all, delete-orphan")
    assigned_tasks = relationship("TaskModel", back_populates="assignee", foreign_keys="TaskModel.assignee_id")
    created_tasks = relationship("TaskModel", back_populates="creator", foreign_keys="TaskModel.creator_id")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
