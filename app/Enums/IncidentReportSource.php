<?php

declare(strict_types=1);

namespace App\Enums;

enum IncidentReportSource: string
{
    case EVENT_CONTROL = 'EVENT_CONTROL';
    case PRODUCTION = 'PRODUCTION';
    case SECURITY = 'SECURITY';
    case MEDICS = 'MEDICS';
    case OTHER = 'OTHER';

    public function label(): string
    {
        return match ($this) {
            self::EVENT_CONTROL => 'Event Control',
            self::PRODUCTION => 'Production',
            self::SECURITY => 'Security',
            self::MEDICS => 'Medics',
            self::OTHER => 'Other',
        };
    }
}
