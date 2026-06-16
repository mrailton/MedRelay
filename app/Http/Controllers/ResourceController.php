<?php

namespace App\Http\Controllers;

use App\Models\AuditLog;
use App\Models\Event;
use App\Models\Resource;
use Illuminate\Http\Request;

class ResourceController extends Controller
{
    public function index($eventId)
    {
        $event = Event::findOrFail($eventId);
        $resources = $event->resources()->with('staff')->get();
        return view('resources.index', compact('event', 'resources'));
    }

    public function show(Resource $resource)
    {
        $resource->load(['event', 'staff', 'incidents']);
        return view('resources.show', compact('resource'));
    }

    public function store(Request $request, $eventId)
    {
        $event = Event::findOrFail($eventId);

        $data = $request->validate([
            'name' => 'required|string|max:255',
            'resource_type' => 'required|in:ambulance,patrol,team_lead,buggy,other',
            'staff_ids' => 'nullable|array',
            'staff_ids.*' => 'exists:staff,id',
        ]);

        $data['event_id'] = $event->id;
        $data['status'] = 'available';

        $resource = Resource::create($data);

        if (! empty($data['staff_ids'])) {
            $resource->staff()->attach($data['staff_ids']);
            $resource->recalculateCapability();
        }

        AuditLog::log('resource.created', 'resource', (string) $resource->id, after: $resource->toArray());

        return redirect()->route('resources.show', $resource)
            ->with('success', 'Resource created.');
    }

    public function updateStatus(Request $request, Resource $resource)
    {
        $data = $request->validate([
            'status' => 'required|in:available,assigned,en_route,on_scene,transporting,returning,out_of_service',
        ]);

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

    public function assignStaff(Request $request, Resource $resource)
    {
        $data = $request->validate([
            'staff_id' => 'required|exists:staff,id',
        ]);

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

    public function removeStaff(Request $request, Resource $resource)
    {
        $data = $request->validate([
            'staff_id' => 'required|exists:staff,id',
        ]);

        $resource->staff()->detach($data['staff_id']);
        $resource->recalculateCapability();

        AuditLog::log('resource.staff-removed', 'resource', (string) $resource->id);

        return redirect()->route('resources.show', $resource)
            ->with('success', 'Staff removed.');
    }
}
