@extends('layouts.app')

@section('title', $resource->name)

@section('content')
<div class="space-y-6">
    <div class="mr-page-header">
        <div>
            <h1 class="mr-page-title">{{ $resource->name }}</h1>
            <p class="mr-page-subtitle">{{ $resource->event->name }} &middot; {{ $resource->resource_type->label() }}</p>
        </div>
        <a href="{{ route('dashboard', ['event_id' => $resource->event_id]) }}" class="btn btn-ghost btn-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
            Back to Dashboard
        </a>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="space-y-4">
            <div class="mr-card">
                <div class="card-body">
                    <h2 class="mr-card-title mb-3">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        Details
                    </h2>
                    <div class="space-y-3">
                        <div class="mr-detail-item">
                            <div class="mr-detail-label">Type</div>
                            <div class="mr-detail-value">{{ $resource->resource_type->label() }}</div>
                        </div>
                        <div class="mr-detail-item">
                            <div class="mr-detail-label">Status</div>
                            <div class="mt-0.5">@include('shared.status-badge', ['status' => $resource->status->value])</div>
                        </div>
                        <div class="mr-detail-item">
                            <div class="mr-detail-label">Highest Clinical Level</div>
                            <div class="mr-detail-value">{{ $resource->highest_clinical_level?->label() ?? 'N/A' }}</div>
                        </div>
                        <div class="mr-detail-item">
                            <div class="mr-detail-label">Deployable</div>
                            <div class="mr-detail-value">
                                @if ($resource->is_deployable)
                                    <span class="badge badge-soft badge-success badge-sm font-medium">Yes</span>
                                @else
                                    <span class="badge badge-ghost badge-sm">No</span>
                                @endif
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            @if (auth()->user()->isControllerOrAdmin())
                <div class="mr-card">
                    <div class="card-body">
                        <h2 class="mr-card-title mb-3">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                            Update Status
                        </h2>
                        <form method="POST" action="{{ route('resources.update-status', $resource) }}" class="flex gap-2">
                            @csrf
                            <select name="status" class="mr-select flex-1">
                                @foreach (\App\Enums\ResourceStatus::cases() as $status)
                                    <option value="{{ $status->value }}" @selected($resource->status === $status)>
                                        {{ $status->label() }}
                                    </option>
                                @endforeach
                            </select>
                            <button type="submit" class="btn btn-primary btn-sm">Update</button>
                        </form>
                    </div>
                </div>
            @endif
        </div>

        <div class="space-y-4">
            <div class="mr-card">
                <div class="card-body">
                    <div class="flex items-center justify-between mb-3">
                        <h2 class="mr-card-title">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                            Assigned Staff
                        </h2>
                        <span class="text-xs text-base-content/40">{{ $resource->staff->count() }} assigned</span>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="mr-data-table table-zebra">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Clinical Level</th>
                                    <th class="text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                @forelse ($resource->staff as $staff)
                                    <tr>
                                        <td class="font-medium text-sm">{{ $staff->full_name }}</td>
                                        <td><span class="badge badge-ghost badge-sm font-normal">{{ $staff->clinical_level->label() }}</span></td>
                                        <td class="text-right">
                                            @if (auth()->user()->isControllerOrAdmin())
                                                <form method="POST" action="{{ route('resources.remove-staff', $resource) }}" class="inline">
                                                    @csrf
                                                    <input type="hidden" name="staff_id" value="{{ $staff->id }}" />
                                                    <button type="submit" class="btn btn-ghost btn-xs text-error">Remove</button>
                                                </form>
                                            @endif
                                        </td>
                                    </tr>
                                @empty
                                    <tr>
                                        <td colspan="3">
                                            <div class="mr-empty-state py-6">
                                                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857"/></svg>
                                                <p>No staff assigned.</p>
                                            </div>
                                        </td>
                                    </tr>
                                @endforelse
                            </tbody>
                        </table>
                    </div>

                    @if (auth()->user()->isControllerOrAdmin())
                        <form method="POST" action="{{ route('resources.assign-staff', $resource) }}" class="flex gap-2 mt-4 pt-4 border-t border-base-200">
                            @csrf
                            <select name="staff_id" class="mr-select flex-1 select-sm">
                                @foreach (\App\Models\Staff::orderBy('first_name')->get() as $staff)
                                    <option value="{{ $staff->id }}">{{ $staff->full_name }} ({{ $staff->clinical_level->label() }})</option>
                                @endforeach
                            </select>
                            <button type="submit" class="btn btn-primary btn-sm">Assign</button>
                        </form>
                    @endif
                </div>
            </div>

            <div class="mr-card">
                <div class="card-body">
                    <div class="flex items-center justify-between mb-3">
                        <h2 class="mr-card-title">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                            Active Incidents
                        </h2>
                        @php
                            $activeIncidents = $resource->incidents
                                ->filter(fn ($incident) => $incident->status === \App\Enums\IncidentLifecycleStatus::Open);
                        @endphp
                        <span class="text-xs text-base-content/40">{{ $activeIncidents->count() }} total</span>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="mr-data-table table-zebra">
                            <thead>
                                <tr>
                                    <th>Reference</th>
                                    <th>Priority</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                @forelse ($activeIncidents as $incident)
                                    <tr>
                                        <td class="font-mono text-sm font-medium">
                                            <a href="{{ route('incidents.show', $incident) }}" class="link link-primary">{{ $incident->reference }}</a>
                                        </td>
                                        <td><span class="badge badge-sm">{{ $incident->priority }}</span></td>
                                        <td>@include('shared.status-badge', ['status' => $incident->status->value])</td>
                                    </tr>
                                @empty
                                    <tr>
                                        <td colspan="3">
                                            <div class="mr-empty-state py-6">
                                                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                                                <p>No active incidents.</p>
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
    </div>
</div>
@endsection
