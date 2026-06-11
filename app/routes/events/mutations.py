from __future__ import annotations

from urllib.parse import urlparse

from fastapi import Depends, Request

from app.dependencies import ControllerUser, CurrentOrg, DbSession
from app.routes.events.router import router
from app.schemas.forms import EventCreateForm, EventUpdateForm, event_create_form, event_update_form
from app.services.events import create_event, get_event, update_event
from app.web import handle, redirect_to, resolved_entity, split_entity, verified_form


def _redirect_after_event_create(request: Request, event_id: int) -> str:
    referer = request.headers.get("referer", "")
    path = urlparse(referer).path if referer else ""
    if path in ("/", ""):
        request.session["selected_event_id"] = event_id
        return "/"
    if path == "/events":
        return "/events"
    return f"/events/{event_id}"


@router.post("", name="events.store")
def events_store(
    request: Request,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: EventCreateForm = Depends(verified_form(event_create_form)),
):
    event = create_event(db, form.to_service_dict(organisation_id), user, request)
    url = _redirect_after_event_create(request, event.id)
    return handle(
        request,
        redirect_to(url, commit=True, flash=("success", f"Event '{event.name}' created.")),
        db=db,
    )


@router.api_route("/{event_id}", methods=["PUT", "POST"], name="events.update")
def events_update(
    request: Request,
    event_id: int,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: EventUpdateForm = Depends(verified_form(event_update_form)),
):
    miss, event = split_entity(get_event(db, event_id, organisation_id), "/events")
    if miss:
        return handle(request, miss)
    event = resolved_entity(miss, event)
    update_event(db, event, form.to_service_dict(), user, request)
    return handle(request, redirect_to(f"/events/{event.id}", commit=True), db=db)
