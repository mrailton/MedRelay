<?php

namespace Tests\Feature;

use App\Models\Event;
use App\Models\Incident;
use App\Models\Resource;

test('controller can create incident', function () {
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

test('incident show page displays details', function () {
    login();
    $incident = Incident::factory()->create();

    $this->get('/incidents/' . $incident->id)
        ->assertStatus(200)
        ->assertSee($incident->reference);
});

test('controller can update incident status', function () {
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

test('controller can assign resource to incident', function () {
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

test('controller can add note to incident', function () {
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
