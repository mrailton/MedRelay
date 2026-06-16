<?php

declare(strict_types=1);

namespace Tests\Unit;

use App\Enums\UserRole;
use App\Models\AuditLog;
use App\Models\Incident;
use App\Models\IncidentNote;
use App\Models\User;

test('is read only returns true for read only role', function (): void {
    $user = User::factory()->readOnly()->create();

    expect($user->isReadOnly())->toBeTrue();
});

test('is read only returns false for other roles', function (): void {
    $admin = User::factory()->admin()->create();
    $controller = User::factory()->create(['role' => UserRole::Controller]);

    expect($admin->isReadOnly())->toBeFalse()
        ->and($controller->isReadOnly())->toBeFalse();
});

test('user has incident notes', function (): void {
    $user = User::factory()->create();
    IncidentNote::create([
        'incident_id' => Incident::factory()->create()->id,
        'user_id' => $user->id,
        'content' => 'Test note',
    ]);

    expect($user->incidentNotes)->toHaveCount(1);
});

test('user has audit logs', function (): void {
    $user = User::factory()->create();
    AuditLog::create([
        'user_id' => $user->id,
        'action' => 'test.action',
        'entity_type' => 'user',
        'entity_id' => (string) $user->id,
    ]);

    expect($user->auditLogs)->toHaveCount(1);
});
