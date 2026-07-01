<?php

declare(strict_types=1);

namespace Database\Factories;

use App\Enums\ClinicalLevel;
use Illuminate\Database\Eloquent\Factories\Factory;

class StaffFactory extends Factory
{
    public function definition(): array
    {
        return [
            'first_name' => $this->faker->firstName(),
            'last_name' => $this->faker->lastName(),
            'clinical_level' => $this->faker->randomElement(ClinicalLevel::class),
        ];
    }
}
