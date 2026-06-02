from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.dependencies import ControllerUser, CurrentOrg, CurrentUser, DbSession, verify_csrf
from app.schemas.forms import (
    ResourceAssignStaffForm,
    ResourceCreateForm,
    ResourceStatusForm,
    resource_assign_staff_form,
    resource_create_form,
    resource_status_form,
)
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

router = APIRouter(tags=["resources"])


@router.get("/events/{event_id}/resources", name="events.resources.index")
def resources_index(request: Request, event_id: int, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    event = get_event(db, event_id, organisation_id)
    resources = list_resources_by_event(db, event_id, organisation_id)
    return render(request, "resources/index.html", {"event": event, "resources": resources}, user=user)


@router.post("/events/{event_id}/resources", name="events.resources.store")
def resources_store(
    request: Request,
    event_id: int,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: ResourceCreateForm = Depends(resource_create_form),
):
    verify_csrf(request, form.csrf_token)
    event = get_event(db, event_id, organisation_id)
    if not event:
        return RedirectResponse(url="/events", status_code=303)
    resource = create_resource(db, event, form.to_service_dict(), user, request)
    db.commit()
    return RedirectResponse(url=f"/resources/{resource.id}", status_code=303)


@router.get("/resources/{resource_id}", name="resources.show")
def resources_show(request: Request, resource_id: int, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    resource = get_resource_with_details(db, resource_id, organisation_id)
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
    db: DbSession,
    organisation_id: CurrentOrg,
    form: ResourceStatusForm = Depends(resource_status_form),
):
    verify_csrf(request, form.csrf_token)
    resource = get_resource_with_details(db, resource_id, organisation_id)
    if not resource:
        return RedirectResponse(url="/", status_code=303)
    update_resource_status(db, resource, form.status, user, request)
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
    db: DbSession,
    organisation_id: CurrentOrg,
    form: ResourceAssignStaffForm = Depends(resource_assign_staff_form),
):
    verify_csrf(request, form.csrf_token)
    resource = get_resource_with_details(db, resource_id, organisation_id)
    if not resource:
        return RedirectResponse(url="/", status_code=303)
    staff = get_staff(db, form.staff_id, organisation_id)
    if not staff:
        return RedirectResponse(url=request.headers.get("referer", f"/resources/{resource_id}"), status_code=303)
    assign_staff_to_resource(db, resource, staff, user, request, organisation_id=organisation_id)
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
    db: DbSession,
    organisation_id: CurrentOrg,
    form: ResourceAssignStaffForm = Depends(resource_assign_staff_form),
):
    verify_csrf(request, form.csrf_token)
    resource = get_resource_with_details(db, resource_id, organisation_id)
    if not resource:
        return RedirectResponse(url="/", status_code=303)
    staff = get_staff(db, form.staff_id, organisation_id)
    if not staff:
        return RedirectResponse(url=request.headers.get("referer", f"/resources/{resource_id}"), status_code=303)
    remove_staff_from_resource(db, resource, staff, user, request, organisation_id=organisation_id)
    db.commit()
    return RedirectResponse(url=request.headers.get("referer", f"/resources/{resource_id}"), status_code=303)
