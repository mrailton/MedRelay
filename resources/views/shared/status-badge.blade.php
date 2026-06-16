@php
$badgeClass = match($status) {
    'new', 'available' => 'badge-soft badge-success',
    'dispatched', 'assigned' => 'badge-soft badge-info',
    'en_route' => 'badge-soft badge-warning',
    'on_scene', 'transporting' => 'badge-soft badge-warning',
    'complete' => 'badge-soft badge-success',
    'cancelled', 'out_of_service' => 'badge-soft badge-error',
    'returning' => 'badge-ghost',
    default => 'badge-ghost',
};
@endphp
<span class="badge {{ $badgeClass }} badge-sm font-medium">{{ str_replace('_', ' ', ucfirst($status)) }}</span>
