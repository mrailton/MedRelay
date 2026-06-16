<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Event;
use App\Models\Incident;
use App\Models\Resource;

test('incidents index page is accessible', function (): void {
    login();
    $event = Event::factory()->create();

    $this->get('/events/' . $event->id . '/incidents')
        ->assertStatus(200);
});

test('controller can create incident', function (): void {
    login();
    $event = Event::factory()->create();

    $this->post('/events/' . $event->id . '/incidents', [
        'location' => 'Incident Location',
        'priority' => 'P1',
        'category' => 'medical',
        'description' => 'Test incident description',
    ])->assertSessionHas('success');

    $this->assertDatabaseHas('incidents', [
        'event_id' => $event->id,
        'location' => 'Incident Location',
    ]);
});

test('incident show page displays details', function (): void {
    login();
    $incident = Incident::factory()->create();

    $this->get('/incidents/' . $incident->id)
        ->assertStatus(200)
        ->assertSee($incident->reference);
});

test('controller can update incident status', function (): void {
    login();
    $incident = Incident::factory()->create(['status' => 'new']);

    $this->post('/incidents/' . $incident->id . '/status', [
        'status' => 'dispatched',
    ])->assertSessionHas('success');

    $this->assertDatabaseHas('incidents', [
        'id' => $incident->id,
        'status' => 'dispatched',
    ]);
});

test('controller can assign resource to incident', function (): void {
    login();
    $event = Event::factory()->create();
    $incident = Incident::factory()->create(['event_id' => $event->id]);
    $resource = Resource::factory()->create(['event_id' => $event->id]);

    $this->post('/incidents/' . $incident->id . '/assign-resource', [
        'resource_id' => $resource->id,
    ])->assertSessionHas('success');

    $this->assertDatabaseHas('incident_resource', [
        'incident_id' => $incident->id,
        'resource_id' => $resource->id,
    ]);
});

test('controller can add note to incident', function (): void {
    login();
    $incident = Incident::factory()->create();

    $this->post('/incidents/' . $incident->id . '/notes', [
        'content' => 'Test note content',
    ])->assertSessionHas('success');

    $this->assertDatabaseHas('incident_notes', [
        'incident_id' => $incident->id,
        'content' => 'Test note content',
    ]);
});

test('controller can unassign resource from incident', function (): void {
    login();
    $event = Event::factory()->create();
    $incident = Incident::factory()->create(['event_id' => $event->id]);
    $resource = Resource::factory()->create(['event_id' => $event->id]);

    $incident->resources()->attach($resource->id);

    $this->post('/incidents/' . $incident->id . '/assign-resource', [
        'resource_id' => $resource->id,
    ])->assertSessionHas('success', 'Resource unassigned.');

    $this->assertDatabaseMissing('incident_resource', [
        'incident_id' => $incident->id,
        'resource_id' => $resource->id,
    ]);
});

test('updating incident to dispatched sets assigned resources status', function (): void {
    login();
    $event = Event::factory()->create();
    $incident = Incident::factory()->create(['event_id' => $event->id, 'status' => 'new']);
    $resource = Resource::factory()->create(['event_id' => $event->id, 'status' => 'available']);

    $incident->resources()->attach($resource->id);

    $this->post('/incidents/' . $incident->id . '/status', [
        'status' => 'dispatched',
    ])->assertSessionHas('success');

    $this->assertDatabaseHas('resources', [
        'id' => $resource->id,
        'status' => 'assigned',
    ]);
});

test('updating incident to complete sets assigned resources to available', function (): void {
    login();
    $event = Event::factory()->create();
    $incident = Incident::factory()->create(['event_id' => $event->id, 'status' => 'dispatched']);
    $resource = Resource::factory()->create(['event_id' => $event->id, 'status' => 'assigned']);

    $incident->resources()->attach($resource->id);

    $this->post('/incidents/' . $incident->id . '/status', [
        'status' => 'complete',
    ])->assertSessionHas('success');

    $this->assertDatabaseHas('resources', [
        'id' => $resource->id,
        'status' => 'available',
    ]);
});

test('assigning resource to new incident auto dispatches it', function (): void {
    login();
    $event = Event::factory()->create();
    $incident = Incident::factory()->create(['event_id' => $event->id, 'status' => 'new']);
    $resource = Resource::factory()->create(['event_id' => $event->id]);

    $this->post('/incidents/' . $incident->id . '/assign-resource', [
        'resource_id' => $resource->id,
    ])->assertSessionHas('success', 'Resource assigned.');

    $this->assertDatabaseHas('incidents', [
        'id' => $incident->id,
        'status' => 'dispatched',
    ]);
});
