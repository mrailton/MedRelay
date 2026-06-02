from __future__ import annotations

from sqlalchemy.orm import Session

from app import policies
from app.repositories import User
from app.services.events import get_event
from app.web.responses import ActionResult, redirect_to, render_page


def open_create_form(user: User) -> ActionResult:
    if not policies.can_create_event(user):
        return redirect_to("/events")
    return render_page("events/create.html", {})


def open_edit_form(
    db: Session,
    user: User,
    event_id: int,
    organisation_id: int,
) -> ActionResult:
    event = get_event(db, event_id, organisation_id)
    if not event or not policies.can_update_event(user, event):
        return redirect_to(f"/events/{event_id}")
    return render_page("events/edit.html", {"event": event})
