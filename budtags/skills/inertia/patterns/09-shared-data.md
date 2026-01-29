# Pattern 9: Shared Data

## Overview

Shared data is props available on **every** Inertia request without manually including them in each controller response.

Common use cases:
- Current authenticated user
- Permissions/roles
- Flash messages
- Session data
- Application settings

---

## HandleInertiaRequests Middleware

The middleware's `share()` method defines shared data:

```php
// app/Http/Middleware/HandleInertiaRequests.php
namespace App\Http\Middleware;

use Illuminate\Http\Request;
use Inertia\Middleware;

class HandleInertiaRequests extends Middleware
{
    protected $rootView = 'app';

    public function share(Request $request): array
    {
        return array_merge(parent::share($request), [
            // Synchronous
            'appName' => config('app.name'),

            // Lazy-loaded (closure)
            'auth' => fn () => [
                'user' => $request->user(),
            ],
        ]);
    }
}
```

---

## Lazy Loading

Wrap data in closures for lazy evaluation:

```php
public function share(Request $request): array
{
    return array_merge(parent::share($request), [
        // Always evaluated
        'appName' => config('app.name'),

        // Only evaluated when accessed
        'auth' => fn () => [
            'user' => $request->user()
                ? $request->user()->only('id', 'name', 'email')
                : null,
        ],

        // Evaluated lazily
        'permissions' => fn () => $request->user()
            ?->getAllPermissions()->pluck('name')
            ?? [],
    ]);
}
```

---

## BudTags HandleInertiaRequests

```php
class HandleInertiaRequests extends Middleware
{
    protected $rootView = 'app';

    public function version(Request $request): ?string
    {
        return parent::version($request);
    }

    public function share(Request $request): array
    {
        $user = $request->user();
        $user?->load(['active_org.features']);

        return array_merge(parent::share($request), [
            // User with active organization
            'user' => fn() => $user ?? null,

            // User's roles in active org
            'roles' => fn() => $user?->active_org_roles() ?? [],

            // User's permissions in active org
            'permissions' => fn() => $user?->active_org_perms() ?? [],

            // UI preferences
            'ui_preferences' => fn() => $user?->ui_preferences ?? [],

            // Latest announcement
            'latest_announcement' => fn() => Announcement::where('is_published', true)
                ->orderBy('release_date', 'desc')
                ->first(),

            // Session data (Metrc license, flash messages)
            'session' => [
                'licenses' => fn () => $request->session()->get('licenses'),
                'license' => fn () => $request->session()->get('license'),
                'org' => fn () => $request->session()->get('org'),
                'message' => fn () => $request->session()->get('message'),
                'facility_permissions' => fn () => $request->session()->get('facility_permissions', []),
            ],
        ]);
    }
}
```

---

## Accessing Shared Data (React)

### usePage Hook

```tsx
import { usePage } from '@inertiajs/react';
import { PageProps } from '@/Types/types';

function Header() {
  const { user, permissions, session } = usePage<PageProps>().props;

  return (
    <header>
      {user ? (
        <span>Welcome, {user.name}</span>
      ) : (
        <Link href="/login">Login</Link>
      )}

      {permissions.includes('admin') && (
        <Link href="/admin">Admin Panel</Link>
      )}
    </header>
  );
}
```

### In Page Components

```tsx
export default function Dashboard({ stats }) {
  const { user, session } = usePage<PageProps>().props;

  // Both page props (stats) and shared props (user, session) available
  return (
    <div>
      <h1>Welcome, {user?.name}</h1>
      {session.message && <Alert>{session.message}</Alert>}
      <StatsWidget stats={stats} />
    </div>
  );
}
```

### In Layout Components

```tsx
export default function MainLayout({ children }) {
  const { user, permissions, session } = usePage<PageProps>().props;
  const lastMessage = useRef<string | null>(null);

  // Handle flash messages
  useEffect(() => {
    if (session.message && session.message !== lastMessage.current) {
      toast.success(session.message);
      lastMessage.current = session.message;
    }
  }, [session.message]);

  return (
    <div className="min-h-screen">
      <Navbar user={user} permissions={permissions} />
      <main>{children}</main>
      <ToastContainer />
    </div>
  );
}
```

---

## Flash Messages

### Server-Side (Laravel)

```php
// Controller
public function store(Request $request)
{
    User::create($request->validated());

    return redirect()
        ->route('users.index')
        ->with('message', 'User created successfully!');
}
```

### Share in Middleware

```php
'session' => [
    'message' => fn () => $request->session()->get('message'),
],
```

### Display in React

```tsx
function MainLayout({ children }) {
  const { session } = usePage<PageProps>().props;

  useEffect(() => {
    if (session.message) {
      toast.success(session.message);
    }
  }, [session.message]);

  return <div>{children}</div>;
}
```

---

## Manual Sharing

Share data outside the middleware:

```php
// In a service provider or controller
use Inertia\Inertia;

Inertia::share('appVersion', '1.0.0');

// With closure
Inertia::share('notifications', fn () => auth()->user()?->unreadNotifications);
```

---

## TypeScript Types

Define types for shared data:

```tsx
// resources/js/Types/types.tsx
export interface User {
  id: number;
  name: string;
  email: string;
  active_org?: Organization;
}

export interface PageProps {
  user: User | null;
  roles: string[];
  permissions: string[];
  ui_preferences: Record<string, any>;
  latest_announcement: Announcement | null;
  session: {
    licenses?: string[];
    license?: string;
    org?: number;
    message?: string;
    facility_permissions?: string[];
  };
}
```

Use with `usePage`:

```tsx
const { user, permissions } = usePage<PageProps>().props;
// user is User | null
// permissions is string[]
```

---

## Best Practices

### Keep It Minimal

Only share frequently needed data:

```php
// Good - commonly used
'user' => fn() => $request->user()?->only('id', 'name', 'email'),

// Bad - rarely needed, include in specific pages
'allUsers' => fn() => User::all(),
```

### Use Lazy Loading

Wrap queries in closures to avoid unnecessary database calls:

```php
// Good - only runs when accessed
'permissions' => fn() => $request->user()?->permissions,

// Bad - always runs
'permissions' => $request->user()?->permissions,
```

### Namespace Data

Organize related data under keys:

```php
'auth' => fn() => [
    'user' => $request->user(),
    'permissions' => $request->user()?->permissions,
],

'session' => [
    'message' => fn() => session('message'),
    'license' => fn() => session('license'),
],
```

---

## Next Steps

- **Partial Reloads** → Read `10-partial-reloads.md`
- **Deferred Props** → Read `11-deferred-props.md`
- **Authentication** → Read `13-authentication.md`
