@extends('layouts.app')

@section('title', $event->name)

@section('content')
<div class="space-y-6">
    <div class="mr-page-header">
        <div>
            <h1 class="mr-page-title">{{ $event->name }}</h1>
            <p class="mr-page-subtitle">{{ $event->location }} &middot; {{ $event->start_time->format('M j, Y') }}</p>
        </div>
        <div class="flex gap-2">
            <a href="{{ route('dashboard', ['event_id' => $event->id]) }}" class="btn btn-ghost btn-sm">Dashboard</a>
            <a href="{{ route('events.incidents.index', $event) }}" class="btn btn-ghost btn-sm">Incidents</a>
            <a href="{{ route('events.resources.index', $event) }}" class="btn btn-ghost btn-sm">Resources</a>
            @if (auth()->user()->isControllerOrAdmin())
                <a href="{{ route('events.edit', $event) }}" class="btn btn-outline btn-sm">Edit</a>
            @endif
        </div>
    </div>

    <div class="mr-card">
        <div class="card-body">
            <div class="mr-detail-grid">
                <div class="mr-detail-item">
                    <div class="mr-detail-label">Start Time</div>
                    <div class="mr-detail-value">{{ $event->start_time->format('F j, Y g:ia') }}</div>
                </div>
                <div class="mr-detail-item">
                    <div class="mr-detail-label">End Time</div>
                    <div class="mr-detail-value">{{ $event->end_time?->format('F j, Y g:ia') ?? 'Not set' }}</div>
                </div>
                <div class="mr-detail-item">
                    <div class="mr-detail-label">Status</div>
                    <div class="mr-detail-value">
                        @if ($event->is_active)
                            <span class="badge badge-soft badge-success badge-sm font-medium">Active</span>
                        @else
                            <span class="badge badge-ghost badge-sm">Inactive</span>
                        @endif
                    </div>
                </div>
                <div class="mr-detail-item">
                    <div class="mr-detail-label">Location</div>
                    <div class="mr-detail-value">{{ $event->location }}</div>
                </div>
            </div>
            @if ($event->notes)
                <div class="mt-4 pt-4 border-t border-base-200">
                    <div class="mr-detail-label mb-1">Notes</div>
                    <p class="text-sm whitespace-pre-wrap">{{ $event->notes }}</p>
                </div>
            @endif
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="mr-card">
            <div class="card-body">
                <div class="flex items-center justify-between mb-3">
                    <h2 class="mr-card-title">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                        Incidents
                    </h2>
                    <span class="text-xs text-base-content/40">{{ $event->incidents->count() }} total</span>
                </div>
                @include('incidents.table', ['incidents' => $event->incidents])
            </div>
        </div>
        <div class="mr-card">
            <div class="card-body">
                <div class="flex items-center justify-between mb-3">
                    <h2 class="mr-card-title">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
                        Resources
                    </h2>
                    <span class="text-xs text-base-content/40">{{ $event->resources->count() }} total</span>
                </div>
                @include('resources.table', ['resources' => $event->resources])
            </div>
        </div>
    </div>
</div>
@endsection
