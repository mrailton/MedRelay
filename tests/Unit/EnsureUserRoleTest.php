<?php

declare(strict_types=1);

namespace Tests\Unit;

use App\Http\Middleware\EnsureUserRole;
use Illuminate\Http\Request;
use RuntimeException;

test('middleware redirects guests to login', function (): void {
    $middleware = new EnsureUserRole();
    $request = new Request();

    $response = $middleware->handle($request, fn () => throw new RuntimeException('should not reach'));

    expect($response->isRedirect(route('login')))->toBeTrue();
});
