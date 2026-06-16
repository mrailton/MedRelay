<?php

namespace Database\Seeders;

use App\Enums\UserRole;
use App\Models\User;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        User::factory()->create([
            'name' => 'Admin User',
            'email' => 'admin@medrelay.test',
            'password' => 'password',
            'role' => UserRole::Admin,
        ]);

        User::factory()->create([
            'name' => 'Controller User',
            'email' => 'controller@medrelay.test',
            'password' => 'password',
            'role' => UserRole::Controller,
        ]);

        User::factory()->create([
            'name' => 'Read Only User',
            'email' => 'readonly@medrelay.test',
            'password' => 'password',
            'role' => UserRole::ReadOnly,
        ]);
    }
}
