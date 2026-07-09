"""
app/tests/test_rbac.py
──────────────────────
Unit tests for app/core/rbac.py. No DB or HTTP client required.
Constructs domain entities directly with explicit UUIDs.
"""

import uuid

from app.core.rbac import is_admin, can_manage_project, can_manage_task
from app.domain.entities.user import User
from app.domain.entities.project import Project
from app.domain.entities.task import Task

ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
MEMBER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
OWNER_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
CREATOR_ID = uuid.UUID("00000000-0000-0000-0000-000000000004")
PROJECT_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
TASK_ID = uuid.UUID("00000000-0000-0000-0000-000000000020")


def _admin() -> User:
    return User(id=ADMIN_ID, role="admin")


def _member(uid: uuid.UUID = MEMBER_ID) -> User:
    return User(id=uid, role="member")


def _project(owner_id: uuid.UUID = OWNER_ID) -> Project:
    return Project(id=PROJECT_ID, owner_id=owner_id)


def _task(creator_id: uuid.UUID = CREATOR_ID) -> Task:
    return Task(id=TASK_ID, creator_id=creator_id, project_id=PROJECT_ID)


def test_is_admin_true_for_admin():
    assert is_admin(_admin()) is True


def test_is_admin_false_for_member():
    assert is_admin(_member()) is False


def test_can_manage_project_member_owner():
    user = _member(uid=OWNER_ID)
    assert can_manage_project(user, _project(owner_id=OWNER_ID)) is True


def test_can_manage_project_member_non_owner():
    user = _member(uid=MEMBER_ID)
    assert can_manage_project(user, _project(owner_id=OWNER_ID)) is False


def test_can_manage_project_admin_non_owner():
    user = _admin()
    assert can_manage_project(user, _project(owner_id=OWNER_ID)) is True


def test_can_manage_task_member_creator():
    user = _member(uid=CREATOR_ID)
    task = _task(creator_id=CREATOR_ID)
    project = _project(owner_id=OWNER_ID)
    assert can_manage_task(user, task, project) is True


def test_can_manage_task_member_project_owner():
    user = _member(uid=OWNER_ID)
    task = _task(creator_id=CREATOR_ID)
    project = _project(owner_id=OWNER_ID)
    assert can_manage_task(user, task, project) is True


def test_can_manage_task_member_unrelated():
    user = _member(uid=MEMBER_ID)
    task = _task(creator_id=CREATOR_ID)
    project = _project(owner_id=OWNER_ID)
    assert can_manage_task(user, task, project) is False


def test_can_manage_task_admin_unrelated():
    user = _admin()
    task = _task(creator_id=CREATOR_ID)
    project = _project(owner_id=OWNER_ID)
    assert can_manage_task(user, task, project) is True


def test_can_manage_task_project_none_creator():
    user = _member(uid=CREATOR_ID)
    task = _task(creator_id=CREATOR_ID)
    assert can_manage_task(user, task, None) is True


def test_can_manage_task_project_none_non_creator():
    user = _member(uid=MEMBER_ID)
    task = _task(creator_id=CREATOR_ID)
    assert can_manage_task(user, task, None) is False
