@extends('layouts.app')

@section('title', 'Resources')

@section('content')
<div class="space-y-6">
    <div class="mr-page-header">
        <div>
            <h1 class="mr-page-title">Resources</h1>
            <p class="mr-page-subtitle">{{ $event->name }}</p>
        </div>
        @if (auth()->user()->isControllerOrAdmin())
            <button class="btn btn-primary btn-sm" onclick="document.getElementById('create-resource-modal').showModal()">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                New Resource
            </button>
        @endif
    </div>

    <div class="mr-card">
        <div class="card-body p-0">
            @include('resources.table', ['resources' => $resources])
        </div>
    </div>
</div>

@if (auth()->user()->isControllerOrAdmin())
    @include('resources.create-modal', ['event' => $event, 'allStaff' => \App\Models\Staff::orderBy('first_name')->get()])
@endif
@endsection
