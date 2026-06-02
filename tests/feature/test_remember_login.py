import re

from tests.factories import create_organisation, create_user


def test_login_with_remember_sets_session_flag(client, db_session):
    org = create_organisation(db_session, code="rememberorg", name="Remember Org")
    user = create_user(db_session, organisation=org)
    db_session.commit()

    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post(
        "/login",
        data={
            "organisation_code": org.code,
            "email": user.email,
            "password": "password",
            "csrf_token": csrf,
            "remember": "on",
        },
        follow_redirects=False,
    )
    assert client.cookies
    # Session is cookie-backed; follow-up request should stay authenticated
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 200
