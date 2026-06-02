from __future__ import annotations

from app import policies
from app.repositories import User
from app.web.responses import ActionResult, redirect_to, render_page


def open_create_form(user: User) -> ActionResult:
    if not policies.can_create_staff(user):
        return redirect_to("/staff")
    return render_page("staff/create.html", {})
