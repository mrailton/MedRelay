<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Event;
use App\Models\Incident;

test('dashboard shows active events', function (): void {
    login();
    $event = Event::factory()->create(['is_active' => true]);

    $response = $this->get('/');

    $response->assertStatus(200);
    $response->assertSee($event->name);
});

test('dashboard can filter by event', function (): void {
    login();
    $event = Event::factory()->create(['is_active' => true]);
    $incident = Incident::factory()->create([
        'event_id' => $event->id,
    ]);

    $response = $this->get('/?event_id=' . $event->id);

    $response->assertStatus(200);
    $response->assertSee($incident->reference);
});

test('dashboard handles ajax request', function (): void {
    login();
    $this->get('/', ['X-Requested-With' => 'XMLHttpRequest'])
        ->assertNoContent();
});

test('dashboard clears event filter when empty event_id provided', function (): void {
    login();
    session(['selected_event_id' => 999]);
    $this->get('/?event_id=')
        ->assertStatus(200);
});
