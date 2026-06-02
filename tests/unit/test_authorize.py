import pytest

from app.policies import AuthorizationError, authorize
from tests.factories import create_organisation, create_user


def test_authorize_allows_controller_create_incident(db_session):
    org = create_organisation(db_session, code="authorg")
    user = create_user(db_session, role="CONTROLLER", organisation=org)
    authorize(user, "create", "incident", organisation_id=org.id)


def test_authorize_denies_read_only_create_incident(db_session):
    org = create_organisation(db_session, code="authorg2")
    user = create_user(db_session, role="READ_ONLY", organisation=org)
    with pytest.raises(AuthorizationError):
        authorize(user, "create", "incident", organisation_id=org.id)
