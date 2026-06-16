<?php

declare(strict_types=1);

namespace Tests\Unit;

use App\Enums\UserRole;
use App\Models\AuditLog;
use App\Models\User;

test('audit log belongs to a user', function (): void {
    $user = User::factory()->create(['role' => UserRole::Admin]);
    $log = AuditLog::create([
        'user_id' => $user->id,
        'action' => 'test.action',
        'entity_type' => 'user',
        'entity_id' => (string) $user->id,
    ]);

    expect($log->user)->toBeInstanceOf(User::class)
        ->and($log->user->id)->toBe($user->id);
});
