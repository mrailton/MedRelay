from __future__ import annotations

from fastapi import Depends, Request

from app.dependencies import ControllerUser, CurrentOrg, DbSession
from app.routes.resources.router import router
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
    remove_staff_from_resource,
    update_resource_status,
)
from app.services.staff import get_staff
from app.web import handle, redirect_to, referer_or, resolved_entity, split_entity, verified_form


@router.post("/events/{event_id}/resources", name="events.resources.store")
def resources_store(
    request: Request,
    event_id: int,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: ResourceCreateForm = Depends(verified_form(resource_create_form)),
):
    miss, event = split_entity(get_event(db, event_id, organisation_id), "/events")
    if miss:
        return handle(request, miss)
    event = resolved_entity(miss, event)
    resource = create_resource(db, event, form.to_service_dict(), user, request)
    return handle(request, redirect_to(f"/resources/{resource.id}", commit=True), db=db)


@router.api_route("/resources/{resource_id}/status", methods=["PUT", "POST"], name="resources.update-status")
def resources_update_status(
    request: Request,
    resource_id: int,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: ResourceStatusForm = Depends(verified_form(resource_status_form)),
):
    miss, resource = split_entity(get_resource_with_details(db, resource_id, organisation_id))
    if miss:
        return handle(request, miss)
    resource = resolved_entity(miss, resource)
    update_resource_status(db, resource, form.status, user, request)
    url = referer_or(request, f"/resources/{resource_id}")
    return handle(request, redirect_to(url, commit=True), db=db)


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
    form: ResourceAssignStaffForm = Depends(verified_form(resource_assign_staff_form)),
):
    miss, resource = split_entity(get_resource_with_details(db, resource_id, organisation_id))
    if miss:
        return handle(request, miss)
    resource = resolved_entity(miss, resource)
    staff = get_staff(db, form.staff_id, organisation_id)
    url = referer_or(request, f"/resources/{resource_id}")
    if not staff:
        return handle(request, redirect_to(url))
    assign_staff_to_resource(db, resource, staff, user, request, organisation_id=organisation_id)
    return handle(request, redirect_to(url, commit=True), db=db)


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
    form: ResourceAssignStaffForm = Depends(verified_form(resource_assign_staff_form)),
):
    miss, resource = split_entity(get_resource_with_details(db, resource_id, organisation_id))
    if miss:
        return handle(request, miss)
    resource = resolved_entity(miss, resource)
    staff = get_staff(db, form.staff_id, organisation_id)
    url = referer_or(request, f"/resources/{resource_id}")
    if not staff:
        return handle(request, redirect_to(url))
    remove_staff_from_resource(db, resource, staff, user, request, organisation_id=organisation_id)
    return handle(request, redirect_to(url, commit=True), db=db)
