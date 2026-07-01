<?php

declare(strict_types=1);

namespace App\Enums;

enum ClinicalLevel: string
{
    case EFR = 'efr';
    case EMT = 'emt';
    case Paramedic = 'paramedic';
    case AdvancedParamedic = 'advanced_paramedic';
    case Nurse = 'nurse';
    case Doctor = 'doctor';

    public function label(): string
    {
        return match ($this) {
            self::EFR => 'EFR',
            self::EMT => 'EMT',
            self::Paramedic => 'Paramedic',
            self::AdvancedParamedic => 'Advanced Paramedic',
            self::Nurse => 'Nurse',
            self::Doctor => 'Doctor',
        };
    }

    public function rank(): int
    {
        return match ($this) {
            self::EFR => 1,
            self::EMT => 2,
            self::Paramedic => 3,
            self::AdvancedParamedic => 4,
            self::Nurse => 5,
            self::Doctor => 6,
        };
    }
}
