<div class="overflow-x-auto">
    <table class="mr-data-table table-zebra">
        <thead>
            <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Status</th>
                <th>Staff</th>
                <th class="text-right">Actions</th>
            </tr>
        </thead>
        <tbody>
            @forelse ($resources as $resource)
                <tr class="animate-fade-in">
                    <td class="font-medium">{{ $resource->name }}</td>
                    <td><span class="text-sm">{{ $resource->resource_type->label() }}</span></td>
                    <td>@include('shared.status-badge', ['status' => $resource->status->value])</td>
                    <td>
                        @if ($resource->staff->count() > 0)
                            <div class="flex flex-wrap gap-1">
                                @foreach ($resource->staff as $staff)
                                    <span class="badge badge-ghost badge-sm font-normal">{{ $staff->first_name }} {{ strtoupper(substr($staff->last_name, 0, 1)) }}.</span>
                                @endforeach
                            </div>
                        @else
                            <span class="text-xs text-base-content/40">No staff</span>
                        @endif
                    </td>
                    <td class="text-right">
                        <a href="{{ route('resources.show', $resource) }}" class="btn btn-ghost btn-xs text-primary">
                            View
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                        </a>
                    </td>
                </tr>
            @empty
                <tr>
                    <td colspan="5">
                        <div class="mr-empty-state">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                            <p>No resources yet.</p>
                        </div>
                    </td>
                </tr>
            @endforelse
        </tbody>
    </table>
</div>
