<?php

declare(strict_types=1);

namespace Tests\Feature;

test('unauthenticated user is redirected to login for protected routes', function (): void {
    $this->get('/events')->assertRedirect('/login');
});

test('unauthenticated user accessing admin routes is redirected to login', function (): void {
    $this->get('/admin/users')->assertRedirect('/login');
});

test('read only user cannot access admin routes', function (): void {
    $readOnly = createReadOnly();
    $this->actingAs($readOnly)->get('/admin/users')->assertStatus(403);
});
