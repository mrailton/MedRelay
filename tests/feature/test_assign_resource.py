from medrelay.enums import IncidentStatus, ResourceStatus
from medrelay.services.incidents import assign_resource_to_incident
from tests.factories import create_event, create_user, make_incident
from medrelay.db.models.resource import Resource
from datetime import UTC, datetime


def test_assign_resource_syncs_status(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    incident = make_incident(db_session, event)
    resource = Resource(
        event_id=event.id,
        name="Alpha",
        resource_type="AMBULANCE",
        status=ResourceStatus.AVAILABLE.value,
        availability="AVAILABLE",
        is_deployable=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(resource)
    db_session.commit()

    assign_resource_to_incident(db_session, incident, [resource.id], user)
    db_session.commit()
    db_session.refresh(incident)
    db_session.refresh(resource)

    assert incident.status == IncidentStatus.DISPATCHED.value
    assert resource.status == ResourceStatus.ASSIGNED.value
