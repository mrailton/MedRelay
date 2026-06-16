<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Enums\IncidentStatus;
use App\Http\Requests\AssignIncidentResourceRequest;
use App\Http\Requests\StoreIncidentNoteRequest;
use App\Http\Requests\StoreIncidentRequest;
use App\Http\Requests\UpdateIncidentStatusRequest;
use App\Models\AuditLog;
use App\Models\Event;
use App\Models\Incident;
use App\Models\Resource;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;

class IncidentController extends Controller
{
    public function index(string $eventId): View
    {
        $event = Event::findOrFail($eventId);
        $incidents = $event->incidents()->orderBy('created_at', 'desc')->get();
        return view('incidents.index', compact('event', 'incidents'));
    }

    public function show(Incident $incident): View
    {
        $incident->load(['event', 'resources.staff', 'notes.user']);
        return view('incidents.show', compact('incident'));
    }

    public function store(StoreIncidentRequest $request, string $eventId): RedirectResponse
    {
        $event = Event::findOrFail($eventId);

        $data = $request->validated();

        $data['event_id'] = $event->id;
        $data['reference'] = Incident::generateReference($event->id);
        $data['status'] = 'new';

        $incident = Incident::create($data);

        AuditLog::log('incident.created', 'incident', (string) $incident->id, after: $incident->toArray());

        return redirect()->route('incidents.show', $incident)
            ->with('success', 'Incident created successfully.');
    }

    public function updateStatus(UpdateIncidentStatusRequest $request, Incident $incident): RedirectResponse
    {
        $data = $request->validated();

        $before = $incident->toArray();
        $incident->update($data);

        if ($incident->wasChanged('status')) {
            $incident->resources()->each(function ($resource) use ($incident): void {
                if (IncidentStatus::Dispatched === $incident->status || IncidentStatus::EnRoute === $incident->status) {
                    $resource->update(['status' => 'assigned']);
                } elseif (IncidentStatus::Complete === $incident->status || IncidentStatus::Cancelled === $incident->status) {
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

    public function assignResource(AssignIncidentResourceRequest $request, Incident $incident): RedirectResponse
    {
        $data = $request->validated();

        $resource = Resource::findOrFail($data['resource_id']);

        if ($incident->resources()->where('resource_id', $resource->id)->exists()) {
            $incident->resources()->detach($resource->id);
            $resource->update(['status' => 'available']);
            $message = 'Resource unassigned.';
        } else {
            $incident->resources()->attach($resource->id);
            $resource->update(['status' => 'assigned']);

            if (IncidentStatus::New === $incident->status) {
                $incident->update(['status' => 'dispatched']);
            }

            $message = 'Resource assigned.';
        }

        AuditLog::log('incident.resource-assigned', 'incident', (string) $incident->id);

        return redirect()->route('incidents.show', $incident)
            ->with('success', $message);
    }

    public function storeNote(StoreIncidentNoteRequest $request, Incident $incident): RedirectResponse
    {
        $data = $request->validated();

        $incident->notes()->create([
            'content' => $data['content'],
            'user_id' => auth()->id(),
        ]);

        AuditLog::log('incident.note-added', 'incident', (string) $incident->id);

        return redirect()->route('incidents.show', $incident)
            ->with('success', 'Note added.');
    }
}
