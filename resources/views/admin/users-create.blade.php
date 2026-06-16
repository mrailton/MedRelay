@extends('layouts.app')

@section('title', 'Create User')

@section('content')
<div class="max-w-xl mx-auto space-y-6">
    <div>
        <h1 class="mr-page-title">Create User</h1>
        <p class="mr-page-subtitle">Add a new user to the system</p>
    </div>

    <div class="mr-form-card">
        <div class="card-body">
            <form method="POST" action="{{ route('admin.users.store') }}" class="space-y-4">
                @csrf
                <div class="form-control">
                    <label class="mr-form-label"><span class="label-text">Name</span></label>
                    <input type="text" name="name" class="mr-input w-full @error('name') input-error @enderror" value="{{ old('name') }}" placeholder="Full name" required />
                    @error('name') <label class="label pt-1"><span class="label-text-alt text-error text-xs">{{ $message }}</span></label> @enderror
                </div>

                <div class="form-control">
                    <label class="mr-form-label"><span class="label-text">Email</span></label>
                    <input type="email" name="email" class="mr-input w-full @error('email') input-error @enderror" value="{{ old('email') }}" placeholder="email@example.com" required />
                    @error('email') <label class="label pt-1"><span class="label-text-alt text-error text-xs">{{ $message }}</span></label> @enderror
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="mr-form-label"><span class="label-text">Password</span></label>
                        <input type="password" name="password" class="mr-input w-full @error('password') input-error @enderror" placeholder="&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;" required />
                        @error('password') <label class="label pt-1"><span class="label-text-alt text-error text-xs">{{ $message }}</span></label> @enderror
                    </div>
                    <div class="form-control">
                        <label class="mr-form-label"><span class="label-text">Confirm Password</span></label>
                        <input type="password" name="password_confirmation" class="mr-input w-full" placeholder="&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;" required />
                    </div>
                </div>

                <div class="form-control">
                    <label class="mr-form-label"><span class="label-text">Role</span></label>
                    <select name="role" class="mr-select w-full" required>
                        @foreach (\App\Enums\UserRole::cases() as $role)
                            <option value="{{ $role->value }}">{{ $role->label() }}</option>
                        @endforeach
                    </select>
                </div>

                <div class="flex gap-3 pt-2">
                    <a href="{{ route('admin.users') }}" class="btn btn-ghost">Cancel</a>
                    <button type="submit" class="btn btn-primary">Create User</button>
                </div>
            </form>
        </div>
    </div>
</div>
@endsection
