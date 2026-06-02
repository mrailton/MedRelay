from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    def is_admin(self) -> bool:
        return self.user_role == UserRole.ADMIN

    def is_controller(self) -> bool:
        return self.user_role == UserRole.CONTROLLER

    def is_read_only(self) -> bool:
        return self.user_role == UserRole.READ_ONLY
