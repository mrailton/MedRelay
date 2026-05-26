from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, Response
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.db.models.event import Event
from app.db.models.incident import Incident
from app.db.models.resource import Resource
from app.db.models.staff import Staff
from app.db.session import get_db
from app.dependencies import CurrentUser, verify_csrf
from app.enums import IncidentStatus, ResourceStatus
from app.templating import render

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

    active_events = db.query(Event).filter(Event.is_active.is_(True)).order_by(Event.name).all()
    selected_event_id = request.session.get("selected_event_id")
    if selected_event_id is None and active_events:
        selected_event_id = active_events[0].id

    selected_event = None
    dashboard_data = None

    if selected_event_id is not None:
        selected_event = db.get(Event, selected_event_id)
        if selected_event:
            incidents = (
                db.query(Incident)
                .filter(Incident.event_id == selected_event.id)
                .options(joinedload(Incident.resources))
                .order_by(Incident.created_at.desc())
                .all()
            )
            resources = (
                db.query(Resource)
                .filter(Resource.event_id == selected_event.id)
                .options(joinedload(Resource.staff))
                .order_by(Resource.name)
                .all()
            )
            total_incidents = db.query(func.count(Incident.id)).filter(
                Incident.event_id == selected_event.id
            ).scalar()
            active_incidents = (
                db.query(func.count(Incident.id))
                .filter(
                    Incident.event_id == selected_event.id,
                    Incident.status.notin_(
                        [IncidentStatus.COMPLETE.value, IncidentStatus.CANCELLED.value]
                    ),
                )
                .scalar()
            )
            available_resources = (
                db.query(func.count(Resource.id))
                .filter(
                    Resource.event_id == selected_event.id,
                    Resource.status == ResourceStatus.AVAILABLE.value,
                )
                .scalar()
            )
            deployed_resources = (
                db.query(func.count(Resource.id))
                .filter(
                    Resource.event_id == selected_event.id,
                    Resource.status.notin_(
                        [ResourceStatus.AVAILABLE.value, ResourceStatus.OUT_OF_SERVICE.value]
                    ),
                )
                .scalar()
            )
            out_of_service = (
                db.query(func.count(Resource.id))
                .filter(
                    Resource.event_id == selected_event.id,
                    Resource.status == ResourceStatus.OUT_OF_SERVICE.value,
                )
                .scalar()
            )
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

    all_staff = db.query(Staff).order_by(Staff.last_name, Staff.first_name).all()

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
