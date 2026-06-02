"""Add multi-tenant organisations support"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organisations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "user_organisation",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("organisation_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organisation_id"], ["organisations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "organisation_id"),
    )

    # Seed a default organisation for existing data
    op.execute("INSERT INTO organisations (code, name, created_at, updated_at) VALUES ('default', 'Default Organisation', NOW(), NOW())")

    # Add organisation_id to events
    op.add_column("events", sa.Column("organisation_id", sa.Integer(), nullable=True))
    op.execute("UPDATE events SET organisation_id = (SELECT id FROM organisations WHERE code = 'default')")
    op.alter_column("events", "organisation_id", existing_type=sa.Integer(), nullable=False)
    op.create_foreign_key("fk_events_organisation", "events", "organisations", ["organisation_id"], ["id"], ondelete="CASCADE")

    # Add organisation_id to staff
    op.add_column("staff", sa.Column("organisation_id", sa.Integer(), nullable=True))
    op.execute("UPDATE staff SET organisation_id = (SELECT id FROM organisations WHERE code = 'default')")
    op.alter_column("staff", "organisation_id", existing_type=sa.Integer(), nullable=False)
    op.create_foreign_key("fk_staff_organisation", "staff", "organisations", ["organisation_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint("fk_staff_organisation", "staff", type_="foreignkey")
    op.drop_column("staff", "organisation_id")
    op.drop_constraint("fk_events_organisation", "events", type_="foreignkey")
    op.drop_column("events", "organisation_id")
    op.drop_table("user_organisation")
    op.drop_table("organisations")
