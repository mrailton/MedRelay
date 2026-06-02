from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.dependencies import CurrentUser, DbSession, get_csrf_token, require_guest, verify_csrf
from app.schemas.forms import LoginForm, LogoutForm, login_form, logout_form
from app.services.auth import authenticate
from app.services.types import LoginFailure
from app.templating import render
from app.web import handle, redirect_to, render_page, verified_form

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
    result = authenticate(db, form)
    if isinstance(result, LoginFailure):
        return handle(
            request,
            render_page(
                "auth/login.html",
                {
                    "email": result.email,
                    "organisation_code": result.organisation_code,
                },
                errors=result.errors,
                status_code=200,
            ),
        )

    request.session.clear()
    request.session["user_id"] = result.user_id
    request.session["organisation_id"] = result.organisation_id
    request.session["organisation_code"] = result.organisation_code
    if result.remember:
        request.session["remember_me"] = True
    get_csrf_token(request)
    return handle(request, redirect_to("/"))


@router.post("/logout", name="logout")
def logout(request: Request, user: CurrentUser, form: LogoutForm = Depends(verified_form(logout_form))):
    request.session.clear()
    return handle(request, redirect_to("/login"))
