<?php

namespace App\Http\Controllers;

use App\Models\Event;
use App\Models\Staff;
use Illuminate\Http\Request;

class DashboardController extends Controller
{
    public function __invoke(Request $request)
    {
        $activeEvents = Event::where('is_active', true)
            ->orWhere('end_time', '>=', now())
            ->orderBy('name')
            ->get();

        $selectedEvent = null;
        $incidents = collect();
        $resources = collect();
        $allStaff = collect();

        if ($request->has('event_id') && blank($request->event_id)) {
            session()->forget('selected_event_id');
        }

        $eventId = $request->input('event_id', session('selected_event_id'));

        if ($eventId) {
            $selectedEvent = Event::find($eventId);
            if ($selectedEvent) {
                session(['selected_event_id' => $selectedEvent->id]);
                $incidents = $selectedEvent->incidents()->orderBy('created_at', 'desc')->get();
                $resources = $selectedEvent->resources()->with('staff')->get();
            }
        }

        if ($request->ajax()) {
            return response()->noContent();
        }

        $allStaff = Staff::orderBy('first_name')->get();

        return view('dashboard', compact(
            'activeEvents',
            'selectedEvent',
            'incidents',
            'resources',
            'allStaff',
        ));
    }
}
