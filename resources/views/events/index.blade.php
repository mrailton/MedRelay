@extends('layouts.app')

@section('title', 'Events')

@section('content')
<div class="space-y-6">
    <div class="mr-page-header">
        <div>
            <h1 class="mr-page-title">Events</h1>
            <p class="mr-page-subtitle">Manage your operational events</p>
        </div>
        @if (auth()->user()->isControllerOrAdmin())
            <button class="btn btn-primary btn-sm" onclick="document.getElementById('create-event-modal').showModal()">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                New Event
            </button>
        @endif
    </div>

    <div class="mr-card">
        <div class="card-body p-0">
            <div class="overflow-x-auto">
                <table class="mr-data-table table-zebra">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Location</th>
                            <th>Start Time</th>
                            <th>Status</th>
                            <th class="text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        @forelse ($events as $event)
                            <tr class="animate-fade-in">
                                <td class="font-medium">{{ $event->name }}</td>
                                <td class="text-sm">{{ $event->location }}</td>
                                <td class="text-sm">{{ $event->start_time->format('M j, Y g:ia') }}</td>
                                <td>
                                    @if ($event->is_active)
                                        <span class="badge badge-soft badge-success badge-sm font-medium">Active</span>
                                    @else
                                        <span class="badge badge-ghost badge-sm">Inactive</span>
                                    @endif
                                </td>
                                <td class="text-right">
                                    <div class="flex items-center justify-end gap-1">
                                        <a href="{{ route('events.show', $event) }}" class="btn btn-ghost btn-xs text-primary">View</a>
                                        @if (auth()->user()->isControllerOrAdmin())
                                            <a href="{{ route('events.edit', $event) }}" class="btn btn-ghost btn-xs">Edit</a>
                                        @endif
                                    </div>
                                </td>
                            </tr>
                        @empty
                            <tr>
                                <td colspan="5">
                                    <div class="mr-empty-state">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                                        <p>No events yet.</p>
                                        <p class="text-xs mt-1">Create your first event to get started.</p>
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

@if (auth()->user()->isControllerOrAdmin())
    <dialog id="create-event-modal" class="modal modal-bottom sm:modal-middle">
        <div class="modal-box mr-modal-box max-w-lg">
            <form method="POST" action="{{ route('events.store') }}">
                @csrf
                <div class="mr-modal-header">
                    <h3>Create Event</h3>
                    <button type="button" class="btn btn-ghost btn-sm btn-square" onclick="document.getElementById('create-event-modal').close()">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                </div>

                <div class="mr-modal-body space-y-4">
                    <div class="form-control">
                        <label class="mr-form-label"><span class="label-text">Name</span></label>
                        <input type="text" name="name" class="mr-input w-full" placeholder="Event name" required />
                    </div>

                    <div class="form-control">
                        <label class="mr-form-label"><span class="label-text">Location</span></label>
                        <input type="text" name="location" class="mr-input w-full" placeholder="Event location" required />
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div class="form-control">
                            <label class="mr-form-label"><span class="label-text">Start Time</span></label>
                            <input type="datetime-local" name="start_time" class="mr-input w-full" required />
                        </div>
                        <div class="form-control">
                            <label class="mr-form-label"><span class="label-text">End Time</span></label>
                            <input type="datetime-local" name="end_time" class="mr-input w-full" />
                        </div>
                    </div>

                    <div class="form-control">
                        <label class="label cursor-pointer justify-start gap-2">
                            <input type="checkbox" name="is_active" value="1" class="checkbox checkbox-primary checkbox-sm" checked />
                            <span class="label-text text-sm">Active</span>
                        </label>
                    </div>

                    <div class="form-control">
                        <label class="mr-form-label"><span class="label-text">Notes</span></label>
                        <textarea name="notes" class="mr-textarea w-full" rows="2" placeholder="Optional notes..."></textarea>
                    </div>
                </div>

                <div class="mr-modal-footer">
                    <button type="button" class="btn btn-ghost btn-sm" onclick="document.getElementById('create-event-modal').close()">Cancel</button>
                    <button type="submit" class="btn btn-primary btn-sm">Create Event</button>
                </div>
            </form>
        </div>
        <form method="dialog" class="modal-backdrop">
            <button>close</button>
        </form>
    </dialog>
@endif
@endsection
