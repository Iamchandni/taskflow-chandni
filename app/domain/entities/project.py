"""
app/domain/entities/project.py
──────────────────────────────
Pure domain entity for Project. Plain dataclass — no framework deps.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Project:
    """A project that contains tasks."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: Optional[str] = None
    owner_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
