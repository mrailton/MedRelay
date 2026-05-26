from datetime import UTC, datetime

from sqlalchemy.orm import Session
from starlette.requests import Request

from medrelay.db.models.event import Event
from medrelay.db.models.resource import Resource
from medrelay.db.models.staff import Staff
from medrelay.db.models.user import User
from medrelay.enums import ResourceStatus
from medrelay.realtime.hub import realtime_hub
from medrelay.serialization import resource_to_dict
from medrelay.services.audit import write_audit_log
from medrelay.services.resource_capability import recalculate_resource_capability


def _publish_resource(resource: Resource) -> None:
    realtime_hub.publish_sync(
        realtime_hub.resource_channel(resource.event_id),
        "resource.updated",
        {"resource": resource_to_dict(resource)},
    )


def create_resource(
    db: Session, event: Event, data: dict, user: User, request: Request | None = None
) -> Resource:
    resource = Resource(
        event_id=event.id,
        name=data["name"],
        resource_type=data["resource_type"],
        status=ResourceStatus.AVAILABLE.value,
        availability="AVAILABLE",
        highest_clinical_level=None,
        is_deployable=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(resource)
    db.flush()

    staff_ids = data.get("staff_ids") or []
    if staff_ids:
        if not isinstance(staff_ids, list):
            staff_ids = [staff_ids]
        resource.staff = list(db.query(Staff).filter(Staff.id.in_(staff_ids)).all())
        recalculate_resource_capability(db, resource)
        db.refresh(resource, attribute_names=["staff"])

    write_audit_log(
        db,
        action="resource.created",
        entity_type="resource",
        entity_id=str(resource.id),
        after=resource_to_dict(resource),
        user=user,
        request=request,
    )
    _publish_resource(resource)
    return resource


def update_resource_status(
    db: Session,
    resource: Resource,
    status: ResourceStatus,
    user: User,
    request: Request | None = None,
) -> Resource:
    before = resource_to_dict(resource)
    resource.status = status.value
    resource.updated_at = datetime.now(UTC)
    db.flush()
    db.refresh(resource, attribute_names=["staff"])
    write_audit_log(
        db,
        action="resource.status.updated",
        entity_type="resource",
        entity_id=str(resource.id),
        before=before,
        after=resource_to_dict(resource),
        user=user,
        request=request,
    )
    _publish_resource(resource)
    return resource


def assign_staff_to_resource(
    db: Session,
    resource: Resource,
    staff: Staff,
    user: User,
    request: Request | None = None,
) -> Resource:
    if staff not in resource.staff:
        resource.staff.append(staff)
    recalculate_resource_capability(db, resource)
    db.refresh(resource, attribute_names=["staff"])
    write_audit_log(
        db,
        action="resource.staff.assigned",
        entity_type="resource",
        entity_id=str(resource.id),
        after={"staff_id": staff.id, "staff_name": staff.full_name},
        user=user,
        request=request,
    )
    _publish_resource(resource)
    return resource


def remove_staff_from_resource(
    db: Session,
    resource: Resource,
    staff: Staff,
    user: User,
    request: Request | None = None,
) -> Resource:
    if staff in resource.staff:
        resource.staff.remove(staff)
    recalculate_resource_capability(db, resource)
    db.refresh(resource, attribute_names=["staff"])
    write_audit_log(
        db,
        action="resource.staff.removed",
        entity_type="resource",
        entity_id=str(resource.id),
        after={"staff_id": staff.id, "staff_name": staff.full_name},
        user=user,
        request=request,
    )
    _publish_resource(resource)
    return resource
