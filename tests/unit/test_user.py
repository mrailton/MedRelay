from app.db.models.user import User
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


def test_user_is_admin_with_org_id(db_session):
    org = create_organisation(db_session, code="test")
    admin = create_user(db_session, role=UserRole.ADMIN.value, organisation=org)
    assert admin.is_admin(org.id) is True


def test_user_is_controller_with_org_id(db_session):
    org = create_organisation(db_session, code="test")
    user = create_user(db_session, role=UserRole.CONTROLLER.value, organisation=org)
    assert user.is_controller(org.id) is True


def test_user_is_read_only_with_org_id(db_session):
    org = create_organisation(db_session, code="test")
    user = create_user(db_session, role=UserRole.READ_ONLY.value, organisation=org)
    assert user.is_read_only(org.id) is True
    assert user.is_controller(org.id) is False
    assert user.is_admin(org.id) is False


def test_user_org_role_detached():
    user = User(
        name="Detached",
        email="detached@example.com",
        password="x",
        role=UserRole.CONTROLLER.value,
    )
    assert user.user_role == UserRole.CONTROLLER
    assert user.is_admin(None) is False
    assert user.is_controller(None) is True
    assert user.is_read_only(None) is False


def test_user_get_role(db_session):
    org = create_organisation(db_session, code="test")
    admin = create_user(db_session, role=UserRole.ADMIN.value, organisation=org)
    assert admin.get_role(org.id) == UserRole.ADMIN


def test_user_get_role_fallback_when_no_session():
    user = User(
        name="NoSession",
        email="nosession@example.com",
        password="x",
        role=UserRole.CONTROLLER.value,
    )
    role = user.get_role(1)
    assert role == UserRole.CONTROLLER


def test_user_role_property(db_session):
    org = create_organisation(db_session, code="test")
    user = create_user(db_session, role=UserRole.READ_ONLY.value, organisation=org)
    assert user.user_role == UserRole.READ_ONLY


def test_user_email_verified_at_defaults_none(db_session):
    org = create_organisation(db_session, code="test")
    user = create_user(db_session, organisation=org)
    assert user.email_verified_at is None


def test_user_remember_token_defaults_none(db_session):
    org = create_organisation(db_session, code="test")
    user = create_user(db_session, organisation=org)
    assert user.remember_token is None


def test_organisation_is_default(db_session):
    default = create_organisation(db_session, code="default", name="Default")
    other = create_organisation(db_session, code="other", name="Other")
    assert default.is_default is True
    assert other.is_default is False
    org = create_organisation(db_session, code="test")
    user = create_user(db_session, organisation=org)
    assert user.remember_token is None
