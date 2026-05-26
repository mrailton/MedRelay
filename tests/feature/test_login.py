from tests.factories import create_user


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "MedRelay CAD" in response.text


def test_login_success(client, db_session):
    user = create_user(db_session, email="login@example.com")
    response = client.get("/login")
    csrf = _extract_csrf(response.text)
    response = client.post(
        "/login",
        data={"email": user.email, "password": "password", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def _extract_csrf(html: str) -> str:
    import re

    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    return m.group(1) if m else ""
