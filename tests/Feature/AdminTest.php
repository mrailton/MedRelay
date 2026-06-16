<?php

declare(strict_types=1);

namespace Tests\Feature;

test('admin can view users page', function (): void {
    $admin = createAdmin();
    $this->actingAs($admin)->get('/admin/users')->assertStatus(200);
});

test('controller cannot view users page', function (): void {
    $controller = createController();
    $this->actingAs($controller)->get('/admin/users')->assertStatus(403);
});

test('admin can create user', function (): void {
    $admin = createAdmin();
    $this->actingAs($admin)->post('/admin/users', [
        'name' => 'New User',
        'email' => 'newuser@test.com',
        'password' => 'password',
        'password_confirmation' => 'password',
        'role' => 'controller',
    ])->assertSessionHas('success');

    $this->assertDatabaseHas('users', [
        'email' => 'newuser@test.com',
        'role' => 'controller',
    ]);
});

test('admin can view audit logs', function (): void {
    $admin = createAdmin();
    $this->actingAs($admin)->get('/admin/audit-logs')->assertStatus(200);
});

test('admin can view create user page', function (): void {
    $admin = createAdmin();
    $this->actingAs($admin)->get('/admin/users/create')->assertStatus(200);
});
