<?php

declare(strict_types=1);

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StoreIncidentRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'location' => ['required', 'string', 'max:255'],
            'priority' => ['required', 'in:P1,P2,P3'],
            'category' => ['required', 'string', 'max:50'],
            'description' => ['required', 'string'],
        ];
    }
}
