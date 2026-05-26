from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import policies
from app.db.models.staff import Staff
from app.db.session import get_db
from app.dependencies import ControllerUser, CurrentUser, verify_csrf
from app.services.staff import create_staff
from app.templating import render

router = APIRouter(prefix="/staff", tags=["staff"])


@router.get("", name="staff.index")
def staff_index(request: Request, user: CurrentUser, db: Session = Depends(get_db)):
    staff_list = db.query(Staff).order_by(Staff.last_name, Staff.first_name).all()
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
    db: Session = Depends(get_db),
    first_name: str = Form(...),
    last_name: str = Form(...),
    clinical_level: str = Form(...),
    notes: str | None = Form(None),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    staff = create_staff(
        db,
        {
            "first_name": first_name,
            "last_name": last_name,
            "clinical_level": clinical_level,
            "notes": notes,
        },
        user,
        request,
    )
    db.commit()
    return RedirectResponse(url="/staff", status_code=303)
