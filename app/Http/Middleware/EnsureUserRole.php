<?php

declare(strict_types=1);

namespace App\Http\Middleware;

use App\Enums\UserRole;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class EnsureUserRole
{
    public function handle(Request $request, Closure $next, string ...$roles): Response
    {
        $user = $request->user();

        if ( ! $user) {
            return redirect()->route('login');
        }

        $userRole = $user->role;

        foreach ($roles as $role) {
            if ($userRole instanceof UserRole && $userRole->value === $role) {
                return $next($request);
            }
        }

        abort(403);
    }
}
