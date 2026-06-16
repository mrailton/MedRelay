<?php

declare(strict_types=1);

namespace App\Enums;

enum ResourceType: string
{
    case Ambulance = 'ambulance';
    case Patrol = 'patrol';
    case TeamLead = 'team_lead';
    case Buggy = 'buggy';
    case Other = 'other';

    public function label(): string
    {
        return match ($this) {
            self::Ambulance => 'Ambulance',
            self::Patrol => 'Patrol',
            self::TeamLead => 'Team Lead',
            self::Buggy => 'Buggy',
            self::Other => 'Other',
        };
    }
}
