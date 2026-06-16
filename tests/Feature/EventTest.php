<?php

namespace Tests\Feature;

use App\Models\Event;

test('events index page is accessible', function () {
    login();
    $this->get('/events')->assertStatus(200);
});

test('controller can create event', function () {
    $user = \App\Models\User::factory()->create();

    login($user);

    $this->post('/events', [
        'name' => 'Test Event',
        'location' => 'Test Location',
        'start_time' => now()->addHour()->format('Y-m-d\TH:i'),
        'is_active' => true,
    ])->assertRedirect('/events');

    $this->assertDatabaseHas('events', [
        'name' => 'Test Event',
        'location' => 'Test Location',
    ]);
});

test('event show page displays details', function () {
    login();
    $event = Event::factory()->create();

    $this->get('/events/' . $event->id)
        ->assertStatus(200)
        ->assertSee($event->name);
});

test('controller can update event', function () {
    login();
    $event = Event::factory()->create();

    $this->post('/events/' . $event->id, [
        'name' => 'Updated Name',
        'location' => $event->location,
        'start_time' => $event->start_time->format('Y-m-d\TH:i'),
        'is_active' => $event->is_active,
    ])->assertRedirect('/events/' . $event->id);

    $this->assertDatabaseHas('events', [
        'id' => $event->id,
        'name' => 'Updated Name',
    ]);
});
