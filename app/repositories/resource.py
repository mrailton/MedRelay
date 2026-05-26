from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.enums import ResourceStatus
from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.db.models.resource import Resource


class ResourceRepository(BaseRepository):
    def get(self, resource_id: int) -> Resource | None:
        from app.db.models.resource import Resource

        return self.db.get(Resource, resource_id)

    def get_with_event_staff_incidents(self, resource_id: int) -> Resource | None:
        from app.db.models.resource import Resource

        return (
            self.db.query(Resource)
            .filter(Resource.id == resource_id)
            .options(
                joinedload(Resource.event),
                joinedload(Resource.staff),
                joinedload(Resource.incidents),
            )
            .first()
        )

    def list_by_event(self, event_id: int) -> list[Resource]:
        from app.db.models.resource import Resource

        return self.db.query(Resource).filter(Resource.event_id == event_id).options(joinedload(Resource.staff)).order_by(Resource.name).all()

    def get_by_ids(self, ids: list[int]) -> list[Resource]:
        from app.db.models.resource import Resource

        return self.db.query(Resource).filter(Resource.id.in_(ids)).all()

    def count_by_event(self, event_id: int) -> int:
        from app.db.models.resource import Resource

        return self.db.query(func.count(Resource.id)).filter(Resource.event_id == event_id).scalar() or 0

    def count_available_by_event(self, event_id: int) -> int:
        from app.db.models.resource import Resource

        return (
            self.db.query(func.count(Resource.id))
            .filter(
                Resource.event_id == event_id,
                Resource.status == ResourceStatus.AVAILABLE.value,
            )
            .scalar()
            or 0
        )

    def count_deployed_by_event(self, event_id: int) -> int:
        from app.db.models.resource import Resource

        return (
            self.db.query(func.count(Resource.id))
            .filter(
                Resource.event_id == event_id,
                Resource.status.notin_([ResourceStatus.AVAILABLE.value, ResourceStatus.OUT_OF_SERVICE.value]),
            )
            .scalar()
            or 0
        )

    def count_out_of_service_by_event(self, event_id: int) -> int:
        from app.db.models.resource import Resource

        return (
            self.db.query(func.count(Resource.id))
            .filter(
                Resource.event_id == event_id,
                Resource.status == ResourceStatus.OUT_OF_SERVICE.value,
            )
            .scalar()
            or 0
        )

    def bulk_update_status(self, ids: list[int], status: ResourceStatus) -> None:
        from app.db.models.resource import Resource

        self.db.query(Resource).filter(Resource.id.in_(ids)).update({"status": status.value}, synchronize_session=False)

    def create(self, **data: object) -> Resource:
        from app.db.models.resource import Resource

        resource = Resource(**data)
        self.db.add(resource)
        self.db.flush()
        return resource
