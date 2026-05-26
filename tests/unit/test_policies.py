from medrelay import policies
from medrelay.enums import UserRole
from tests.factories import create_user


def test_admin_can_view_users(db_session):
    admin = create_user(db_session, role=UserRole.ADMIN.value)
    readonly = create_user(db_session, role=UserRole.READ_ONLY.value)
    assert policies.can_view_any_user(admin)
    assert not policies.can_view_any_user(readonly)


def test_controller_can_create_incident(db_session):
    controller = create_user(db_session, role=UserRole.CONTROLLER.value)
    readonly = create_user(db_session, role=UserRole.READ_ONLY.value)
    assert policies.can_create_incident(controller)
    assert not policies.can_create_incident(readonly)
