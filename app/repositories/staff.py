from __future__ import annotations

from typing import TYPE_CHECKING

from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.db.models.staff import Staff


class StaffRepository(BaseRepository):
    def get(self, staff_id: int, organisation_id: int | None = None) -> Staff | None:
        from app.db.models.staff import Staff

        q = self.db.query(Staff)
        if organisation_id is not None:
            q = q.filter(Staff.organisation_id == organisation_id)
        return q.filter(Staff.id == staff_id).first()

    def list_all(self, organisation_id: int | None = None) -> list[Staff]:
        from app.db.models.staff import Staff

        q = self.db.query(Staff)
        if organisation_id is not None:
            q = q.filter(Staff.organisation_id == organisation_id)
        return q.order_by(Staff.last_name, Staff.first_name).all()

    def list_all_by_last_name(self, organisation_id: int | None = None) -> list[Staff]:
        from app.db.models.staff import Staff

        q = self.db.query(Staff)
        if organisation_id is not None:
            q = q.filter(Staff.organisation_id == organisation_id)
        return q.order_by(Staff.last_name).all()

    def list_by_ids(self, ids: list[int], organisation_id: int | None = None) -> list[Staff]:
        from app.db.models.staff import Staff

        q = self.db.query(Staff).filter(Staff.id.in_(ids))
        if organisation_id is not None:
            q = q.filter(Staff.organisation_id == organisation_id)
        return q.all()

    def create(self, **data: object) -> Staff:
        from app.db.models.staff import Staff

        staff = Staff(**data)
        self.db.add(staff)
        self.db.flush()
        return staff
