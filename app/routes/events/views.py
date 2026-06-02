from __future__ import annotations

from fastapi import Request

from app.actions import events as event_actions
from app.dependencies import CurrentOrg, CurrentUser, DbSession
from app.routes.events.router import router
from app.services.events import get_event, list_events
from app.templating import render
from app.web import handle, resolved_entity, split_entity


@router.get("", name="events.index")
def events_index(request: Request, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    events = list_events(db, organisation_id)
    return render(request, "events/index.html", {"events": events}, user=user)


@router.get("/create", name="events.create")
def events_create(request: Request, user: CurrentUser):
    return handle(request, event_actions.open_create_form(user), user=user)


@router.get("/{event_id}", name="events.show")
def events_show(request: Request, event_id: int, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    miss, event = split_entity(get_event(db, event_id, organisation_id), "/events")
    if miss:
        return handle(request, miss)
    event = resolved_entity(miss, event)
    return render(request, "events/show.html", {"event": event}, user=user)


@router.get("/{event_id}/edit", name="events.edit")
def events_edit(request: Request, event_id: int, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    return handle(
        request,
        event_actions.open_edit_form(db, user, event_id, organisation_id),
        user=user,
    )
