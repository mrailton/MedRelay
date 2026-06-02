from app.repositories.incident import IncidentRepository
from app.repositories.resource import ResourceRepository
from tests.factories import create_event, create_organisation, make_incident


def test_list_incidents_by_event_scoped_to_organisation(db_session):
    org_a = create_organisation(db_session, code="lista", name="Org A")
    org_b = create_organisation(db_session, code="listb", name="Org B")
    event_a = create_event(db_session, organisation=org_a)
    event_b = create_event(db_session, organisation=org_b)
    incident_a = make_incident(db_session, event_a)
    make_incident(db_session, event_b)
    db_session.commit()

    repo = IncidentRepository(db_session)
    scoped = repo.list_by_event(event_a.id, organisation_id=org_a.id)
    assert len(scoped) == 1
    assert scoped[0].id == incident_a.id

    cross = repo.list_by_event(event_a.id, organisation_id=org_b.id)
    assert cross == []


def test_list_resources_by_event_scoped_to_organisation(db_session):
    from app.services.resources import create_resource
    from tests.factories import create_user

    org_a = create_organisation(db_session, code="reslista", name="Org A")
    org_b = create_organisation(db_session, code="reslistb", name="Org B")
    user_a = create_user(db_session, organisation=org_a)
    event_a = create_event(db_session, organisation=org_a)
    event_b = create_event(db_session, organisation=org_b)
    resource_a = create_resource(db_session, event_a, {"name": "A1", "resource_type": "AMBULANCE"}, user_a)
    create_resource(
        db_session,
        event_b,
        {"name": "B1", "resource_type": "AMBULANCE"},
        create_user(db_session, organisation=org_b),
    )
    db_session.commit()

    repo = ResourceRepository(db_session)
    scoped = repo.list_by_event(event_a.id, organisation_id=org_a.id)
    assert len(scoped) == 1
    assert scoped[0].id == resource_a.id

    cross = repo.list_by_event(event_a.id, organisation_id=org_b.id)
    assert cross == []
