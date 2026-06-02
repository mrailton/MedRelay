import re

from app.repositories.organisation import OrganisationRepository
from tests.factories import create_organisation, create_user


def _login_as_admin(client, db_session, organisation):
    user = create_user(db_session, role="ADMIN", email="admin@org.example.com", organisation=organisation)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"organisation_code": organisation.code, "email": user.email, "password": "password", "csrf_token": csrf})
    return user


def _csrf(client):
    return re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)


def test_organisations_index(client, db_session):
    org = create_organisation(db_session, code="default", name="Default Org")
    _login_as_admin(client, db_session, org)
    response = client.get("/admin/organisations")
    assert response.status_code == 200


def test_organisations_index_requires_default_org_admin(client, db_session):
    org = create_organisation(db_session, code="notdefault", name="Not Default")
    create_user(db_session, role="ADMIN", email="nd@example.com", organisation=org)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', client.get("/login").text).group(1)
    client.post("/login", data={"organisation_code": org.code, "email": "nd@example.com", "password": "password", "csrf_token": csrf})
    response = client.get("/admin/organisations", follow_redirects=False)
    assert response.status_code == 403


def test_organisations_create_get(client, db_session):
    org = create_organisation(db_session, code="default", name="Default Org")
    _login_as_admin(client, db_session, org)
    response = client.get("/admin/organisations/create")
    assert response.status_code == 200


def test_organisations_store_success(client, db_session):
    org = create_organisation(db_session, code="default", name="Default Org")
    _login_as_admin(client, db_session, org)
    csrf = _csrf(client)
    response = client.post(
        "/admin/organisations",
        data={"code": "neworg", "name": "New Organisation", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
    repo = OrganisationRepository(db_session)
    created = repo.get_by_code("neworg")
    assert created is not None
    assert created.name == "New Organisation"


def test_organisations_store_duplicate_code(client, db_session):
    org = create_organisation(db_session, code="default", name="Default Org")
    create_organisation(db_session, code="existing", name="Existing")
    _login_as_admin(client, db_session, org)
    csrf = _csrf(client)
    response = client.post(
        "/admin/organisations",
        data={"code": "existing", "name": "Duplicate", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert "already exists" in response.text


def test_organisations_edit_found(client, db_session):
    default = create_organisation(db_session, code="default", name="Default Org")
    target = create_organisation(db_session, code="editable", name="Editable Org")
    _login_as_admin(client, db_session, default)
    response = client.get(f"/admin/organisations/{target.id}/edit")
    assert response.status_code == 200
    assert "Editable Org" in response.text


def test_organisations_edit_not_found(client, db_session):
    org = create_organisation(db_session, code="default", name="Default Org")
    _login_as_admin(client, db_session, org)
    response = client.get("/admin/organisations/9999/edit", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/organisations"


def test_organisations_update_success(client, db_session):
    org = create_organisation(db_session, code="default", name="Default Org")
    target = create_organisation(db_session, code="oldcode", name="Old Name")
    _login_as_admin(client, db_session, org)
    csrf = _csrf(client)
    response = client.post(
        f"/admin/organisations/{target.id}",
        data={"code": "newcode", "name": "New Name", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
    db_session.expire_all()
    repo = OrganisationRepository(db_session)
    updated = repo.get(target.id)
    assert updated is not None
    assert updated.code == "newcode"
    assert updated.name == "New Name"


def test_organisations_update_duplicate_code(client, db_session):
    default = create_organisation(db_session, code="default", name="Default Org")
    target = create_organisation(db_session, code="unique", name="Unique")
    create_organisation(db_session, code="taken", name="Taken")
    _login_as_admin(client, db_session, default)
    csrf = _csrf(client)
    response = client.post(
        f"/admin/organisations/{target.id}",
        data={"code": "taken", "name": "Unique", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert "already exists" in response.text


def test_organisations_update_not_found(client, db_session):
    org = create_organisation(db_session, code="default", name="Default Org")
    _login_as_admin(client, db_session, org)
    csrf = _csrf(client)
    response = client.post(
        "/admin/organisations/9999",
        data={"code": "nope", "name": "Gone", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303
