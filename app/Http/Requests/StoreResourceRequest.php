<?php

declare(strict_types=1);

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StoreResourceRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'name' => ['required', 'string', 'max:255'],
            'resource_type' => ['required', 'in:ambulance,patrol,team_lead,buggy,other'],
            'staff_ids' => ['nullable', 'array'],
            'staff_ids.*' => ['exists:staff,id'],
        ];
    }
}
