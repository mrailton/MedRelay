from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func

from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.db.models.audit_log import AuditLog


class AuditLogRepository(BaseRepository):
    def list_by_entity(self, entity_type: str, entity_id: str) -> list[AuditLog]:
        from app.db.models.audit_log import AuditLog

        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
            .order_by(AuditLog.created_at.desc())
            .all()
        )

    def list_paginated(self, page: int, per_page: int, organisation_id: int) -> list[AuditLog]:
        from app.db.models.audit_log import AuditLog

        return (
            self.db.query(AuditLog)
            .filter(AuditLog.organisation_id == organisation_id)
            .order_by(AuditLog.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

    def count_for_organisation(self, organisation_id: int) -> int:
        from app.db.models.audit_log import AuditLog

        return self.db.query(func.count(AuditLog.id)).filter(AuditLog.organisation_id == organisation_id).scalar() or 0

    def create(self, **data: object) -> AuditLog:
        from app.db.models.audit_log import AuditLog

        log = AuditLog(**data)
        self.db.add(log)
        self.db.flush()
        return log
