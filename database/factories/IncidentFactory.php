<?php

namespace Database\Factories;

use Illuminate\Database\Eloquent\Factories\Factory;

class IncidentFactory extends Factory
{
    public function definition(): array
    {
        return [
            'event_id' => \App\Models\Event::factory(),
            'reference' => fn (array $attrs) => \App\Models\Incident::generateReference($attrs['event_id']),
            'location' => fake()->address(),
            'priority' => fake()->randomElement(['P1', 'P2', 'P3']),
            'category' => fake()->randomElement(['medical', 'trauma', 'other']),
            'description' => fake()->paragraph(),
            'status' => 'new',
        ];
    }
}
