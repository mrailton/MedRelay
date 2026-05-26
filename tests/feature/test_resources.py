import re

from app.db.models.audit_log import AuditLog
from app.enums import ResourceStatus
from app.repositories.resource import ResourceRepository
from app.repositories.staff import StaffRepository
from app.services.resources import (
    assign_staff_to_resource,
    count_available_resources_by_event,
    count_deployed_resources_by_event,
    count_out_of_service_resources_by_event,
    count_resources_by_event,
    create_resource,
    get_resource,
    get_resource_with_details,
    list_resources_by_event,
    remove_staff_from_resource,
    update_resource_status,
)
from tests.factories import create_event, create_user


def _login(client, db_session):
    user = create_user(db_session)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"email": user.email, "password": "password", "csrf_token": csrf})
    return user


def _csrf(client):
    return re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)


# -- HTTP route tests ---------------------------------------------------------


def test_resources_index(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    response = client.get(f"/events/{event.id}/resources")
    assert response.status_code == 200


def test_resources_store_creates_resource(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    csrf = _csrf(client)
    response = client.post(
        f"/events/{event.id}/resources",
        data={"name": "Ambulance-1", "resource_type": "AMBULANCE", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
    resource = ResourceRepository(db_session).get(1)
    assert resource is not None
    assert resource.name == "Ambulance-1"
    assert resource.resource_type == "AMBULANCE"
    assert resource.status == ResourceStatus.AVAILABLE.value


def test_resources_store_with_staff(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    staff = StaffRepository(db_session).create(first_name="John", last_name="Doe", clinical_level="EMT")
    db_session.commit()
    csrf = _csrf(client)
    response = client.post(
        f"/events/{event.id}/resources",
        data={"name": "Unit-1", "resource_type": "AMBULANCE", "staff_ids": [staff.id], "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
    resource = ResourceRepository(db_session).get(1)
    assert resource is not None
    assert len(resource.staff) == 1
    assert resource.staff[0].id == staff.id


def test_resources_show(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    resource = ResourceRepository(db_session).create(event_id=event.id, name="Unit-1", resource_type="AMBULANCE")
    db_session.commit()
    response = client.get(f"/resources/{resource.id}")
    assert response.status_code == 200
    assert "Unit-1" in response.text


def test_resources_show_404_redirect(client, db_session):
    _login(client, db_session)
    response = client.get("/resources/9999", follow_redirects=False)
    assert response.status_code == 303


def test_resources_requires_auth(client, db_session):
    response = client.get("/resources/1", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_resources_update_status(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    resource = ResourceRepository(db_session).create(event_id=event.id, name="Unit-1", resource_type="AMBULANCE")
    db_session.commit()
    csrf = _csrf(client)
    response = client.post(
        f"/resources/{resource.id}/status",
        data={"status": ResourceStatus.EN_ROUTE.value, "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
    db_session.refresh(resource)
    assert resource.status == ResourceStatus.EN_ROUTE.value


def test_resources_assign_staff(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    resource = ResourceRepository(db_session).create(event_id=event.id, name="Unit-1", resource_type="AMBULANCE")
    staff = StaffRepository(db_session).create(first_name="Jane", last_name="Smith", clinical_level="PARAMEDIC")
    db_session.commit()
    csrf = _csrf(client)
    response = client.post(
        f"/resources/{resource.id}/assign-staff",
        data={"staff_id": staff.id, "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
    db_session.refresh(resource)
    assert len(resource.staff) == 1
    assert resource.staff[0].id == staff.id


def test_resources_remove_staff(client, db_session):
    _login(client, db_session)
    event = create_event(db_session)
    staff = StaffRepository(db_session).create(first_name="Jack", last_name="Brown", clinical_level="EMT")
    resource = ResourceRepository(db_session).create(event_id=event.id, name="Unit-1", resource_type="AMBULANCE")
    resource = assign_staff_to_resource(db_session, resource, staff, _login(client, db_session))
    db_session.commit()
    csrf = _csrf(client)
    response = client.post(
        f"/resources/{resource.id}/remove-staff",
        data={"staff_id": staff.id, "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
    db_session.refresh(resource)
    assert len(resource.staff) == 0


# -- Service-level tests ------------------------------------------------------


def test_create_resource_service(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    resource = create_resource(
        db_session,
        event,
        {"name": "Medic-1", "resource_type": "AMBULANCE"},
        user,
    )
    db_session.commit()
    assert resource.name == "Medic-1"
    assert resource.status == ResourceStatus.AVAILABLE.value
    log = db_session.query(AuditLog).filter_by(action="resource.created").first()
    assert log is not None


def test_create_resource_with_staff_service(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    staff = StaffRepository(db_session).create(first_name="John", last_name="Doe", clinical_level="PARAMEDIC")
    db_session.commit()
    resource = create_resource(
        db_session,
        event,
        {"name": "ALS-1", "resource_type": "AMBULANCE", "staff_ids": [staff.id]},
        user,
    )
    assert len(resource.staff) == 1
    assert resource.is_deployable is True
    assert resource.highest_clinical_level is not None


def test_update_resource_status_service(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    resource = create_resource(db_session, event, {"name": "Unit-1", "resource_type": "AMBULANCE"}, user)
    db_session.commit()
    updated = update_resource_status(db_session, resource, ResourceStatus.ON_SCENE, user)
    assert updated.status == ResourceStatus.ON_SCENE.value
    log = db_session.query(AuditLog).filter_by(action="resource.status.updated").first()
    assert log is not None
    assert log.before["status"] == ResourceStatus.AVAILABLE.value
    assert log.after["status"] == ResourceStatus.ON_SCENE.value


def test_assign_staff_to_resource_service(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    resource = create_resource(db_session, event, {"name": "Unit-1", "resource_type": "AMBULANCE"}, user)
    staff = StaffRepository(db_session).create(first_name="Jane", last_name="Smith", clinical_level="EMT")
    db_session.commit()
    result = assign_staff_to_resource(db_session, resource, staff, user)
    assert staff in result.staff
    log = db_session.query(AuditLog).filter_by(action="resource.staff.assigned").first()
    assert log is not None


def test_assign_same_staff_twice_is_idempotent(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    resource = create_resource(db_session, event, {"name": "Unit-1", "resource_type": "AMBULANCE"}, user)
    staff = StaffRepository(db_session).create(first_name="Jane", last_name="Smith", clinical_level="EMT")
    db_session.commit()
    assign_staff_to_resource(db_session, resource, staff, user)
    assign_staff_to_resource(db_session, resource, staff, user)
    assert resource.staff.count(staff) == 1


def test_remove_staff_from_resource_service(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    resource = create_resource(db_session, event, {"name": "Unit-1", "resource_type": "AMBULANCE"}, user)
    staff = StaffRepository(db_session).create(first_name="Jill", last_name="Jones", clinical_level="EMT")
    db_session.commit()
    assign_staff_to_resource(db_session, resource, staff, user)
    result = remove_staff_from_resource(db_session, resource, staff, user)
    assert staff not in result.staff
    log = db_session.query(AuditLog).filter_by(action="resource.staff.removed").first()
    assert log is not None


def test_get_resource_service(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    resource = create_resource(db_session, event, {"name": "Unit-1", "resource_type": "AMBULANCE"}, user)
    db_session.commit()
    assert get_resource(db_session, resource.id) is not None
    assert get_resource(db_session, 9999) is None


def test_get_resource_with_details_service(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    resource = create_resource(db_session, event, {"name": "Unit-1", "resource_type": "AMBULANCE"}, user)
    db_session.commit()
    assert get_resource_with_details(db_session, resource.id) is not None


def test_list_resources_by_event(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    create_resource(db_session, event, {"name": "A", "resource_type": "AMBULANCE"}, user)
    create_resource(db_session, event, {"name": "B", "resource_type": "AMBULANCE"}, user)
    db_session.commit()
    assert len(list_resources_by_event(db_session, event.id)) == 2


def test_count_resources_by_event(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    create_resource(db_session, event, {"name": "A", "resource_type": "AMBULANCE"}, user)
    db_session.commit()
    assert count_resources_by_event(db_session, event.id) == 1


def test_count_available_resources(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    create_resource(db_session, event, {"name": "A", "resource_type": "AMBULANCE"}, user)
    db_session.commit()
    assert count_available_resources_by_event(db_session, event.id) == 1
    update_resource_status(db_session, get_resource(db_session, 1), ResourceStatus.EN_ROUTE, user)
    assert count_available_resources_by_event(db_session, event.id) == 0


def test_count_deployed_resources(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    create_resource(db_session, event, {"name": "A", "resource_type": "AMBULANCE"}, user)
    db_session.commit()
    assert count_deployed_resources_by_event(db_session, event.id) == 0
    update_resource_status(db_session, get_resource(db_session, 1), ResourceStatus.EN_ROUTE, user)
    assert count_deployed_resources_by_event(db_session, event.id) == 1


def test_count_out_of_service_resources(db_session):
    event = create_event(db_session)
    user = create_user(db_session)
    create_resource(db_session, event, {"name": "A", "resource_type": "AMBULANCE"}, user)
    db_session.commit()
    update_resource_status(db_session, get_resource(db_session, 1), ResourceStatus.OUT_OF_SERVICE, user)
    assert count_out_of_service_resources_by_event(db_session, event.id) == 1
