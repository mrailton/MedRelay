<?php

namespace App\Models;

use App\Enums\UserRole;
use Database\Factories\UserFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

class User extends Authenticatable
{
    /** @use HasFactory<UserFactory> */
    use HasFactory;
    use Notifiable;

    protected $fillable = [
        'name',
        'email',
        'password',
        'role',
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',
            'role' => UserRole::class,
        ];
    }

    public function isAdmin(): bool
    {
        return $this->role === UserRole::Admin;
    }

    public function isController(): bool
    {
        return $this->role === UserRole::Controller;
    }

    public function isReadOnly(): bool
    {
        return $this->role === UserRole::ReadOnly;
    }

    public function isControllerOrAdmin(): bool
    {
        return $this->isAdmin() || $this->isController();
    }

    public function incidentNotes()
    {
        return $this->hasMany(IncidentNote::class);
    }

    public function auditLogs()
    {
        return $this->hasMany(AuditLog::class);
    }
}
