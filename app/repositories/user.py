from __future__ import annotations

from typing import TYPE_CHECKING

from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.db.models.user import User


class UserRepository(BaseRepository):
    def get(self, user_id: int) -> User | None:
        from app.db.models.user import User

        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        from app.db.models.user import User

        return self.db.query(User).filter(User.email == email).first()

    def list_all(self) -> list[User]:
        from app.db.models.user import User

        return self.db.query(User).order_by(User.name).all()

    def create(self, **data: object) -> User:
        from app.db.models.user import User

        user = User(**data)
        self.db.add(user)
        self.db.flush()
        return user

    def email_exists(self, email: str) -> bool:
        from app.db.models.user import User

        return self.db.query(User).filter(User.email == email).first() is not None
