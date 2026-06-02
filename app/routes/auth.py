from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.dependencies import CurrentUser, DbSession, get_csrf_token, require_guest, verify_csrf
from app.repositories.organisation import OrganisationRepository
from app.repositories.user import UserRepository
from app.schemas.forms import LoginForm, LogoutForm, login_form, logout_form
from app.security import verify_password
from app.templating import render

router = APIRouter(tags=["auth"])


@router.api_route("/login", methods=["GET", "POST"], name="login")
def login(
    request: Request,
    db: DbSession,
    _: None = Depends(require_guest),
    form: LoginForm = Depends(login_form),
):
    if request.method == "GET":
        return render(request, "auth/login.html", {"errors": {}})

    verify_csrf(request, form.csrf_token)

    org = OrganisationRepository(db).get_by_code(form.organisation_code_normalized)
    if not org:
        return render(
            request,
            "auth/login.html",
            {
                "errors": {"organisation_code": "Invalid organisation code."},
                "email": form.email,
                "organisation_code": form.organisation_code,
            },
        )

    user = UserRepository(db).get_by_email_and_organisation(form.email or "", org.id)
    if not user or not verify_password(form.password or "", user.password):
        return render(
            request,
            "auth/login.html",
            {
                "errors": {"email": "The provided credentials do not match our records."},
                "email": form.email,
                "organisation_code": form.organisation_code,
            },
        )

    request.session.clear()
    request.session["user_id"] = user.id
    request.session["organisation_id"] = org.id
    request.session["organisation_code"] = org.code
    if form.remember:
        request.session["remember_me"] = True
    get_csrf_token(request)
    return RedirectResponse(url="/", status_code=303)


@router.post("/logout", name="logout")
def logout(request: Request, user: CurrentUser, form: LogoutForm = Depends(logout_form)):
    verify_csrf(request, form.csrf_token)
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
