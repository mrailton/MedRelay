<dialog id="create-incident-modal" class="modal modal-bottom sm:modal-middle">
    <div class="modal-box mr-modal-box max-w-lg">
        <form method="POST" action="{{ route('events.incidents.store', $event) }}">
            @csrf
            <div class="mr-modal-header">
                <h3>Create Incident</h3>
                <button type="button" class="btn btn-ghost btn-sm btn-square" onclick="document.getElementById('create-incident-modal').close()">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>

            <div class="mr-modal-body space-y-4">
                <div class="form-control">
                    <label class="mr-form-label"><span class="label-text">Location</span></label>
                    <input type="text" name="location" class="mr-input w-full" placeholder="Incident location" required />
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="mr-form-label"><span class="label-text">Priority</span></label>
                        <select name="priority" class="mr-select w-full" required>
                            <option value="P1">P1 - Critical</option>
                            <option value="P2">P2 - Urgent</option>
                            <option value="P3">P3 - Routine</option>
                        </select>
                    </div>
                    <div class="form-control">
                        <label class="mr-form-label"><span class="label-text">Category</span></label>
                        <select name="category" class="mr-select w-full" required>
                            <option value="medical">Medical</option>
                            <option value="trauma">Trauma</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>

                <div class="form-control">
                    <label class="mr-form-label"><span class="label-text">Description</span></label>
                    <textarea name="description" class="mr-textarea w-full" rows="3" placeholder="Describe the incident..." required></textarea>
                </div>
            </div>

            <div class="mr-modal-footer">
                <button type="button" class="btn btn-ghost btn-sm" onclick="document.getElementById('create-incident-modal').close()">Cancel</button>
                <button type="submit" class="btn btn-primary btn-sm">Create Incident</button>
            </div>
        </form>
    </div>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
</dialog>
