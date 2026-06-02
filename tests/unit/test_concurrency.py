from __future__ import annotations

import asyncio

from app.realtime.hub import RealtimeHub
from app.repositories.incident import IncidentRepository
from app.services.incidents import assign_resource_to_incident, create_incident
from app.services.resources import create_resource
from tests.factories import create_event, create_user


def test_get_next_reference_increments_after_each_incident(db_session, organisation):
    event = create_event(db_session, organisation=organisation)
    repo = IncidentRepository(db_session)
    ref1 = repo.get_next_reference(event.id)
    repo.create(
        event_id=event.id,
        reference=ref1,
        location="A",
        priority="P1",
        category="medical",
        description="One",
        status="NEW",
    )
    db_session.flush()
    ref2 = repo.get_next_reference(event.id)
    assert ref1 != ref2
    assert ref1.startswith(str(event.id))
    assert ref2.startswith(str(event.id))


def test_create_incident_serial_unique_references(db_session, organisation):
    user = create_user(db_session, organisation=organisation, role="CONTROLLER")
    event = create_event(db_session, organisation=organisation)
    refs = []
    for _ in range(4):
        incident = create_incident(
            db_session,
            event,
            {
                "location": "A",
                "priority": "P1",
                "category": "medical",
                "description": "Test",
            },
            user,
            organisation_id=organisation.id,
        )
        refs.append(incident.reference)
    assert len(refs) == len(set(refs))


def test_assign_resource_under_lock_preserves_both_resources(db_session, organisation):
    user = create_user(db_session, organisation=organisation, role="CONTROLLER")
    event = create_event(db_session, organisation=organisation)
    incident = create_incident(
        db_session,
        event,
        {
            "location": "A",
            "priority": "P1",
            "category": "medical",
            "description": "Test",
        },
        user,
        organisation_id=organisation.id,
    )
    r1 = create_resource(db_session, event, {"name": "Unit 1", "resource_type": "AMBULANCE"}, user)
    r2 = create_resource(db_session, event, {"name": "Unit 2", "resource_type": "AMBULANCE"}, user)
    db_session.commit()

    assign_resource_to_incident(db_session, incident, [r1.id], user, organisation_id=organisation.id)
    db_session.commit()
    incident = IncidentRepository(db_session).get_with_event_resources_notes(incident.id, organisation.id)
    assign_resource_to_incident(db_session, incident, [r1.id, r2.id], user, organisation_id=organisation.id)
    db_session.commit()

    incident = IncidentRepository(db_session).get_with_event_resources_notes(incident.id, organisation.id)
    assert incident is not None
    assert {r.id for r in incident.resources} == {r1.id, r2.id}


def test_realtime_hub_thread_safe_publish():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    hub = RealtimeHub(queue_maxsize=8, max_subscribers_per_channel=16)
    hub.bind_loop(loop)

    async def consume():
        queue = await hub.subscribe("event.1.incidents")
        await asyncio.sleep(0.05)
        message = await asyncio.wait_for(queue.get(), timeout=1.0)
        await hub.unsubscribe("event.1.incidents", queue)
        return message

    async def run():
        task = asyncio.create_task(consume())
        hub.publish_sync("event.1.incidents", "incident.updated", {"incident": {"id": 1}})
        return await task

    message = loop.run_until_complete(run())
    loop.close()
    assert "incident.updated" in message


def test_realtime_subscriber_cap():
    hub = RealtimeHub(queue_maxsize=4, max_subscribers_per_channel=2)

    async def run():
        await hub.subscribe("cap")
        await hub.subscribe("cap")
        try:
            await hub.subscribe("cap")
            raise AssertionError("expected capacity error")
        except RuntimeError:
            pass

    asyncio.run(run())
