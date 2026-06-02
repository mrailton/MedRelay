from app.enums import UserRole
from app.repositories.organisation import OrganisationRepository
from app.repositories.session import create_session
from tests.factories import create_organisation, create_user


def test_org_repo_get(db_session):
    org = create_organisation(db_session, code="gettest", name="Get Test")
    repo = OrganisationRepository(db_session)
    assert repo.get(org.id) is not None
    assert repo.get(org.id).id == org.id
    assert repo.get(9999) is None


def test_org_repo_list_all(db_session):
    create_organisation(db_session, code="aaa", name="A Org")
    create_organisation(db_session, code="bbb", name="B Org")
    repo = OrganisationRepository(db_session)
    orgs = repo.list_all()
    assert len(orgs) == 2
    assert orgs[0].name <= orgs[1].name


def test_org_repo_get_default(db_session):
    default = create_organisation(db_session, code="default", name="Default")
    create_organisation(db_session, code="other", name="Other")
    repo = OrganisationRepository(db_session)
    result = repo.get_default()
    assert result is not None
    assert result.id == default.id


def test_org_repo_get_default_none(db_session):
    repo = OrganisationRepository(db_session)
    assert repo.get_default() is None


def test_org_repo_create(db_session):
    repo = OrganisationRepository(db_session)
    org = repo.create(code="neworg", name="New Organisation")
    db_session.commit()
    assert org.id is not None
    assert org.code == "neworg"
    assert org.name == "New Organisation"
    assert org.created_at is not None


def test_org_repo_update(db_session):
    org = create_organisation(db_session, code="old", name="Old Name")
    repo = OrganisationRepository(db_session)
    result = repo.update(org.id, code="new", name="New Name")
    db_session.commit()
    assert result is not None
    assert result.code == "new"
    assert result.name == "New Name"


def test_org_repo_update_not_found(db_session):
    repo = OrganisationRepository(db_session)
    assert repo.update(9999, code="x", name="X") is None


def test_org_repo_does_user_belong(db_session):
    org = create_organisation(db_session, code="testorg")
    user = create_user(db_session, organisation=org)
    repo = OrganisationRepository(db_session)
    assert repo.does_user_belong(user.id, org.id) is True
    assert repo.does_user_belong(9999, org.id) is False


def test_org_repo_add_user(db_session):
    org = create_organisation(db_session, code="testorg")
    user = create_user(db_session)
    repo = OrganisationRepository(db_session)
    repo.add_user(user.id, org.id, role=UserRole.CONTROLLER.value)
    db_session.commit()
    assert repo.does_user_belong(user.id, org.id) is True


def test_org_repo_get_user_role(db_session):
    org = create_organisation(db_session, code="testorg")
    user = create_user(db_session, role=UserRole.ADMIN.value, organisation=org)
    repo = OrganisationRepository(db_session)
    assert repo.get_user_role(user.id, org.id) == UserRole.ADMIN.value
    assert repo.get_user_role(9999, org.id) is None


def test_org_repo_set_user_role(db_session):
    org = create_organisation(db_session, code="testorg")
    user = create_user(db_session, role=UserRole.CONTROLLER.value, organisation=org)
    repo = OrganisationRepository(db_session)
    repo.set_user_role(user.id, org.id, UserRole.READ_ONLY.value)
    db_session.commit()
    assert repo.get_user_role(user.id, org.id) == UserRole.READ_ONLY.value


def test_org_repo_get_by_code(db_session):
    org = create_organisation(db_session, code="bycode", name="By Code")
    repo = OrganisationRepository(db_session)
    assert repo.get_by_code("bycode") is not None
    assert repo.get_by_code("bycode").id == org.id
    assert repo.get_by_code("nonexistent") is None


def test_create_session(db_session):
    sess = create_session()
    assert sess is not None
    assert sess.is_active
    sess.close()
