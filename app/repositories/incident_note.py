from __future__ import annotations

from typing import TYPE_CHECKING

from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.db.models.incident_note import IncidentNote


class IncidentNoteRepository(BaseRepository):
    def create(self, **data: object) -> IncidentNote:
        from app.db.models.incident_note import IncidentNote

        note = IncidentNote(**data)
        self.db.add(note)
        self.db.flush()
        return note
