from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.repositories import Event, User
from app.repositories.event import EventRepository


def create_event(db: Session, data: dict, user: User, request: Request | None = None) -> Event:
    repo = EventRepository(db)
    event = repo.create(
        name=data["name"],
        location=data["location"],
        start_time=data["start_time"],
        end_time=data.get("end_time"),
        is_active=data.get("is_active", False),
        notes=data.get("notes"),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    from app.services.audit import write_audit_log

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


def update_event(db: Session, event: Event, data: dict, user: User, request: Request | None = None) -> Event:
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
    from app.services.audit import write_audit_log

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


def get_event(db: Session, event_id: int) -> Event | None:
    return EventRepository(db).get(event_id)


def list_events(db: Session) -> list[Event]:
    return EventRepository(db).list_all()


def list_active_events(db: Session) -> list[Event]:
    return EventRepository(db).list_active()
