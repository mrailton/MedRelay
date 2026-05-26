from medrelay.realtime.hub import realtime_hub
from medrelay.serialization import incident_to_dict
from tests.factories import create_event, make_incident


def test_incident_channel_name():
    event = type("E", (), {"id": 5})()
    assert realtime_hub.incident_channel(5) == "event.5.incidents"


def test_publish_payload_shape(db_session):
    event = create_event(db_session)
    incident = make_incident(db_session, event)
    payload = {"incident": incident_to_dict(incident)}
    assert "incident" in payload
    assert "resources" in payload["incident"]
    assert "notes" in payload["incident"]
