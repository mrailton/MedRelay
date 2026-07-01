<?php

declare(strict_types=1);

use App\Http\Controllers\AdminController;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\EventController;
use App\Http\Controllers\IncidentController;
use App\Http\Controllers\ResourceController;
use App\Http\Controllers\StaffController;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Route;

Route::get('/up', function () {
    try {
        DB::select('SELECT 1');
        return response()->json(['status' => 'ok', 'database' => 'ok']);
    } catch (Exception $e) {
        return response()->json(['status' => 'degraded', 'database' => 'unavailable'], 503);
    }
});

Route::middleware('guest')->group(function (): void {
    Route::get('/login', [AuthController::class, 'login'])->name('login');
    Route::post('/login', [AuthController::class, 'authenticate']);
});

Route::post('/logout', [AuthController::class, 'logout'])->name('logout');

Route::middleware('auth')->group(function (): void {
    Route::get('/', DashboardController::class)->name('dashboard');

    Route::get('/events', [EventController::class, 'index'])->name('events.index');
    Route::post('/events', [EventController::class, 'store'])->name('events.store');
    Route::get('/events/{event}', [EventController::class, 'show'])->name('events.show');
    Route::get('/events/{event}/edit', [EventController::class, 'edit'])->name('events.edit');
    Route::post('/events/{event}', [EventController::class, 'update'])->name('events.update');

    Route::get('/events/{event}/incidents', [IncidentController::class, 'index'])->name('events.incidents.index');
    Route::post('/events/{event}/incidents', [IncidentController::class, 'store'])->name('events.incidents.store');
    Route::get('/incidents/{incident}', [IncidentController::class, 'show'])->name('incidents.show');
    Route::post('/incidents/{incident}/status', [IncidentController::class, 'updateStatus'])->name('incidents.update-status');
    Route::post('/incidents/{incident}/resources/{resource}/status', [IncidentController::class, 'updateResourceStatus'])
        ->name('incidents.resources.update-status');
    Route::post('/incidents/{incident}/assign-resource', [IncidentController::class, 'assignResource'])->name('incidents.assign-resource');
    Route::post('/incidents/{incident}/notes', [IncidentController::class, 'storeNote'])->name('incidents.notes.store');

    Route::get('/events/{event}/resources', [ResourceController::class, 'index'])->name('events.resources.index');
    Route::post('/events/{event}/resources', [ResourceController::class, 'store'])->name('events.resources.store');
    Route::get('/resources/{resource}', [ResourceController::class, 'show'])->name('resources.show');
    Route::post('/resources/{resource}/status', [ResourceController::class, 'updateStatus'])->name('resources.update-status');
    Route::post('/resources/{resource}/assign-staff', [ResourceController::class, 'assignStaff'])->name('resources.assign-staff');
    Route::post('/resources/{resource}/remove-staff', [ResourceController::class, 'removeStaff'])->name('resources.remove-staff');

    Route::get('/staff', [StaffController::class, 'index'])->name('staff.index');
    Route::post('/staff', [StaffController::class, 'store'])->name('staff.store');

    Route::middleware('role:admin')->group(function (): void {
        Route::get('/admin/users', [AdminController::class, 'users'])->name('admin.users');
        Route::get('/admin/users/create', [AdminController::class, 'createUser'])->name('admin.users.create');
        Route::post('/admin/users', [AdminController::class, 'storeUser'])->name('admin.users.store');
        Route::get('/admin/audit-logs', [AdminController::class, 'auditLogs'])->name('admin.audit-logs');
    });
});
