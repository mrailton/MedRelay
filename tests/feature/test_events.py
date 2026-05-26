import re

from app.services.events import get_event
from tests.factories import create_event, create_user


def _login(client, db_session):
    user = create_user(db_session)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"email": user.email, "password": "password", "csrf_token": csrf})
    return user


def _csrf(client):
    return re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)


def test_events_index(client, db_session):
    _login(client, db_session)
    create_event(db_session, name="Event A")
    response = client.get("/events")
    assert response.status_code == 200
    assert "Event A" in response.text


def test_events_index_requires_auth(client, db_session):
    response = client.get("/events", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_events_create_get(client, db_session):
    _login(client, db_session)
    response = client.get("/events/create")
    assert response.status_code == 200


def test_events_store(client, db_session):
    _login(client, db_session)
    csrf = _csrf(client)
    response = client.post(
        "/events",
        data={
            "name": "New Event",
            "location": "New Location",
            "start_time": "2026-06-01T10:00:00+00:00",
            "is_active": True,
            "csrf_token": csrf,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    event = get_event(db_session, 1)
    assert event is not None
    assert event.name == "New Event"
    assert event.location == "New Location"


def test_events_show(client, db_session):
    _login(client, db_session)
    event = create_event(db_session, name="Detail Event")
    response = client.get(f"/events/{event.id}")
    assert response.status_code == 200
    assert "Detail Event" in response.text


def test_events_show_404(client, db_session):
    _login(client, db_session)
    response = client.get("/events/9999", follow_redirects=False)
    assert response.status_code == 303


def test_events_edit(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    response = client.get(f"/events/{event.id}/edit")
    assert response.status_code == 200


def test_events_update(client, db_session):
    _login(client, db_session)
    event = create_event(db_session, name="Original")
    csrf = _csrf(client)
    response = client.post(
        f"/events/{event.id}",
        data={
            "name": "Updated Name",
            "location": "New Location",
            "start_time": "2026-07-01T12:00:00+00:00",
            "is_active": True,
            "csrf_token": csrf,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    db_session.refresh(event)
    assert event.name == "Updated Name"
    assert event.location == "New Location"
