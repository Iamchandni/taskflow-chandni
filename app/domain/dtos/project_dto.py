"""
app/domain/dtos/project_dto.py
──────────────────────────────
DTOs for project endpoints — create, update, and response schemas.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ── Requests ────────────────────────────────────────────────────


class ProjectCreateRequest(BaseModel):
    """POST /projects request body."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class ProjectUpdateRequest(BaseModel):
    """PATCH /projects/:id request body. All fields optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


# ── Responses ───────────────────────────────────────────────────


class ProjectResponse(BaseModel):
    """Project summary (used in list endpoints)."""

    id: UUID
    name: str
    description: Optional[str]
    owner_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskInProjectResponse(BaseModel):
    """Abbreviated task view embedded inside project detail."""

    id: UUID
    title: str
    status: str
    priority: str
    assignee_id: Optional[UUID]
    due_date: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetailResponse(BaseModel):
    """Full project detail including its tasks."""

    id: UUID
    name: str
    description: Optional[str]
    owner_id: UUID
    created_at: datetime
    tasks: list[TaskInProjectResponse] = []

    model_config = {"from_attributes": True}


class StatusCount(BaseModel):
    status: str
    count: int


class AssigneeCount(BaseModel):
    assignee_id: Optional[UUID]
    assignee_name: Optional[str]
    count: int


class ProjectStatsResponse(BaseModel):
    """Task statistics for a project."""

    project_id: UUID
    by_status: list[StatusCount]
    by_assignee: list[AssigneeCount]
