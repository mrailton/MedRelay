from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.enums import ResourceStatus
from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.db.models.resource import Resource


class ResourceRepository(BaseRepository):
    def get(self, resource_id: int, organisation_id: int | None = None) -> Resource | None:
        from app.db.models.event import Event
        from app.db.models.resource import Resource

        stmt = select(Resource).where(Resource.id == resource_id)
        if organisation_id is not None:
            stmt = stmt.join(Event, Resource.event_id == Event.id).where(Event.organisation_id == organisation_id)
        return self.db.scalars(stmt).first()

    def get_with_event_staff_incidents(self, resource_id: int, organisation_id: int | None = None) -> Resource | None:
        from app.db.models.event import Event
        from app.db.models.resource import Resource

        stmt = select(Resource).where(Resource.id == resource_id)
        if organisation_id is not None:
            stmt = stmt.join(Event, Resource.event_id == Event.id).where(Event.organisation_id == organisation_id)
        stmt = stmt.options(
            joinedload(Resource.event),
            joinedload(Resource.staff),
            joinedload(Resource.incidents),
        )
        return self.db.scalars(stmt).unique().first()

    def get_by_ids_for_event(self, event_id: int, ids: list[int]) -> list[Resource]:
        from app.db.models.resource import Resource

        if not ids:
            return []
        stmt = select(Resource).where(Resource.id.in_(ids), Resource.event_id == event_id)
        return list(self.db.scalars(stmt).all())

    def list_by_event(self, event_id: int, organisation_id: int | None = None) -> list[Resource]:
        from app.db.models.event import Event
        from app.db.models.resource import Resource

        stmt = select(Resource).where(Resource.event_id == event_id)
        if organisation_id is not None:
            stmt = stmt.join(Event, Resource.event_id == Event.id).where(Event.organisation_id == organisation_id)
        stmt = stmt.options(joinedload(Resource.staff)).order_by(Resource.name)
        return list(self.db.scalars(stmt).unique().all())

    def get_by_ids(self, ids: list[int]) -> list[Resource]:
        from app.db.models.resource import Resource

        if not ids:
            return []
        stmt = select(Resource).where(Resource.id.in_(ids))
        return list(self.db.scalars(stmt).all())

    def count_by_event(self, event_id: int, organisation_id: int | None = None) -> int:
        from app.db.models.event import Event
        from app.db.models.resource import Resource

        stmt = select(func.count(Resource.id)).where(Resource.event_id == event_id)
        if organisation_id is not None:
            stmt = stmt.join(Event, Resource.event_id == Event.id).where(Event.organisation_id == organisation_id)
        return self.db.scalar(stmt) or 0

    def count_available_by_event(self, event_id: int, organisation_id: int | None = None) -> int:
        from app.db.models.event import Event
        from app.db.models.resource import Resource

        stmt = select(func.count(Resource.id)).where(
            Resource.event_id == event_id,
            Resource.status == ResourceStatus.AVAILABLE.value,
        )
        if organisation_id is not None:
            stmt = stmt.join(Event, Resource.event_id == Event.id).where(Event.organisation_id == organisation_id)
        return self.db.scalar(stmt) or 0

    def count_deployed_by_event(self, event_id: int, organisation_id: int | None = None) -> int:
        from app.db.models.event import Event
        from app.db.models.resource import Resource

        stmt = select(func.count(Resource.id)).where(
            Resource.event_id == event_id,
            Resource.status.notin_([ResourceStatus.AVAILABLE.value, ResourceStatus.OUT_OF_SERVICE.value]),
        )
        if organisation_id is not None:
            stmt = stmt.join(Event, Resource.event_id == Event.id).where(Event.organisation_id == organisation_id)
        return self.db.scalar(stmt) or 0

    def count_out_of_service_by_event(self, event_id: int, organisation_id: int | None = None) -> int:
        from app.db.models.event import Event
        from app.db.models.resource import Resource

        stmt = select(func.count(Resource.id)).where(
            Resource.event_id == event_id,
            Resource.status == ResourceStatus.OUT_OF_SERVICE.value,
        )
        if organisation_id is not None:
            stmt = stmt.join(Event, Resource.event_id == Event.id).where(Event.organisation_id == organisation_id)
        return self.db.scalar(stmt) or 0

    def bulk_update_status(self, ids: list[int], status: ResourceStatus) -> None:
        from app.db.models.resource import Resource

        self.db.query(Resource).filter(Resource.id.in_(ids)).update({"status": status.value}, synchronize_session=False)

    def create(self, **data: object) -> Resource:
        from app.db.models.resource import Resource

        resource = Resource(**data)
        self.db.add(resource)
        self.db.flush()
        return resource
