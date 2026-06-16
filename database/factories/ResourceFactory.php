<?php

declare(strict_types=1);

namespace Database\Factories;

use App\Models\Event;
use Illuminate\Database\Eloquent\Factories\Factory;

class ResourceFactory extends Factory
{
    public function definition(): array
    {
        return [
            'event_id' => Event::factory(),
            'name' => fake()->word() . ' ' . fake()->randomNumber(2),
            'resource_type' => fake()->randomElement(['ambulance', 'patrol', 'team_lead', 'buggy', 'other']),
            'status' => 'available',
            'availability' => 'available',
        ];
    }
}
