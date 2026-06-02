import re

from tests.factories import create_organisation, create_user


def _login_as_default_org_admin(client, db_session, organisation):
    user = create_user(db_session, role="ADMIN", email="platform@example.com", organisation=organisation)
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


def test_platform_system_requires_default_org_admin(client, db_session):
    org = create_organisation(db_session, code="notdefault", name="Other")
    user = create_user(db_session, role="ADMIN", email="other@example.com", organisation=org)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post(
        "/login",
        data={"organisation_code": org.code, "email": user.email, "password": "password", "csrf_token": csrf},
    )
    response = client.get("/platform/system", follow_redirects=False)
    assert response.status_code == 403


def test_platform_system_shows_metrics(client, db_session):
    org = create_organisation(db_session, code="default", name="Default Org")
    _login_as_default_org_admin(client, db_session, org)
    response = client.get("/platform/system")
    assert response.status_code == 200
    assert "Database connection pool" in response.text
    assert "Realtime" in response.text


def test_legacy_admin_organisations_redirects(client, db_session):
    org = create_organisation(db_session, code="default", name="Default Org")
    _login_as_default_org_admin(client, db_session, org)
    response = client.get("/admin/organisations", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/platform/organisations"
