from __future__ import annotations

from typing import TYPE_CHECKING

from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.db.models.organisation import Organisation


class OrganisationRepository(BaseRepository):
    def get_by_code(self, code: str) -> Organisation | None:
        from app.db.models.organisation import Organisation

        return self.db.query(Organisation).filter(Organisation.code == code).first()

    def get(self, organisation_id: int) -> Organisation | None:
        from app.db.models.organisation import Organisation

        return self.db.get(Organisation, organisation_id)

    def list_all(self) -> list[Organisation]:
        from app.db.models.organisation import Organisation

        return self.db.query(Organisation).order_by(Organisation.name).all()

    def create(self, code: str, name: str) -> Organisation:
        from datetime import UTC, datetime

        from app.db.models.organisation import Organisation

        org = Organisation(code=code, name=name, created_at=datetime.now(UTC), updated_at=datetime.now(UTC))
        self.db.add(org)
        self.db.flush()
        return org

    def does_user_belong(self, user_id: int, organisation_id: int) -> bool:
        from app.db.models.user import User

        user = self.db.get(User, user_id)
        if not user:
            return False
        return any(o.id == organisation_id for o in user.organisations)
