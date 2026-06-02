from __future__ import annotations

from typing import TYPE_CHECKING

from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.db.models.event import Event


class EventRepository(BaseRepository):
    def get(self, event_id: int, organisation_id: int | None = None) -> Event | None:
        from app.db.models.event import Event

        q = self.db.query(Event)
        if organisation_id is not None:
            q = q.filter(Event.organisation_id == organisation_id)
        return q.filter(Event.id == event_id).first()

    def list_all(self, organisation_id: int | None = None) -> list[Event]:
        from app.db.models.event import Event

        q = self.db.query(Event)
        if organisation_id is not None:
            q = q.filter(Event.organisation_id == organisation_id)
        return q.order_by(Event.start_time.desc()).all()

    def list_active(self, organisation_id: int | None = None) -> list[Event]:
        from app.db.models.event import Event

        q = self.db.query(Event).filter(Event.is_active.is_(True))
        if organisation_id is not None:
            q = q.filter(Event.organisation_id == organisation_id)
        return q.order_by(Event.name).all()

    def create(self, **data: object) -> Event:
        from app.db.models.event import Event

        event = Event(**data)
        self.db.add(event)
        self.db.flush()
        return event
