from app import policies
from app.enums import UserRole
from tests.factories import create_event, create_organisation, create_user


def _make_org(db_session, code="test"):
    return create_organisation(db_session, code=code)


def _make_user(db_session, role, org=None):
    if org is None:
        org = _make_org(db_session)
    return create_user(db_session, role=role, organisation=org)


def _make_event(db_session, org=None):
    if org is None:
        org = _make_org(db_session)
    return create_event(db_session, organisation=org)


def _setup(db_session):
    org = _make_org(db_session)
    return org


def test_can_view_any_event(db_session):
    org = _setup(db_session)
    user = _make_user(db_session, UserRole.READ_ONLY.value, org)
    assert policies.can_view_any_event(user) is True


def test_can_create_event(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    ro = _make_user(db_session, UserRole.READ_ONLY.value, org)
    assert policies.can_create_event(ctrl) is True
    assert policies.can_create_event(ro) is False


def test_can_update_event(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    ro = _make_user(db_session, UserRole.READ_ONLY.value, org)
    event = _make_event(db_session, org)
    assert policies.can_update_event(ctrl, event) is True
    assert policies.can_update_event(ro, event) is False


def test_can_delete_event(db_session):
    org = _setup(db_session)
    admin = _make_user(db_session, UserRole.ADMIN.value, org)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    event = _make_event(db_session, org)
    assert policies.can_delete_event(admin, event) is True
    assert policies.can_delete_event(ctrl, event) is False


def test_can_create_incident(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    ro = _make_user(db_session, UserRole.READ_ONLY.value, org)
    assert policies.can_create_incident(ctrl) is True
    assert policies.can_create_incident(ro) is False


def test_can_update_incident(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    ro = _make_user(db_session, UserRole.READ_ONLY.value, org)
    event = _make_event(db_session, org)
    incident = type("I", (), {"event_id": event.id})()
    assert policies.can_update_incident(ctrl, incident) is True
    assert policies.can_update_incident(ro, incident) is False


def test_can_update_incident_status(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    ro = _make_user(db_session, UserRole.READ_ONLY.value, org)
    assert policies.can_update_incident_status(ctrl, None) is True
    assert policies.can_update_incident_status(ro, None) is False


def test_can_assign_resource(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    ro = _make_user(db_session, UserRole.READ_ONLY.value, org)
    assert policies.can_assign_resource(ctrl, None) is True
    assert policies.can_assign_resource(ro, None) is False


def test_can_create_resource(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    ro = _make_user(db_session, UserRole.READ_ONLY.value, org)
    assert policies.can_create_resource(ctrl) is True
    assert policies.can_create_resource(ro) is False


def test_can_update_resource(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    ro = _make_user(db_session, UserRole.READ_ONLY.value, org)
    assert policies.can_update_resource(ctrl, None) is True
    assert policies.can_update_resource(ro, None) is False


def test_can_create_staff(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    ro = _make_user(db_session, UserRole.READ_ONLY.value, org)
    assert policies.can_create_staff(ctrl) is True
    assert policies.can_create_staff(ro) is False


def test_can_update_staff(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    ro = _make_user(db_session, UserRole.READ_ONLY.value, org)
    assert policies.can_update_staff(ctrl, object()) is True
    assert policies.can_update_staff(ro, object()) is False


def test_can_view_any_user(db_session):
    org = _setup(db_session)
    admin = _make_user(db_session, UserRole.ADMIN.value, org)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    assert policies.can_view_any_user(admin) is True
    assert policies.can_view_any_user(ctrl) is False


def test_can_create_user(db_session):
    org = _setup(db_session)
    admin = _make_user(db_session, UserRole.ADMIN.value, org)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    assert policies.can_create_user(admin) is True
    assert policies.can_create_user(ctrl) is False


# -- can() convenience gateway --------------------------------------------------


def test_can_admin_only(db_session):
    org = _setup(db_session)
    admin = _make_user(db_session, UserRole.ADMIN.value, org)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    assert policies.can(admin, "admin-only") is True
    assert policies.can(ctrl, "admin-only") is False


def test_can_subject_lookup(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    ro = _make_user(db_session, UserRole.READ_ONLY.value, org)
    assert policies.can(ctrl, "create", "incident") is True
    assert policies.can(ro, "create", "incident") is False


def test_can_mapping_fallback(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    result = policies.can(ctrl, "viewAny", "nonexistent")
    assert result is False


def test_can_with_object_event_update(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    ro = _make_user(db_session, UserRole.READ_ONLY.value, org)
    event = _make_event(db_session, org)
    assert policies.can(ctrl, "update", "event", event) is True
    assert policies.can(ro, "update", "event", event) is False


def test_can_with_object_incident_status(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    assert policies.can(ctrl, "updateStatus", "incident", object()) is True


def test_can_with_object_incident_assign(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    assert policies.can(ctrl, "assignResource", "incident", object()) is True


def test_can_with_object_incident_update(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    assert policies.can(ctrl, "update", "incident", object()) is True


def test_can_with_object_resource_update(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    assert policies.can(ctrl, "update", "resource", object()) is True


def test_can_with_object_unmatched_subject(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    assert policies.can(ctrl, "update", "staff", object()) is False


def test_can_subject_is_none(db_session):
    org = _setup(db_session)
    ctrl = _make_user(db_session, UserRole.CONTROLLER.value, org)
    assert policies.can(ctrl, "nonexistent") is False
