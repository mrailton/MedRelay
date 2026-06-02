from __future__ import annotations

from fastapi import Depends, Request

from app.dependencies import ControllerUser, CurrentOrg, DbSession
from app.routes.incidents.router import router
from app.schemas.forms import (
    IncidentAssignResourcesForm,
    IncidentCreateForm,
    IncidentNoteForm,
    IncidentStatusForm,
    incident_assign_resources_form,
    incident_create_form,
    incident_note_form,
    incident_status_form,
)
from app.services.events import get_event
from app.services.incidents import (
    add_incident_note,
    assign_resource_to_incident,
    create_incident,
    get_incident_with_details,
    update_incident_status,
)
from app.web import handle, redirect_to, referer_or, resolved_entity, split_entity, verified_form


@router.post("/events/{event_id}/incidents", name="events.incidents.store")
def incidents_store(
    request: Request,
    event_id: int,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: IncidentCreateForm = Depends(verified_form(incident_create_form)),
):
    miss, event = split_entity(get_event(db, event_id, organisation_id), "/events")
    if miss:
        return handle(request, miss)
    event = resolved_entity(miss, event)
    incident = create_incident(
        db,
        event,
        form.to_service_dict(),
        user,
        request,
        organisation_id=organisation_id,
    )
    return handle(request, redirect_to(f"/incidents/{incident.id}", commit=True), db=db)


@router.api_route("/incidents/{incident_id}/status", methods=["PUT", "POST"], name="incidents.update-status")
def incidents_update_status(
    request: Request,
    incident_id: int,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: IncidentStatusForm = Depends(verified_form(incident_status_form)),
):
    miss, incident = split_entity(get_incident_with_details(db, incident_id, organisation_id))
    if miss:
        return handle(request, miss)
    incident = resolved_entity(miss, incident)
    update_incident_status(db, incident, form.status, user, request, organisation_id=organisation_id)
    url = referer_or(request, f"/incidents/{incident_id}")
    return handle(request, redirect_to(url, commit=True), db=db)


@router.api_route(
    "/incidents/{incident_id}/assign-resource",
    methods=["PUT", "POST"],
    name="incidents.assign-resource",
)
def incidents_assign_resource(
    request: Request,
    incident_id: int,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: IncidentAssignResourcesForm = Depends(verified_form(incident_assign_resources_form)),
):
    miss, incident = split_entity(get_incident_with_details(db, incident_id, organisation_id))
    if miss:
        return handle(request, miss)
    incident = resolved_entity(miss, incident)
    assign_resource_to_incident(db, incident, form.resource_ids, user, request, organisation_id=organisation_id)
    url = referer_or(request, f"/incidents/{incident_id}")
    return handle(request, redirect_to(url, commit=True), db=db)


@router.post("/incidents/{incident_id}/notes", name="incidents.notes.store")
def incidents_notes_store(
    request: Request,
    incident_id: int,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: IncidentNoteForm = Depends(verified_form(incident_note_form)),
):
    miss, incident = split_entity(get_incident_with_details(db, incident_id, organisation_id))
    if miss:
        return handle(request, miss)
    incident = resolved_entity(miss, incident)
    add_incident_note(db, incident, form.content, user, request, organisation_id=organisation_id)
    return handle(request, redirect_to(f"/incidents/{incident_id}", commit=True), db=db)
