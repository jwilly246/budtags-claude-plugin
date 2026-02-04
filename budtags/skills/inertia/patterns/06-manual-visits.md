# Pattern 6: Manual Visits (router)

> **⚠️ BudTags Note:** Examples in this file show `confirm()` for simplicity. In BudTags, **NEVER use `confirm()` or `window.confirm()`**. Use a modal-based confirmation component or the `useConfirmDelete` hook instead.

## Overview

The `router` object enables programmatic navigation without `<Link>`:

```tsx
import { router } from '@inertiajs/react';

// Navigate to URL
router.visit('/users');

// Shorthand methods
router.get('/users');
router.post('/users', data);
router.put('/users/1', data);
router.patch('/users/1', data);
router.delete('/users/1');
```

---

## router.visit()

The most flexible navigation method:

```tsx
router.visit(url, options);

// Basic
router.visit('/users');

// With options
router.visit('/users', {
  method: 'post',
  data: { name: 'John' },
  preserveScroll: true,
  preserveState: true,
});
```

---

## HTTP Method Shortcuts

### GET Requests

```tsx
// Simple
router.get('/users');

// With query params
router.get('/users', { search: 'john', page: 2 });

// Explicit URL params
router.get('/users?search=john&page=2');
```

### POST Requests

```tsx
router.post('/users', {
  name: 'John Doe',
  email: 'john@example.com',
});
```

### PUT/PATCH Requests

```tsx
router.put('/users/1', {
  name: 'Updated Name',
});

router.patch('/users/1', {
  email: 'new@example.com',
});
```

### DELETE Requests

```tsx
router.delete('/users/1');

// With confirmation
if (confirm('Delete this user?')) {
  router.delete('/users/1');
}
```

---

## Visit Options

### method

HTTP method (default: `'get'`):

```tsx
router.visit('/logout', { method: 'post' });
```

### data

Request payload:

```tsx
router.visit('/search', {
  method: 'get',
  data: { query: 'inertia', page: 1 },
});
```

### preserveState

Keep React component state:

```tsx
router.get('/users?page=2', {}, {
  preserveState: true,
});
```

### preserveScroll

Keep scroll position:

```tsx
router.post('/update', data, {
  preserveScroll: true,
});
```

### replace

Replace history entry (no back button):

```tsx
router.get('/filtered', filters, {
  replace: true,
});
```

### only / except

Partial reloads:

```tsx
// Only reload 'users' prop
router.reload({ only: ['users'] });

// Reload everything except 'analytics'
router.reload({ except: ['analytics'] });
```

### headers

Custom request headers:

```tsx
router.post('/api/action', data, {
  headers: {
    'X-Custom-Header': 'value',
  },
});
```

---

## Event Callbacks

### onBefore

Runs before request, return `false` to cancel:

```tsx
router.delete('/users/1', {}, {
  onBefore: (visit) => {
    return confirm('Delete this user?');
  },
});
```

### onStart

Runs when request starts:

```tsx
router.get('/users', {}, {
  onStart: () => {
    setLoading(true);
  },
});
```

### onProgress

Track upload progress:

```tsx
router.post('/upload', { file }, {
  onProgress: (progress) => {
    console.log(`${progress.percentage}% uploaded`);
    setProgress(progress.percentage);
  },
});
```

### onSuccess

Runs on successful response:

```tsx
router.post('/users', data, {
  onSuccess: (page) => {
    toast.success('User created!');
    closeModal();
  },
});
```

### onError

Runs on validation errors:

```tsx
router.post('/users', data, {
  onError: (errors) => {
    toast.error(errors.email || 'Validation failed');
  },
});
```

### onFinish

Runs after success or error:

```tsx
router.post('/users', data, {
  onFinish: () => {
    setLoading(false);
  },
});
```

### onCancel

Runs if request is cancelled:

```tsx
router.get('/search', { q: query }, {
  onCancel: () => {
    console.log('Search cancelled');
  },
});
```

---

## router.reload()

Reload the current page:

```tsx
// Full reload
router.reload();

// Partial reload
router.reload({ only: ['users'] });
router.reload({ except: ['analytics'] });

// With options
router.reload({
  only: ['notifications'],
  preserveScroll: true,
});
```

---

## Cancelling Requests

### Cancel active visit

```tsx
router.cancel();

// Example: Cancel on unmount
useEffect(() => {
  return () => {
    router.cancel();
  };
}, []);
```

### Debounced search

```tsx
function SearchInput() {
  const [query, setQuery] = useState('');

  useEffect(() => {
    const timeout = setTimeout(() => {
      router.get('/search', { q: query }, {
        preserveState: true,
        replace: true,
      });
    }, 300);

    return () => {
      clearTimeout(timeout);
      router.cancel();
    };
  }, [query]);

  return (
    <input
      value={query}
      onChange={e => setQuery(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

---

## Event Listeners

Global event listeners for all visits:

```tsx
import { router } from '@inertiajs/react';

// In app setup or layout
router.on('start', (event) => {
  console.log('Starting visit to:', event.detail.visit.url);
});

router.on('finish', (event) => {
  console.log('Visit finished');
});

router.on('navigate', (event) => {
  // Track page views
  analytics.track('pageview', { url: event.detail.page.url });
});
```

### Available Events

| Event | When |
|-------|------|
| `before` | Before making visit |
| `start` | Request started |
| `progress` | Upload progress |
| `success` | Successful response |
| `error` | Error response |
| `finish` | After success or error |
| `navigate` | After page component swap |
| `invalid` | Invalid response received |
| `exception` | Unexpected error |

---

## BudTags Examples

### Button with Manual Visit

```tsx
function RefreshButton() {
  const [loading, setLoading] = useState(false);

  const handleRefresh = () => {
    router.reload({
      only: ['packages'],
      onStart: () => setLoading(true),
      onFinish: () => setLoading(false),
    });
  };

  return (
    <Button onClick={handleRefresh} disabled={loading}>
      {loading ? 'Refreshing...' : 'Refresh'}
    </Button>
  );
}
```

### Search with Debounce

```tsx
function PackageSearch({ initialSearch = '' }) {
  const [search, setSearch] = useState(initialSearch);

  useEffect(() => {
    const timer = setTimeout(() => {
      router.get('/packages', { search }, {
        preserveState: true,
        preserveScroll: true,
        replace: true,
      });
    }, 300);

    return () => clearTimeout(timer);
  }, [search]);

  return (
    <input
      value={search}
      onChange={e => setSearch(e.target.value)}
      placeholder="Search packages..."
    />
  );
}
```

### Delete with Confirmation

```tsx
function DeletePackageButton({ packageId, label }) {
  const handleDelete = () => {
    if (!confirm(`Delete package ${label}?`)) return;

    router.delete(`/packages/${packageId}`, {
      preserveScroll: true,
      onSuccess: () => toast.success('Package deleted'),
      onError: (errors) => toast.error(errors.message || 'Delete failed'),
    });
  };

  return (
    <Button danger onClick={handleDelete}>
      Delete
    </Button>
  );
}
```

---

## Next Steps

- **Forms** → Read `07-forms-useform.md`
- **Partial Reloads** → Read `10-partial-reloads.md`
- **Events & Lifecycle** → Read `21-events-lifecycle.md`
