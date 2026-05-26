from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, joinedload

from app.db.models.audit_log import AuditLog
from app.db.models.event import Event
from app.db.models.incident import Incident
from app.db.models.incident_note import IncidentNote
from app.db.models.resource import Resource
from app.db.session import get_db
from app.dependencies import ControllerUser, CurrentUser, verify_csrf
from app.enums import IncidentStatus
from app.services.incidents import (
    add_incident_note,
    assign_resource_to_incident,
    create_incident,
    update_incident_status,
)
from app.templating import render

router = APIRouter(tags=["incidents"])


@router.get("/events/{event_id}/incidents", name="events.incidents.index")
def incidents_index(
    request: Request, event_id: int, user: CurrentUser, db: Session = Depends(get_db)
):
    event = db.get(Event, event_id)
    incidents = (
        db.query(Incident)
        .filter(Incident.event_id == event_id)
        .options(joinedload(Incident.resources))
        .order_by(Incident.created_at.desc())
        .all()
    )
    return render(request, "incidents/index.html", {"event": event, "incidents": incidents}, user=user)


@router.post("/events/{event_id}/incidents", name="events.incidents.store")
def incidents_store(
    request: Request,
    event_id: int,
    user: ControllerUser,
    db: Session = Depends(get_db),
    reference: str = Form(...),
    location: str = Form(...),
    priority: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    event = db.get(Event, event_id)
    incident = create_incident(
        db,
        event,
        {
            "reference": reference,
            "location": location,
            "priority": priority,
            "category": category,
            "description": description,
        },
        user,
        request,
    )
    db.commit()
    return RedirectResponse(url=f"/incidents/{incident.id}", status_code=303)


@router.get("/incidents/{incident_id}", name="incidents.show")
def incidents_show(
    request: Request, incident_id: int, user: CurrentUser, db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .options(
            joinedload(Incident.event),
            joinedload(Incident.resources),
            joinedload(Incident.notes).joinedload(IncidentNote.user),
        )
        .first()
    )
    if not incident:
        return RedirectResponse(url="/", status_code=303)
    audit_logs = (
        db.query(AuditLog)
        .filter(AuditLog.entity_type == "incident", AuditLog.entity_id == str(incident_id))
        .order_by(AuditLog.created_at.desc())
        .all()
    )
    event_resources = (
        db.query(Resource).filter(Resource.event_id == incident.event_id).order_by(Resource.name).all()
    )
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
    db: Session = Depends(get_db),
    status: str = Form(...),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    incident = db.get(Incident, incident_id)
    update_incident_status(db, incident, IncidentStatus(status), user, request)
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
    db: Session = Depends(get_db),
    resource_ids: list[int] = Form(default=[]),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    incident = db.get(Incident, incident_id)
    assign_resource_to_incident(db, incident, resource_ids, user, request)
    db.commit()
    return RedirectResponse(url=request.headers.get("referer", f"/incidents/{incident_id}"), status_code=303)


@router.post("/incidents/{incident_id}/notes", name="incidents.notes.store")
def incidents_notes_store(
    request: Request,
    incident_id: int,
    user: ControllerUser,
    db: Session = Depends(get_db),
    content: str = Form(...),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    incident = db.get(Incident, incident_id)
    add_incident_note(db, incident, content, user, request)
    db.commit()
    return RedirectResponse(url=f"/incidents/{incident_id}", status_code=303)
