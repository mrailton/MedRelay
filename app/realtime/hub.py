import asyncio
import json
from collections import defaultdict
from typing import Any


class RealtimeHub:
    """In-process SSE pub/sub keyed by channel name."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[str]]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(self, channel: str) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue()
        async with self._lock:
            self._subscribers[channel].append(queue)
        return queue

    async def unsubscribe(self, channel: str, queue: asyncio.Queue[str]) -> None:
        async with self._lock:
            subs = self._subscribers.get(channel, [])
            if queue in subs:
                subs.remove(queue)
            if not subs and channel in self._subscribers:
                del self._subscribers[channel]

    def clear(self) -> None:
        """Remove all subscribers and drain pending queues for clean shutdown."""
        for channel, queues in self._subscribers.items():
            for queue in queues:
                while not queue.empty():
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
        self._subscribers.clear()

    def publish_sync(self, channel: str, event: str, data: dict[str, Any]) -> None:
        """Publish from sync code (e.g. after DB commit in services)."""
        message = self._format_sse(event, data)
        for queue in list(self._subscribers.get(channel, [])):
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                pass

    @staticmethod
    def _format_sse(event: str, data: dict[str, Any]) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    @staticmethod
    def incident_channel(event_id: int) -> str:
        return f"event.{event_id}.incidents"

    @staticmethod
    def resource_channel(event_id: int) -> str:
        return f"event.{event_id}.resources"


realtime_hub = RealtimeHub()
