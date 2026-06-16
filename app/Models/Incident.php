<?php

namespace App\Models;

use App\Enums\IncidentStatus;
use Database\Factories\IncidentFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Incident extends Model
{
    /** @use HasFactory<IncidentFactory> */
    use HasFactory;

    protected $fillable = [
        'event_id',
        'reference',
        'location',
        'priority',
        'category',
        'description',
        'status',
    ];

    protected function casts(): array
    {
        return [
            'status' => IncidentStatus::class,
        ];
    }

    public function event(): BelongsTo
    {
        return $this->belongsTo(Event::class);
    }

    public function resources(): BelongsToMany
    {
        return $this->belongsToMany(Resource::class, 'incident_resource')
            ->withTimestamps();
    }

    public function notes(): HasMany
    {
        return $this->hasMany(IncidentNote::class);
    }

    public static function generateReference(int $eventId): string
    {
        $count = static::where('event_id', $eventId)->count();
        return $eventId . str_pad((string) ($count + 1), 5, '0', STR_PAD_LEFT);
    }
}
