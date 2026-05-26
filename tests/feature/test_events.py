from tests.factories import create_event, create_user


def test_events_index(client, db_session):
    user = create_user(db_session)
    create_event(db_session, name="Event A")
    import re

    csrf = re.search(
        r'name="csrf_token" value="([^"]+)"',
        client.get("/login").text,
    ).group(1)
    client.post("/login", data={"email": user.email, "password": "password", "csrf_token": csrf})
    response = client.get("/events")
    assert response.status_code == 200
    assert "Event A" in response.text
