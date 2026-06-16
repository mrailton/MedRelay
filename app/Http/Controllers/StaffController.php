<?php

namespace App\Http\Controllers;

use App\Models\AuditLog;
use App\Models\Staff;
use Illuminate\Http\Request;

class StaffController extends Controller
{
    public function index()
    {
        $staff = Staff::orderBy('first_name')->get();
        return view('staff.index', compact('staff'));
    }

    public function store(Request $request)
    {
        $data = $request->validate([
            'first_name' => 'required|string|max:255',
            'last_name' => 'required|string|max:255',
            'clinical_level' => 'required|in:far,efr,emt,paramedic,advanced_paramedic',
            'notes' => 'nullable|string',
        ]);

        $staff = Staff::create($data);

        AuditLog::log('staff.created', 'staff', (string) $staff->id, after: $staff->toArray());

        return redirect()->route('staff.index')
            ->with('success', 'Staff member added.');
    }
}
