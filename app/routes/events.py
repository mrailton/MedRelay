from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app import policies
from app.dependencies import ControllerUser, CurrentOrg, CurrentUser, DbSession, verify_csrf
from app.schemas.forms import EventCreateForm, EventUpdateForm, event_create_form, event_update_form
from app.services.events import create_event, get_event, list_events, update_event
from app.templating import render

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", name="events.index")
def events_index(request: Request, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    events = list_events(db, organisation_id)
    return render(request, "events/index.html", {"events": events}, user=user)


@router.get("/create", name="events.create")
def events_create(request: Request, user: CurrentUser):
    if not policies.can_create_event(user):
        return RedirectResponse(url="/events", status_code=303)
    return render(request, "events/create.html", {}, user=user)


@router.post("", name="events.store")
def events_store(
    request: Request,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: EventCreateForm = Depends(event_create_form),
):
    verify_csrf(request, form.csrf_token)
    event = create_event(db, form.to_service_dict(organisation_id), user, request)
    db.commit()
    return RedirectResponse(url=f"/events/{event.id}", status_code=303)


@router.get("/{event_id}", name="events.show")
def events_show(request: Request, event_id: int, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    event = get_event(db, event_id, organisation_id)
    if not event:
        return RedirectResponse(url="/events", status_code=303)
    return render(request, "events/show.html", {"event": event}, user=user)


@router.get("/{event_id}/edit", name="events.edit")
def events_edit(request: Request, event_id: int, user: CurrentUser, db: DbSession, organisation_id: CurrentOrg):
    event = get_event(db, event_id, organisation_id)
    if not event or not policies.can_update_event(user, event):
        return RedirectResponse(url=f"/events/{event_id}", status_code=303)
    return render(request, "events/edit.html", {"event": event}, user=user)


@router.api_route("/{event_id}", methods=["PUT", "POST"], name="events.update")
def events_update(
    request: Request,
    event_id: int,
    user: ControllerUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: EventUpdateForm = Depends(event_update_form),
):
    verify_csrf(request, form.csrf_token)
    event = get_event(db, event_id, organisation_id)
    if not event:
        return RedirectResponse(url="/events", status_code=303)
    update_event(db, event, form.to_service_dict(), user, request)
    db.commit()
    return RedirectResponse(url=f"/events/{event.id}", status_code=303)
