<?php

namespace Tests\Feature;

use App\Models\Event;
use App\Models\Resource;
use App\Models\Staff;

test('controller can create resource', function () {
    login();
    $event = Event::factory()->create();

    $this->post('/events/' . $event->id . '/resources', [
        'name' => 'Ambulance 1',
        'resource_type' => 'ambulance',
    ])->assertSessionHas('success');

    $this->assertDatabaseHas('resources', [
        'event_id' => $event->id,
        'name' => 'Ambulance 1',
    ]);
});

test('resource show page displays details', function () {
    login();
    $resource = Resource::factory()->create();

    $this->get('/resources/' . $resource->id)
        ->assertStatus(200)
        ->assertSee($resource->name);
});

test('controller can update resource status', function () {
    login();
    $resource = Resource::factory()->create();

    $this->post('/resources/' . $resource->id . '/status', [
        'status' => 'out_of_service',
    ])->assertSessionHas('success');

    $this->assertDatabaseHas('resources', [
        'id' => $resource->id,
        'status' => 'out_of_service',
    ]);
});

test('controller can assign staff to resource', function () {
    login();
    $event = Event::factory()->create();
    $resource = Resource::factory()->create(['event_id' => $event->id]);
    $staff = Staff::factory()->create();

    $this->post('/resources/' . $resource->id . '/assign-staff', [
        'staff_id' => $staff->id,
    ])->assertSessionHas('success');

    $this->assertDatabaseHas('resource_staff', [
        'resource_id' => $resource->id,
        'staff_id' => $staff->id,
    ]);
});
