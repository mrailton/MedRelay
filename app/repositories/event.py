from __future__ import annotations

from typing import TYPE_CHECKING

from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.db.models.event import Event


class EventRepository(BaseRepository):
    def get(self, event_id: int) -> Event | None:
        from app.db.models.event import Event

        return self.db.get(Event, event_id)

    def list_all(self) -> list[Event]:
        from app.db.models.event import Event

        return self.db.query(Event).order_by(Event.start_time.desc()).all()

    def list_active(self) -> list[Event]:
        from app.db.models.event import Event

        return self.db.query(Event).filter(Event.is_active.is_(True)).order_by(Event.name).all()

    def create(self, **data: object) -> Event:
        from app.db.models.event import Event

        event = Event(**data)
        self.db.add(event)
        self.db.flush()
        return event
