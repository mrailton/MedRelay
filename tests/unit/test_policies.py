from app import policies
from app.enums import UserRole
from tests.factories import create_organisation, create_user


def _make_org(db_session):
    return create_organisation(db_session, code="test")


def test_admin_can_view_users(db_session):
    org = _make_org(db_session)
    admin = create_user(db_session, role=UserRole.ADMIN.value, organisation=org)
    readonly = create_user(db_session, role=UserRole.READ_ONLY.value, organisation=org)
    assert policies.can_view_any_user(admin)
    assert not policies.can_view_any_user(readonly)


def test_controller_can_create_incident(db_session):
    org = _make_org(db_session)
    controller = create_user(db_session, role=UserRole.CONTROLLER.value, organisation=org)
    readonly = create_user(db_session, role=UserRole.READ_ONLY.value, organisation=org)
    assert policies.can_create_incident(controller)
    assert not policies.can_create_incident(readonly)
