<?php

declare(strict_types=1);

namespace App\Http\Requests;

use App\Enums\IncidentLifecycleStatus;
use Illuminate\Foundation\Http\FormRequest;

class UpdateIncidentStatusRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'status' => ['required', 'in:' . implode(',', IncidentLifecycleStatus::values())],
            'close_notes' => ['nullable', 'string', 'max:2000'],
            'reopen_notes' => ['required_if:status,open', 'string', 'max:2000'],
        ];
    }
}
