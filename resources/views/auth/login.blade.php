@extends('layouts.auth')

@section('content')
<form method="POST" action="{{ route('login') }}" class="space-y-4">
    @csrf

    <div class="form-control">
        <label class="mr-form-label" for="email">
            <span class="label-text">Email</span>
        </label>
        <div class="relative">
            <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-base-content/40">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
            </span>
            <input
                type="email"
                id="email"
                name="email"
                class="mr-input pl-10 w-full @error('email') input-error @enderror"
                value="{{ old('email') }}"
                placeholder="you@example.com"
                required
                autofocus
            />
        </div>
        @error('email')
            <label class="label pt-1">
                <span class="label-text-alt text-error text-xs">{{ $message }}</span>
            </label>
        @enderror
    </div>

    <div class="form-control">
        <label class="mr-form-label" for="password">
            <span class="label-text">Password</span>
        </label>
        <div class="relative">
            <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-base-content/40">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
            </span>
            <input
                type="password"
                id="password"
                name="password"
                class="mr-input pl-10 w-full @error('password') input-error @enderror"
                placeholder="&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;"
                required
            />
        </div>
        @error('password')
            <label class="label pt-1">
                <span class="label-text-alt text-error text-xs">{{ $message }}</span>
            </label>
        @enderror
    </div>

    <div class="flex items-center justify-between">
        <label class="label cursor-pointer justify-start gap-2">
            <input type="checkbox" name="remember" class="checkbox checkbox-primary checkbox-sm" />
            <span class="label-text text-sm">Remember me</span>
        </label>
    </div>

    <button type="submit" class="btn btn-primary w-full">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/></svg>
        Sign In
    </button>
</form>
@endsection
