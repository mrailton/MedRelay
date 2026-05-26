import re

from tests.factories import create_user


def _login_as_admin(client, db_session):
    user = create_user(db_session, role="ADMIN", email="admin@example.com")
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"email": user.email, "password": "password", "csrf_token": csrf})
    return user


def _login(client, db_session):
    user = create_user(db_session)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"email": user.email, "password": "password", "csrf_token": csrf})
    return user


def _csrf(client):
    return re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)


def test_admin_users_index_requires_admin(client, db_session):
    _login(client, db_session)
    response = client.get("/admin/users", follow_redirects=False)
    assert response.status_code == 403


def test_admin_users_index(client, db_session):
    _login_as_admin(client, db_session)
    response = client.get("/admin/users")
    assert response.status_code == 200


def test_admin_users_create_get(client, db_session):
    _login_as_admin(client, db_session)
    response = client.get("/admin/users/create")
    assert response.status_code == 200


def test_admin_users_store(client, db_session):
    _login_as_admin(client, db_session)
    csrf = _csrf(client)
    response = client.post(
        "/admin/users",
        data={
            "name": "New Admin User",
            "email": "newadmin@example.com",
            "password": "password123",
            "password_confirmation": "password123",
            "role": "ADMIN",
            "csrf_token": csrf,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/users"


def test_admin_users_store_password_mismatch(client, db_session):
    _login_as_admin(client, db_session)
    csrf = _csrf(client)
    response = client.post(
        "/admin/users",
        data={
            "name": "Bad User",
            "email": "bad@example.com",
            "password": "password123",
            "password_confirmation": "different",
            "role": "CONTROLLER",
            "csrf_token": csrf,
        },
    )
    assert response.status_code == 200
    # The render call returns the create page with errors; "Create User" is page title
    assert "Create User" in response.text


def test_admin_users_store_short_password(client, db_session):
    _login_as_admin(client, db_session)
    csrf = _csrf(client)
    response = client.post(
        "/admin/users",
        data={
            "name": "Short Pwd",
            "email": "short@example.com",
            "password": "short",
            "password_confirmation": "short",
            "role": "CONTROLLER",
            "csrf_token": csrf,
        },
    )
    assert response.status_code == 200
    assert "Create User" in response.text


def test_admin_users_store_duplicate_email(client, db_session):
    create_user(db_session, role="ADMIN", email="dup@example.com")
    db_session.commit()
    _login_as_admin(client, db_session)
    csrf = _csrf(client)
    response = client.post(
        "/admin/users",
        data={
            "name": "Dup User",
            "email": "dup@example.com",
            "password": "password123",
            "password_confirmation": "password123",
            "role": "CONTROLLER",
            "csrf_token": csrf,
        },
    )
    assert response.status_code == 200
    assert "Email already exists" in response.text


def test_admin_audit_logs(client, db_session):
    _login_as_admin(client, db_session)
    response = client.get("/admin/audit-logs")
    assert response.status_code == 200
