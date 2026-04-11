"""
app/domain/dtos/task_dto.py
───────────────────────────
DTOs for task endpoints — create, update, and response schemas.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.constants import TaskPriority, TaskStatus


# ── Requests ────────────────────────────────────────────────────


class TaskCreateRequest(BaseModel):
    """POST /projects/:id/tasks request body."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None


class TaskUpdateRequest(BaseModel):
    """PATCH /tasks/:id request body. All fields optional."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None


# ── Responses ───────────────────────────────────────────────────


class TaskResponse(BaseModel):
    """Full task representation."""

    id: UUID
    title: str
    description: Optional[str]
    status: str
    priority: str
    project_id: UUID
    assignee_id: Optional[UUID]
    creator_id: UUID
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
