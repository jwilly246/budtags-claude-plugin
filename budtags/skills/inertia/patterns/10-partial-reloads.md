# Pattern 10: Partial Reloads

## Overview

Partial reloads fetch only specific props from the server, reducing data transfer and improving performance.

```tsx
// Instead of reloading everything...
router.reload();

// Only reload the 'users' prop
router.reload({ only: ['users'] });
```

---

## only Option

Specify which props to fetch:

```tsx
import { router } from '@inertiajs/react';

// Single prop
router.reload({ only: ['users'] });

// Multiple props
router.reload({ only: ['users', 'stats'] });

// With Link
<Link href="/dashboard" only={['notifications']}>
  Refresh Notifications
</Link>
```

---

## except Option

Fetch all props except specified ones:

```tsx
// Reload everything except analytics (expensive)
router.reload({ except: ['analytics'] });

// With Link
<Link href="/dashboard" except={['heavyData']}>
  Refresh
</Link>
```

---

## Server-Side Lazy Evaluation

For partial reloads to be efficient, wrap props in closures:

```php
// Controller
public function index()
{
    return Inertia::render('Users/Index', [
        // Always included (cheap)
        'filters' => request()->only(['search', 'status']),

        // Only evaluated when requested
        'users' => fn () => User::paginate(10),

        // Only evaluated when requested
        'stats' => fn () => $this->calculateStats(),

        // Never included unless explicitly requested
        'analytics' => Inertia::optional(fn () => $this->heavyAnalytics()),
    ]);
}
```

### How It Works

| Request Type | `users` closure | `stats` closure |
|-------------|-----------------|-----------------|
| Full page load | Evaluated | Evaluated |
| `only: ['users']` | Evaluated | Not evaluated |
| `only: ['stats']` | Not evaluated | Evaluated |
| `except: ['stats']` | Evaluated | Not evaluated |

---

## Inertia::optional()

Props that are **never** included unless explicitly requested:

```php
return Inertia::render('Dashboard', [
    'user' => $user,
    'notifications' => fn () => $user->notifications,

    // Only included when: router.reload({ only: ['analytics'] })
    'analytics' => Inertia::optional(fn () => $this->heavyCalculation()),
]);
```

---

## Inertia::always()

Props that are **always** included, even in partial reloads:

```php
return Inertia::render('Users/Index', [
    'users' => fn () => User::paginate(),

    // Always included, even with only: ['users']
    'flash' => Inertia::always(fn () => session('message')),
]);
```

---

## Common Use Cases

### Refresh List After Action

```tsx
function UsersList({ users }) {
  const handleDelete = async (userId: number) => {
    await router.delete(`/users/${userId}`, {
      onSuccess: () => {
        // Only reload the users list
        router.reload({ only: ['users'] });
      },
    });
  };

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>
          {user.name}
          <button onClick={() => handleDelete(user.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

### Polling/Auto-Refresh

```tsx
function Notifications({ notifications }) {
  useEffect(() => {
    const interval = setInterval(() => {
      router.reload({ only: ['notifications'] });
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return <NotificationList items={notifications} />;
}
```

### Pagination

```tsx
function UsersTable({ users, filters }) {
  const handlePageChange = (page: number) => {
    router.get('/users', { ...filters, page }, {
      only: ['users'],
      preserveState: true,
      preserveScroll: true,
    });
  };

  return (
    <div>
      <Table data={users.data} />
      <Pagination
        currentPage={users.current_page}
        lastPage={users.last_page}
        onPageChange={handlePageChange}
      />
    </div>
  );
}
```

### Search/Filter

```tsx
function SearchableList({ users, filters }) {
  const [search, setSearch] = useState(filters.search || '');

  useEffect(() => {
    const timer = setTimeout(() => {
      router.get('/users', { search }, {
        only: ['users', 'filters'],
        preserveState: true,
        preserveScroll: true,
        replace: true,
      });
    }, 300);

    return () => clearTimeout(timer);
  }, [search]);

  return (
    <div>
      <input
        value={search}
        onChange={e => setSearch(e.target.value)}
        placeholder="Search..."
      />
      <UsersList users={users} />
    </div>
  );
}
```

---

## Combining with preserveState

Partial reloads work well with state preservation:

```tsx
router.reload({
  only: ['users'],
  preserveState: true,   // Keep React component state
  preserveScroll: true,  // Keep scroll position
});
```

---

## BudTags Example

### Refresh Metrc Data

```tsx
function PackagesPage({ packages, locations, filters }) {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefreshPackages = () => {
    setIsRefreshing(true);
    router.reload({
      only: ['packages'],
      preserveScroll: true,
      onFinish: () => setIsRefreshing(false),
    });
  };

  const handleRefreshLocations = () => {
    router.reload({
      only: ['locations'],
      preserveScroll: true,
    });
  };

  return (
    <div>
      <div className="flex gap-2">
        <Button onClick={handleRefreshPackages} disabled={isRefreshing}>
          {isRefreshing ? 'Refreshing...' : 'Refresh Packages'}
        </Button>
        <Button onClick={handleRefreshLocations}>
          Refresh Locations
        </Button>
      </div>

      <PackagesTable packages={packages} locations={locations} />
    </div>
  );
}
```

---

## Performance Tips

1. **Use closures** for expensive queries on the server
2. **Use `optional()`** for rarely-needed heavy data
3. **Use `always()`** for data that must always be fresh (flash messages)
4. **Combine with `preserveState`** to avoid React re-renders
5. **Use `replace: true`** for filters to avoid history bloat

---

## Next Steps

- **Deferred Props** → Read `11-deferred-props.md`
- **Scroll Management** → Read `12-scroll-management.md`
- **Events** → Read `21-events-lifecycle.md`
