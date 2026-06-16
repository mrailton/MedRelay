@extends('layouts.app')

@section('title', 'Staff')

@section('content')
<div class="space-y-6">
    <div class="mr-page-header">
        <div>
            <h1 class="mr-page-title">Staff</h1>
            <p class="mr-page-subtitle">Manage your clinical personnel</p>
        </div>
        @if (auth()->user()->isControllerOrAdmin())
            <button class="btn btn-primary btn-sm" onclick="document.getElementById('create-staff-modal').showModal()">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                Add Staff
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
                            <th>Clinical Level</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        @forelse ($staff as $member)
                            <tr class="animate-fade-in">
                                <td>
                                    <div class="flex items-center gap-3">
                                        <div class="w-8 h-8 rounded-full bg-primary/10 text-primary text-xs font-bold flex items-center justify-center">
                                            {{ substr($member->first_name, 0, 1) }}{{ substr($member->last_name, 0, 1) }}
                                        </div>
                                        <span class="font-medium">{{ $member->full_name }}</span>
                                    </div>
                                </td>
                                <td><span class="badge badge-ghost badge-sm font-normal">{{ $member->clinical_level->label() }}</span></td>
                                <td class="max-w-xs">
                                    @if ($member->notes)
                                        <span class="text-sm text-base-content/60 truncate block">{{ $member->notes }}</span>
                                    @else
                                        <span class="text-xs text-base-content/30">—</span>
                                    @endif
                                </td>
                            </tr>
                        @empty
                            <tr>
                                <td colspan="3">
                                    <div class="mr-empty-state">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                                        <p>No staff members.</p>
                                        <p class="text-xs mt-1">Add your first staff member to get started.</p>
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
    <dialog id="create-staff-modal" class="modal modal-bottom sm:modal-middle">
        <div class="modal-box mr-modal-box max-w-md">
            <form method="POST" action="{{ route('staff.store') }}">
                @csrf
                <div class="mr-modal-header">
                    <h3>Add Staff Member</h3>
                    <button type="button" class="btn btn-ghost btn-sm btn-square" onclick="document.getElementById('create-staff-modal').close()">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                </div>

                <div class="mr-modal-body space-y-4">
                    <div class="grid grid-cols-2 gap-3">
                        <div class="form-control">
                            <label class="mr-form-label"><span class="label-text">First Name</span></label>
                            <input type="text" name="first_name" class="mr-input w-full" placeholder="John" required />
                        </div>
                        <div class="form-control">
                            <label class="mr-form-label"><span class="label-text">Last Name</span></label>
                            <input type="text" name="last_name" class="mr-input w-full" placeholder="Doe" required />
                        </div>
                    </div>

                    <div class="form-control">
                        <label class="mr-form-label"><span class="label-text">Clinical Level</span></label>
                        <select name="clinical_level" class="mr-select w-full" required>
                            @foreach (\App\Enums\ClinicalLevel::cases() as $level)
                                <option value="{{ $level->value }}">{{ $level->label() }}</option>
                            @endforeach
                        </select>
                    </div>

                    <div class="form-control">
                        <label class="mr-form-label"><span class="label-text">Notes</span></label>
                        <textarea name="notes" class="mr-textarea w-full" rows="2" placeholder="Optional notes..."></textarea>
                    </div>
                </div>

                <div class="mr-modal-footer">
                    <button type="button" class="btn btn-ghost btn-sm" onclick="document.getElementById('create-staff-modal').close()">Cancel</button>
                    <button type="submit" class="btn btn-primary btn-sm">Add Staff</button>
                </div>
            </form>
        </div>
        <form method="dialog" class="modal-backdrop">
            <button>close</button>
        </form>
    </dialog>
@endif
@endsection
