from __future__ import annotations

from fastapi import Depends, Request

from app.dependencies import ControllerUser, CurrentOrg, DbSession
from app.routes.staff.router import router
from app.schemas.forms import StaffCreateForm, staff_create_form
from app.services.staff import create_staff
from app.web import handle, redirect_to, verified_form


@router.post("", name="staff.store")
def staff_store(
    request: Request,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: StaffCreateForm = Depends(verified_form(staff_create_form)),
):
    create_staff(db, form.to_service_dict(organisation_id), user, request)
    return handle(
        request,
        redirect_to("/staff", commit=True, flash=("success", "Staff member added.")),
        db=db,
    )
