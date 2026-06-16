<?php

namespace Tests\Feature;

use App\Models\Event;

test('dashboard shows active events', function () {
    login();
    $event = Event::factory()->create(['is_active' => true]);

    $response = $this->get('/');

    $response->assertStatus(200);
    $response->assertSee($event->name);
});

test('dashboard can filter by event', function () {
    login();
    $event = Event::factory()->create(['is_active' => true]);
    $incident = \App\Models\Incident::factory()->create([
        'event_id' => $event->id,
    ]);

    $response = $this->get('/?event_id=' . $event->id);

    $response->assertStatus(200);
    $response->assertSee($incident->reference);
});
