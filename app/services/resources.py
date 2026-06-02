from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.enums import ResourceStatus
from app.policies import authorize
from app.realtime.hub import realtime_hub
from app.repositories import Event, Resource, Staff, User
from app.repositories.resource import ResourceRepository
from app.repositories.staff import StaffRepository


def _publish_resource(resource: Resource) -> None:
    from app.serialization import resource_to_dict

    realtime_hub.publish_sync(
        realtime_hub.resource_channel(resource.event_id),
        "resource.updated",
        {"resource": resource_to_dict(resource)},
    )


def create_resource(
    db: Session,
    event: Event,
    data: dict,
    user: User,
    request: Request | None = None,
) -> Resource:
    authorize(user, "create", "resource", organisation_id=event.organisation_id)
    repo = ResourceRepository(db)
    resource = repo.create(
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

    staff_ids = data.get("staff_ids") or []
    if staff_ids:
        if not isinstance(staff_ids, list):
            staff_ids = [staff_ids]
        staff_repo = StaffRepository(db)
        resource.staff = staff_repo.list_by_ids(staff_ids)
        from app.services.resource_capability import recalculate_resource_capability

        recalculate_resource_capability(db, resource)
        db.refresh(resource, attribute_names=["staff"])

    from app.serialization import resource_to_dict
    from app.services.audit import write_audit_log

    write_audit_log(
        db,
        action="resource.created",
        entity_type="resource",
        entity_id=str(resource.id),
        organisation_id=event.organisation_id,
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
    org_id = resource.event.organisation_id if resource.event else None
    authorize(user, "update", "resource", resource, organisation_id=org_id)
    assert org_id is not None
    from app.serialization import resource_to_dict

    before = resource_to_dict(resource)
    resource.status = status.value
    resource.updated_at = datetime.now(UTC)
    db.flush()
    db.refresh(resource, attribute_names=["staff"])
    from app.services.audit import write_audit_log

    write_audit_log(
        db,
        action="resource.status.updated",
        entity_type="resource",
        entity_id=str(resource.id),
        organisation_id=org_id,
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
    organisation_id: int | None = None,
) -> Resource:
    org_id = organisation_id or (resource.event.organisation_id if resource.event else None)
    authorize(user, "update", "resource", resource, organisation_id=org_id)
    assert org_id is not None
    if staff not in resource.staff:
        resource.staff.append(staff)
    from app.services.resource_capability import recalculate_resource_capability

    recalculate_resource_capability(db, resource)
    db.refresh(resource, attribute_names=["staff"])
    from app.services.audit import write_audit_log

    write_audit_log(
        db,
        action="resource.staff.assigned",
        entity_type="resource",
        entity_id=str(resource.id),
        organisation_id=org_id,
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
    organisation_id: int | None = None,
) -> Resource:
    org_id = organisation_id or (resource.event.organisation_id if resource.event else None)
    authorize(user, "update", "resource", resource, organisation_id=org_id)
    assert org_id is not None
    if staff in resource.staff:
        resource.staff.remove(staff)
    from app.services.resource_capability import recalculate_resource_capability

    recalculate_resource_capability(db, resource)
    db.refresh(resource, attribute_names=["staff"])
    from app.services.audit import write_audit_log

    write_audit_log(
        db,
        action="resource.staff.removed",
        entity_type="resource",
        entity_id=str(resource.id),
        organisation_id=org_id,
        after={"staff_id": staff.id, "staff_name": staff.full_name},
        user=user,
        request=request,
    )
    _publish_resource(resource)
    return resource


def get_resource(db: Session, resource_id: int, organisation_id: int | None = None) -> Resource | None:
    return ResourceRepository(db).get(resource_id, organisation_id)


def get_resource_with_details(db: Session, resource_id: int, organisation_id: int | None = None) -> Resource | None:
    return ResourceRepository(db).get_with_event_staff_incidents(resource_id, organisation_id)


def list_resources_by_event(db: Session, event_id: int, organisation_id: int | None = None) -> list[Resource]:
    return ResourceRepository(db).list_by_event(event_id, organisation_id)


def count_resources_by_event(db: Session, event_id: int, organisation_id: int | None = None) -> int:
    return ResourceRepository(db).count_by_event(event_id, organisation_id)


def count_available_resources_by_event(db: Session, event_id: int, organisation_id: int | None = None) -> int:
    return ResourceRepository(db).count_available_by_event(event_id, organisation_id)


def count_deployed_resources_by_event(db: Session, event_id: int, organisation_id: int | None = None) -> int:
    return ResourceRepository(db).count_deployed_by_event(event_id, organisation_id)


def count_out_of_service_resources_by_event(db: Session, event_id: int, organisation_id: int | None = None) -> int:
    return ResourceRepository(db).count_out_of_service_by_event(event_id, organisation_id)
