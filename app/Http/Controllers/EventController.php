<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\StoreEventRequest;
use App\Models\AuditLog;
use App\Models\Event;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;

class EventController extends Controller
{
    public function index(): View
    {
        $events = Event::orderBy('created_at', 'desc')->get();
        return view('events.index', compact('events'));
    }

    public function store(StoreEventRequest $request): RedirectResponse
    {
        $event = Event::create($request->validated());

        AuditLog::log('event.created', 'event', (string) $event->id, after: $event->toArray());

        return redirect()->route('events.index')
            ->with('success', 'Event created successfully.');
    }

    public function show(Event $event): View
    {
        return view('events.show', compact('event'));
    }

    public function edit(Event $event): View
    {
        return view('events.edit', compact('event'));
    }

    public function update(StoreEventRequest $request, Event $event): RedirectResponse
    {
        $before = $event->toArray();
        $event->update($request->validated());
        AuditLog::log('event.updated', 'event', (string) $event->id, before: $before, after: $event->toArray());

        return redirect()->route('events.show', $event)
            ->with('success', 'Event updated successfully.');
    }
}
