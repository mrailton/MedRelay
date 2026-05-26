import re

from app.db.models.audit_log import AuditLog
from app.repositories.staff import StaffRepository
from app.services.staff import create_staff, get_staff, list_staff, list_staff_by_last_name
from tests.factories import create_user


def _login(client, db_session):
    user = create_user(db_session)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"email": user.email, "password": "password", "csrf_token": csrf})
    return user


def _csrf(client):
    return re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)


# -- HTTP route tests ---------------------------------------------------------


def test_staff_index(client, db_session):
    _login(client, db_session)
    response = client.get("/staff")
    assert response.status_code == 200


def test_staff_requires_auth(client, db_session):
    response = client.get("/staff", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_staff_create_get(client, db_session):
    _login(client, db_session)
    response = client.get("/staff/create")
    assert response.status_code == 200


def test_staff_store(client, db_session):
    _login(client, db_session)
    csrf = _csrf(client)
    response = client.post(
        "/staff",
        data={
            "first_name": "Alice",
            "last_name": "Johnson",
            "clinical_level": "EMT",
            "csrf_token": csrf,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    staff = StaffRepository(db_session).get(1)
    assert staff is not None
    assert staff.first_name == "Alice"
    assert staff.last_name == "Johnson"


def test_staff_store_with_notes(client, db_session):
    _login(client, db_session)
    csrf = _csrf(client)
    response = client.post(
        "/staff",
        data={
            "first_name": "Bob",
            "last_name": "Smith",
            "clinical_level": "PARAMEDIC",
            "notes": "Certified",
            "csrf_token": csrf,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    staff = StaffRepository(db_session).get(1)
    assert staff.notes == "Certified"


# -- Service-level tests ------------------------------------------------------


def test_create_staff_service(db_session):
    user = create_user(db_session)
    staff = create_staff(
        db_session,
        {"first_name": "Charlie", "last_name": "Brown", "clinical_level": "EFR"},
        user,
    )
    db_session.commit()
    assert staff.first_name == "Charlie"
    assert staff.clinical_level == "EFR"
    assert staff.full_name == "Charlie Brown"
    log = db_session.query(AuditLog).filter_by(action="staff.created").first()
    assert log is not None


def test_list_staff(db_session):
    user = create_user(db_session)
    create_staff(db_session, {"first_name": "A", "last_name": "Z", "clinical_level": "EMT"}, user)
    create_staff(db_session, {"first_name": "B", "last_name": "M", "clinical_level": "EMT"}, user)
    db_session.commit()
    assert len(list_staff(db_session)) == 2


def test_list_staff_by_last_name(db_session):
    user = create_user(db_session)
    create_staff(db_session, {"first_name": "A", "last_name": "Z", "clinical_level": "EMT"}, user)
    create_staff(db_session, {"first_name": "B", "last_name": "B", "clinical_level": "EMT"}, user)
    db_session.commit()
    names = [s.last_name for s in list_staff_by_last_name(db_session)]
    assert names == sorted(names)


def test_get_staff(db_session):
    user = create_user(db_session)
    staff = create_staff(db_session, {"first_name": "Diana", "last_name": "Prince", "clinical_level": "PARAMEDIC"}, user)
    db_session.commit()
    assert get_staff(db_session, staff.id) is not None
    assert get_staff(db_session, 9999) is None
