from tests.factories import create_organisation, create_user


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "Organisation Code" in response.text
    assert "MedRelay CAD" in response.text


def test_login_success(client, db_session):
    org = create_organisation(db_session, code="testorg")
    user = create_user(db_session, email="login@example.com", organisation=org)
    response = client.get("/login")
    csrf = _extract_csrf(response.text)
    response = client.post(
        "/login",
        data={"organisation_code": org.code, "email": user.email, "password": "password", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_login_invalid_org(client, db_session):
    user = create_user(db_session, email="user@example.com")
    response = client.get("/login")
    csrf = _extract_csrf(response.text)
    response = client.post(
        "/login",
        data={"organisation_code": "nonexistent", "email": user.email, "password": "password", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert "Invalid organisation code" in response.text


def test_login_user_not_in_org(client, db_session):
    org = create_organisation(db_session, code="org1")
    user = create_user(db_session, email="user@example.com")  # not linked to org
    response = client.get("/login")
    csrf = _extract_csrf(response.text)
    response = client.post(
        "/login",
        data={"organisation_code": org.code, "email": user.email, "password": "password", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert "credentials do not match" in response.text


def _extract_csrf(html: str) -> str:
    import re

    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    return m.group(1) if m else ""
