"""
app/shared/constants.py
───────────────────────
Shared constants, enum values, and default pagination settings.
SQL query fragments that are reused across repositories also live here,
keeping the persistence layer DRY.
"""

from enum import Enum

# ── Task enums ──────────────────────────────────────────────────


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ── Pagination defaults ────────────────────────────────────────

DEFAULT_PAGE = 1
DEFAULT_LIMIT = 20
MAX_LIMIT = 100

# ── SQL fragments (reusable across repos) ──────────────────────

SQL_PROJECTS_FOR_USER = """
    SELECT DISTINCT p.*
    FROM projects p
    LEFT JOIN tasks t ON t.project_id = p.id
    WHERE p.owner_id = :user_id OR t.assignee_id = :user_id
    ORDER BY p.created_at DESC
    LIMIT :limit OFFSET :offset
"""

SQL_PROJECTS_FOR_USER_COUNT = """
    SELECT COUNT(DISTINCT p.id)
    FROM projects p
    LEFT JOIN tasks t ON t.project_id = p.id
    WHERE p.owner_id = :user_id OR t.assignee_id = :user_id
"""

SQL_TASK_COUNTS_BY_STATUS = """
    SELECT status, COUNT(*) as count
    FROM tasks
    WHERE project_id = :project_id
    GROUP BY status
"""

SQL_TASK_COUNTS_BY_ASSIGNEE = """
    SELECT
        t.assignee_id,
        u.name as assignee_name,
        COUNT(*) as count
    FROM tasks t
    LEFT JOIN users u ON u.id = t.assignee_id
    WHERE t.project_id = :project_id AND t.assignee_id IS NOT NULL
    GROUP BY t.assignee_id, u.name
"""
