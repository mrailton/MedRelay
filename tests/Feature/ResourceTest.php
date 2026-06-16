<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Event;
use App\Models\Resource;
use App\Models\Staff;

test('controller can create resource', function (): void {
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

test('resource show page displays details', function (): void {
    login();
    $resource = Resource::factory()->create();

    $this->get('/resources/' . $resource->id)
        ->assertStatus(200)
        ->assertSee($resource->name);
});

test('controller can update resource status', function (): void {
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

test('controller can assign staff to resource', function (): void {
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

test('controller cannot assign already assigned staff to resource', function (): void {
    login();
    $event = Event::factory()->create();
    $resource = Resource::factory()->create(['event_id' => $event->id]);
    $staff = Staff::factory()->create();

    $resource->staff()->attach($staff->id);

    $this->post('/resources/' . $resource->id . '/assign-staff', [
        'staff_id' => $staff->id,
    ])->assertSessionHas('error');
});

test('controller can remove staff from resource', function (): void {
    login();
    $event = Event::factory()->create();
    $resource = Resource::factory()->create(['event_id' => $event->id]);
    $staff = Staff::factory()->create();

    $resource->staff()->attach($staff->id);
    $resource->recalculateCapability();

    $this->post('/resources/' . $resource->id . '/remove-staff', [
        'staff_id' => $staff->id,
    ])->assertSessionHas('success');

    $this->assertDatabaseMissing('resource_staff', [
        'resource_id' => $resource->id,
        'staff_id' => $staff->id,
    ]);
});

test('resource index page is accessible', function (): void {
    login();
    $event = Event::factory()->create();

    $this->get('/events/' . $event->id . '/resources')
        ->assertStatus(200);
});

test('controller can create resource with staff', function (): void {
    login();
    $event = Event::factory()->create();
    $staff = Staff::factory()->create();

    $this->post('/events/' . $event->id . '/resources', [
        'name' => 'Ambulance 2',
        'resource_type' => 'ambulance',
        'staff_ids' => [$staff->id],
    ])->assertSessionHas('success');

    $this->assertDatabaseHas('resource_staff', [
        'staff_id' => $staff->id,
    ]);
});
