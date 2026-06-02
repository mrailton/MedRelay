"""Cross-organisation access must be denied (IDOR prevention)."""

import re

from tests.factories import create_event, create_organisation, create_user, make_incident


def _login(client, db_session, organisation):
    user = create_user(db_session, organisation=organisation)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post(
        "/login",
        data={
            "organisation_code": organisation.code,
            "email": user.email,
            "password": "password",
            "csrf_token": csrf,
        },
    )
    return user


def _csrf(client):
    return re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)


def test_cannot_view_other_org_incident(client, db_session):
    org_a = create_organisation(db_session, code="orga", name="Org A")
    org_b = create_organisation(db_session, code="orgb", name="Org B")
    event_b = create_event(db_session, organisation=org_b)
    incident_b = make_incident(db_session, event_b)
    db_session.commit()

    _login(client, db_session, org_a)
    response = client.get(f"/incidents/{incident_b.id}", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_cannot_view_other_org_resource(client, db_session):
    from app.services.resources import create_resource

    org_a = create_organisation(db_session, code="orga2", name="Org A2")
    org_b = create_organisation(db_session, code="orgb2", name="Org B2")
    user_b = create_user(db_session, organisation=org_b)
    event_b = create_event(db_session, organisation=org_b)
    resource_b = create_resource(
        db_session,
        event_b,
        {"name": "Amb-1", "resource_type": "AMBULANCE"},
        user_b,
    )
    db_session.commit()

    _login(client, db_session, org_a)
    response = client.get(f"/resources/{resource_b.id}", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_cannot_view_other_org_event(client, db_session):
    org_a = create_organisation(db_session, code="orga3", name="Org A3")
    org_b = create_organisation(db_session, code="orgb3", name="Org B3")
    event_b = create_event(db_session, organisation=org_b)
    db_session.commit()

    _login(client, db_session, org_a)
    response = client.get(f"/events/{event_b.id}", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/events"


def test_cannot_update_other_org_incident_status(client, db_session):
    org_a = create_organisation(db_session, code="orga4", name="Org A4")
    org_b = create_organisation(db_session, code="orgb4", name="Org B4")
    event_b = create_event(db_session, organisation=org_b)
    incident_b = make_incident(db_session, event_b)
    db_session.commit()

    _login(client, db_session, org_a)
    csrf = _csrf(client)
    response = client.post(
        f"/incidents/{incident_b.id}/status",
        data={"status": "DISPATCHED", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_web_entrypoint_exports_app():
    from app.main import app as main_app
    from web import app as web_app

    assert web_app is main_app
