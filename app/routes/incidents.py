from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.dependencies import ControllerUser, CurrentOrg, CurrentUser, DbSession, verify_csrf
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
from app.services.audit import list_audit_logs_for_entity
from app.services.events import get_event
from app.services.incidents import (
    add_incident_note,
    assign_resource_to_incident,
    create_incident,
    get_incident_with_details,
    list_incidents_by_event,
    update_incident_status,
)
from app.services.resources import list_resources_by_event
from app.templating import render

router = APIRouter(tags=["incidents"])


@router.get("/events/{event_id}/incidents", name="events.incidents.index")
def incidents_index(request: Request, event_id: int, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    event = get_event(db, event_id, organisation_id)
    incidents = list_incidents_by_event(db, event_id, organisation_id)
    return render(request, "incidents/index.html", {"event": event, "incidents": incidents}, user=user)


@router.post("/events/{event_id}/incidents", name="events.incidents.store")
def incidents_store(
    request: Request,
    event_id: int,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: IncidentCreateForm = Depends(incident_create_form),
):
    verify_csrf(request, form.csrf_token)
    event = get_event(db, event_id, organisation_id)
    if not event:
        return RedirectResponse(url="/events", status_code=303)
    incident = create_incident(
        db,
        event,
        form.to_service_dict(),
        user,
        request,
        organisation_id=organisation_id,
    )
    db.commit()
    return RedirectResponse(url=f"/incidents/{incident.id}", status_code=303)


@router.get("/incidents/{incident_id}", name="incidents.show")
def incidents_show(request: Request, incident_id: int, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    incident = get_incident_with_details(db, incident_id, organisation_id)
    if not incident:
        return RedirectResponse(url="/", status_code=303)
    audit_logs = list_audit_logs_for_entity(db, "incident", str(incident_id))
    event_resources = list_resources_by_event(db, incident.event_id, organisation_id)
    return render(
        request,
        "incidents/show.html",
        {
            "incident": incident,
            "audit_logs": audit_logs,
            "event_resources": event_resources,
        },
        user=user,
    )


@router.api_route("/incidents/{incident_id}/status", methods=["PUT", "POST"], name="incidents.update-status")
def incidents_update_status(
    request: Request,
    incident_id: int,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: IncidentStatusForm = Depends(incident_status_form),
):
    verify_csrf(request, form.csrf_token)
    incident = get_incident_with_details(db, incident_id, organisation_id)
    if not incident:
        return RedirectResponse(url="/", status_code=303)
    update_incident_status(db, incident, form.status, user, request, organisation_id=organisation_id)
    db.commit()
    return RedirectResponse(url=request.headers.get("referer", f"/incidents/{incident_id}"), status_code=303)


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
    form: IncidentAssignResourcesForm = Depends(incident_assign_resources_form),
):
    verify_csrf(request, form.csrf_token)
    incident = get_incident_with_details(db, incident_id, organisation_id)
    if not incident:
        return RedirectResponse(url="/", status_code=303)
    assign_resource_to_incident(db, incident, form.resource_ids, user, request, organisation_id=organisation_id)
    db.commit()
    return RedirectResponse(url=request.headers.get("referer", f"/incidents/{incident_id}"), status_code=303)


@router.post("/incidents/{incident_id}/notes", name="incidents.notes.store")
def incidents_notes_store(
    request: Request,
    incident_id: int,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: IncidentNoteForm = Depends(incident_note_form),
):
    verify_csrf(request, form.csrf_token)
    incident = get_incident_with_details(db, incident_id, organisation_id)
    if not incident:
        return RedirectResponse(url="/", status_code=303)
    add_incident_note(db, incident, form.content, user, request, organisation_id=organisation_id)
    db.commit()
    return RedirectResponse(url=f"/incidents/{incident_id}", status_code=303)
