from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import select, update

from app.db.models.user_organisation import user_organisation
from app.enums import UserRole
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

    def get_default(self) -> Organisation | None:
        from app.db.models.organisation import Organisation

        return self.db.query(Organisation).filter(Organisation.code == "default").first()

    def create(self, code: str, name: str) -> Organisation:
        from app.db.models.organisation import Organisation

        org = Organisation(code=code, name=name, created_at=datetime.now(UTC), updated_at=datetime.now(UTC))
        self.db.add(org)
        self.db.flush()
        return org

    def update(self, organisation_id: int, code: str, name: str) -> Organisation | None:
        from app.db.models.organisation import Organisation

        org = self.db.get(Organisation, organisation_id)
        if not org:
            return None
        org.code = code
        org.name = name
        org.updated_at = datetime.now(UTC)
        self.db.flush()
        return org

    def does_user_belong(self, user_id: int, organisation_id: int) -> bool:
        from app.db.models.user import User

        user = self.db.get(User, user_id)
        if not user:
            return False
        return any(o.id == organisation_id for o in user.organisations)

    def add_user(self, user_id: int, organisation_id: int, role: str = UserRole.CONTROLLER.value) -> None:
        stmt = user_organisation.insert().values(
            user_id=user_id,
            organisation_id=organisation_id,
            role=role,
            created_at=datetime.now(UTC),
        )
        self.db.execute(stmt)
        self.db.flush()

    def get_user_role(self, user_id: int, organisation_id: int) -> str | None:
        result = self.db.execute(
            select(user_organisation.c.role).where(
                user_organisation.c.user_id == user_id,
                user_organisation.c.organisation_id == organisation_id,
            )
        ).scalar()
        return result

    def set_user_role(self, user_id: int, organisation_id: int, role: str) -> None:
        stmt = (
            update(user_organisation)
            .where(
                user_organisation.c.user_id == user_id,
                user_organisation.c.organisation_id == organisation_id,
            )
            .values(role=role)
        )
        self.db.execute(stmt)
        self.db.flush()
