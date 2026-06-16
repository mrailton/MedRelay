@extends('layouts.app')

@section('title', 'Audit Logs')

@section('content')
<div class="space-y-6">
    <div class="mr-page-header">
        <div>
            <h1 class="mr-page-title">Audit Logs</h1>
            <p class="mr-page-subtitle">Track all system changes and events</p>
        </div>
    </div>

    <div class="mr-card">
        <div class="card-body p-0">
            <div class="overflow-x-auto">
                <table class="mr-data-table table-zebra">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>User</th>
                            <th>Action</th>
                            <th>Entity</th>
                            <th>Entity ID</th>
                        </tr>
                    </thead>
                    <tbody>
                        @forelse ($logs as $log)
                            <tr class="animate-fade-in">
                                <td class="text-sm whitespace-nowrap">{{ $log->created_at->format('M j, Y g:ia') }}</td>
                                <td class="text-sm font-medium">{{ $log->user?->name ?? '<span class="text-base-content/40">System</span>' }}</td>
                                <td><code class="px-2 py-0.5 rounded bg-base-200 text-xs font-mono">{{ $log->action }}</code></td>
                                <td><span class="text-sm capitalize">{{ str_replace('_', ' ', $log->entity_type) }}</span></td>
                                <td class="font-mono text-xs text-base-content/60">{{ $log->entity_id }}</td>
                            </tr>
                        @empty
                            <tr>
                                <td colspan="5">
                                    <div class="mr-empty-state">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                                        <p>No audit logs yet.</p>
                                    </div>
                                </td>
                            </tr>
                        @endforelse
                    </tbody>
                </table>
            </div>
            @if ($logs->hasPages())
                <div class="px-6 py-4 border-t border-base-200">
                    {{ $logs->links() }}
                </div>
            @endif
        </div>
    </div>
</div>
@endsection
