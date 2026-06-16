<?php

namespace App\Models;

use App\Enums\ResourceStatus;
use App\Enums\ResourceType;
use App\Enums\ClinicalLevel;
use Database\Factories\ResourceFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Resource extends Model
{
    /** @use HasFactory<ResourceFactory> */
    use HasFactory;

    protected $fillable = [
        'event_id',
        'name',
        'resource_type',
        'status',
        'availability',
        'highest_clinical_level',
        'is_deployable',
    ];

    protected function casts(): array
    {
        return [
            'resource_type' => ResourceType::class,
            'status' => ResourceStatus::class,
            'is_deployable' => 'boolean',
            'highest_clinical_level' => ClinicalLevel::class,
        ];
    }

    public function event(): BelongsTo
    {
        return $this->belongsTo(Event::class);
    }

    public function staff(): BelongsToMany
    {
        return $this->belongsToMany(Staff::class, 'resource_staff')
            ->withTimestamps();
    }

    public function incidents(): BelongsToMany
    {
        return $this->belongsToMany(Incident::class, 'incident_resource')
            ->withTimestamps();
    }

    public function recalculateCapability(): void
    {
        $highest = $this->staff()
            ->get()
            ->pluck('clinical_level')
            ->filter()
            ->sort(fn (ClinicalLevel $a, ClinicalLevel $b) => $b->rank() <=> $a->rank())
            ->first();

        $this->highest_clinical_level = $highest;
        $this->is_deployable = $this->staff()->count() > 0;
        $this->save();
    }
}
