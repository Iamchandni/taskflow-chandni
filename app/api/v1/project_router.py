"""
app/api/v1/project_router.py
────────────────────────────
HTTP router for project endpoints. HTTP concerns only — delegates to
ProjectService and StatsProcessor for all business logic.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.dependencies import (
    get_current_user,
    get_project_service,
    get_stats_processor,
)
from app.application.processors.stats_processor import StatsProcessor
from app.application.services.project_service import ProjectService
from app.domain.dtos.common_dto import MessageResponse, PaginatedResponse
from app.domain.dtos.project_dto import (
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectStatsResponse,
    ProjectUpdateRequest,
)
from app.domain.entities.user import User
from app.shared.constants import DEFAULT_LIMIT, DEFAULT_PAGE

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
        status.HTTP_403_FORBIDDEN: {"description": "Not authorized to perform this action"},
        status.HTTP_404_NOT_FOUND: {"description": "Project not found"},
    },
)


@router.get(
    "",
    response_model=PaginatedResponse[ProjectResponse],
    summary="List projects",
)
async def list_projects(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """List projects the current user owns or has tasks in."""
    return await project_service.list_projects(current_user.id, page, limit)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
)
async def create_project(
    request: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Create a new project. The current user becomes the owner."""
    return await project_service.create_project(request, current_user.id)


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Get project details",
)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Get project details including all its tasks."""
    return await project_service.get_project_detail(project_id)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project",
)
async def update_project(
    project_id: UUID,
    request: ProjectUpdateRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Update project name/description. Owner only."""
    return await project_service.update_project(project_id, request, current_user.id)


@router.delete(
    "/{project_id}",
    response_model=MessageResponse,
    summary="Delete a project",
)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Delete a project and all its tasks. Owner only."""
    await project_service.delete_project(project_id, current_user.id)
    return MessageResponse(message="project deleted")


@router.get(
    "/{project_id}/stats",
    response_model=ProjectStatsResponse,
    summary="Get project statistics",
)
async def get_project_stats(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    stats_processor: StatsProcessor = Depends(get_stats_processor),
):
    """Get task counts by status and by assignee for a project."""
    return await stats_processor.get_project_stats(project_id)
