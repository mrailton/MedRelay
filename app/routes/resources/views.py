from __future__ import annotations

from fastapi import Request

from app.actions import resources as resource_actions
from app.dependencies import CurrentOrg, CurrentUser, DbSession
from app.routes.resources.router import router
from app.services.events import get_event
from app.services.resources import list_resources_by_event
from app.templating import render
from app.web import handle


@router.get("/events/{event_id}/resources", name="events.resources.index")
def resources_index(request: Request, event_id: int, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    event = get_event(db, event_id, organisation_id)
    resources = list_resources_by_event(db, event_id, organisation_id)
    return render(request, "resources/index.html", {"event": event, "resources": resources}, user=user)


@router.get("/resources/{resource_id}", name="resources.show")
def resources_show(request: Request, resource_id: int, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    return handle(
        request,
        resource_actions.show_page(db, resource_id, organisation_id),
        user=user,
    )
