from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.db.models.event import Event


class EventRepository(BaseRepository):
    def get(self, event_id: int, organisation_id: int | None = None) -> Event | None:
        from app.db.models.event import Event

        stmt = select(Event).where(Event.id == event_id)
        if organisation_id is not None:
            stmt = stmt.where(Event.organisation_id == organisation_id)
        return self.db.scalars(stmt).first()

    def list_all(self, organisation_id: int | None = None) -> list[Event]:
        from app.db.models.event import Event

        stmt = select(Event)
        if organisation_id is not None:
            stmt = stmt.where(Event.organisation_id == organisation_id)
        stmt = stmt.order_by(Event.start_time.desc())
        return list(self.db.scalars(stmt).all())

    def list_active(self, organisation_id: int | None = None) -> list[Event]:
        from app.db.models.event import Event

        stmt = select(Event).where(Event.is_active.is_(True))
        if organisation_id is not None:
            stmt = stmt.where(Event.organisation_id == organisation_id)
        stmt = stmt.order_by(Event.name)
        return list(self.db.scalars(stmt).all())

    def create(self, **data: object) -> Event:
        from app.db.models.event import Event

        event = Event(**data)
        self.db.add(event)
        self.db.flush()
        return event
