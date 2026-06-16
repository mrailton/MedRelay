<dialog id="create-resource-modal" class="modal modal-bottom sm:modal-middle">
    <div class="modal-box mr-modal-box max-w-lg">
        <form method="POST" action="{{ route('events.resources.store', $event) }}">
            @csrf
            <div class="mr-modal-header">
                <h3>Create Resource</h3>
                <button type="button" class="btn btn-ghost btn-sm btn-square" onclick="document.getElementById('create-resource-modal').close()">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>

            <div class="mr-modal-body space-y-4">
                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="mr-form-label"><span class="label-text">Name</span></label>
                        <input type="text" name="name" class="mr-input w-full" placeholder="Resource name" required />
                    </div>
                    <div class="form-control">
                        <label class="mr-form-label"><span class="label-text">Type</span></label>
                        <select name="resource_type" class="mr-select w-full" required>
                            @foreach (\App\Enums\ResourceType::cases() as $type)
                                <option value="{{ $type->value }}">{{ $type->label() }}</option>
                            @endforeach
                        </select>
                    </div>
                </div>

                <div class="form-control">
                    <label class="mr-form-label"><span class="label-text">Assign Staff</span></label>
                    <div class="max-h-40 overflow-y-auto space-y-1.5 border border-base-200 rounded-xl p-3">
                        @forelse ($allStaff as $staff)
                            <label class="flex items-center gap-2 cursor-pointer px-1 py-0.5 rounded hover:bg-base-200/50 transition-colors">
                                <input type="checkbox" name="staff_ids[]" value="{{ $staff->id }}" class="checkbox checkbox-primary checkbox-sm" />
                                <span class="text-sm">{{ $staff->full_name }}</span>
                                <span class="badge badge-ghost badge-xs ml-auto">{{ $staff->clinical_level->label() }}</span>
                            </label>
                        @empty
                            <p class="text-sm text-base-content/40 text-center py-4">No staff available. <a href="{{ route('staff.index') }}" class="link link-primary">Add staff first.</a></p>
                        @endforelse
                    </div>
                </div>
            </div>

            <div class="mr-modal-footer">
                <button type="button" class="btn btn-ghost btn-sm" onclick="document.getElementById('create-resource-modal').close()">Cancel</button>
                <button type="submit" class="btn btn-primary btn-sm">Create Resource</button>
            </div>
        </form>
    </div>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
</dialog>
