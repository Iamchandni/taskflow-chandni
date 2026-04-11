"""
app/infrastructure/persistence/repositories/project_repository.py
────────────────────────────────────────────────────────────────
Concrete implementation of IProjectRepository using SQLAlchemy async sessions.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, text, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.project import Project
from app.domain.interfaces.project_repository import IProjectRepository
from app.infrastructure.mappers.project_mapper import ProjectMapper
from app.infrastructure.persistence.models.project_model import ProjectModel
from app.infrastructure.persistence.models.task_model import TaskModel


class ProjectRepository(IProjectRepository):
    """SQLAlchemy-backed project repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, project: Project) -> Project:
        model = ProjectMapper.to_model(project)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return ProjectMapper.to_entity(model)

    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        stmt = select(ProjectModel).where(ProjectModel.id == project_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return ProjectMapper.to_entity(model) if model else None

    async def list_for_user(
        self, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[Project], int]:
        # Subquery: project IDs where user has tasks
        task_project_ids = (
            select(TaskModel.project_id)
            .where(TaskModel.assignee_id == user_id)
            .distinct()
            .subquery()
        )

        # Projects owned by user OR where user has assigned tasks
        where_clause = or_(
            ProjectModel.owner_id == user_id,
            ProjectModel.id.in_(select(task_project_ids.c.project_id)),
        )

        # Count
        count_stmt = select(func.count()).select_from(ProjectModel).where(where_clause)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Paginated list
        list_stmt = (
            select(ProjectModel)
            .where(where_clause)
            .order_by(ProjectModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(list_stmt)
        models = result.scalars().all()

        return [ProjectMapper.to_entity(m) for m in models], total

    async def update(self, project: Project) -> Project:
        stmt = select(ProjectModel).where(ProjectModel.id == project.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Project {project.id} not found")

        model.name = project.name
        model.description = project.description
        await self._session.flush()
        await self._session.refresh(model)
        return ProjectMapper.to_entity(model)

    async def delete(self, project_id: UUID) -> None:
        stmt = select(ProjectModel).where(ProjectModel.id == project_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
