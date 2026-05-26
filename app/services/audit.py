from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.repositories import User
from app.repositories.audit_log import AuditLogRepository


def write_audit_log(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: str,
    before: dict | None = None,
    after: dict | None = None,
    user: User | None = None,
    request: Request | None = None,
) -> None:
    repo = AuditLogRepository(db)
    repo.create(
        user_id=user.id if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before=before,
        after=after,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
        created_at=datetime.now(UTC),
    )


def list_audit_logs_for_entity(db: Session, entity_type: str, entity_id: str) -> list:
    return AuditLogRepository(db).list_by_entity(entity_type, entity_id)


def list_audit_logs_paginated(db: Session, page: int = 1, per_page: int = 50) -> list:
    return AuditLogRepository(db).list_paginated(page, per_page)


def count_audit_logs(db: Session) -> int:
    return AuditLogRepository(db).count_all()
