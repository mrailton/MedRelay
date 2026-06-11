import re

from tests.factories import create_event, create_user


def test_dashboard_requires_auth(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_dashboard_ok(client, db_session, organisation):
    user = create_user(db_session, organisation=organisation)
    create_event(db_session, organisation=organisation)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"organisation_code": organisation.code, "email": user.email, "password": "password", "csrf_token": csrf})
    response = client.get("/")
    assert response.status_code == 200
    assert "Dashboard" in response.text


def test_dashboard_shows_events(client, db_session, organisation):
    user = create_user(db_session, organisation=organisation)
    create_event(db_session, name="Event A", organisation=organisation)
    create_event(db_session, name="Event B", organisation=organisation)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"organisation_code": organisation.code, "email": user.email, "password": "password", "csrf_token": csrf})
    response = client.get("/")
    assert response.status_code == 200
    assert "Event A" in response.text
    assert "Event B" in response.text


def test_dashboard_resource_modal_includes_searchable_staff_multiselect(client, db_session, organisation):
    from app.repositories.staff import StaffRepository

    user = create_user(db_session, organisation=organisation)
    event = create_event(db_session, organisation=organisation)
    StaffRepository(db_session).create(
        first_name="Jane",
        last_name="Smith",
        clinical_level="PARAMEDIC",
        organisation_id=organisation.id,
    )
    db_session.commit()
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post(
        "/login",
        data={"organisation_code": organisation.code, "email": user.email, "password": "password", "csrf_token": csrf},
    )
    client.post("/", data={"selected_event_id": str(event.id), "csrf_token": csrf}, follow_redirects=True)
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="create-resource-modal"' in response.text
    assert 'name="staff_ids"' in response.text
    assert "Jane Smith" in response.text
    assert "Search by name or clinical level" in response.text
