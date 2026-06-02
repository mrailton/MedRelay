from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.audit import list_audit_logs_for_entity
from app.services.incidents import get_incident_with_details
from app.services.resources import list_resources_by_event
from app.web.responses import ActionResult, redirect_to, render_page


def show_page(
    db: Session,
    incident_id: int,
    organisation_id: int,
) -> ActionResult:
    incident = get_incident_with_details(db, incident_id, organisation_id)
    if not incident:
        return redirect_to("/")
    audit_logs = list_audit_logs_for_entity(db, "incident", str(incident_id))
    event_resources = list_resources_by_event(db, incident.event_id, organisation_id)
    return render_page(
        "incidents/show.html",
        {
            "incident": incident,
            "audit_logs": audit_logs,
            "event_resources": event_resources,
        },
    )
