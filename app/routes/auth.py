from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import CurrentUser, get_csrf_token, require_guest, verify_csrf
from app.repositories.organisation import OrganisationRepository
from app.repositories.session import get_db
from app.repositories.user import UserRepository
from app.security import verify_password
from app.templating import render

if TYPE_CHECKING:
    pass

router = APIRouter(tags=["auth"])


@router.api_route("/login", methods=["GET", "POST"], name="login")
def login(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_guest),
    organisation_code: str | None = Form(None),
    email: str | None = Form(None),
    password: str | None = Form(None),
    remember: bool = Form(False),
    csrf_token: str | None = Form(None),
):
    if request.method == "GET":
        return render(request, "auth/login.html", {"errors": {}})

    verify_csrf(request, csrf_token)

    org = OrganisationRepository(db).get_by_code((organisation_code or "").strip())
    if not org:
        return render(
            request,
            "auth/login.html",
            {"errors": {"organisation_code": "Invalid organisation code."}, "email": email, "organisation_code": organisation_code},
        )

    user = UserRepository(db).get_by_email_and_organisation(email or "", org.id)
    if not user or not verify_password(password or "", user.password):
        return render(
            request,
            "auth/login.html",
            {"errors": {"email": "The provided credentials do not match our records."}, "email": email, "organisation_code": organisation_code},
        )

    request.session.clear()
    request.session["user_id"] = user.id
    request.session["organisation_id"] = org.id
    request.session["organisation_code"] = org.code
    get_csrf_token(request)
    return RedirectResponse(url="/", status_code=303)


@router.post("/logout", name="logout")
def logout(request: Request, user: CurrentUser, csrf_token: str | None = Form(None)):
    verify_csrf(request, csrf_token)
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
