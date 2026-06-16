<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\StoreStaffRequest;
use App\Models\AuditLog;
use App\Models\Staff;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;

class StaffController extends Controller
{
    public function index(): View
    {
        $staff = Staff::orderBy('first_name')->get();
        return view('staff.index', compact('staff'));
    }

    public function store(StoreStaffRequest $request): RedirectResponse
    {
        $staff = Staff::create($request->validated());

        AuditLog::log('staff.created', 'staff', (string) $staff->id, after: $staff->toArray());

        return redirect()->route('staff.index')
            ->with('success', 'Staff member added.');
    }
}
