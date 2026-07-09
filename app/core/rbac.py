from typing import Optional

from app.domain.entities.project import Project
from app.domain.entities.task import Task
from app.domain.entities.user import User
from app.shared.constants import UserRole


def is_admin(user: User) -> bool:
    return user.role == UserRole.ADMIN.value


def can_manage_project(user: User, project: Project) -> bool:
    return is_admin(user) or project.owner_id == user.id


def can_manage_task(user: User, task: Task, project: Optional[Project]) -> bool:
    if is_admin(user):
        return True
    if task.creator_id == user.id:
        return True
    return project is not None and project.owner_id == user.id
