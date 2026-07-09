"""Add user_role enum and role column to users

Revision ID: 002_add_user_role
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_add_user_role"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role = sa.Enum("admin", "member", name="user_role")
    user_role.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "users",
        sa.Column("role", user_role, nullable=False, server_default="member"),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
