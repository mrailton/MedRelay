import asyncio

from app.realtime.hub import realtime_hub
from app.serialization import incident_to_dict
from tests.factories import create_event, make_incident


def test_incident_channel_name():
    type("E", (), {"id": 5})()
    assert realtime_hub.incident_channel(5) == "event.5.incidents"


def test_resource_channel_name():
    assert realtime_hub.resource_channel(3) == "event.3.resources"


def test_publish_payload_shape(db_session, organisation):
    event = create_event(db_session, organisation=organisation)
    incident = make_incident(db_session, event)
    payload = {"incident": incident_to_dict(incident)}
    assert "incident" in payload
    assert "resources" in payload["incident"]
    assert "notes" in payload["incident"]


def test_subscribe_unsubscribe():
    ch = "test.channel"

    async def run():
        q = await realtime_hub.subscribe(ch)
        assert q is not None
        assert len(realtime_hub._subscribers[ch]) == 1
        await realtime_hub.unsubscribe(ch, q)
        assert ch not in realtime_hub._subscribers

    asyncio.run(run())


def test_publish_sync_delivers_message():
    ch = "test.deliver"

    async def run():
        q = await realtime_hub.subscribe(ch)
        realtime_hub.publish_sync(ch, "test.event", {"key": "value"})
        msg = await asyncio.wait_for(q.get(), timeout=1.0)
        assert "test.event" in msg
        assert "key" in msg
        await realtime_hub.unsubscribe(ch, q)

    asyncio.run(run())


def test_publish_sync_queue_full_does_not_raise():
    """When a queue is full, publish_sync silently drops the message."""
    ch = "test.full"

    async def run():
        q = asyncio.Queue(maxsize=0)
        realtime_hub._subscribers[ch] = [q]
        # Should not raise even though queue is full
        realtime_hub.publish_sync(ch, "test.event", {"x": "y"})
        # Clean up
        await realtime_hub.unsubscribe(ch, q)

    asyncio.run(run())


def test_format_sse():
    msg = realtime_hub._format_sse("myevent", {"foo": "bar"})
    assert "event: myevent" in msg
    assert "data:" in msg
    assert "foo" in msg
