<div class="overflow-x-auto">
    <table class="mr-data-table table-zebra">
        <thead>
            <tr>
                <th>Reference</th>
                <th>Priority</th>
                <th>Category</th>
                <th>Location</th>
                <th>Status</th>
                <th class="text-center">Resources</th>
                <th class="text-right">Actions</th>
            </tr>
        </thead>
        <tbody>
            @forelse ($incidents as $incident)
                <tr class="animate-fade-in">
                    <td>
                        <span class="font-mono text-sm font-medium">{{ $incident->reference }}</span>
                    </td>
                    <td>
                        @php
                            $badgeClass = match($incident->priority) {
                                'P1' => 'mr-badge-p1',
                                'P2' => 'mr-badge-p2',
                                'P3' => 'mr-badge-p3',
                                default => 'badge badge-ghost badge-sm',
                            };
                        @endphp
                        <span class="{{ $badgeClass }}">{{ $incident->priority }}</span>
                    </td>
                    <td><span class="text-sm">{{ $incident->category }}</span></td>
                    <td class="max-w-[200px]">
                        <span class="text-sm truncate block" title="{{ $incident->location }}">{{ $incident->location }}</span>
                    </td>
                    <td>@include('shared.status-badge', ['status' => $incident->status->value])</td>
                    <td class="text-center">
                        <span class="mr-kbd">{{ $incident->resources->count() }}</span>
                    </td>
                    <td class="text-right">
                        <a href="{{ route('incidents.show', $incident) }}" class="btn btn-ghost btn-xs text-primary">
                            View
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                        </a>
                    </td>
                </tr>
            @empty
                <tr>
                    <td colspan="7">
                        <div class="mr-empty-state">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                            <p>No incidents yet.</p>
                        </div>
                    </td>
                </tr>
            @endforelse
        </tbody>
    </table>
</div>
