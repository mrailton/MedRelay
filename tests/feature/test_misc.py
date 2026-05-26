import re

from app.enums import ResourceStatus
from app.repositories.resource import ResourceRepository
from app.repositories.staff import StaffRepository
from app.services.incidents import assign_resource_to_incident
from app.services.resources import create_resource
from tests.factories import create_event, create_user, make_incident


def _login(client, db_session):
    user = create_user(db_session)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"email": user.email, "password": "password", "csrf_token": csrf})
    return user


def test_health_endpoint(client):
    response = client.get("/up")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_failure(client, db_session):
    create_user(db_session, email="fail@example.com")
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    response = client.post(
        "/login",
        data={"email": "fail@example.com", "password": "wrong-password", "csrf_token": csrf},
    )
    assert response.status_code == 200
    assert "MedRelay CAD" in response.text


def test_login_nonexistent_user(client, db_session):
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    response = client.post(
        "/login",
        data={"email": "noone@example.com", "password": "anything", "csrf_token": csrf},
    )
    assert response.status_code == 200
    assert "MedRelay CAD" in response.text


def test_logout(client, db_session):
    _login(client, db_session)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    response = client.post("/logout", data={"csrf_token": csrf}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_resource_staff_ids_as_single_int(client, db_session):
    """Cover the branch where staff_ids is a single int, not a list."""
    user = _login(client, db_session)
    event = create_event(db_session)
    staff = StaffRepository(db_session).create(first_name="Test", last_name="User", clinical_level="EMT")
    db_session.commit()
    resource = create_resource(
        db_session,
        event,
        {"name": "Test-Unit", "resource_type": "AMBULANCE", "staff_ids": staff.id},
        user,
    )
    assert len(resource.staff) == 1


def test_incident_resource_removal_updates_status(db_session):
    """Cover the removed_ids branch in assign_resource_to_incident."""
    event = create_event(db_session)
    user = create_user(db_session)
    incident = make_incident(db_session, event)
    r1 = ResourceRepository(db_session).create(event_id=event.id, name="R1", resource_type="AMBULANCE")
    r2 = ResourceRepository(db_session).create(event_id=event.id, name="R2", resource_type="AMBULANCE")
    db_session.commit()
    # assign both
    assign_resource_to_incident(db_session, incident, [r1.id, r2.id], user)
    db_session.commit()
    # remove r1 - this triggers the removed_ids path
    assign_resource_to_incident(db_session, incident, [r2.id], user)
    db_session.commit()
    db_session.refresh(incident)
    assert len(incident.resources) == 1
    assert incident.resources[0].id == r2.id
    db_session.refresh(r1)
    assert r1.status == ResourceStatus.AVAILABLE.value


def test_dashboard_no_events(client, db_session):
    """Cover dashboard when there are no events (no active event selected)."""
    user = create_user(db_session)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"email": user.email, "password": "password", "csrf_token": csrf})
    response = client.get("/")
    assert response.status_code == 200


def test_staff_create_requires_auth(client, db_session):
    response = client.get("/staff/create", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_staff_create_requires_controller(client, db_session):
    user = create_user(db_session, role="READ_ONLY")
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"email": user.email, "password": "password", "csrf_token": csrf})
    response = client.get("/staff/create", follow_redirects=False)
    assert response.status_code == 303


def test_events_edit_404(client, db_session):
    _login(client, db_session)
    response = client.get("/events/9999/edit", follow_redirects=False)
    assert response.status_code == 303


def test_dashboard_event_selection_post_redirect(client, db_session):
    """Cover the POST handler for selecting an event on the dashboard."""
    _login(client, db_session)
    event = create_event(db_session)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    response = client.post(
        "/",
        data={"selected_event_id": str(event.id), "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_dashboard_event_selection_post_json(client, db_session):
    """Cover the JSON response path in dashboard POST."""
    _login(client, db_session)
    event = create_event(db_session)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    response = client.post(
        "/",
        data={"selected_event_id": str(event.id), "csrf_token": csrf},
        headers={"accept": "application/json"},
        follow_redirects=False,
    )
    assert response.status_code == 204


def test_events_create_page_requires_controller(client, db_session):
    """Cover policy check on events.create page."""
    create_user(db_session, role="READ_ONLY")
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"email": "user0@example.com", "password": "password", "csrf_token": csrf})
    response = client.get("/events/create", follow_redirects=False)
    assert response.status_code == 303


def test_events_update_404(client, db_session):
    """Cover 404 redirect in events.update route."""
    _login(client, db_session)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    response = client.post(
        "/events/9999",
        data={"name": "Whatever", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
