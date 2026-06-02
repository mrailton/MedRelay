from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import ControllerUser, CurrentUser, require_organisation, verify_csrf
from app.enums import ResourceStatus
from app.repositories.session import get_db
from app.services.events import get_event
from app.services.resources import (
    assign_staff_to_resource,
    create_resource,
    get_resource_with_details,
    list_resources_by_event,
    remove_staff_from_resource,
    update_resource_status,
)
from app.services.staff import get_staff, list_staff_by_last_name
from app.templating import render

if TYPE_CHECKING:
    pass

router = APIRouter(tags=["resources"])


@router.get("/events/{event_id}/resources", name="events.resources.index")
def resources_index(request: Request, event_id: int, user: CurrentUser, db: Session = Depends(get_db), organisation_id: int = Depends(require_organisation)):
    event = get_event(db, event_id, organisation_id)
    resources = list_resources_by_event(db, event_id)
    return render(request, "resources/index.html", {"event": event, "resources": resources}, user=user)


@router.post("/events/{event_id}/resources", name="events.resources.store")
def resources_store(
    request: Request,
    event_id: int,
    user: ControllerUser,
    db: Session = Depends(get_db),
    organisation_id: int = Depends(require_organisation),
    name: str = Form(...),
    resource_type: str = Form(...),
    staff_ids: list[int] = Form(default=[]),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    event = get_event(db, event_id, organisation_id)
    if not event:
        return RedirectResponse(url="/events", status_code=303)
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
def resources_show(request: Request, resource_id: int, user: CurrentUser, db: Session = Depends(get_db), organisation_id: int = Depends(require_organisation)):
    resource = get_resource_with_details(db, resource_id)
    if not resource:
        return RedirectResponse(url="/", status_code=303)
    all_staff = list_staff_by_last_name(db, organisation_id)
    return render(
        request,
        "resources/show.html",
        {"resource": resource, "all_staff": all_staff},
        user=user,
    )


@router.api_route("/resources/{resource_id}/status", methods=["PUT", "POST"], name="resources.update-status")
def resources_update_status(
    request: Request,
    resource_id: int,
    user: ControllerUser,
    db: Session = Depends(get_db),
    organisation_id: int = Depends(require_organisation),
    status: str = Form(...),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    resource = get_resource_with_details(db, resource_id)
    if not resource:
        return RedirectResponse(url="/", status_code=303)
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
    organisation_id: int = Depends(require_organisation),
    staff_id: int = Form(...),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    resource = get_resource_with_details(db, resource_id)
    if not resource:
        return RedirectResponse(url="/", status_code=303)
    staff = get_staff(db, staff_id, organisation_id)
    if not staff:
        return RedirectResponse(url=request.headers.get("referer", f"/resources/{resource_id}"), status_code=303)
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
    organisation_id: int = Depends(require_organisation),
    staff_id: int = Form(...),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    resource = get_resource_with_details(db, resource_id)
    if not resource:
        return RedirectResponse(url="/", status_code=303)
    staff = get_staff(db, staff_id, organisation_id)
    if not staff:
        return RedirectResponse(url=request.headers.get("referer", f"/resources/{resource_id}"), status_code=303)
    remove_staff_from_resource(db, resource, staff, user, request)
    db.commit()
    return RedirectResponse(url=request.headers.get("referer", f"/resources/{resource_id}"), status_code=303)
