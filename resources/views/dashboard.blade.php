@extends('layouts.app')

@section('title', 'Dashboard')

@section('content')
<div class="space-y-6">
    <div class="mr-page-header">
        <div>
            <h1 class="mr-page-title">Dashboard</h1>
            <p class="mr-page-subtitle">Overview of active operations</p>
        </div>

        <div class="flex items-center gap-3">
            <form method="GET" action="{{ route('dashboard') }}">
                <select name="event_id" class="mr-select select-sm min-w-[180px]" onchange="this.form.submit()">
                    <option value="">Select Event...</option>
                    @foreach ($activeEvents as $event)
                        <option value="{{ $event->id }}" @selected($selectedEvent && $selectedEvent->id === $event->id)>
                            {{ $event->name }}
                        </option>
                    @endforeach
                </select>
            </form>

            @if ($selectedEvent && auth()->user()->isControllerOrAdmin())
                <button class="btn btn-primary btn-sm" onclick="document.getElementById('create-incident-modal').showModal()">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                    New Incident
                </button>
                <button class="btn btn-outline btn-sm" onclick="document.getElementById('create-resource-modal').showModal()">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                    New Resource
                </button>
            @endif
        </div>
    </div>

    @if ($selectedEvent)
        @php
            $totalIncidents = $incidents->count();
            $activeIncidents = $incidents
                ->filter(fn ($incident) => $incident->status === \App\Enums\IncidentLifecycleStatus::Open)
                ->count();
            $availableResources = $resources->where('status', 'available')->count();
            $deployedResources = $resources->whereIn('status', ['assigned', 'en_route', 'on_scene', 'transporting'])->count();
            $outOfServiceResources = $resources->where('status', 'out_of_service')->count();
        @endphp

        <div class="grid grid-cols-2 lg:grid-cols-5 gap-3">
            <div class="mr-stat">
                <div class="mr-stat-title">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
                    Total Incidents
                </div>
                <div class="mr-stat-value text-primary">{{ $totalIncidents }}</div>
            </div>
            <div class="mr-stat">
                <div class="mr-stat-title">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                    Active Incidents
                </div>
                <div class="mr-stat-value text-warning">{{ $activeIncidents }}</div>
            </div>
            <div class="mr-stat">
                <div class="mr-stat-title">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                    Available Resources
                </div>
                <div class="mr-stat-value text-success">{{ $availableResources }}</div>
            </div>
            <div class="mr-stat">
                <div class="mr-stat-title">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>
                    Deployed Resources
                </div>
                <div class="mr-stat-value text-info">{{ $deployedResources }}</div>
            </div>
            <div class="mr-stat">
                <div class="mr-stat-title">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/></svg>
                    Out of Service
                </div>
                <div class="mr-stat-value text-error">{{ $outOfServiceResources }}</div>
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
                        <span class="text-xs text-base-content/40">{{ $incidents->count() }} total</span>
                    </div>
                    @include('incidents.table', ['incidents' => $incidents])
                </div>
            </div>

            <div class="mr-card">
                <div class="card-body">
                    <div class="flex items-center justify-between mb-3">
                        <h2 class="mr-card-title">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
                            Resources
                        </h2>
                        <span class="text-xs text-base-content/40">{{ $resources->count() }} total</span>
                    </div>
                    @include('resources.table', ['resources' => $resources])
                </div>
            </div>
        </div>
    @else
        <div class="mr-card">
            <div class="card-body">
                <div class="mr-empty-state">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
                    <p class="text-base font-medium text-base-content/60 mt-2">No event selected</p>
                    <p class="text-sm text-base-content/40 mt-1">Select an event from the dropdown to view the dashboard.</p>
                    @if ($activeEvents->isEmpty())
                        <a href="{{ route('events.index') }}" class="btn btn-primary btn-sm mt-4">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                            Create Event
                        </a>
                    @endif
                </div>
            </div>
        </div>
    @endif
</div>

@if ($selectedEvent && auth()->user()->isControllerOrAdmin())
    @include('incidents.create-modal', ['event' => $selectedEvent])
    @include('resources.create-modal', ['event' => $selectedEvent, 'allStaff' => $allStaff])
@endif
@endsection
