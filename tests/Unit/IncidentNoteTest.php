<?php

declare(strict_types=1);

namespace Tests\Unit;

use App\Models\Incident;
use App\Models\IncidentNote;
use App\Models\User;

test('incident note belongs to an incident', function (): void {
    $incident = Incident::factory()->create();
    $note = IncidentNote::create([
        'incident_id' => $incident->id,
        'user_id' => User::factory()->create()->id,
        'content' => 'Test note',
    ]);

    expect($note->incident)->toBeInstanceOf(Incident::class)
        ->and($note->incident->id)->toBe($incident->id);
});

test('incident note belongs to a user', function (): void {
    $user = User::factory()->create();
    $note = IncidentNote::create([
        'incident_id' => Incident::factory()->create()->id,
        'user_id' => $user->id,
        'content' => 'Test note',
    ]);

    expect($note->user)->toBeInstanceOf(User::class)
        ->and($note->user->id)->toBe($user->id);
});
