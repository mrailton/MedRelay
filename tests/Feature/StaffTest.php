<?php

namespace Tests\Feature;

test('staff index page is accessible', function () {
    login();
    $this->get('/staff')->assertStatus(200);
});

test('controller can create staff', function () {
    login();

    $this->post('/staff', [
        'first_name' => 'John',
        'last_name' => 'Doe',
        'clinical_level' => 'emt',
    ])->assertSessionHas('success');

    $this->assertDatabaseHas('staff', [
        'first_name' => 'John',
        'last_name' => 'Doe',
    ]);
});
