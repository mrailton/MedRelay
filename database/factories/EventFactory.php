<?php

namespace Database\Factories;

use Illuminate\Database\Eloquent\Factories\Factory;

class EventFactory extends Factory
{
    public function definition(): array
    {
        return [
            'name' => fake()->sentence(3),
            'location' => fake()->city(),
            'start_time' => now()->addDays(rand(0, 30)),
            'end_time' => now()->addDays(rand(1, 60)),
            'is_active' => true,
            'notes' => fake()->optional()->paragraph(),
        ];
    }
}
