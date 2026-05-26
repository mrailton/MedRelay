from __future__ import annotations

from typing import TYPE_CHECKING

from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.db.models.staff import Staff


class StaffRepository(BaseRepository):
    def get(self, staff_id: int) -> Staff | None:
        from app.db.models.staff import Staff

        return self.db.get(Staff, staff_id)

    def list_all(self) -> list[Staff]:
        from app.db.models.staff import Staff

        return self.db.query(Staff).order_by(Staff.last_name, Staff.first_name).all()

    def list_all_by_last_name(self) -> list[Staff]:
        from app.db.models.staff import Staff

        return self.db.query(Staff).order_by(Staff.last_name).all()

    def list_by_ids(self, ids: list[int]) -> list[Staff]:
        from app.db.models.staff import Staff

        return self.db.query(Staff).filter(Staff.id.in_(ids)).all()

    def create(self, **data: object) -> Staff:
        from app.db.models.staff import Staff

        staff = Staff(**data)
        self.db.add(staff)
        self.db.flush()
        return staff
