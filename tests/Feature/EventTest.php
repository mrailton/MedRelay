<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Event;
use App\Models\User;

test('events index page is accessible', function (): void {
    login();
    $this->get('/events')->assertStatus(200);
});

test('controller can create event', function (): void {
    $user = User::factory()->create();

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

test('event show page displays details', function (): void {
    login();
    $event = Event::factory()->create();

    $this->get('/events/' . $event->id)
        ->assertStatus(200)
        ->assertSee($event->name);
});

test('event edit page is accessible', function (): void {
    login();
    $event = Event::factory()->create();

    $this->get('/events/' . $event->id . '/edit')
        ->assertStatus(200)
        ->assertSee($event->name);
});

test('controller can update event', function (): void {
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
