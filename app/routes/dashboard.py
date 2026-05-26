from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session

from app.dependencies import CurrentUser, verify_csrf
from app.repositories.session import get_db
from app.services.events import get_event, list_active_events
from app.services.incidents import (
    count_active_incidents_by_event,
    count_incidents_by_event,
    list_incidents_by_event,
)
from app.services.resources import (
    count_available_resources_by_event,
    count_deployed_resources_by_event,
    count_out_of_service_resources_by_event,
    list_resources_by_event,
)
from app.services.staff import list_staff
from app.templating import render

if TYPE_CHECKING:
    pass

router = APIRouter(tags=["dashboard"])


@router.api_route("/", methods=["GET", "POST"], name="dashboard")
def dashboard(
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
    selected_event_id: int | None = Form(None),
    csrf_token: str | None = Form(None),
):
    if request.method == "POST" and selected_event_id is not None:
        verify_csrf(request, csrf_token)
        request.session["selected_event_id"] = int(selected_event_id)
        accept = request.headers.get("accept", "")
        if "application/json" in accept or request.headers.get("x-requested-with") == "XMLHttpRequest":
            return Response(status_code=204)
        return RedirectResponse(url="/", status_code=303)

    active_events = list_active_events(db)
    selected_event_id = request.session.get("selected_event_id")
    if selected_event_id is None and active_events:
        selected_event_id = active_events[0].id

    selected_event = None
    dashboard_data = None

    if selected_event_id is not None:
        selected_event = get_event(db, selected_event_id)
        if selected_event:
            incidents = list_incidents_by_event(db, selected_event.id)
            resources = list_resources_by_event(db, selected_event.id)
            total_incidents = count_incidents_by_event(db, selected_event.id)
            active_incidents = count_active_incidents_by_event(db, selected_event.id)
            available_resources = count_available_resources_by_event(db, selected_event.id)
            deployed_resources = count_deployed_resources_by_event(db, selected_event.id)
            out_of_service = count_out_of_service_resources_by_event(db, selected_event.id)
            dashboard_data = {
                "event": selected_event,
                "incidents": incidents,
                "resources": resources,
                "summary": {
                    "total_incidents": total_incidents or 0,
                    "active_incidents": active_incidents or 0,
                    "available_resources": available_resources or 0,
                    "deployed_resources": deployed_resources or 0,
                    "out_of_service": out_of_service or 0,
                },
            }

    all_staff = list_staff(db)

    return render(
        request,
        "dashboard.html",
        {
            "active_events": active_events,
            "selected_event": selected_event,
            "dashboard_data": dashboard_data,
            "all_staff": all_staff,
        },
        user=user,
    )
