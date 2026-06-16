@extends('layouts.app')

@section('title', 'Edit Event')

@section('content')
<div class="max-w-2xl mx-auto space-y-6">
    <div>
        <h1 class="mr-page-title">Edit Event</h1>
        <p class="mr-page-subtitle">Update event details</p>
    </div>

    <div class="mr-form-card">
        <div class="card-body">
            <form method="POST" action="{{ route('events.update', $event) }}" class="space-y-4">
                @csrf
                <div class="form-control">
                    <label class="mr-form-label"><span class="label-text">Name</span></label>
                    <input type="text" name="name" class="mr-input w-full @error('name') input-error @enderror" value="{{ old('name', $event->name) }}" required />
                    @error('name') <label class="label pt-1"><span class="label-text-alt text-error text-xs">{{ $message }}</span></label> @enderror
                </div>

                <div class="form-control">
                    <label class="mr-form-label"><span class="label-text">Location</span></label>
                    <input type="text" name="location" class="mr-input w-full @error('location') input-error @enderror" value="{{ old('location', $event->location) }}" required />
                    @error('location') <label class="label pt-1"><span class="label-text-alt text-error text-xs">{{ $message }}</span></label> @enderror
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div class="form-control">
                        <label class="mr-form-label"><span class="label-text">Start Time</span></label>
                        <input type="datetime-local" name="start_time" class="mr-input w-full @error('start_time') input-error @enderror" value="{{ old('start_time', $event->start_time->format('Y-m-d\TH:i')) }}" required />
                        @error('start_time') <label class="label pt-1"><span class="label-text-alt text-error text-xs">{{ $message }}</span></label> @enderror
                    </div>
                    <div class="form-control">
                        <label class="mr-form-label"><span class="label-text">End Time</span></label>
                        <input type="datetime-local" name="end_time" class="mr-input w-full" value="{{ old('end_time', $event->end_time?->format('Y-m-d\TH:i')) }}" />
                    </div>
                </div>

                <div class="form-control">
                    <label class="label cursor-pointer justify-start gap-2">
                        <input type="checkbox" name="is_active" value="1" class="checkbox checkbox-primary checkbox-sm" @checked(old('is_active', $event->is_active)) />
                        <span class="label-text text-sm">Active</span>
                    </label>
                </div>

                <div class="form-control">
                    <label class="mr-form-label"><span class="label-text">Notes</span></label>
                    <textarea name="notes" class="mr-textarea w-full" rows="3">{{ old('notes', $event->notes) }}</textarea>
                </div>

                <div class="flex gap-3 pt-2">
                    <a href="{{ route('events.show', $event) }}" class="btn btn-ghost">Cancel</a>
                    <button type="submit" class="btn btn-primary">Update Event</button>
                </div>
            </form>
        </div>
    </div>
</div>
@endsection
