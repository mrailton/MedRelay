from app.enums import UserRole
from tests.factories import create_user


def test_user_role_helpers(db_session):
    admin = create_user(db_session, role=UserRole.ADMIN.value)
    controller = create_user(db_session, role=UserRole.CONTROLLER.value)
    readonly = create_user(db_session, role=UserRole.READ_ONLY.value)
    assert admin.is_admin()
    assert controller.is_controller()
    assert readonly.is_read_only()
