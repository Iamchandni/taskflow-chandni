"""
app/domain/interfaces/task_repository.py
────────────────────────────────────────
Abstract repository contract for Task persistence.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID

from app.domain.entities.task import Task


class ITaskRepository(ABC):
    """Contract for task persistence operations."""

    @abstractmethod
    async def create(self, task: Task) -> Task:
        """Persist a new task."""
        ...

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """Get a task by ID. Returns None if not found."""
        ...

    @abstractmethod
    async def list_for_project(
        self,
        project_id: UUID,
        status: Optional[str] = None,
        assignee_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Task], int]:
        """
        List tasks for a project with optional filters.
        Returns (tasks, total_count) for pagination.
        """
        ...

    @abstractmethod
    async def update(self, task: Task) -> Task:
        """Update an existing task."""
        ...

    @abstractmethod
    async def delete(self, task_id: UUID) -> None:
        """Delete a task."""
        ...

    @abstractmethod
    async def get_status_counts(self, project_id: UUID) -> list[dict[str, Any]]:
        """Get task counts grouped by status for a project."""
        ...

    @abstractmethod
    async def get_assignee_counts(self, project_id: UUID) -> list[dict[str, Any]]:
        """Get task counts grouped by assignee for a project."""
        ...
