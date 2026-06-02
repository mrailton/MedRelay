from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app import policies
from app.dependencies import ControllerUser, CurrentOrg, CurrentUser, DbSession, verify_csrf
from app.schemas.forms import StaffCreateForm, staff_create_form
from app.services.staff import create_staff, list_staff
from app.templating import render

router = APIRouter(prefix="/staff", tags=["staff"])


@router.get("", name="staff.index")
def staff_index(request: Request, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    staff_list = list_staff(db, organisation_id)
    return render(request, "staff/index.html", {"staff_list": staff_list}, user=user)


@router.get("/create", name="staff.create")
def staff_create(request: Request, user: CurrentUser):
    if not policies.can_create_staff(user):
        return RedirectResponse(url="/staff", status_code=303)
    return render(request, "staff/create.html", {}, user=user)


@router.post("", name="staff.store")
def staff_store(
    request: Request,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: StaffCreateForm = Depends(staff_create_form),
):
    verify_csrf(request, form.csrf_token)
    create_staff(db, form.to_service_dict(organisation_id), user, request)
    db.commit()
    return RedirectResponse(url="/staff", status_code=303)
