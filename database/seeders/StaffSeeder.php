<?php

declare(strict_types=1);

namespace Database\Seeders;

use App\Models\Staff;
use Illuminate\Database\Seeder;

class StaffSeeder extends Seeder
{
    public function run(): void
    {
        Staff::factory()->count(50)->create();
    }
}
