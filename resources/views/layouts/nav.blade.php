<div class="navbar bg-base-100/80 backdrop-blur-sm border-b border-base-200 px-4 sticky top-0 z-30">
    <div class="flex-none lg:hidden">
        <label for="app-drawer" class="btn btn-square btn-ghost">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block h-5 w-5 stroke-current">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
        </label>
    </div>
    <div class="flex-1 flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-content text-sm font-bold">
            M
        </div>
        <span class="text-lg font-bold tracking-tight">{{ config('app.name') }}</span>
    </div>
    <div class="flex-none flex items-center gap-3">
        <div class="badge badge-soft badge-sm">{{ auth()->user()->role->label() }}</div>
        <div class="avatar placeholder">
            <div class="w-8 h-8 rounded-full bg-base-200 text-base-content/60 text-xs font-bold">
                {{ substr(auth()->user()->name, 0, 1) }}
            </div>
        </div>
        <span class="text-sm font-medium hidden sm:block">{{ auth()->user()->name }}</span>
        <form method="POST" action="{{ route('logout') }}" class="inline">
            @csrf
            <button type="submit" class="btn btn-ghost btn-sm text-base-content/60 hover:text-error">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
            </button>
        </form>
    </div>
</div>
