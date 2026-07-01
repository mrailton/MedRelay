@extends('layouts.app')

@section('title', 'Incident ' . $incident->reference)

@section('content')
<div class="space-y-6">
    <div class="mr-page-header">
        <div>
            <div class="flex items-center gap-3">
                <h1 class="mr-page-title font-mono tracking-tight">{{ $incident->reference }}</h1>
                @include('shared.status-badge', ['status' => $incident->status->value])
            </div>
            <p class="mr-page-subtitle">{{ $incident->event->name }} &middot; {{ $incident->location }}</p>
        </div>
        <a href="{{ route('dashboard', ['event_id' => $incident->event_id]) }}" class="btn btn-ghost btn-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
            Back to Dashboard
        </a>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-1 space-y-4">
            <div class="mr-card">
                <div class="card-body">
                    <h2 class="mr-card-title mb-3">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        Details
                    </h2>
                    <div class="space-y-3">
                        <div class="mr-detail-item">
                            <div class="mr-detail-label">Priority</div>
                            <div>
                                @php
                                    $badgeClass = match($incident->priority) {
                                        'P1' => 'mr-badge-p1',
                                        'P2' => 'mr-badge-p2',
                                        'P3' => 'mr-badge-p3',
                                        default => 'badge badge-ghost badge-sm',
                                    };
                                @endphp
                                <span class="{{ $badgeClass }}">{{ $incident->priority }}</span>
                            </div>
                        </div>
                        <div class="mr-detail-item">
                            <div class="mr-detail-label">Category</div>
                            <div class="mr-detail-value">{{ $incident->category }}</div>
                        </div>
                        <div class="mr-detail-item">
                            <div class="mr-detail-label">Location</div>
                            <div class="mr-detail-value">{{ $incident->location }}</div>
                        </div>
                        <div class="mr-detail-item">
                            <div class="mr-detail-label">Source</div>
                            <div class="mr-detail-value">{{ $incident->source->label() }}</div>
                        </div>
                        <div class="mr-detail-item">
                            <div class="mr-detail-label">Description</div>
                            <p class="text-sm whitespace-pre-wrap mt-1">{{ $incident->description }}</p>
                        </div>
                        <div class="mr-detail-item">
                            <div class="mr-detail-label">Created</div>
                            <div class="mr-detail-value">{{ $incident->created_at->format('M j, Y g:ia') }}</div>
                        </div>
                    </div>
                </div>
            </div>

            @if (auth()->user()->isControllerOrAdmin())
                <div class="mr-card">
                    <div class="card-body">
                        <h2 class="mr-card-title mb-3">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                            Incident Status
                        </h2>
                        <div class="flex items-center justify-between gap-3">
                            <div class="text-sm text-base-content/70">Current: {{ $incident->status->label() }}</div>
                            @if ($incident->status === \App\Enums\IncidentLifecycleStatus::Open)
                                <button
                                    type="button"
                                    class="btn btn-primary btn-sm"
                                    onclick="document.getElementById('close-incident-modal').showModal()"
                                >
                                    Close Incident
                                </button>
                            @else
                                <button
                                    type="button"
                                    class="btn btn-outline btn-sm"
                                    onclick="document.getElementById('reopen-incident-modal').showModal()"
                                >
                                    Reopen Incident
                                </button>
                            @endif
                        </div>
                    </div>
                </div>
            @endif

            @if (auth()->user()->isControllerOrAdmin() && $incident->status === \App\Enums\IncidentLifecycleStatus::Open)
                <dialog id="close-incident-modal" class="modal modal-bottom sm:modal-middle">
                    <div class="modal-box mr-modal-box max-w-lg">
                        <form method="POST" action="{{ route('incidents.update-status', $incident) }}">
                            @csrf
                            <input type="hidden" name="status" value="{{ \App\Enums\IncidentLifecycleStatus::Closed->value }}" />

                            <div class="mr-modal-header">
                                <h3>Close Incident</h3>
                                <button type="button" class="btn btn-ghost btn-sm btn-square" onclick="document.getElementById('close-incident-modal').close()">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                                </button>
                            </div>

                            <div class="mr-modal-body space-y-4">
                                <p class="text-sm text-base-content/70">Add optional closure notes for this incident.</p>
                                <div class="form-control">
                                    <label class="mr-form-label"><span class="label-text">Closure Notes (Optional)</span></label>
                                    <textarea name="close_notes" class="mr-textarea w-full" rows="4" placeholder="Add closure notes..."></textarea>
                                </div>
                            </div>

                            <div class="mr-modal-footer">
                                <button type="button" class="btn btn-ghost btn-sm" onclick="document.getElementById('close-incident-modal').close()">Cancel</button>
                                <button type="submit" class="btn btn-primary btn-sm">Close Incident</button>
                            </div>
                        </form>
                    </div>
                    <form method="dialog" class="modal-backdrop">
                        <button>close</button>
                    </form>
                </dialog>
            @endif

            @if (auth()->user()->isControllerOrAdmin() && $incident->status === \App\Enums\IncidentLifecycleStatus::Closed)
                <dialog id="reopen-incident-modal" class="modal modal-bottom sm:modal-middle">
                    <div class="modal-box mr-modal-box max-w-lg">
                        <form method="POST" action="{{ route('incidents.update-status', $incident) }}">
                            @csrf
                            <input type="hidden" name="status" value="{{ \App\Enums\IncidentLifecycleStatus::Open->value }}" />

                            <div class="mr-modal-header">
                                <h3>Reopen Incident</h3>
                                <button type="button" class="btn btn-ghost btn-sm btn-square" onclick="document.getElementById('reopen-incident-modal').close()">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                                </button>
                            </div>

                            <div class="mr-modal-body space-y-4">
                                <p class="text-sm text-base-content/70">Add a note explaining why this incident is being reopened.</p>
                                <div class="form-control">
                                    <label class="mr-form-label"><span class="label-text">Reopen Notes</span></label>
                                    <textarea name="reopen_notes" class="mr-textarea w-full" rows="4" placeholder="Why is this incident being reopened?" required></textarea>
                                </div>
                            </div>

                            <div class="mr-modal-footer">
                                <button type="button" class="btn btn-ghost btn-sm" onclick="document.getElementById('reopen-incident-modal').close()">Cancel</button>
                                <button type="submit" class="btn btn-primary btn-sm">Reopen Incident</button>
                            </div>
                        </form>
                    </div>
                    <form method="dialog" class="modal-backdrop">
                        <button>close</button>
                    </form>
                </dialog>
            @endif
        </div>

        <div class="lg:col-span-2 space-y-4">
            <div class="mr-card">
                <div class="card-body">
                    <div class="flex items-center justify-between mb-3">
                        <h2 class="mr-card-title">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
                            Assigned Resources
                        </h2>
                        <span class="text-xs text-base-content/40">{{ $incident->resources->count() }} assigned</span>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="mr-data-table table-zebra">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Type</th>
                                    <th>Resource Status</th>
                                    <th>Incident Status</th>
                                    <th class="text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                @forelse ($incident->resources as $resource)
                                    <tr>
                                        <td class="font-medium">{{ $resource->name }}</td>
                                        <td><span class="text-sm">{{ $resource->resource_type->label() }}</span></td>
                                        <td>@include('shared.status-badge', ['status' => $resource->status->value])</td>
                                        <td>
                                            @include('shared.status-badge', ['status' => $resource->pivot->status])
                                        </td>
                                        <td class="text-right">
                                            @if (auth()->user()->isControllerOrAdmin())
                                                <form method="POST" action="{{ route('incidents.resources.update-status', [$incident, $resource]) }}" class="inline-flex items-center gap-2 mr-2">
                                                    @csrf
                                                    <select name="status" class="mr-select select-xs w-36">
                                                        @foreach (\App\Enums\IncidentStatus::cases() as $status)
                                                            <option value="{{ $status->value }}" @selected($resource->pivot->status === $status->value)>
                                                                {{ $status->label() }}
                                                            </option>
                                                        @endforeach
                                                    </select>
                                                    <button type="submit" class="btn btn-ghost btn-xs">Set</button>
                                                </form>
                                                <form method="POST" action="{{ route('incidents.assign-resource', $incident) }}" class="inline">
                                                    @csrf
                                                    <input type="hidden" name="resource_id" value="{{ $resource->id }}" />
                                                    <button type="submit" class="btn btn-ghost btn-xs text-error">Remove</button>
                                                </form>
                                            @endif
                                        </td>
                                    </tr>
                                @empty
                                    <tr>
                                        <td colspan="5">
                                            <div class="mr-empty-state py-6">
                                                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                                                <p>No resources assigned.</p>
                                            </div>
                                        </td>
                                    </tr>
                                @endforelse
                            </tbody>
                        </table>
                    </div>

                    @if (auth()->user()->isControllerOrAdmin() && $incident->event->resources->count() > 0)
                        <form method="POST" action="{{ route('incidents.assign-resource', $incident) }}" class="flex gap-2 mt-4 pt-4 border-t border-base-200">
                            @csrf
                            <select name="resource_id" class="mr-select flex-1 select-sm">
                                @foreach ($incident->event->resources as $resource)
                                    <option value="{{ $resource->id }}">{{ $resource->name }} ({{ $resource->status->label() }})</option>
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
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"/></svg>
                            Notes
                        </h2>
                        <span class="text-xs text-base-content/40">{{ $incident->notes->count() }} total</span>
                    </div>

                    <div class="space-y-3 mb-4">
                        @forelse ($incident->notes as $note)
                            <div class="mr-note">
                                <div class="flex items-center justify-between mb-1.5">
                                    <span class="text-xs font-semibold">{{ $note->user?->name ?? 'Unknown' }}</span>
                                    <span class="text-xs text-base-content/40">{{ $note->created_at->diffForHumans() }}</span>
                                </div>
                                <p class="text-sm whitespace-pre-wrap">{{ $note->content }}</p>
                            </div>
                        @empty
                            <div class="mr-empty-state py-6">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"/></svg>
                                <p>No notes yet.</p>
                            </div>
                        @endforelse
                    </div>

                    @if (auth()->user()->isControllerOrAdmin())
                        <form method="POST" action="{{ route('incidents.notes.store', $incident) }}" class="pt-4 border-t border-base-200">
                            @csrf
                            <div class="form-control">
                                <textarea name="content" class="mr-textarea w-full" placeholder="Add a note..." rows="2" required></textarea>
                            </div>
                            <div class="flex justify-end mt-2">
                                <button type="submit" class="btn btn-primary btn-sm">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
                                    Add Note
                                </button>
                            </div>
                        </form>
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>
@endsection
