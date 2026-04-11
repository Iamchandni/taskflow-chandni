"""
app/infrastructure/mappers/task_mapper.py
─────────────────────────────────────────
Bidirectional mapper between Task entity and TaskModel ORM.
"""

from app.domain.entities.task import Task
from app.infrastructure.persistence.models.task_model import TaskModel
from app.shared.constants import TaskStatus, TaskPriority


class TaskMapper:
    """Converts between Task (domain) ↔ TaskModel (ORM)."""

    @staticmethod
    def to_entity(model: TaskModel) -> Task:
        return Task(
            id=model.id,
            title=model.title,
            description=model.description,
            status=TaskStatus(model.status) if isinstance(model.status, str) else model.status,
            priority=TaskPriority(model.priority) if isinstance(model.priority, str) else model.priority,
            project_id=model.project_id,
            assignee_id=model.assignee_id,
            creator_id=model.creator_id,
            due_date=model.due_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Task) -> TaskModel:
        return TaskModel(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            status=entity.status.value if isinstance(entity.status, TaskStatus) else entity.status,
            priority=entity.priority.value if isinstance(entity.priority, TaskPriority) else entity.priority,
            project_id=entity.project_id,
            assignee_id=entity.assignee_id,
            creator_id=entity.creator_id,
            due_date=entity.due_date,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
