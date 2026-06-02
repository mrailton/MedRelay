from __future__ import annotations

from fastapi import Request

from app.actions import staff as staff_actions
from app.dependencies import CurrentOrg, CurrentUser, DbSession
from app.routes.staff.router import router
from app.services.staff import list_staff
from app.templating import render
from app.web import handle


@router.get("", name="staff.index")
def staff_index(request: Request, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    staff_list = list_staff(db, organisation_id)
    return render(request, "staff/index.html", {"staff_list": staff_list}, user=user)


@router.get("/create", name="staff.create")
def staff_create(request: Request, user: CurrentUser):
    return handle(request, staff_actions.open_create_form(user), user=user)
