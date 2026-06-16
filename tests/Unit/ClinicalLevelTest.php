<?php

declare(strict_types=1);

namespace Tests\Unit;

use App\Enums\ClinicalLevel;

test('label returns correct display name for each case', function (ClinicalLevel $case, string $expected): void {
    expect($case->label())->toBe($expected);
})->with([
    [ClinicalLevel::FAR, 'FAR'],
    [ClinicalLevel::EFR, 'EFR'],
    [ClinicalLevel::EMT, 'EMT'],
    [ClinicalLevel::Paramedic, 'Paramedic'],
    [ClinicalLevel::AdvancedParamedic, 'Advanced Paramedic'],
]);

test('rank returns correct numeric value for each case', function (ClinicalLevel $case, int $expected): void {
    expect($case->rank())->toBe($expected);
})->with([
    [ClinicalLevel::FAR, 1],
    [ClinicalLevel::EFR, 2],
    [ClinicalLevel::EMT, 3],
    [ClinicalLevel::Paramedic, 4],
    [ClinicalLevel::AdvancedParamedic, 5],
]);
