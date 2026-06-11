from app.actions import events, staff
from app.web.responses import ActionResult
from tests.factories import create_organisation, create_user


def test_open_create_event_denied_for_read_only(db_session):
    org = create_organisation(db_session)
    user = create_user(db_session, role="READ_ONLY", organisation=org)
    result = events.open_create_form(user)
    assert isinstance(result, ActionResult)
    assert result.redirect_url == "/events"


def test_open_create_event_allowed_for_controller(db_session):
    org = create_organisation(db_session)
    user = create_user(db_session, role="CONTROLLER", organisation=org)
    result = events.open_create_form(user)
    assert result.redirect_url == "/events?create=1"


def test_open_create_staff_denied_for_read_only(db_session):
    org = create_organisation(db_session)
    user = create_user(db_session, role="READ_ONLY", organisation=org)
    result = staff.open_create_form(user)
    assert result.redirect_url == "/staff"
