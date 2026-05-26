from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.repositories import User
from app.repositories.user import UserRepository
from app.security import hash_password


def create_user(db: Session, data: dict, actor: User, request: Request | None = None) -> User:
    repo = UserRepository(db)
    user = repo.create(
        name=data["name"],
        email=data["email"],
        password=hash_password(data["password"]),
        role=data["role"],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    from app.services.audit import write_audit_log

    write_audit_log(
        db,
        action="user.created",
        entity_type="user",
        entity_id=str(user.id),
        after={"id": user.id, "name": user.name, "email": user.email, "role": user.role},
        user=actor,
        request=request,
    )
    return user


def list_users(db: Session) -> list[User]:
    return UserRepository(db).list_all()


def get_user_by_email(db: Session, email: str) -> User | None:
    return UserRepository(db).get_by_email(email)
