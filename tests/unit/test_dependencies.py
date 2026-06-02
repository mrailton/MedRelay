import re

import pytest
from fastapi import HTTPException, status
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from app.dependencies import (
    LoginRequired,
    get_current_organisation_code,
    get_current_organisation_id,
    require_organisation,
    verify_csrf,
)
from app.main import app
from tests.factories import create_organisation, create_user


@pytest.fixture
def session_request():
    """Return a Request with session middleware installed."""
    SessionMiddleware(app, secret_key="test")
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "query_string": b"",
        "client": ("127.0.0.1", 8000),
        "app": app,
    }
    request = Request(scope)
    # Initialize session by calling the middleware's mock
    request.scope["session"] = {}
    return request


def test_get_current_organisation_id_from_session(session_request):
    session_request.session["organisation_id"] = 42
    assert get_current_organisation_id(session_request) == 42


def test_get_current_organisation_code_from_session(session_request):
    session_request.session["organisation_code"] = "mycode"
    assert get_current_organisation_code(session_request) == "mycode"


def test_verify_csrf_success(session_request):
    session_request.session["csrf_token"] = "mytoken"
    verify_csrf(session_request, "mytoken")


def test_verify_csrf_mismatch(session_request):
    session_request.session["csrf_token"] = "real-token"
    with pytest.raises(HTTPException) as exc:
        verify_csrf(session_request, "wrong-token")
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


def test_verify_csrf_missing_session_token(session_request):
    with pytest.raises(HTTPException) as exc:
        verify_csrf(session_request, "some-token")
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


def test_verify_csrf_missing_body_token(session_request):
    session_request.session["csrf_token"] = "real-token"
    with pytest.raises(HTTPException) as exc:
        verify_csrf(session_request, None)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


def test_require_organisation_raises_login_required():
    with pytest.raises(LoginRequired):
        require_organisation(None)


def test_require_organisation_returns_id():
    assert require_organisation(5) == 5


def test_require_guest_redirects_when_authenticated(client, db_session, organisation):
    user = create_user(db_session, organisation=organisation)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"organisation_code": organisation.code, "email": user.email, "password": "password", "csrf_token": csrf})
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 303


def test_require_guest_allows_anonymous(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_require_default_org_admin_no_default_org(client, db_session, organisation):
    user = create_user(db_session, role="ADMIN", organisation=organisation)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"organisation_code": organisation.code, "email": user.email, "password": "password", "csrf_token": csrf})
    response = client.get("/admin/organisations", follow_redirects=False)
    assert response.status_code == 403


def test_require_default_org_admin_success(client, db_session):
    default_org = create_organisation(db_session, code="default", name="Default")
    user = create_user(db_session, role="ADMIN", organisation=default_org)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"organisation_code": default_org.code, "email": user.email, "password": "password", "csrf_token": csrf})
    response = client.get("/admin/organisations")
    assert response.status_code == 200


def test_verify_csrf_mismatch_via_login(client):
    response = client.post("/login", data={"csrf_token": "wrong-token"}, follow_redirects=False)
    assert response.status_code == 403


def test_require_auth_redirects_anonymous(client):
    response = client.get("/events", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_admin_route_blocks_controller(client, db_session, organisation):
    user = create_user(db_session, organisation=organisation)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"organisation_code": organisation.code, "email": user.email, "password": "password", "csrf_token": csrf})
    response = client.get("/admin/users", follow_redirects=False)
    assert response.status_code == 403


def test_admin_route_blocks_readonly(client, db_session, organisation):
    user = create_user(db_session, role="READ_ONLY", organisation=organisation)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"organisation_code": organisation.code, "email": user.email, "password": "password", "csrf_token": csrf})
    response = client.get("/admin/users", follow_redirects=False)
    assert response.status_code == 403


def test_controller_route_blocks_readonly(client, db_session, organisation):
    """Controller-protected route (resource status update) should 403 for READ_ONLY."""
    from app.repositories.resource import ResourceRepository
    from tests.factories import create_event

    user = create_user(db_session, role="READ_ONLY", organisation=organisation)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"organisation_code": organisation.code, "email": user.email, "password": "password", "csrf_token": csrf})
    event = create_event(db_session, organisation=organisation)
    resource = ResourceRepository(db_session).create(event_id=event.id, name="R1", resource_type="AMBULANCE")
    db_session.commit()
    response = client.post(
        f"/resources/{resource.id}/status",
        data={"status": "EN_ROUTE", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 403
