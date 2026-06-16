<?php

namespace Database\Factories;

use Illuminate\Database\Eloquent\Factories\Factory;

class StaffFactory extends Factory
{
    public function definition(): array
    {
        return [
            'first_name' => fake()->firstName(),
            'last_name' => fake()->lastName(),
            'clinical_level' => fake()->randomElement(['far', 'efr', 'emt', 'paramedic', 'advanced_paramedic']),
            'notes' => fake()->optional()->sentence(),
        ];
    }
}
