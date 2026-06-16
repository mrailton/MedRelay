<?php

declare(strict_types=1);

namespace App\Enums;

enum ResourceStatus: string
{
    case Available = 'available';
    case Assigned = 'assigned';
    case EnRoute = 'en_route';
    case OnScene = 'on_scene';
    case Transporting = 'transporting';
    case Returning = 'returning';
    case OutOfService = 'out_of_service';

    public function label(): string
    {
        return match ($this) {
            self::Available => 'Available',
            self::Assigned => 'Assigned',
            self::EnRoute => 'En Route',
            self::OnScene => 'On Scene',
            self::Transporting => 'Transporting',
            self::Returning => 'Returning',
            self::OutOfService => 'Out of Service',
        };
    }
}
