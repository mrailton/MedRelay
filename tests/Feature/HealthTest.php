<?php

namespace Tests\Feature;

test('health check endpoint returns ok', function () {
    $response = $this->get('/up');
    $response->assertStatus(200);
    $response->assertJson([
        'status' => 'ok',
        'database' => 'ok',
    ]);
});
