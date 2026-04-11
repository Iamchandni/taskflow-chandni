"""
app/domain/entities/task.py
───────────────────────────
Pure domain entity for Task. Plain dataclass — no framework deps.
Uses string enums from shared/constants.py for status and priority.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from app.shared.constants import TaskStatus, TaskPriority


@dataclass
class Task:
    """A task belonging to a project, optionally assigned to a user."""

    id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    project_id: UUID = field(default_factory=uuid4)
    assignee_id: Optional[UUID] = None
    creator_id: UUID = field(default_factory=uuid4)
    due_date: Optional[date] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
