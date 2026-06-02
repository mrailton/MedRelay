from __future__ import annotations

from fastapi import Request

from app.actions import incidents as incident_actions
from app.dependencies import CurrentOrg, CurrentUser, DbSession
from app.routes.incidents.router import router
from app.services.events import get_event
from app.services.incidents import list_incidents_by_event
from app.templating import render
from app.web import handle


@router.get("/events/{event_id}/incidents", name="events.incidents.index")
def incidents_index(request: Request, event_id: int, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    event = get_event(db, event_id, organisation_id)
    incidents = list_incidents_by_event(db, event_id, organisation_id)
    return render(request, "incidents/index.html", {"event": event, "incidents": incidents}, user=user)


@router.get("/incidents/{incident_id}", name="incidents.show")
def incidents_show(request: Request, incident_id: int, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    return handle(
        request,
        incident_actions.show_page(db, incident_id, organisation_id),
        user=user,
    )
