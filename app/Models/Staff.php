<?php

declare(strict_types=1);

namespace App\Models;

use App\Enums\ClinicalLevel;
use Database\Factories\StaffFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Staff extends Model
{
    /** @use HasFactory<StaffFactory> */
    use HasFactory;

    protected $fillable = [
        'first_name',
        'last_name',
        'clinical_level',
        'notes',
    ];

    public function getFullNameAttribute(): string
    {
        return "{$this->first_name} {$this->last_name}";
    }

    public function resources(): BelongsToMany
    {
        return $this->belongsToMany(Resource::class, 'resource_staff')
            ->withTimestamps();
    }

    protected function casts(): array
    {
        return [
            'clinical_level' => ClinicalLevel::class,
        ];
    }
}
