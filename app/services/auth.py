from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.organisation import OrganisationRepository
from app.repositories.user import UserRepository
from app.schemas.forms.auth import LoginForm
from app.security import verify_password
from app.services.types import AuthenticatedUser, LoginFailure


def authenticate(db: Session, form: LoginForm) -> AuthenticatedUser | LoginFailure:
    org = OrganisationRepository(db).get_by_code(form.organisation_code_normalized)
    if not org:
        return LoginFailure(
            errors={"organisation_code": "Invalid organisation code."},
            email=form.email,
            organisation_code=form.organisation_code,
        )

    user = UserRepository(db).get_by_email_and_organisation(form.email or "", org.id)
    if not user or not verify_password(form.password or "", user.password):
        return LoginFailure(
            errors={"email": "The provided credentials do not match our records."},
            email=form.email,
            organisation_code=form.organisation_code,
        )

    return AuthenticatedUser(
        user_id=user.id,
        organisation_id=org.id,
        organisation_code=org.code,
        remember=form.remember,
    )
