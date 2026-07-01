# MedRelay

MedRelay is a Laravel-based event medical management system for tracking events, incidents, resources, staff, and admin users.

## Requirements

- PHP 8.5+
- Composer
- Node.js 20+ and npm
- SQLite by default, or another database supported by Laravel

## Quick start

From a fresh clone:

```bash
composer run setup
```

That script will:

1. Install PHP dependencies
2. Copy `.env.example` to `.env` if needed
3. Generate an application key
4. Run migrations
5. Install frontend dependencies
6. Build the frontend assets

## Run the app locally

Start the full local stack with:

```bash
composer run dev
```

This runs the Laravel server, queue listener, log viewer, and Vite dev server together.

If you only need one piece:

```bash
php artisan serve
npm run dev
```

## Common commands

```bash
php artisan migrate
php artisan test
composer run lint
composer run analyse
composer run format
```

## What the app does

- Authenticate users
- Manage events
- Track incidents and incident notes
- Assign resources and staff
- Update incident and resource status
- View admin tools like user management and audit logs

## Health check

The app exposes a simple health endpoint:

```bash
GET /up
```

It returns a JSON response showing whether the app and database are available.

## Main routes

- `/login` - sign in
- `/` - dashboard
- `/events` - events
- `/incidents/{incident}` - incident details
- `/resources/{resource}` - resource details
- `/staff` - staff directory
- `/admin/users` - admin user management
- `/admin/audit-logs` - audit logs

## Notes

- The default environment example uses SQLite.
- Sessions, cache, and queues are configured to use the database by default.

