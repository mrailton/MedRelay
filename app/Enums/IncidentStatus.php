<?php

declare(strict_types=1);

namespace App\Enums;

enum IncidentStatus: string
{
    case New = 'new';
    case Dispatched = 'dispatched';
    case EnRoute = 'en_route';
    case OnScene = 'on_scene';
    case Transporting = 'transporting';
    case Complete = 'complete';
    case Cancelled = 'cancelled';

    public function label(): string
    {
        return match ($this) {
            self::New => 'New',
            self::Dispatched => 'Dispatched',
            self::EnRoute => 'En Route',
            self::OnScene => 'On Scene',
            self::Transporting => 'Transporting',
            self::Complete => 'Complete',
            self::Cancelled => 'Cancelled',
        };
    }
}
