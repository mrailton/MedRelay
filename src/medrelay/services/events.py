from datetime import UTC, datetime

from sqlalchemy.orm import Session
from starlette.requests import Request

from medrelay.db.models.event import Event
from medrelay.db.models.user import User
from medrelay.services.audit import write_audit_log


def create_event(db: Session, data: dict, user: User, request: Request | None = None) -> Event:
    event = Event(
        name=data["name"],
        location=data["location"],
        start_time=data["start_time"],
        end_time=data.get("end_time"),
        is_active=data.get("is_active", False),
        notes=data.get("notes"),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(event)
    db.flush()
    write_audit_log(
        db,
        action="event.created",
        entity_type="event",
        entity_id=str(event.id),
        after={
            "id": event.id,
            "name": event.name,
            "location": event.location,
            "is_active": event.is_active,
        },
        user=user,
        request=request,
    )
    return event


def update_event(
    db: Session, event: Event, data: dict, user: User, request: Request | None = None
) -> Event:
    before = {
        "id": event.id,
        "name": event.name,
        "location": event.location,
        "is_active": event.is_active,
    }
    for key in ("name", "location", "start_time", "end_time", "is_active", "notes"):
        if key in data and data[key] is not None:
            setattr(event, key, data[key])
    event.updated_at = datetime.now(UTC)
    db.flush()
    write_audit_log(
        db,
        action="event.updated",
        entity_type="event",
        entity_id=str(event.id),
        before=before,
        after={
            "id": event.id,
            "name": event.name,
            "location": event.location,
            "is_active": event.is_active,
        },
        user=user,
        request=request,
    )
    return event
