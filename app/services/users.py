from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.enums import UserRole
from app.repositories import User
from app.repositories.organisation import OrganisationRepository
from app.repositories.user import UserRepository
from app.schemas.forms.admin import AdminUserCreateForm
from app.security import hash_password
from app.services.types import CreateUserOutcome


def create_user(
    db: Session,
    data: dict,
    actor: User,
    request: Request | None = None,
    *,
    organisation_id: int | None = None,
) -> User:
    repo = UserRepository(db)
    user = repo.create(
        name=data["name"],
        email=data["email"],
        password=hash_password(data["password"]),
        role=data["role"],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    org_repo = OrganisationRepository(db)
    organisation_ids = data.get("organisation_ids") or []
    org_roles = data.get("org_roles") or {}

    for oid in organisation_ids:
        org = org_repo.get(oid)
        if not org:
            continue
        role = org_roles.get(str(oid), data["role"])
        org_repo.add_user(user.id, oid, role)

    from app.services.audit import write_audit_log

    audit_org_id = organisation_id or (organisation_ids[0] if organisation_ids else None)
    if audit_org_id is not None:
        write_audit_log(
            db,
            action="user.created",
            entity_type="user",
            entity_id=str(user.id),
            organisation_id=audit_org_id,
            after={"id": user.id, "name": user.name, "email": user.email, "role": user.role},
            user=actor,
            request=request,
        )
    return user


def list_users(db: Session) -> list[User]:
    return UserRepository(db).list_all()


def get_user_by_email(db: Session, email: str) -> User | None:
    return UserRepository(db).get_by_email(email)


def get_user_by_email_and_organisation(db: Session, email: str, organisation_id: int) -> User | None:
    return UserRepository(db).get_by_email_and_organisation(email, organisation_id)


def get_admin_user_create_context(db: Session, organisation_id: int) -> dict:
    org = OrganisationRepository(db).get(organisation_id)
    return {
        "roles": UserRole,
        "organisations": [org] if org else [],
    }


def list_users_for_organisation(db: Session, organisation_id: int) -> list[User]:
    return UserRepository(db).list_all_by_organisation(organisation_id)


def create_admin_user(
    db: Session,
    form: AdminUserCreateForm,
    organisation_id: int,
    actor: User,
    request: Request | None = None,
) -> CreateUserOutcome:
    org_ids = form.filtered_organisation_ids(organisation_id)
    if not org_ids:
        return CreateUserOutcome(
            success=False,
            errors={"organisation_ids": "You must assign the user to your organisation."},
        )

    if form.password != form.password_confirmation:
        return CreateUserOutcome(success=False, errors={"password": "Passwords do not match."})

    if len(form.password) < 8:
        return CreateUserOutcome(success=False, errors={"password": "Password must be at least 8 characters."})

    if UserRepository(db).email_exists(form.email):
        return CreateUserOutcome(success=False, errors={"email": "Email already exists."})

    user = create_user(db, form.to_service_dict(org_ids), actor, request, organisation_id=organisation_id)
    return CreateUserOutcome(success=True, user=user)
