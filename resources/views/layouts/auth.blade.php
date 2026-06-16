<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>{{ config('app.name') }} @hasSection('title') - @yield('title') @endif</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body class="min-h-screen bg-gradient-to-br from-base-200 via-base-100 to-base-200">
    <div class="flex min-h-screen items-center justify-center p-4">
        <div class="card w-full max-w-md bg-base-100 shadow-xl border border-base-200/50 animate-slide-up">
            <div class="card-body p-8">
                <div class="text-center mb-6">
                    <div class="w-14 h-14 rounded-2xl bg-primary flex items-center justify-center text-primary-content text-xl font-bold mx-auto mb-4 shadow-sm">
                        M
                    </div>
                    <h1 class="text-2xl font-bold tracking-tight">{{ config('app.name') }}</h1>
                    <p class="text-sm text-base-content/50 mt-1">Medical Event CAD Dispatch</p>
                </div>

                @if (session('error'))
                    <div class="mr-alert mr-alert-error mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 stroke-current flex-shrink-0" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        <span>{{ session('error') }}</span>
                    </div>
                @endif

                @yield('content')
            </div>
        </div>
    </div>
</body>
</html>
