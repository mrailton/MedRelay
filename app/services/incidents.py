from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.enums import IncidentStatus, ResourceStatus
from app.realtime.hub import realtime_hub
from app.repositories import Event, Incident, IncidentNote, Resource, User
from app.repositories.incident import IncidentRepository
from app.repositories.incident_note import IncidentNoteRepository
from app.repositories.resource import ResourceRepository


def _publish_incident(incident: Incident) -> None:
    db = Session.object_session(incident)
    if db is None:
        return
    db.refresh(incident)
    incident.resources  # noqa: B018 — load relationship
    for note in incident.notes:
        if note.user:
            db.refresh(note.user)
    from app.serialization import incident_to_dict

    realtime_hub.publish_sync(
        realtime_hub.incident_channel(incident.event_id),
        "incident.updated",
        {"incident": incident_to_dict(incident)},
    )


def _publish_resource(resource: Resource) -> None:
    from app.serialization import resource_to_dict

    realtime_hub.publish_sync(
        realtime_hub.resource_channel(resource.event_id),
        "resource.updated",
        {"resource": resource_to_dict(resource)},
    )


def create_incident(
    db: Session,
    event: Event,
    data: dict,
    user: User,
    request: Request | None = None,
) -> Incident:
    repo = IncidentRepository(db)
    incident = repo.create(
        event_id=event.id,
        reference=repo.get_next_reference(event.id),
        location=data["location"],
        priority=data["priority"],
        category=data["category"],
        description=data["description"],
        status=IncidentStatus.NEW.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    from app.serialization import incident_to_dict
    from app.services.audit import write_audit_log

    write_audit_log(
        db,
        action="incident.created",
        entity_type="incident",
        entity_id=str(incident.id),
        after=incident_to_dict(incident),
        user=user,
        request=request,
    )
    db.refresh(incident)
    _publish_incident(incident)
    return incident


def _resource_status_for_incident(status: IncidentStatus) -> ResourceStatus | None:
    return {
        IncidentStatus.DISPATCHED: ResourceStatus.ASSIGNED,
        IncidentStatus.EN_ROUTE: ResourceStatus.EN_ROUTE,
        IncidentStatus.ON_SCENE: ResourceStatus.ON_SCENE,
        IncidentStatus.TRANSPORTING: ResourceStatus.TRANSPORTING,
        IncidentStatus.COMPLETE: ResourceStatus.AVAILABLE,
        IncidentStatus.CANCELLED: ResourceStatus.AVAILABLE,
        IncidentStatus.NEW: None,
    }.get(status)


def update_incident_status(
    db: Session,
    incident: Incident,
    status: IncidentStatus,
    user: User,
    request: Request | None = None,
) -> Incident:
    from app.serialization import incident_to_dict

    db.refresh(incident, attribute_names=["resources"])
    before = incident_to_dict(incident)

    incident.status = status.value
    incident.updated_at = datetime.now(UTC)

    resource_status = _resource_status_for_incident(status)
    if resource_status is not None:
        for resource in incident.resources:
            if resource.status != resource_status.value:
                resource.status = resource_status.value
                resource.updated_at = datetime.now(UTC)
                db.flush()
                db.refresh(resource, attribute_names=["staff"])
                _publish_resource(resource)

    db.flush()
    db.refresh(incident, attribute_names=["resources", "notes"])
    from app.services.audit import write_audit_log

    write_audit_log(
        db,
        action="incident.status.updated",
        entity_type="incident",
        entity_id=str(incident.id),
        before=before,
        after=incident_to_dict(incident),
        user=user,
        request=request,
    )
    _publish_incident(incident)
    return incident


def assign_resource_to_incident(
    db: Session,
    incident: Incident,
    resource_ids: list[int],
    user: User,
    request: Request | None = None,
) -> Incident:
    from app.serialization import incident_to_dict

    db.refresh(incident, attribute_names=["resources"])
    before = incident_to_dict(incident)

    current_ids = {r.id for r in incident.resources}
    new_ids = set(resource_ids)
    added_ids = new_ids - current_ids
    removed_ids = current_ids - new_ids

    resource_repo = ResourceRepository(db)
    incident.resources.clear()
    if resource_ids:
        incident.resources.extend(resource_repo.get_by_ids(resource_ids))
    incident.updated_at = datetime.now(UTC)

    if added_ids:
        resource_repo.bulk_update_status(list(added_ids), ResourceStatus.ASSIGNED)
        if incident.status == IncidentStatus.NEW.value:
            incident.status = IncidentStatus.DISPATCHED.value
    if removed_ids:
        resource_repo.bulk_update_status(list(removed_ids), ResourceStatus.AVAILABLE)

    db.flush()
    db.refresh(incident, attribute_names=["resources"])

    from app.services.audit import write_audit_log

    write_audit_log(
        db,
        action="incident.resource.assigned",
        entity_type="incident",
        entity_id=str(incident.id),
        before=before,
        after=incident_to_dict(incident),
        user=user,
        request=request,
    )

    _publish_incident(incident)

    affected = list(new_ids | removed_ids)
    for resource in resource_repo.get_by_ids(affected):
        db.refresh(resource, attribute_names=["staff"])
        _publish_resource(resource)

    return incident


def add_incident_note(
    db: Session,
    incident: Incident,
    content: str,
    user: User,
    request: Request | None = None,
) -> IncidentNote:
    note_repo = IncidentNoteRepository(db)
    note = note_repo.create(
        incident_id=incident.id,
        user_id=user.id,
        content=content,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    from app.services.audit import write_audit_log

    write_audit_log(
        db,
        action="incident.note.added",
        entity_type="incident",
        entity_id=str(incident.id),
        after={"content": content},
        user=user,
        request=request,
    )
    db.refresh(incident, attribute_names=["resources", "notes"])
    for note in incident.notes:
        if note.user_id:
            db.refresh(note, attribute_names=["user"])
    _publish_incident(incident)
    return note


def get_incident(db: Session, incident_id: int) -> Incident | None:
    return IncidentRepository(db).get(incident_id)


def get_incident_with_details(db: Session, incident_id: int) -> Incident | None:
    return IncidentRepository(db).get_with_event_resources_notes(incident_id)


def list_incidents_by_event(db: Session, event_id: int) -> list[Incident]:
    return IncidentRepository(db).list_by_event(event_id)


def count_incidents_by_event(db: Session, event_id: int) -> int:
    return IncidentRepository(db).count_by_event(event_id)


def count_active_incidents_by_event(db: Session, event_id: int) -> int:
    return IncidentRepository(db).count_active_by_event(event_id)
