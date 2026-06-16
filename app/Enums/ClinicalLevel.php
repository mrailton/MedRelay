<?php

declare(strict_types=1);

namespace App\Enums;

enum ClinicalLevel: string
{
    case FAR = 'far';
    case EFR = 'efr';
    case EMT = 'emt';
    case Paramedic = 'paramedic';
    case AdvancedParamedic = 'advanced_paramedic';

    public function label(): string
    {
        return match ($this) {
            self::FAR => 'FAR',
            self::EFR => 'EFR',
            self::EMT => 'EMT',
            self::Paramedic => 'Paramedic',
            self::AdvancedParamedic => 'Advanced Paramedic',
        };
    }

    public function rank(): int
    {
        return match ($this) {
            self::FAR => 1,
            self::EFR => 2,
            self::EMT => 3,
            self::Paramedic => 4,
            self::AdvancedParamedic => 5,
        };
    }
}
