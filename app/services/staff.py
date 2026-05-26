from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.repositories import Staff, User
from app.repositories.staff import StaffRepository


def create_staff(db: Session, data: dict, user: User, request: Request | None = None) -> Staff:
    repo = StaffRepository(db)
    staff = repo.create(
        first_name=data["first_name"],
        last_name=data["last_name"],
        clinical_level=data["clinical_level"],
        notes=data.get("notes"),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    from app.services.audit import write_audit_log

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


def list_staff(db: Session) -> list[Staff]:
    return StaffRepository(db).list_all()


def list_staff_by_last_name(db: Session) -> list[Staff]:
    return StaffRepository(db).list_all_by_last_name()


def get_staff(db: Session, staff_id: int) -> Staff | None:
    return StaffRepository(db).get(staff_id)
