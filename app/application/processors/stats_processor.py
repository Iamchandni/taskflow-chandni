"""
app/application/processors/stats_processor.py
─────────────────────────────────────────────
Processor for computing project statistics (task counts by status and by
assignee). Processors handle metric computation and workflow logic that
is more complex than simple CRUD orchestration.

DDD rules:
- Depends on repository interfaces, not concrete impls
- Never imports SQLAlchemy
- Returns DTOs, not raw dicts
"""

from uuid import UUID

from app.core.exceptions import NotFoundError
from app.domain.dtos.project_dto import (
    AssigneeCount,
    ProjectStatsResponse,
    StatusCount,
)
from app.domain.interfaces.project_repository import IProjectRepository
from app.domain.interfaces.task_repository import ITaskRepository


class StatsProcessor:
    """Computes project-level task statistics."""

    def __init__(
        self,
        project_repo: IProjectRepository,
        task_repo: ITaskRepository,
    ):
        self._project_repo = project_repo
        self._task_repo = task_repo

    async def get_project_stats(self, project_id: UUID) -> ProjectStatsResponse:
        """
        Compute task counts by status and by assignee for a project.
        Used by GET /projects/:id/stats.
        """
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("not found")

        status_rows = await self._task_repo.get_status_counts(project_id)
        assignee_rows = await self._task_repo.get_assignee_counts(project_id)

        return ProjectStatsResponse(
            project_id=project_id,
            by_status=[
                StatusCount(status=row["status"], count=row["count"])
                for row in status_rows
            ],
            by_assignee=[
                AssigneeCount(
                    assignee_id=row.get("assignee_id"),
                    assignee_name=row.get("assignee_name"),
                    count=row["count"],
                )
                for row in assignee_rows
            ],
        )
