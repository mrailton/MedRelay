<?php

namespace App\Http\Controllers;

use App\Enums\IncidentStatus;
use App\Models\AuditLog;
use App\Models\Incident;
use App\Models\Resource;
use Illuminate\Http\Request;

class IncidentController extends Controller
{
    public function index($eventId)
    {
        $event = \App\Models\Event::findOrFail($eventId);
        $incidents = $event->incidents()->orderBy('created_at', 'desc')->get();
        return view('incidents.index', compact('event', 'incidents'));
    }

    public function show(Incident $incident)
    {
        $incident->load(['event', 'resources.staff', 'notes.user']);
        return view('incidents.show', compact('incident'));
    }

    public function store(Request $request, $eventId)
    {
        $event = \App\Models\Event::findOrFail($eventId);

        $data = $request->validate([
            'location' => 'required|string|max:255',
            'priority' => 'required|in:P1,P2,P3',
            'category' => 'required|string|max:50',
            'description' => 'required|string',
        ]);

        $data['event_id'] = $event->id;
        $data['reference'] = Incident::generateReference($event->id);
        $data['status'] = 'new';

        $incident = Incident::create($data);

        AuditLog::log('incident.created', 'incident', (string) $incident->id, after: $incident->toArray());

        return redirect()->route('incidents.show', $incident)
            ->with('success', 'Incident created successfully.');
    }

    public function updateStatus(Request $request, Incident $incident)
    {
        $data = $request->validate([
            'status' => 'required|in:new,dispatched,en_route,on_scene,transporting,complete,cancelled',
        ]);

        $before = $incident->toArray();
        $incident->update($data);

        if ($incident->wasChanged('status')) {
            $incident->resources()->each(function ($resource) use ($incident) {
                if ($incident->status === 'dispatched' || $incident->status === 'en_route') {
                    $resource->update(['status' => 'assigned']);
                } elseif (in_array($incident->status, ['complete', 'cancelled'])) {
                    $resource->update(['status' => 'available']);
                }
            });

            AuditLog::log(
                'incident.updated',
                'incident',
                (string) $incident->id,
                before: $before,
                after: $incident->toArray()
            );
        }

        return redirect()->route('incidents.show', $incident)
            ->with('success', 'Incident status updated.');
    }

    public function assignResource(Request $request, Incident $incident)
    {
        $request->validate([
            'resource_id' => 'required|exists:resources,id',
        ]);

        $resource = Resource::findOrFail($request->resource_id);

        if ($incident->resources()->where('resource_id', $resource->id)->exists()) {
            $incident->resources()->detach($resource->id);
            $resource->update(['status' => 'available']);
            $message = 'Resource unassigned.';
        } else {
            $incident->resources()->attach($resource->id);
            $resource->update(['status' => 'assigned']);

            if ($incident->status === IncidentStatus::New) {
                $incident->update(['status' => 'dispatched']);
            }

            $message = 'Resource assigned.';
        }

        AuditLog::log('incident.resource-assigned', 'incident', (string) $incident->id);

        return redirect()->route('incidents.show', $incident)
            ->with('success', $message);
    }

    public function storeNote(Request $request, Incident $incident)
    {
        $data = $request->validate([
            'content' => 'required|string',
        ]);

        $incident->notes()->create([
            'content' => $data['content'],
            'user_id' => auth()->id(),
        ]);

        AuditLog::log('incident.note-added', 'incident', (string) $incident->id);

        return redirect()->route('incidents.show', $incident)
            ->with('success', 'Note added.');
    }
}
