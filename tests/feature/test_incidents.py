import re

from app.db.models.audit_log import AuditLog
from app.enums import IncidentStatus
from app.repositories.resource import ResourceRepository
from app.services.incidents import (
    add_incident_note,
    count_active_incidents_by_event,
    count_incidents_by_event,
    get_incident,
    get_incident_with_details,
    list_incidents_by_event,
)
from app.services.resources import create_resource
from tests.factories import create_event, create_user, make_incident


def _login(client, db_session):
    user = create_user(db_session)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"email": user.email, "password": "password", "csrf_token": csrf})
    return user


def _csrf(client):
    return re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)


# -- HTTP route tests ---------------------------------------------------------


def test_incidents_index(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    response = client.get(f"/events/{event.id}/incidents")
    assert response.status_code == 200


def test_incidents_store(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    csrf = _csrf(client)
    response = client.post(
        f"/events/{event.id}/incidents",
        data={
            "reference": "INC-001",
            "location": "Somewhere",
            "priority": "P1",
            "category": "medical",
            "description": "Test incident",
            "csrf_token": csrf,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    incident = get_incident(db_session, 1)
    assert incident is not None
    assert incident.reference == "INC-001"


def test_incidents_show(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    incident = make_incident(db_session, event)
    response = client.get(f"/incidents/{incident.id}")
    assert response.status_code == 200
    assert incident.reference in response.text


def test_incidents_show_404(client, db_session):
    _login(client, db_session)
    response = client.get("/incidents/9999", follow_redirects=False)
    assert response.status_code == 303


def test_incidents_update_status(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    incident = make_incident(db_session, event)
    resource = create_resource(db_session, event, {"name": "Unit-1", "resource_type": "AMBULANCE"}, _login(client, db_session))
    db_session.commit()
    incident.resources.append(resource)
    db_session.commit()
    csrf = _csrf(client)
    response = client.post(
        f"/incidents/{incident.id}/status",
        data={"status": IncidentStatus.EN_ROUTE.value, "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
    db_session.refresh(incident)
    assert incident.status == IncidentStatus.EN_ROUTE.value


def test_incidents_assign_resource(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    incident = make_incident(db_session, event)
    resource = ResourceRepository(db_session).create(event_id=event.id, name="Res-1", resource_type="AMBULANCE")
    db_session.commit()
    csrf = _csrf(client)
    response = client.post(
        f"/incidents/{incident.id}/assign-resource",
        data={"resource_ids": [resource.id], "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
    db_session.refresh(incident)
    assert len(incident.resources) == 1


def test_incidents_add_note(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    incident = make_incident(db_session, event)
    csrf = _csrf(client)
    response = client.post(
        f"/incidents/{incident.id}/notes",
        data={"content": "Test note content", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
    db_session.refresh(incident)
    assert len(incident.notes) == 1
    assert incident.notes[0].content == "Test note content"


# -- Service-level tests ------------------------------------------------------


def test_add_incident_note_service(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    incident = make_incident(db_session, event)
    note = add_incident_note(db_session, incident, "Service note", user)
    db_session.commit()
    assert note.content == "Service note"
    assert note.user_id == user.id
    log = db_session.query(AuditLog).filter_by(action="incident.note.added").first()
    assert log is not None


def test_get_incident_service(db_session):
    event = create_event(db_session)
    incident = make_incident(db_session, event)
    assert get_incident(db_session, incident.id) is not None
    assert get_incident(db_session, 9999) is None


def test_get_incident_with_details_service(db_session):
    event = create_event(db_session)
    incident = make_incident(db_session, event)
    result = get_incident_with_details(db_session, incident.id)
    assert result is not None
    assert result.event.id == event.id


def test_list_incidents_by_event(db_session):
    event = create_event(db_session)
    make_incident(db_session, event, reference="INC-001")
    make_incident(db_session, event, reference="INC-002")
    assert len(list_incidents_by_event(db_session, event.id)) == 2


def test_count_incidents_by_event(db_session):
    event = create_event(db_session)
    assert count_incidents_by_event(db_session, event.id) == 0
    make_incident(db_session, event)
    assert count_incidents_by_event(db_session, event.id) == 1


def test_count_active_incidents_by_event(db_session):
    event = create_event(db_session)
    make_incident(db_session, event, status=IncidentStatus.NEW.value)
    make_incident(db_session, event, reference="INC-002", status=IncidentStatus.COMPLETE.value)
    assert count_active_incidents_by_event(db_session, event.id) == 1
