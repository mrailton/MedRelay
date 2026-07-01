<?php

declare(strict_types=1);

namespace Database\Factories;

use App\Enums\IncidentLifecycleStatus;
use App\Models\Event;
use App\Models\Incident;
use Illuminate\Database\Eloquent\Factories\Factory;

class IncidentFactory extends Factory
{
    public function definition(): array
    {
        return [
            'event_id' => Event::factory(),
            'reference' => fn (array $attrs) => Incident::generateReference($attrs['event_id']),
            'location' => fake()->address(),
            'priority' => fake()->randomElement(['P1', 'P2', 'P3']),
            'category' => fake()->randomElement(['medical', 'trauma', 'other']),
            'description' => fake()->paragraph(),
            'status' => IncidentLifecycleStatus::Open->value,
        ];
    }
}
