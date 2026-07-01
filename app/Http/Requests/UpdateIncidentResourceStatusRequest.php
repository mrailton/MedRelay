<?php

declare(strict_types=1);

namespace App\Http\Requests;

use App\Enums\IncidentStatus;
use Illuminate\Foundation\Http\FormRequest;

class UpdateIncidentResourceStatusRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'status' => ['required', 'in:' . implode(',', IncidentStatus::values())],
        ];
    }
}
