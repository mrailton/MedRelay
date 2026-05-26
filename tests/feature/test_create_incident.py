from app.db.models.audit_log import AuditLog
from app.services.incidents import create_incident
from tests.factories import create_event, create_user


def test_create_incident_action_creates_incident_and_audit_log(db_session):
    event = create_event(db_session)
    user = create_user(db_session)

    incident = create_incident(
        db_session,
        event,
        {
            "reference": "INC-001",
            "location": "Test Location",
            "priority": "P1",
            "category": "medical",
            "description": "Test incident description",
        },
        user,
    )
    db_session.commit()

    assert incident.reference == "INC-001"
    assert incident.status == "NEW"
    assert incident.event_id == event.id

    log = (
        db_session.query(AuditLog)
        .filter_by(action="incident.created", entity_id=str(incident.id))
        .first()
    )
    assert log is not None
