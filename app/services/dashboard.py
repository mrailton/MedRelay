from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories import Event
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


def resolve_selected_event_id(active_events: list[Event], session_event_id: int | None) -> int | None:
    if session_event_id is not None:
        return session_event_id
    if active_events:
        return active_events[0].id
    return None


def build_dashboard_context(
    db: Session,
    organisation_id: int,
    selected_event_id: int | None,
) -> dict:
    active_events = list_active_events(db, organisation_id)
    resolved_id = resolve_selected_event_id(active_events, selected_event_id)

    selected_event = None
    dashboard_data = None

    if resolved_id is not None:
        selected_event = get_event(db, resolved_id, organisation_id)
        if selected_event:
            dashboard_data = {
                "event": selected_event,
                "incidents": list_incidents_by_event(db, selected_event.id, organisation_id),
                "resources": list_resources_by_event(db, selected_event.id, organisation_id),
                "summary": {
                    "total_incidents": count_incidents_by_event(db, selected_event.id, organisation_id) or 0,
                    "active_incidents": count_active_incidents_by_event(db, selected_event.id, organisation_id) or 0,
                    "available_resources": count_available_resources_by_event(db, selected_event.id, organisation_id) or 0,
                    "deployed_resources": count_deployed_resources_by_event(db, selected_event.id, organisation_id) or 0,
                    "out_of_service": count_out_of_service_resources_by_event(db, selected_event.id, organisation_id) or 0,
                },
            }

    return {
        "active_events": active_events,
        "selected_event": selected_event,
        "dashboard_data": dashboard_data,
        "all_staff": list_staff(db, organisation_id),
    }
