from datetime import UTC, datetime

from sqlalchemy.orm import Session
from starlette.requests import Request

from medrelay.db.models.event import Event
from medrelay.db.models.incident import Incident
from medrelay.db.models.incident_note import IncidentNote
from medrelay.db.models.resource import Resource
from medrelay.db.models.user import User
from medrelay.enums import IncidentStatus, ResourceStatus
from medrelay.realtime.hub import realtime_hub
from medrelay.serialization import incident_to_dict, resource_to_dict
from medrelay.services.audit import write_audit_log


def _publish_incident(incident: Incident) -> None:
    db = Session.object_session(incident)
    if db is None:
        return
    db.refresh(incident)
    incident.resources  # noqa: B018 — load relationship
    for note in incident.notes:
        if note.user:
            db.refresh(note.user)
    realtime_hub.publish_sync(
        realtime_hub.incident_channel(incident.event_id),
        "incident.updated",
        {"incident": incident_to_dict(incident)},
    )


def _publish_resource(resource: Resource) -> None:
    realtime_hub.publish_sync(
        realtime_hub.resource_channel(resource.event_id),
        "resource.updated",
        {"resource": resource_to_dict(resource)},
    )


def create_incident(
    db: Session, event: Event, data: dict, user: User, request: Request | None = None
) -> Incident:
    incident = Incident(
        event_id=event.id,
        reference=data["reference"],
        location=data["location"],
        priority=data["priority"],
        category=data["category"],
        description=data["description"],
        status=IncidentStatus.NEW.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(incident)
    db.flush()
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
    db.refresh(incident, attribute_names=["resources"])
    before = incident_to_dict(incident)

    current_ids = {r.id for r in incident.resources}
    new_ids = set(resource_ids)
    removed_ids = current_ids - new_ids
    added_ids = new_ids - current_ids

    incident.resources.clear()
    if resource_ids:
        incident.resources.extend(
            db.query(Resource).filter(Resource.id.in_(resource_ids)).all()
        )
    incident.status = (
        IncidentStatus.DISPATCHED.value if resource_ids else IncidentStatus.NEW.value
    )
    incident.updated_at = datetime.now(UTC)

    if added_ids:
        db.query(Resource).filter(Resource.id.in_(added_ids)).update(
            {"status": ResourceStatus.ASSIGNED.value}, synchronize_session=False
        )
    if removed_ids:
        db.query(Resource).filter(Resource.id.in_(removed_ids)).update(
            {"status": ResourceStatus.AVAILABLE.value}, synchronize_session=False
        )

    db.flush()
    db.refresh(incident, attribute_names=["resources"])

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
    for resource in db.query(Resource).filter(Resource.id.in_(affected)).all():
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
    note = IncidentNote(
        incident_id=incident.id,
        user_id=user.id,
        content=content,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(note)
    db.flush()
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
