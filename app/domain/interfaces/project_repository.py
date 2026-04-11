"""
app/domain/interfaces/project_repository.py
───────────────────────────────────────────
Abstract repository contract for Project persistence.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.project import Project


class IProjectRepository(ABC):
    """Contract for project persistence operations."""

    @abstractmethod
    async def create(self, project: Project) -> Project:
        """Persist a new project."""
        ...

    @abstractmethod
    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """Get a project by ID. Returns None if not found."""
        ...

    @abstractmethod
    async def list_for_user(
        self, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[Project], int]:
        """
        List projects the user owns or has tasks in.
        Returns (projects, total_count) for pagination.
        """
        ...

    @abstractmethod
    async def update(self, project: Project) -> Project:
        """Update an existing project."""
        ...

    @abstractmethod
    async def delete(self, project_id: UUID) -> None:
        """Delete a project and all its tasks (cascade)."""
        ...
