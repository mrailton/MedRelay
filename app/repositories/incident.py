from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.enums import IncidentStatus
from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.db.models.incident import Incident


class IncidentRepository(BaseRepository):
    def get(self, incident_id: int) -> Incident | None:
        from app.db.models.incident import Incident

        return self.db.get(Incident, incident_id)

    def get_with_event_resources_notes(self, incident_id: int) -> Incident | None:
        from app.db.models.incident import Incident
        from app.db.models.incident_note import IncidentNote

        return (
            self.db.query(Incident)
            .filter(Incident.id == incident_id)
            .options(
                joinedload(Incident.event),
                joinedload(Incident.resources),
                joinedload(Incident.notes).joinedload(IncidentNote.user),
            )
            .first()
        )

    def list_by_event(self, event_id: int) -> list[Incident]:
        from app.db.models.incident import Incident

        return self.db.query(Incident).filter(Incident.event_id == event_id).options(joinedload(Incident.resources)).order_by(Incident.created_at.desc()).all()

    def count_by_event(self, event_id: int) -> int:
        from app.db.models.incident import Incident

        return self.db.query(func.count(Incident.id)).filter(Incident.event_id == event_id).scalar() or 0

    def count_active_by_event(self, event_id: int) -> int:
        from app.db.models.incident import Incident

        return (
            self.db.query(func.count(Incident.id))
            .filter(
                Incident.event_id == event_id,
                Incident.status.notin_([IncidentStatus.COMPLETE.value, IncidentStatus.CANCELLED.value]),
            )
            .scalar()
            or 0
        )

    def get_next_reference(self, event_id: int) -> str:
        from app.db.models.incident import Incident

        max_ref = (
            self.db.query(func.max(Incident.reference))
            .filter(Incident.event_id == event_id)
            .scalar()
        )
        seq = (int(max_ref[-5:]) + 1) if max_ref else 1
        return f"{event_id}{seq:05d}"

    def create(self, **data: object) -> Incident:
        from app.db.models.incident import Incident

        incident = Incident(**data)
        self.db.add(incident)
        self.db.flush()
        return incident
