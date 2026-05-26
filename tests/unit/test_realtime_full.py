import asyncio
import json

from app.realtime.hub import realtime_hub


def test_resource_channel_name():
    assert realtime_hub.resource_channel(3) == "event.3.resources"


def test_subscribe_and_unsubscribe():
    async def run():
        queue = await realtime_hub.subscribe("test-channel")
        assert queue is not None
        assert realtime_hub._subscribers["test-channel"] == [queue]
        await realtime_hub.unsubscribe("test-channel", queue)
        assert "test-channel" not in realtime_hub._subscribers

    asyncio.run(run())


def test_unsubscribe_nonexistent_queue():
    async def run():
        queue: asyncio.Queue[str] = asyncio.Queue()
        await realtime_hub.unsubscribe("no-such-channel", queue)

    asyncio.run(run())


def test_publish_sync_delivers_to_subscriber():
    received = []

    async def run():
        queue = await realtime_hub.subscribe("pub-test")
        realtime_hub.publish_sync("pub-test", "myevent", {"key": "val"})
        msg = await asyncio.wait_for(queue.get(), timeout=1.0)
        received.append(msg)
        await realtime_hub.unsubscribe("pub-test", queue)

    asyncio.run(run())
    assert len(received) == 1
    data = received[0]
    assert "event: myevent" in data
    assert "key" in json.loads(data.split("data: ")[1].strip())


def test_publish_sync_no_subscribers():
    realtime_hub.publish_sync("empty-channel", "test", {"a": 1})


def test_format_sse():
    msg = realtime_hub._format_sse("update", {"id": 1})
    assert msg == 'event: update\ndata: {"id": 1}\n\n'
