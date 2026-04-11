"""
app/application/services/project_service.py
───────────────────────────────────────────
Orchestrates project-related use cases: create, read, update, delete, list.

DDD rules:
- Depends on IProjectRepository + ITaskRepository (interfaces only)
- Enforces authorization (owner-only for update/delete)
- Raises domain exceptions, never HTTP exceptions
- Never imports SQLAlchemy
"""

from uuid import UUID, uuid4

from app.core.exceptions import AuthorizationError, NotFoundError
from app.core.logging import get_logger
from app.domain.dtos.project_dto import (
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectUpdateRequest,
    TaskInProjectResponse,
)
from app.domain.dtos.common_dto import PaginatedResponse
from app.domain.entities.project import Project
from app.domain.interfaces.project_repository import IProjectRepository
from app.domain.interfaces.task_repository import ITaskRepository
from app.shared.constants import DEFAULT_LIMIT, DEFAULT_PAGE, MAX_LIMIT

logger = get_logger(__name__)


class ProjectService:
    """Handles project CRUD and listing."""

    def __init__(
        self,
        project_repo: IProjectRepository,
        task_repo: ITaskRepository,
    ):
        self._project_repo = project_repo
        self._task_repo = task_repo

    async def create_project(
        self, request: ProjectCreateRequest, owner_id: UUID
    ) -> ProjectResponse:
        """Create a new project owned by the current user."""
        project = Project(
            id=uuid4(),
            name=request.name,
            description=request.description,
            owner_id=owner_id,
        )
        created = await self._project_repo.create(project)
        logger.info("project_created", project_id=str(created.id), owner_id=str(owner_id))
        return ProjectResponse(
            id=created.id,
            name=created.name,
            description=created.description,
            owner_id=created.owner_id,
            created_at=created.created_at,
        )

    async def list_projects(
        self, user_id: UUID, page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT
    ) -> PaginatedResponse[ProjectResponse]:
        """List projects the user owns or has tasks in, with pagination."""
        limit = min(limit, MAX_LIMIT)
        offset = (page - 1) * limit

        projects, total = await self._project_repo.list_for_user(user_id, limit, offset)
        pages = (total + limit - 1) // limit if limit > 0 else 0

        return PaginatedResponse(
            items=[
                ProjectResponse(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    owner_id=p.owner_id,
                    created_at=p.created_at,
                )
                for p in projects
            ],
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )

    async def get_project_detail(self, project_id: UUID) -> ProjectDetailResponse:
        """Get a project with all its tasks."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("not found")

        tasks, _ = await self._task_repo.list_for_project(project_id, limit=1000, offset=0)

        return ProjectDetailResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            owner_id=project.owner_id,
            created_at=project.created_at,
            tasks=[
                TaskInProjectResponse(
                    id=t.id,
                    title=t.title,
                    status=t.status.value if hasattr(t.status, 'value') else t.status,
                    priority=t.priority.value if hasattr(t.priority, 'value') else t.priority,
                    assignee_id=t.assignee_id,
                    due_date=str(t.due_date) if t.due_date else None,
                    created_at=t.created_at,
                )
                for t in tasks
            ],
        )

    async def update_project(
        self, project_id: UUID, request: ProjectUpdateRequest, user_id: UUID
    ) -> ProjectResponse:
        """Update a project. Only the owner can update."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("not found")
        if project.owner_id != user_id:
            raise AuthorizationError("permission denied")

        if request.name is not None:
            project.name = request.name
        if request.description is not None:
            project.description = request.description

        updated = await self._project_repo.update(project)
        logger.info("project_updated", project_id=str(project_id))

        return ProjectResponse(
            id=updated.id,
            name=updated.name,
            description=updated.description,
            owner_id=updated.owner_id,
            created_at=updated.created_at,
        )

    async def delete_project(self, project_id: UUID, user_id: UUID) -> None:
        """Delete a project and all its tasks. Only the owner can delete."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("not found")
        if project.owner_id != user_id:
            raise AuthorizationError("permission denied")

        await self._project_repo.delete(project_id)
        logger.info("project_deleted", project_id=str(project_id))
