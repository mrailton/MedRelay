<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\StoreUserRequest;
use App\Models\AuditLog;
use App\Models\User;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;

class AdminController extends Controller
{
    public function users(): View
    {
        $users = User::orderBy('name')->get();
        return view('admin.users', compact('users'));
    }

    public function createUser(): View
    {
        return view('admin.users-create');
    }

    public function storeUser(StoreUserRequest $request): RedirectResponse
    {
        $user = User::create($request->validated());

        AuditLog::log('user.created', 'user', (string) $user->id, after: $user->toArray());

        return redirect()->route('admin.users')
            ->with('success', 'User created successfully.');
    }

    public function auditLogs(): View
    {
        $logs = AuditLog::with('user')
            ->orderBy('created_at', 'desc')
            ->paginate(50);

        return view('admin.audit-logs', compact('logs'));
    }
}
