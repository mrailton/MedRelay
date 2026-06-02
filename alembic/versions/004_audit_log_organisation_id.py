"""Add organisation_id to audit_logs for tenant scoping."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004_audit_log_organisation_id"
down_revision: str | None = "003_add_org_role"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("audit_logs", sa.Column("organisation_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_audit_logs_organisation_id",
        "audit_logs",
        "organisations",
        ["organisation_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_audit_logs_organisation_id", "audit_logs", ["organisation_id"])

    # Best-effort backfill from related entities
    op.execute(
        """
        UPDATE audit_logs SET organisation_id = (
            SELECT organisation_id FROM events
            WHERE audit_logs.entity_type = 'event' AND events.id = CAST(audit_logs.entity_id AS INTEGER)
        ) WHERE entity_type = 'event' AND organisation_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE audit_logs SET organisation_id = (
            SELECT events.organisation_id FROM incidents
            JOIN events ON incidents.event_id = events.id
            WHERE audit_logs.entity_type = 'incident' AND incidents.id = CAST(audit_logs.entity_id AS INTEGER)
        ) WHERE entity_type = 'incident' AND organisation_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE audit_logs SET organisation_id = (
            SELECT events.organisation_id FROM resources
            JOIN events ON resources.event_id = events.id
            WHERE audit_logs.entity_type = 'resource' AND resources.id = CAST(audit_logs.entity_id AS INTEGER)
        ) WHERE entity_type = 'resource' AND organisation_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE audit_logs SET organisation_id = (
            SELECT organisation_id FROM staff
            WHERE audit_logs.entity_type = 'staff' AND staff.id = CAST(audit_logs.entity_id AS INTEGER)
        ) WHERE entity_type = 'staff' AND organisation_id IS NULL
        """
    )


def downgrade() -> None:
    op.drop_index("ix_audit_logs_organisation_id", table_name="audit_logs")
    op.drop_constraint("fk_audit_logs_organisation_id", "audit_logs", type_="foreignkey")
    op.drop_column("audit_logs", "organisation_id")
