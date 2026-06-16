@extends('layouts.app')

@section('title', 'Users')

@section('content')
<div class="space-y-6">
    <div class="mr-page-header">
        <div>
            <h1 class="mr-page-title">Users</h1>
            <p class="mr-page-subtitle">Manage system users and roles</p>
        </div>
        <a href="{{ route('admin.users.create') }}" class="btn btn-primary btn-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            Create User
        </a>
    </div>

    <div class="mr-card">
        <div class="card-body p-0">
            <div class="overflow-x-auto">
                <table class="mr-data-table table-zebra">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        @forelse ($users as $user)
                            <tr class="animate-fade-in">
                                <td>
                                    <div class="flex items-center gap-3">
                                        <div class="w-8 h-8 rounded-full bg-base-200 text-base-content/60 text-xs font-bold flex items-center justify-center">
                                            {{ substr($user->name, 0, 1) }}
                                        </div>
                                        <span class="font-medium">{{ $user->name }}</span>
                                    </div>
                                </td>
                                <td class="text-sm">{{ $user->email }}</td>
                                <td>
                                    @php
                                        $roleBadge = match($user->role->value) {
                                            'admin' => 'badge-soft badge-warning',
                                            'controller' => 'badge-soft badge-info',
                                            'read_only' => 'badge-ghost',
                                            default => 'badge-ghost',
                                        };
                                    @endphp
                                    <span class="badge {{ $roleBadge }} badge-sm font-medium">{{ $user->role->label() }}</span>
                                </td>
                                <td class="text-sm text-base-content/60">{{ $user->created_at->format('M j, Y') }}</td>
                            </tr>
                        @empty
                            <tr>
                                <td colspan="4">
                                    <div class="mr-empty-state">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/></svg>
                                        <p>No users.</p>
                                    </div>
                                </td>
                            </tr>
                        @endforelse
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
@endsection
