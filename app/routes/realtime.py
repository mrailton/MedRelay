import asyncio
import json

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse

from app.dependencies import CurrentUser
from app.realtime.hub import realtime_hub

router = APIRouter(prefix="/realtime", tags=["realtime"])


@router.get("/events", name="realtime.events")
async def realtime_events(
    request: Request,
    user: CurrentUser,
    event_id: int = Query(...),
    incident_id: int | None = Query(None),
):
    channels = [
        realtime_hub.incident_channel(event_id),
        realtime_hub.resource_channel(event_id),
    ]

    queues: list[asyncio.Queue[str]] = []
    try:
        for ch in channels:
            queues.append(await realtime_hub.subscribe(ch))
    except RuntimeError as exc:
        for ch, q in zip(channels, queues, strict=False):
            await realtime_hub.unsubscribe(ch, q)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    async def event_generator():
        try:
            yield ": connected\n\n"
            while True:
                if await request.is_disconnected():
                    break
                for queue in queues:
                    try:
                        message = await asyncio.wait_for(queue.get(), timeout=30.0)
                        if incident_id is not None and "incident.updated" in message:
                            data_line = [line for line in message.split("\n") if line.startswith("data: ")]
                            if data_line:
                                payload = json.loads(data_line[0][6:])
                                inc = payload.get("incident", {})
                                if inc.get("id") != incident_id:
                                    continue
                        yield message
                    except TimeoutError:
                        yield ": keepalive\n\n"
        finally:
            for ch, q in zip(channels, queues, strict=True):
                await realtime_hub.unsubscribe(ch, q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
