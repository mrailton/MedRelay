<?php

declare(strict_types=1);

namespace Tests\Feature;

test('the application redirects unauthenticated users to login', function (): void {
    $response = $this->get('/');
    $response->assertRedirect('/login');
});
