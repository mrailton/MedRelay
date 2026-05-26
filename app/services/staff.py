from datetime import UTC, datetime

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.db.models.staff import Staff
from app.db.models.user import User
from app.services.audit import write_audit_log


def create_staff(
    db: Session, data: dict, user: User, request: Request | None = None
) -> Staff:
    staff = Staff(
        first_name=data["first_name"],
        last_name=data["last_name"],
        clinical_level=data["clinical_level"],
        notes=data.get("notes"),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(staff)
    db.flush()
    write_audit_log(
        db,
        action="staff.created",
        entity_type="staff",
        entity_id=str(staff.id),
        after={
            "id": staff.id,
            "first_name": staff.first_name,
            "last_name": staff.last_name,
            "clinical_level": staff.clinical_level,
        },
        user=user,
        request=request,
    )
    return staff
