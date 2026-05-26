from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from medrelay.db.models.user import User
from medrelay.db.session import get_db
from medrelay.dependencies import CurrentUser, get_csrf_token, require_guest, verify_csrf
from medrelay.security import verify_password
from medrelay.templating import render

router = APIRouter(tags=["auth"])


@router.api_route("/login", methods=["GET", "POST"], name="login")
def login(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_guest),
    email: str | None = Form(None),
    password: str | None = Form(None),
    remember: bool = Form(False),
    csrf_token: str | None = Form(None),
):
    if request.method == "GET":
        return render(request, "auth/login.html", {"errors": {}})

    verify_csrf(request, csrf_token)
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password or "", user.password):
        return render(
            request,
            "auth/login.html",
            {"errors": {"email": "The provided credentials do not match our records."}, "email": email},
        )

    request.session.clear()
    request.session["user_id"] = user.id
    get_csrf_token(request)
    return RedirectResponse(url="/", status_code=303)


@router.post("/logout", name="logout")
def logout(request: Request, user: CurrentUser, csrf_token: str | None = Form(None)):
    verify_csrf(request, csrf_token)
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
