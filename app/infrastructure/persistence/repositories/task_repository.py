"""
app/infrastructure/persistence/repositories/task_repository.py
─────────────────────────────────────────────────────────────
Concrete implementation of ITaskRepository using SQLAlchemy async sessions.
Includes stats queries for the processor layer.
"""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.task import Task
from app.domain.interfaces.task_repository import ITaskRepository
from app.infrastructure.mappers.task_mapper import TaskMapper
from app.infrastructure.persistence.models.task_model import TaskModel
from app.infrastructure.persistence.models.user_model import UserModel
from app.shared.constants import SQL_TASK_COUNTS_BY_STATUS, SQL_TASK_COUNTS_BY_ASSIGNEE


class TaskRepository(ITaskRepository):
    """SQLAlchemy-backed task repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, task: Task) -> Task:
        model = TaskMapper.to_model(task)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return TaskMapper.to_entity(model)

    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return TaskMapper.to_entity(model) if model else None

    async def list_for_project(
        self,
        project_id: UUID,
        status: Optional[str] = None,
        assignee_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Task], int]:
        # Build dynamic where clause
        conditions = [TaskModel.project_id == project_id]
        if status is not None:
            conditions.append(TaskModel.status == status)
        if assignee_id is not None:
            conditions.append(TaskModel.assignee_id == assignee_id)

        # Count
        count_stmt = select(func.count()).select_from(TaskModel).where(*conditions)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Paginated list
        list_stmt = (
            select(TaskModel)
            .where(*conditions)
            .order_by(TaskModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(list_stmt)
        models = result.scalars().all()

        return [TaskMapper.to_entity(m) for m in models], total

    async def update(self, task: Task) -> Task:
        stmt = select(TaskModel).where(TaskModel.id == task.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Task {task.id} not found")

        model.title = task.title
        model.description = task.description
        model.status = task.status.value if hasattr(task.status, 'value') else task.status
        model.priority = task.priority.value if hasattr(task.priority, 'value') else task.priority
        model.assignee_id = task.assignee_id
        model.due_date = task.due_date
        model.updated_at = datetime.now(timezone.utc)

        await self._session.flush()
        await self._session.refresh(model)
        return TaskMapper.to_entity(model)

    async def delete(self, task_id: UUID) -> None:
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def get_status_counts(self, project_id: UUID) -> list[dict[str, Any]]:
        result = await self._session.execute(
            text(SQL_TASK_COUNTS_BY_STATUS),
            {"project_id": str(project_id)},
        )
        return [{"status": row[0], "count": row[1]} for row in result.fetchall()]

    async def get_assignee_counts(self, project_id: UUID) -> list[dict[str, Any]]:
        result = await self._session.execute(
            text(SQL_TASK_COUNTS_BY_ASSIGNEE),
            {"project_id": str(project_id)},
        )
        return [
            {
                "assignee_id": row[0],
                "assignee_name": row[1],
                "count": row[2],
            }
            for row in result.fetchall()
        ]
