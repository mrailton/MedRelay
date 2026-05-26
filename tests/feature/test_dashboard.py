from tests.factories import create_event, create_user


def test_dashboard_requires_auth(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_dashboard_ok(client, db_session):
    user = create_user(db_session)
    create_event(db_session)
    login_page = client.get("/login")
    import re

    csrf = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text).group(1)
    client.post("/login", data={"email": user.email, "password": "password", "csrf_token": csrf})
    response = client.get("/")
    assert response.status_code == 200
    assert "Dashboard" in response.text
