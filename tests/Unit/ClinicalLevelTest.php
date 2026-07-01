<?php

declare(strict_types=1);

namespace Tests\Unit;

use App\Enums\ClinicalLevel;

test('label returns correct display name for each case', function (ClinicalLevel $case, string $expected): void {
    expect($case->label())->toBe($expected);
})->with([
    [ClinicalLevel::EFR, 'EFR'],
    [ClinicalLevel::EMT, 'EMT'],
    [ClinicalLevel::Paramedic, 'Paramedic'],
    [ClinicalLevel::AdvancedParamedic, 'Advanced Paramedic'],
    [ClinicalLevel::Nurse, 'Nurse'],
    [ClinicalLevel::Doctor, 'Doctor'],
]);

test('rank returns correct numeric value for each case', function (ClinicalLevel $case, int $expected): void {
    expect($case->rank())->toBe($expected);
})->with([
    [ClinicalLevel::EFR, 1],
    [ClinicalLevel::EMT, 2],
    [ClinicalLevel::Paramedic, 3],
    [ClinicalLevel::AdvancedParamedic, 4],
    [ClinicalLevel::Nurse, 5],
    [ClinicalLevel::Doctor, 6],
]);
