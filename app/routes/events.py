from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import policies
from app.dependencies import ControllerUser, CurrentUser, verify_csrf
from app.repositories.session import get_db
from app.services.events import create_event, get_event, list_events, update_event
from app.templating import render

if TYPE_CHECKING:
    pass

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", name="events.index")
def events_index(request: Request, user: CurrentUser, db: Session = Depends(get_db)):
    events = list_events(db)
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
    db: Session = Depends(get_db),
    name: str = Form(...),
    location: str = Form(...),
    start_time: str = Form(...),
    end_time: str | None = Form(None),
    is_active: bool = Form(False),
    notes: str | None = Form(None),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    event = create_event(
        db,
        {
            "name": name,
            "location": location,
            "start_time": datetime.fromisoformat(start_time.replace("Z", "+00:00")) if "T" in start_time else datetime.fromisoformat(start_time),
            "end_time": datetime.fromisoformat(end_time) if end_time else None,
            "is_active": is_active,
            "notes": notes,
        },
        user,
        request,
    )
    db.commit()
    return RedirectResponse(url=f"/events/{event.id}", status_code=303)


@router.get("/{event_id}", name="events.show")
def events_show(request: Request, event_id: int, user: CurrentUser, db: Session = Depends(get_db)):
    event = get_event(db, event_id)
    if not event:
        return RedirectResponse(url="/events", status_code=303)
    return render(request, "events/show.html", {"event": event}, user=user)


@router.get("/{event_id}/edit", name="events.edit")
def events_edit(request: Request, event_id: int, user: CurrentUser, db: Session = Depends(get_db)):
    event = get_event(db, event_id)
    if not event or not policies.can_update_event(user, event):
        return RedirectResponse(url=f"/events/{event_id}", status_code=303)
    return render(request, "events/edit.html", {"event": event}, user=user)


@router.api_route("/{event_id}", methods=["PUT", "POST"], name="events.update")
def events_update(
    request: Request,
    event_id: int,
    user: ControllerUser,
    db: Session = Depends(get_db),
    name: str | None = Form(None),
    location: str | None = Form(None),
    start_time: str | None = Form(None),
    end_time: str | None = Form(None),
    is_active: bool = Form(False),
    notes: str | None = Form(None),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    event = get_event(db, event_id)
    if not event:
        return RedirectResponse(url="/events", status_code=303)
    data: dict[str, object] = {}
    if name is not None:
        data["name"] = name
    if location is not None:
        data["location"] = location
    if start_time:
        data["start_time"] = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    data["end_time"] = datetime.fromisoformat(end_time) if end_time else None
    data["is_active"] = is_active
    data["notes"] = notes
    update_event(db, event, data, user, request)
    db.commit()
    return RedirectResponse(url=f"/events/{event.id}", status_code=303)
