<?php

declare(strict_types=1);

namespace Tests\Unit;

use App\Models\Resource;
use App\Models\Staff;

test('staff has full name accessor', function (): void {
    $staff = Staff::factory()->create([
        'first_name' => 'John',
        'last_name' => 'Doe',
    ]);

    expect($staff->full_name)->toBe('John Doe');
});

test('staff can have resources', function (): void {
    $staff = Staff::factory()->create();
    $resource = Resource::factory()->create();

    $staff->resources()->attach($resource->id);

    expect($staff->resources)->toHaveCount(1)
        ->and($staff->resources->first()->id)->toBe($resource->id);
});
