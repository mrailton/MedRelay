<?php

declare(strict_types=1);

namespace App\Enums;

enum UserRole: string
{
    case Admin = 'admin';
    case Controller = 'controller';
    case ReadOnly = 'read_only';

    public function label(): string
    {
        return match ($this) {
            self::Admin => 'Admin',
            self::Controller => 'Controller',
            self::ReadOnly => 'Read Only',
        };
    }
}
