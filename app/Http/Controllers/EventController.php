<?php

namespace App\Http\Controllers;

use App\Models\AuditLog;
use App\Models\Event;
use Illuminate\Http\Request;

class EventController extends Controller
{
    public function index()
    {
        $events = Event::orderBy('created_at', 'desc')->get();
        return view('events.index', compact('events'));
    }

    public function store(Request $request)
    {
        $data = $request->validate([
            'name' => 'required|string|max:255',
            'location' => 'required|string|max:255',
            'start_time' => 'required|date',
            'end_time' => 'nullable|date|after:start_time',
            'is_active' => 'boolean',
            'notes' => 'nullable|string',
        ]);

        $event = Event::create($data);

        AuditLog::log('event.created', 'event', (string) $event->id, after: $event->toArray());

        return redirect()->route('events.index')
            ->with('success', 'Event created successfully.');
    }

    public function show(Event $event)
    {
        return view('events.show', compact('event'));
    }

    public function edit(Event $event)
    {
        return view('events.edit', compact('event'));
    }

    public function update(Request $request, Event $event)
    {
        $data = $request->validate([
            'name' => 'required|string|max:255',
            'location' => 'required|string|max:255',
            'start_time' => 'required|date',
            'end_time' => 'nullable|date|after:start_time',
            'is_active' => 'boolean',
            'notes' => 'nullable|string',
        ]);

        $before = $event->toArray();
        $event->update($data);
        AuditLog::log('event.updated', 'event', (string) $event->id, before: $before, after: $event->toArray());

        return redirect()->route('events.show', $event)
            ->with('success', 'Event updated successfully.');
    }
}
