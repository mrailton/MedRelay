"""Add role column to user_organisation for per-org access levels"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("user_organisation", sa.Column("role", sa.String(20), nullable=True))
    op.execute(
        "UPDATE user_organisation uo "
        "JOIN users u ON uo.user_id = u.id "
        "SET uo.role = u.role"
    )
    op.alter_column("user_organisation", "role", existing_type=sa.String(20), nullable=False)


def downgrade() -> None:
    op.drop_column("user_organisation", "role")
