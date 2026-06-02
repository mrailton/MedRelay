from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.enums import IncidentStatus
from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.db.models.incident import Incident


class IncidentRepository(BaseRepository):
    def get(self, incident_id: int, organisation_id: int | None = None) -> Incident | None:
        from app.db.models.event import Event
        from app.db.models.incident import Incident

        stmt = select(Incident).where(Incident.id == incident_id)
        if organisation_id is not None:
            stmt = stmt.join(Event, Incident.event_id == Event.id).where(Event.organisation_id == organisation_id)
        return self.db.scalars(stmt).first()

    def get_for_update(self, incident_id: int, organisation_id: int | None = None) -> Incident | None:
        from app.db.models.event import Event
        from app.db.models.incident import Incident
        from app.db.models.incident_note import IncidentNote

        stmt = select(Incident).where(Incident.id == incident_id)
        if organisation_id is not None:
            stmt = stmt.join(Event, Incident.event_id == Event.id).where(Event.organisation_id == organisation_id)
        stmt = stmt.options(
            joinedload(Incident.event),
            joinedload(Incident.resources),
            joinedload(Incident.notes).joinedload(IncidentNote.user),
        ).with_for_update()
        return self.db.scalars(stmt).unique().first()

    def get_with_event_resources_notes(self, incident_id: int, organisation_id: int | None = None) -> Incident | None:
        from app.db.models.event import Event
        from app.db.models.incident import Incident
        from app.db.models.incident_note import IncidentNote

        stmt = select(Incident).where(Incident.id == incident_id)
        if organisation_id is not None:
            stmt = stmt.join(Event, Incident.event_id == Event.id).where(Event.organisation_id == organisation_id)
        stmt = stmt.options(
            joinedload(Incident.event),
            joinedload(Incident.resources),
            joinedload(Incident.notes).joinedload(IncidentNote.user),
        )
        return self.db.scalars(stmt).unique().first()

    def list_by_event(self, event_id: int, organisation_id: int | None = None) -> list[Incident]:
        from app.db.models.event import Event
        from app.db.models.incident import Incident

        stmt = select(Incident).where(Incident.event_id == event_id)
        if organisation_id is not None:
            stmt = stmt.join(Event, Incident.event_id == Event.id).where(Event.organisation_id == organisation_id)
        stmt = stmt.options(joinedload(Incident.resources)).order_by(Incident.created_at.desc())
        return list(self.db.scalars(stmt).unique().all())

    def count_by_event(self, event_id: int, organisation_id: int | None = None) -> int:
        from app.db.models.event import Event
        from app.db.models.incident import Incident

        stmt = select(func.count(Incident.id)).where(Incident.event_id == event_id)
        if organisation_id is not None:
            stmt = stmt.join(Event, Incident.event_id == Event.id).where(Event.organisation_id == organisation_id)
        return self.db.scalar(stmt) or 0

    def count_active_by_event(self, event_id: int, organisation_id: int | None = None) -> int:
        from app.db.models.event import Event
        from app.db.models.incident import Incident

        stmt = select(func.count(Incident.id)).where(
            Incident.event_id == event_id,
            Incident.status.notin_([IncidentStatus.COMPLETE.value, IncidentStatus.CANCELLED.value]),
        )
        if organisation_id is not None:
            stmt = stmt.join(Event, Incident.event_id == Event.id).where(Event.organisation_id == organisation_id)
        return self.db.scalar(stmt) or 0

    def get_next_reference(self, event_id: int) -> str:
        from app.db.models.event import Event
        from app.db.models.incident import Incident

        # Serialize reference allocation per event under concurrent creates.
        self.db.scalars(select(Event).where(Event.id == event_id).with_for_update()).first()
        max_ref = self.db.scalar(select(func.max(Incident.reference)).where(Incident.event_id == event_id))
        seq = (int(max_ref[-5:]) + 1) if max_ref else 1
        return f"{event_id}{seq:05d}"

    def create(self, **data: object) -> Incident:
        from app.db.models.incident import Incident

        incident = Incident(**data)
        self.db.add(incident)
        self.db.flush()
        return incident
