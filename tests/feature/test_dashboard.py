import re

from tests.factories import create_event, create_user


def test_dashboard_requires_auth(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_dashboard_ok(client, db_session):
    user = create_user(db_session)
    create_event(db_session)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"email": user.email, "password": "password", "csrf_token": csrf})
    response = client.get("/")
    assert response.status_code == 200
    assert "Dashboard" in response.text


def test_dashboard_shows_events(client, db_session):
    user = create_user(db_session)
    create_event(db_session, name="Event A")
    create_event(db_session, name="Event B")
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"email": user.email, "password": "password", "csrf_token": csrf})
    response = client.get("/")
    assert response.status_code == 200
    assert "Event A" in response.text
    assert "Event B" in response.text
