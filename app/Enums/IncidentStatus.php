<?php

declare(strict_types=1);

namespace App\Enums;

enum IncidentStatus: string
{
    case Dispatched = 'dispatched';
    case EnRoute = 'en_route';
    case OnScene = 'on_scene';
    case Transporting = 'transporting';
    case Complete = 'complete';
    case StoodDown = 'stood_down';

    /**
     * @return list<string>
     */
    public static function values(): array
    {
        return array_map(
            static fn (self $status): string => $status->value,
            self::cases(),
        );
    }

    public function label(): string
    {
        return match ($this) {
            self::Dispatched => 'Dispatched',
            self::EnRoute => 'En Route',
            self::OnScene => 'On Scene',
            self::Transporting => 'Transporting',
            self::Complete => 'Complete',
            self::StoodDown => 'Stood Down',
        };
    }
}
