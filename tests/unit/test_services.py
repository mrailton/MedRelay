from datetime import UTC, datetime

from app.db.models.audit_log import AuditLog
from app.repositories.user import UserRepository
from app.services.audit import count_audit_logs, list_audit_logs_for_entity, list_audit_logs_paginated, write_audit_log
from app.services.events import create_event as create_event_svc
from app.services.events import get_event, list_active_events, list_events, update_event
from app.services.users import create_user as create_user_svc
from app.services.users import get_user_by_email, list_users
from tests.factories import create_event, create_user

# -- Audit service tests ------------------------------------------------------


def test_write_audit_log(db_session):
    user = create_user(db_session)
    write_audit_log(
        db_session,
        action="test.action",
        entity_type="test",
        entity_id="1",
        after={"key": "value"},
        user=user,
    )
    db_session.commit()
    log = db_session.query(AuditLog).first()
    assert log is not None
    assert log.action == "test.action"
    assert log.entity_type == "test"
    assert log.entity_id == "1"
    assert log.after == {"key": "value"}


def test_list_audit_logs_for_entity(db_session):
    user = create_user(db_session)
    for i in range(3):
        write_audit_log(db_session, action=f"test.{i}", entity_type="test", entity_id="e1", user=user)
    db_session.commit()
    logs = list_audit_logs_for_entity(db_session, "test", "e1")
    assert len(logs) == 3


def test_list_audit_logs_paginated(db_session):
    user = create_user(db_session)
    for i in range(5):
        write_audit_log(db_session, action=f"test.{i}", entity_type="test", entity_id=str(i), user=user)
    db_session.commit()
    page1 = list_audit_logs_paginated(db_session, page=1, per_page=2)
    assert len(page1) == 2
    page2 = list_audit_logs_paginated(db_session, page=2, per_page=2)
    assert len(page2) == 2


def test_count_audit_logs(db_session):
    user = create_user(db_session)
    assert count_audit_logs(db_session) == 0
    write_audit_log(db_session, action="test", entity_type="test", entity_id="1", user=user)
    db_session.commit()
    assert count_audit_logs(db_session) == 1


# -- Event service tests ------------------------------------------------------


def test_create_event_service(db_session):
    user = create_user(db_session)
    event = create_event_svc(
        db_session,
        {
            "name": "Test Event",
            "location": "Test Location",
            "start_time": datetime.now(UTC),
            "is_active": True,
        },
        user,
    )
    db_session.commit()
    assert event.name == "Test Event"
    assert event.is_active is True
    log = db_session.query(AuditLog).filter_by(action="event.created").first()
    assert log is not None


def test_update_event_service(db_session):
    user = create_user(db_session)
    event = create_event(db_session)
    updated = update_event(
        db_session,
        event,
        {"name": "Updated Name", "location": "New Location"},
        user,
    )
    db_session.commit()
    assert updated.name == "Updated Name"
    assert updated.location == "New Location"
    log = db_session.query(AuditLog).filter_by(action="event.updated").first()
    assert log is not None


def test_update_event_partial(db_session):
    user = create_user(db_session)
    event = create_event(db_session)
    updated = update_event(
        db_session,
        event,
        {"name": "Only Name"},
        user,
    )
    db_session.commit()
    assert updated.name == "Only Name"
    assert updated.location == "Test Location"


def test_get_event_service(db_session):
    event = create_event(db_session)
    assert get_event(db_session, event.id) is not None
    assert get_event(db_session, 9999) is None


def test_list_events(db_session):
    create_event(db_session, name="A")
    create_event(db_session, name="B")
    assert len(list_events(db_session)) == 2


def test_list_active_events(db_session):
    create_event(db_session, name="Active", is_active=True)
    create_event(db_session, name="Inactive", is_active=False)
    active = list_active_events(db_session)
    assert len(active) == 1
    assert active[0].name == "Active"


# -- User service tests -------------------------------------------------------


def test_create_user_service(db_session):
    actor = create_user(db_session, role="ADMIN")
    user = create_user_svc(
        db_session,
        {"name": "New User", "email": "new@example.com", "password": "secret", "role": "CONTROLLER"},
        actor,
    )
    db_session.commit()
    assert user.name == "New User"
    assert user.email == "new@example.com"
    log = db_session.query(AuditLog).filter_by(action="user.created").first()
    assert log is not None


def test_list_users(db_session):
    create_user(db_session)
    create_user(db_session, email="other@example.com")
    assert len(list_users(db_session)) == 2


def test_get_user_by_email(db_session):
    created = create_user(db_session, email="findme@example.com")
    found = get_user_by_email(db_session, "findme@example.com")
    assert found is not None
    assert found.id == created.id
    assert get_user_by_email(db_session, "nonexistent@example.com") is None


def test_email_exists(db_session):
    repo = UserRepository(db_session)
    create_user(db_session, email="exists@example.com")
    db_session.commit()
    assert repo.email_exists("exists@example.com") is True
    assert repo.email_exists("noone@example.com") is False
