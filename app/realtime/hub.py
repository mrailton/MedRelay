from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)

REDIS_BROADCAST_CHANNEL = "medrelay:realtime"


class RealtimeHub:
    """SSE pub/sub with optional Redis fan-out for multi-worker deployments."""

    def __init__(
        self,
        *,
        queue_maxsize: int = 64,
        max_subscribers_per_channel: int = 32,
        redis_url: str | None = None,
    ) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[str]]] = defaultdict(list)
        self._lock = asyncio.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._queue_maxsize = queue_maxsize
        self._max_subscribers = max_subscribers_per_channel
        self._redis_url = redis_url.strip() if redis_url else None
        self._redis_client: Any = None
        self._redis_listener_task: asyncio.Task[None] | None = None

        if self._redis_url:
            import redis

            self._redis_client = redis.from_url(self._redis_url, decode_responses=True)

    @property
    def redis_enabled(self) -> bool:
        return self._redis_client is not None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def start(self) -> None:
        if not self.redis_enabled or self._redis_listener_task is not None:
            return
        self._redis_listener_task = asyncio.create_task(self._run_redis_listener())

    async def stop(self) -> None:
        if self._redis_listener_task is not None:
            self._redis_listener_task.cancel()
            try:
                await self._redis_listener_task
            except asyncio.CancelledError:
                pass
            self._redis_listener_task = None
        self.clear()

    async def subscribe(self, channel: str) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=self._queue_maxsize)
        async with self._lock:
            if len(self._subscribers[channel]) >= self._max_subscribers:
                raise RuntimeError(f"Realtime channel {channel!r} is at capacity")
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
        for queues in self._subscribers.values():
            for queue in queues:
                while not queue.empty():
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
        self._subscribers.clear()

    def publish_sync(self, channel: str, event: str, data: dict[str, Any]) -> None:
        message = self._format_sse(event, data)
        self._schedule_local_delivery(channel, message)
        if self._redis_client is not None:
            payload = json.dumps({"channel": channel, "message": message})
            try:
                self._redis_client.publish(REDIS_BROADCAST_CHANNEL, payload)
            except Exception:
                logger.exception("Redis realtime publish failed")

    def _schedule_local_delivery(self, channel: str, message: str) -> None:
        loop = self._loop
        if loop is not None and loop.is_running():
            loop.call_soon_threadsafe(self._put_to_subscribers, channel, message)
        else:
            self._put_to_subscribers(channel, message)

    def _put_to_subscribers(self, channel: str, message: str) -> None:
        for queue in list(self._subscribers.get(channel, [])):
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                pass

    async def _run_redis_listener(self) -> None:
        import redis.asyncio as aioredis

        client = aioredis.from_url(self._redis_url or "", decode_responses=True)
        pubsub = client.pubsub()
        await pubsub.subscribe(REDIS_BROADCAST_CHANNEL)
        try:
            async for raw in pubsub.listen():
                if raw["type"] != "message":
                    continue
                payload = json.loads(raw["data"])
                self._put_to_subscribers(payload["channel"], payload["message"])
        finally:
            await pubsub.unsubscribe(REDIS_BROADCAST_CHANNEL)
            await pubsub.close()
            await client.close()

    def status(self) -> dict[str, Any]:
        channel_counts = {ch: len(subs) for ch, subs in self._subscribers.items()}
        redis_status: dict[str, Any] = {"enabled": self.redis_enabled}
        if self._redis_client is not None:
            try:
                self._redis_client.ping()
                redis_status["connected"] = True
            except Exception as exc:
                redis_status["connected"] = False
                redis_status["error"] = str(exc)
        return {
            "backend": "redis" if self.redis_enabled else "local",
            "local_channels": len(self._subscribers),
            "local_subscribers": sum(channel_counts.values()),
            "channel_subscribers": channel_counts,
            "redis": redis_status,
        }

    @staticmethod
    def _format_sse(event: str, data: dict[str, Any]) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    @staticmethod
    def incident_channel(event_id: int) -> str:
        return f"event.{event_id}.incidents"

    @staticmethod
    def resource_channel(event_id: int) -> str:
        return f"event.{event_id}.resources"


def create_realtime_hub() -> RealtimeHub:
    from app.config import get_settings

    settings = get_settings()
    return RealtimeHub(
        queue_maxsize=settings.realtime_queue_maxsize,
        max_subscribers_per_channel=settings.realtime_max_subscribers_per_channel,
        redis_url=settings.redis_url,
    )


realtime_hub = create_realtime_hub()
