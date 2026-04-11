"""
app/application/services/task_service.py
────────────────────────────────────────
Orchestrates task-related use cases: create, list, update, delete.

DDD rules:
- Depends on ITaskRepository + IProjectRepository (interfaces only)
- Enforces authorization (project owner or task creator for delete)
- Never imports SQLAlchemy
"""

from uuid import UUID, uuid4

from app.core.exceptions import AuthorizationError, NotFoundError
from app.core.logging import get_logger
from app.domain.dtos.common_dto import PaginatedResponse
from app.domain.dtos.task_dto import TaskCreateRequest, TaskResponse, TaskUpdateRequest
from app.domain.entities.task import Task
from app.domain.interfaces.project_repository import IProjectRepository
from app.domain.interfaces.task_repository import ITaskRepository
from app.shared.constants import DEFAULT_LIMIT, DEFAULT_PAGE, MAX_LIMIT

logger = get_logger(__name__)


class TaskService:
    """Handles task CRUD and listing."""

    def __init__(
        self,
        task_repo: ITaskRepository,
        project_repo: IProjectRepository,
    ):
        self._task_repo = task_repo
        self._project_repo = project_repo

    async def create_task(
        self, project_id: UUID, request: TaskCreateRequest, creator_id: UUID
    ) -> TaskResponse:
        """Create a task in a project. creator_id is set to the current user."""
        # Verify project exists
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("not found")

        task = Task(
            id=uuid4(),
            title=request.title,
            description=request.description,
            status=request.status,
            priority=request.priority,
            project_id=project_id,
            assignee_id=request.assignee_id,
            creator_id=creator_id,
            due_date=request.due_date,
        )

        created = await self._task_repo.create(task)
        logger.info("task_created", task_id=str(created.id), project_id=str(project_id))

        return self._to_response(created)

    async def list_tasks(
        self,
        project_id: UUID,
        status: str | None = None,
        assignee_id: UUID | None = None,
        page: int = DEFAULT_PAGE,
        limit: int = DEFAULT_LIMIT,
    ) -> PaginatedResponse[TaskResponse]:
        """List tasks in a project with optional filters and pagination."""
        # Verify project exists
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("not found")

        limit = min(limit, MAX_LIMIT)
        offset = (page - 1) * limit

        tasks, total = await self._task_repo.list_for_project(
            project_id, status=status, assignee_id=assignee_id, limit=limit, offset=offset
        )
        pages = (total + limit - 1) // limit if limit > 0 else 0

        return PaginatedResponse(
            items=[self._to_response(t) for t in tasks],
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )

    async def update_task(
        self, task_id: UUID, request: TaskUpdateRequest
    ) -> TaskResponse:
        """Update a task's mutable fields."""
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("not found")

        if request.title is not None:
            task.title = request.title
        if request.description is not None:
            task.description = request.description
        if request.status is not None:
            task.status = request.status
        if request.priority is not None:
            task.priority = request.priority
        if request.assignee_id is not None:
            task.assignee_id = request.assignee_id
        if request.due_date is not None:
            task.due_date = request.due_date

        updated = await self._task_repo.update(task)
        logger.info("task_updated", task_id=str(task_id))

        return self._to_response(updated)

    async def delete_task(self, task_id: UUID, user_id: UUID) -> None:
        """
        Delete a task. Only the project owner or task creator can delete.
        """
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("not found")

        # Check: is the user the task creator?
        if task.creator_id == user_id:
            await self._task_repo.delete(task_id)
            logger.info("task_deleted", task_id=str(task_id), by="creator")
            return

        # Check: is the user the project owner?
        project = await self._project_repo.get_by_id(task.project_id)
        if project and project.owner_id == user_id:
            await self._task_repo.delete(task_id)
            logger.info("task_deleted", task_id=str(task_id), by="project_owner")
            return

        raise AuthorizationError("permission denied")

    @staticmethod
    def _to_response(task: Task) -> TaskResponse:
        """Convert a domain Task entity to a TaskResponse DTO."""
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status.value if hasattr(task.status, 'value') else task.status,
            priority=task.priority.value if hasattr(task.priority, 'value') else task.priority,
            project_id=task.project_id,
            assignee_id=task.assignee_id,
            creator_id=task.creator_id,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
