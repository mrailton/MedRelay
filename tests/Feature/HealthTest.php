<?php

declare(strict_types=1);

namespace Tests\Feature;

test('health check endpoint returns ok', function (): void {
    $response = $this->get('/up');
    $response->assertStatus(200);
    $response->assertJson([
        'status' => 'ok',
        'database' => 'ok',
    ]);
});
