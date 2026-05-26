from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from medrelay.db.base import Base
from medrelay.enums import UserRole


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

    @property
    def user_role(self) -> UserRole:
        return UserRole(self.role)

    def is_admin(self) -> bool:
        return self.user_role == UserRole.ADMIN

    def is_controller(self) -> bool:
        return self.user_role == UserRole.CONTROLLER

    def is_read_only(self) -> bool:
        return self.user_role == UserRole.READ_ONLY
