from app.db.models.resource import Resource
from app.enums import IncidentStatus, ResourceStatus
from app.services.incidents import update_incident_status
from tests.factories import create_event, create_user, make_incident


def test_status_update_couples_resource_status(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    incident = make_incident(db_session, event)
    resource = Resource(
        event_id=event.id,
        name="Unit 1",
        resource_type="AMBULANCE",
        status=ResourceStatus.ASSIGNED.value,
        availability="AVAILABLE",
        is_deployable=True,
    )
    db_session.add(resource)
    db_session.flush()
    incident.resources.append(resource)
    db_session.commit()

    update_incident_status(db_session, incident, IncidentStatus.EN_ROUTE, user)
    db_session.commit()
    db_session.refresh(resource)
    assert resource.status == ResourceStatus.EN_ROUTE.value
