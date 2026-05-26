from datetime import UTC, datetime

from sqlalchemy.orm import Session
from starlette.requests import Request

from medrelay.db.models.user import User
from medrelay.security import hash_password
from medrelay.services.audit import write_audit_log


def create_user(
    db: Session, data: dict, actor: User, request: Request | None = None
) -> User:
    user = User(
        name=data["name"],
        email=data["email"],
        password=hash_password(data["password"]),
        role=data["role"],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(user)
    db.flush()
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
