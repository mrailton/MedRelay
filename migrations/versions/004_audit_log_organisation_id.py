"""Add organisation_id to audit_logs for tenant scoping."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "004_audit_log_organisation_id"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _audit_log_column_names() -> set[str]:
    bind = op.get_bind()
    return {col["name"] for col in inspect(bind).get_columns("audit_logs")}


def _audit_log_index_names() -> set[str]:
    bind = op.get_bind()
    return {idx["name"] for idx in inspect(bind).get_indexes("audit_logs")}


def _audit_log_fk_names() -> set[str]:
    bind = op.get_bind()
    return {fk["name"] for fk in inspect(bind).get_foreign_keys("audit_logs") if fk.get("name")}


def upgrade() -> None:
    columns = _audit_log_column_names()
    if "organisation_id" not in columns:
        op.add_column("audit_logs", sa.Column("organisation_id", sa.Integer(), nullable=True))

    if "fk_audit_logs_organisation_id" not in _audit_log_fk_names():
        op.create_foreign_key(
            "fk_audit_logs_organisation_id",
            "audit_logs",
            "organisations",
            ["organisation_id"],
            ["id"],
            ondelete="CASCADE",
        )

    if "ix_audit_logs_organisation_id" not in _audit_log_index_names():
        op.create_index("ix_audit_logs_organisation_id", "audit_logs", ["organisation_id"])

    # Best-effort backfill from related entities (MySQL-compatible JOIN updates)
    op.execute(
        """
        UPDATE audit_logs al
        INNER JOIN events e ON al.entity_type = 'event' AND e.id = CAST(al.entity_id AS UNSIGNED)
        SET al.organisation_id = e.organisation_id
        WHERE al.organisation_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE audit_logs al
        INNER JOIN incidents i ON al.entity_type = 'incident' AND i.id = CAST(al.entity_id AS UNSIGNED)
        INNER JOIN events e ON i.event_id = e.id
        SET al.organisation_id = e.organisation_id
        WHERE al.organisation_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE audit_logs al
        INNER JOIN resources r ON al.entity_type = 'resource' AND r.id = CAST(al.entity_id AS UNSIGNED)
        INNER JOIN events e ON r.event_id = e.id
        SET al.organisation_id = e.organisation_id
        WHERE al.organisation_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE audit_logs al
        INNER JOIN staff s ON al.entity_type = 'staff' AND s.id = CAST(al.entity_id AS UNSIGNED)
        SET al.organisation_id = s.organisation_id
        WHERE al.organisation_id IS NULL
        """
    )


def downgrade() -> None:
    if "ix_audit_logs_organisation_id" in _audit_log_index_names():
        op.drop_index("ix_audit_logs_organisation_id", table_name="audit_logs")
    if "fk_audit_logs_organisation_id" in _audit_log_fk_names():
        op.drop_constraint("fk_audit_logs_organisation_id", "audit_logs", type_="foreignkey")
    if "organisation_id" in _audit_log_column_names():
        op.drop_column("audit_logs", "organisation_id")
