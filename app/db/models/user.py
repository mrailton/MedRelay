from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.db.base import Base
from app.db.models.user_organisation import user_organisation
from app.enums import UserRole

if TYPE_CHECKING:
    from app.db.models.organisation import Organisation


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default=UserRole.CONTROLLER.value)
    remember_token: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    organisations: Mapped[list[Organisation]] = relationship(secondary=user_organisation, back_populates="users")

    @property
    def user_role(self) -> UserRole:
        return UserRole(self.role)

    def is_admin(self, organisation_id: int | None = None) -> bool:
        if organisation_id is None:
            return self.user_role == UserRole.ADMIN
        return self._get_org_role(organisation_id) == UserRole.ADMIN

    def is_controller(self, organisation_id: int | None = None) -> bool:
        if organisation_id is None:
            return self.user_role == UserRole.CONTROLLER
        return self._get_org_role(organisation_id) == UserRole.CONTROLLER

    def is_read_only(self, organisation_id: int | None = None) -> bool:
        if organisation_id is None:
            return self.user_role == UserRole.READ_ONLY
        return self._get_org_role(organisation_id) == UserRole.READ_ONLY

    def get_role(self, organisation_id: int) -> UserRole:
        return self._get_org_role(organisation_id)

    def _get_org_role(self, organisation_id: int) -> UserRole:
        from sqlalchemy import select

        db = Session.object_session(self)
        if db is None:
            return self.user_role
        result = db.execute(
            select(user_organisation.c.role).where(
                user_organisation.c.user_id == self.id,
                user_organisation.c.organisation_id == organisation_id,
            )
        ).scalar()
        return UserRole(result) if result else self.user_role
