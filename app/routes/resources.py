from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, joinedload

from app.db.models.event import Event
from app.db.models.resource import Resource
from app.db.models.staff import Staff
from app.db.session import get_db
from app.dependencies import ControllerUser, CurrentUser, verify_csrf
from app.enums import ResourceStatus
from app.services.resources import (
    assign_staff_to_resource,
    create_resource,
    remove_staff_from_resource,
    update_resource_status,
)
from app.templating import render

router = APIRouter(tags=["resources"])


@router.get("/events/{event_id}/resources", name="events.resources.index")
def resources_index(
    request: Request, event_id: int, user: CurrentUser, db: Session = Depends(get_db)
):
    event = db.get(Event, event_id)
    resources = (
        db.query(Resource)
        .filter(Resource.event_id == event_id)
        .options(joinedload(Resource.staff))
        .order_by(Resource.name)
        .all()
    )
    return render(request, "resources/index.html", {"event": event, "resources": resources}, user=user)


@router.post("/events/{event_id}/resources", name="events.resources.store")
def resources_store(
    request: Request,
    event_id: int,
    user: ControllerUser,
    db: Session = Depends(get_db),
    name: str = Form(...),
    resource_type: str = Form(...),
    staff_ids: list[int] = Form(default=[]),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    event = db.get(Event, event_id)
    resource = create_resource(
        db,
        event,
        {"name": name, "resource_type": resource_type, "staff_ids": staff_ids},
        user,
        request,
    )
    db.commit()
    return RedirectResponse(url=f"/resources/{resource.id}", status_code=303)


@router.get("/resources/{resource_id}", name="resources.show")
def resources_show(
    request: Request, resource_id: int, user: CurrentUser, db: Session = Depends(get_db)
):
    resource = (
        db.query(Resource)
        .filter(Resource.id == resource_id)
        .options(joinedload(Resource.event), joinedload(Resource.staff), joinedload(Resource.incidents))
        .first()
    )
    if not resource:
        return RedirectResponse(url="/", status_code=303)
    all_staff = db.query(Staff).order_by(Staff.last_name).all()
    return render(
        request,
        "resources/show.html",
        {"resource": resource, "all_staff": all_staff},
        user=user,
    )


@router.api_route(
    "/resources/{resource_id}/status", methods=["PUT", "POST"], name="resources.update-status"
)
def resources_update_status(
    request: Request,
    resource_id: int,
    user: ControllerUser,
    db: Session = Depends(get_db),
    status: str = Form(...),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    resource = db.get(Resource, resource_id)
    update_resource_status(db, resource, ResourceStatus(status), user, request)
    db.commit()
    return RedirectResponse(url=request.headers.get("referer", f"/resources/{resource_id}"), status_code=303)


@router.api_route(
    "/resources/{resource_id}/assign-staff",
    methods=["PUT", "POST"],
    name="resources.assign-staff",
)
def resources_assign_staff(
    request: Request,
    resource_id: int,
    user: ControllerUser,
    db: Session = Depends(get_db),
    staff_id: int = Form(...),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    resource = db.get(Resource, resource_id)
    staff = db.get(Staff, staff_id)
    assign_staff_to_resource(db, resource, staff, user, request)
    db.commit()
    return RedirectResponse(url=request.headers.get("referer", f"/resources/{resource_id}"), status_code=303)


@router.api_route(
    "/resources/{resource_id}/remove-staff",
    methods=["PUT", "POST"],
    name="resources.remove-staff",
)
def resources_remove_staff(
    request: Request,
    resource_id: int,
    user: ControllerUser,
    db: Session = Depends(get_db),
    staff_id: int = Form(...),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    resource = db.get(Resource, resource_id)
    staff = db.get(Staff, staff_id)
    remove_staff_from_resource(db, resource, staff, user, request)
    db.commit()
    return RedirectResponse(url=request.headers.get("referer", f"/resources/{resource_id}"), status_code=303)
