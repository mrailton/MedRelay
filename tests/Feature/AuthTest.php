<?php

namespace Tests\Feature;

use App\Models\User;

test('login page is accessible', function () {
    $response = $this->get('/login');
    $response->assertStatus(200);
});

test('authenticated users cannot access login page', function () {
    login();
    $this->get('/login')->assertRedirect('/');
});

test('users can authenticate', function () {
    $user = User::factory()->create([
        'password' => 'password',
    ]);

    $this->post('/login', [
        'email' => $user->email,
        'password' => 'password',
    ])->assertRedirect('/');

    $this->assertAuthenticated();
});

test('users cannot authenticate with invalid password', function () {
    $user = User::factory()->create();

    $this->post('/login', [
        'email' => $user->email,
        'password' => 'wrong-password',
    ]);

    $this->assertGuest();
});

test('users can logout', function () {
    login();
    $this->post('/logout')->assertRedirect('/login');
    $this->assertGuest();
});
