from datetime import UTC, datetime

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.db.models.audit_log import AuditLog
from app.db.models.user import User


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
) -> AuditLog:
    log = AuditLog(
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
    db.add(log)
    db.flush()
    return log
