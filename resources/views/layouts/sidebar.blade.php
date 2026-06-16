<div class="drawer-side z-40">
    <label for="app-drawer" class="drawer-overlay"></label>
    <aside class="bg-base-100 border-r border-base-200 min-h-full w-64">
        <div class="flex items-center gap-3 px-6 py-5 border-b border-base-200">
            <div class="w-9 h-9 rounded-xl bg-primary flex items-center justify-center text-primary-content text-base font-bold shadow-sm">
                M
            </div>
            <div>
                <h2 class="font-bold text-sm">{{ config('app.name') }}</h2>
                <p class="text-xs text-base-content/40">CAD Dispatch</p>
            </div>
        </div>

        <div class="p-3">
            <div class="mr-sidebar-section-title px-3 pb-2">Main</div>
            <ul class="menu menu-sm gap-0.5">
                <li>
                    <a href="{{ route('dashboard') }}"
                       class="mr-nav-link {{ request()->routeIs('dashboard') ? 'active' : '' }}">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
                        Dashboard
                    </a>
                </li>
                <li>
                    <a href="{{ route('events.index') }}"
                       class="mr-nav-link {{ request()->routeIs('events.*') ? 'active' : '' }}">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                        Events
                    </a>
                </li>
                <li>
                    <a href="{{ route('staff.index') }}"
                       class="mr-nav-link {{ request()->routeIs('staff.*') ? 'active' : '' }}">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                        Staff
                    </a>
                </li>
            </ul>

            @if (auth()->user()->isAdmin())
                <div class="mr-divider"></div>
                <div class="mr-sidebar-section-title px-3 pb-2">Administration</div>
                <ul class="menu menu-sm gap-0.5">
                    <li>
                        <a href="{{ route('admin.users') }}"
                           class="mr-nav-link {{ request()->routeIs('admin.users*') ? 'active' : '' }}">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" /></svg>
                            Users
                        </a>
                    </li>
                    <li>
                        <a href="{{ route('admin.audit-logs') }}"
                           class="mr-nav-link {{ request()->routeIs('admin.audit-logs') ? 'active' : '' }}">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                            Audit Logs
                        </a>
                    </li>
                </ul>
            @endif
        </div>

        <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-base-200 bg-base-100">
            <div class="flex items-center gap-3 px-3">
                <div class="avatar placeholder">
                    <div class="w-8 h-8 rounded-full bg-primary/10 text-primary text-xs font-bold">
                        {{ substr(auth()->user()->name, 0, 1) }}
                    </div>
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium truncate">{{ auth()->user()->name }}</p>
                    <p class="text-xs text-base-content/40 truncate">{{ auth()->user()->email }}</p>
                </div>
            </div>
        </div>
    </aside>
</div>
