<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\AssignResourceStaffRequest;
use App\Http\Requests\RemoveResourceStaffRequest;
use App\Http\Requests\StoreResourceRequest;
use App\Http\Requests\UpdateResourceStatusRequest;
use App\Models\AuditLog;
use App\Models\Event;
use App\Models\Resource;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;

class ResourceController extends Controller
{
    public function index(string $eventId): View
    {
        $event = Event::findOrFail($eventId);
        $resources = $event->resources()->with('staff')->get();
        return view('resources.index', compact('event', 'resources'));
    }

    public function show(Resource $resource): View
    {
        $resource->load(['event', 'staff', 'incidents']);
        return view('resources.show', compact('resource'));
    }

    public function store(StoreResourceRequest $request, string $eventId): RedirectResponse
    {
        $event = Event::findOrFail($eventId);

        $data = $request->validated();

        $data['event_id'] = $event->id;
        $data['status'] = 'available';

        $resource = Resource::create($data);

        if ( ! empty($data['staff_ids'])) {
            $resource->staff()->attach($data['staff_ids']);
            $resource->recalculateCapability();
        }

        AuditLog::log('resource.created', 'resource', (string) $resource->id, after: $resource->toArray());

        return redirect()->route('resources.show', $resource)
            ->with('success', 'Resource created.');
    }

    public function updateStatus(UpdateResourceStatusRequest $request, Resource $resource): RedirectResponse
    {
        $data = $request->validated();

        $before = $resource->toArray();
        $resource->update($data);
        AuditLog::log(
            'resource.updated',
            'resource',
            (string) $resource->id,
            before: $before,
            after: $resource->toArray()
        );

        return redirect()->route('resources.show', $resource)
            ->with('success', 'Resource status updated.');
    }

    public function assignStaff(AssignResourceStaffRequest $request, Resource $resource): RedirectResponse
    {
        $data = $request->validated();

        if ($resource->staff()->where('staff_id', $data['staff_id'])->exists()) {
            return redirect()->route('resources.show', $resource)
                ->with('error', 'Staff member already assigned.');
        }

        $resource->staff()->attach($data['staff_id']);
        $resource->recalculateCapability();

        AuditLog::log('resource.staff-assigned', 'resource', (string) $resource->id);

        return redirect()->route('resources.show', $resource)
            ->with('success', 'Staff assigned.');
    }

    public function removeStaff(RemoveResourceStaffRequest $request, Resource $resource): RedirectResponse
    {
        $data = $request->validated();

        $resource->staff()->detach($data['staff_id']);
        $resource->recalculateCapability();

        AuditLog::log('resource.staff-removed', 'resource', (string) $resource->id);

        return redirect()->route('resources.show', $resource)
            ->with('success', 'Staff removed.');
    }
}
