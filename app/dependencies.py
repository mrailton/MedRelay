from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.enums import UserRole
from app.repositories import User
from app.repositories.session import get_db
from app.repositories.user import UserRepository


class LoginRequired(Exception):
    pass


DbSession = Annotated[Session, Depends(get_db)]


def get_session_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return UserRepository(db).get(user_id)


def require_auth(user: User | None = Depends(get_session_user)) -> User:
    if user is None:
        raise LoginRequired()
    return user

def get_current_organisation_id(request: Request) -> int | None:
    return request.session.get("organisation_id")


def require_guest(
    user: User | None = Depends(get_session_user),
    org_id: int | None = Depends(get_current_organisation_id),
) -> None:
    if user is not None and org_id is not None:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/"},
        )


def require_admin(user: User = Depends(require_auth)) -> User:
    if not user.is_admin():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


def require_controller(user: User = Depends(require_auth)) -> User:
    if user.user_role == UserRole.READ_ONLY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


CurrentUser = Annotated[User, Depends(require_auth)]
ControllerUser = Annotated[User, Depends(require_controller)]
AdminUser = Annotated[User, Depends(require_admin)]



def require_organisation(org_id: int | None = Depends(get_current_organisation_id)) -> int:
    if org_id is None:
        raise LoginRequired()
    return org_id


CurrentOrg = Annotated[int, Depends(require_organisation)]


def get_current_organisation_code(request: Request) -> str | None:
    return request.session.get("organisation_code")


CurrentOrgCode = Annotated[str | None, Depends(get_current_organisation_code)]


def get_csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token


def verify_csrf(request: Request, token: str | None) -> None:
    session_token = request.session.get("csrf_token")
    if not session_token or not token or token != session_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token mismatch")
