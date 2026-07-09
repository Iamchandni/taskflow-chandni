"""
app/api/v1/task_router.py
─────────────────────────
HTTP router for task endpoints. HTTP concerns only — delegates to TaskService.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.dependencies import get_current_user, get_task_service
from app.application.services.task_service import TaskService
from app.domain.dtos.common_dto import MessageResponse, PaginatedResponse
from app.domain.dtos.task_dto import TaskCreateRequest, TaskResponse, TaskUpdateRequest
from app.domain.entities.user import User
from app.shared.constants import DEFAULT_LIMIT, DEFAULT_PAGE

router = APIRouter(
    tags=["Tasks"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
        status.HTTP_403_FORBIDDEN: {"description": "Not authorized to perform this action"},
        status.HTTP_404_NOT_FOUND: {"description": "Task or project not found"},
    },
)


@router.get(
    "/projects/{project_id}/tasks",
    response_model=PaginatedResponse[TaskResponse],
    summary="List tasks in a project",
)
async def list_tasks(
    project_id: UUID,
    status_filter: str | None = Query(None, alias="status"),
    assignee: UUID | None = Query(None, alias="assignee"),
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """List tasks for a project. Supports ?status= and ?assignee= filters."""
    return await task_service.list_tasks(
        project_id,
        status=status_filter,
        assignee_id=assignee,
        page=page,
        limit=limit,
    )


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
)
async def create_task(
    project_id: UUID,
    request: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Create a new task in the project. Creator is set to current user."""
    return await task_service.create_task(project_id, request, current_user.id)


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
)
async def update_task(
    task_id: UUID,
    request: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Update task title, description, status, priority, assignee, or due_date."""
    return await task_service.update_task(task_id, request, current_user)


@router.delete(
    "/tasks/{task_id}",
    response_model=MessageResponse,
    summary="Delete a task",
)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Delete a task. Project owner or task creator only."""
    await task_service.delete_task(task_id, current_user)
    return MessageResponse(message="task deleted")
