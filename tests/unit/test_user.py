from app.enums import UserRole
from tests.factories import create_organisation, create_user


def test_user_role_helpers(db_session):
    org = create_organisation(db_session, code="test")
    admin = create_user(db_session, role=UserRole.ADMIN.value, organisation=org)
    controller = create_user(db_session, role=UserRole.CONTROLLER.value, organisation=org)
    readonly = create_user(db_session, role=UserRole.READ_ONLY.value, organisation=org)
    assert admin.is_admin()
    assert controller.is_controller()
    assert readonly.is_read_only()
