---
name: inertia
description: Inertia.js v2 patterns for Laravel + React full-stack development, including useForm, routing, shared data, and server-side integration
version: 1.0.1
category: project
agent: react-specialist
auto_activate:
  patterns:
    - "**/*.{ts,tsx,js,jsx,php}"
  keywords:
    - "inertia"
    - "useForm"
    - "usePage"
    - "router.visit"
    - "router.post"
    - "router.get"
    - "router.reload"
    - "Inertia::render"
    - "Inertia::defer"
    - "HandleInertiaRequests"
    - "preserveState"
    - "preserveScroll"
    - "createInertiaApp"
    - "@inertiajs/react"
    - "inertiajs/inertia-laravel"
    - "Link component"
    - "partial reload"
    - "deferred props"
    - "shared data"
---

# Inertia.js v2 Skill

> **⚠️ BudTags Note:** Some examples in this skill show `confirm()` for simplicity. In BudTags, **NEVER use `confirm()` or `window.confirm()`**. Use a modal-based confirmation component or the `useConfirmDelete` hook instead.

Comprehensive patterns for **Inertia.js v2** - the glue between your Laravel backend and React frontend, enabling modern SPA experiences without building a separate API.

## Version Targets

| Package | Version | Notes |
|---------|---------|-------|
| **@inertiajs/react** | ^2.2.16 | React adapter (client-side) |
| **inertiajs/inertia-laravel** | ^2.0 | Laravel adapter (server-side) |
| **React** | 19.2.0 | React 19 compatible |
| **Laravel** | 11.x | Laravel 11 |

## What is Inertia.js?

Inertia.js lets you build **modern single-page apps** using classic server-side routing and controllers:

- **No API Required** - No need for JSON APIs, just return Inertia responses from Laravel
- **Server-Side Routing** - Define routes in Laravel, not in React Router
- **Full-Page Reactivity** - SPA experience with React, no page reloads
- **Shared State** - Automatic handling of auth, flash messages, validation errors
- **Form Handling** - Built-in `useForm` hook for form state, validation, and file uploads

## BudTags Stack Context

| Inertia Feature | BudTags Usage |
|-----------------|---------------|
| **useForm** | All form submissions (HarvestPlantsModal, FormEditOrg, etc.) |
| **usePage** | Access user, permissions, session data globally |
| **HandleInertiaRequests** | Shares user, roles, permissions, session, announcements |
| **preserveScroll** | Keeps scroll position on form submission |
| **React Query coexistence** | Metrc API data uses React Query, forms use Inertia |

---

## Progressive Loading Strategy

Load only the patterns you need:

### Quick Start (~350 lines)
```
patterns/01-installation-setup.md       (150 lines)
patterns/02-core-concepts.md            (200 lines)
```

### Server-Side Responses (~325 lines)
```
patterns/03-creating-responses.md       (175 lines)
patterns/09-shared-data.md              (150 lines)
```

### Forms & Validation (~450 lines)
```
patterns/07-forms-useform.md            (250 lines)
patterns/08-form-helper-advanced.md     (200 lines)
```

### Navigation (~375 lines)
```
patterns/05-link-component.md           (175 lines)
patterns/06-manual-visits.md            (200 lines)
```

### Data Loading (~325 lines)
```
patterns/10-partial-reloads.md          (175 lines)
patterns/11-deferred-props.md           (150 lines)
```

### BudTags Patterns (~200 lines)
```
patterns/25-budtags-integration.md      (200 lines)
```

---

## Quick Reference

### useForm Hook (React)

```typescript
import { useForm } from '@inertiajs/react';

function CreateUserForm() {
  const { data, setData, post, processing, errors, reset } = useForm({
    name: '',
    email: '',
    password: '',
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    post('/users', {
      preserveScroll: true,
      onSuccess: () => {
        reset();
        toast.success('User created!');
      },
      onError: (errors) => {
        toast.error(errors.email || 'Failed to create user');
      },
    });
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={data.name}
        onChange={e => setData('name', e.target.value)}
      />
      {errors.name && <span className="error">{errors.name}</span>}

      <button disabled={processing}>
        {processing ? 'Saving...' : 'Create User'}
      </button>
    </form>
  );
}
```

### usePage Hook (React)

```typescript
import { usePage } from '@inertiajs/react';
import { PageProps } from '@/Types/types';

function Header() {
  const { user, permissions, session } = usePage<PageProps>().props;

  return (
    <nav>
      <span>Welcome, {user?.name}</span>
      {permissions.includes('admin') && <AdminLink />}
      {session.message && <Flash message={session.message} />}
    </nav>
  );
}
```

### Laravel Response

```php
// Controller
public function index()
{
    return Inertia::render('Users/Index', [
        'users' => User::paginate(10),
        'filters' => request()->only(['search', 'status']),
    ]);
}

// With lazy/deferred data
public function show(User $user)
{
    return Inertia::render('Users/Show', [
        'user' => $user,
        // Only evaluated when requested
        'orders' => fn () => $user->orders()->latest()->get(),
        // Loaded after initial page render
        'analytics' => Inertia::defer(fn () => $this->calculateAnalytics($user)),
    ]);
}
```

### Shared Data (Middleware)

```php
// app/Http/Middleware/HandleInertiaRequests.php
public function share(Request $request): array
{
    return array_merge(parent::share($request), [
        'user' => fn() => $request->user()?->load(['active_org.features']),
        'permissions' => fn() => $request->user()?->active_org_perms() ?? [],
        'session' => [
            'message' => fn () => $request->session()->get('message'),
            'license' => fn () => $request->session()->get('license'),
        ],
    ]);
}
```

### Link Component

```tsx
import { Link } from '@inertiajs/react';

// Basic navigation
<Link href="/users">Users</Link>

// Preserve state/scroll
<Link href="/users" preserveState preserveScroll>
  Refresh Users
</Link>

// Form-like behavior
<Link
  href={`/posts/${post.id}`}
  method="delete"
  as="button"
  onBefore={() => confirm('Delete this post?')}
>
  Delete
</Link>

// Prefetch on hover
<Link href="/dashboard" prefetch>
  Dashboard
</Link>
```

### Manual Visits (router)

```typescript
import { router } from '@inertiajs/react';

// GET request
router.get('/users', { search: 'john' });

// POST request
router.post('/users', userData, {
  preserveScroll: true,
  onSuccess: () => toast.success('Created!'),
});

// Reload current page (partial)
router.reload({ only: ['users'] });

// Replace history (no back button)
router.visit('/login', { replace: true });
```

---

## All Pattern Files (25 Total)

### Foundation (4 patterns - ~675 lines)
- `01-installation-setup.md` (150) - Laravel & React setup, createInertiaApp
- `02-core-concepts.md` (200) - How Inertia works, the protocol, XHR requests
- `03-creating-responses.md` (175) - Inertia::render(), props, redirects
- `04-pages-components.md` (150) - Page components, layouts, TypeScript

### Navigation (2 patterns - ~375 lines)
- `05-link-component.md` (175) - Link props, prefetch, method, preserveState
- `06-manual-visits.md` (200) - router.visit(), get/post/put/patch/delete

### Forms (2 patterns - ~450 lines)
- `07-forms-useform.md` (250) - useForm hook, validation, processing, errors
- `08-form-helper-advanced.md` (200) - transform, remember, file uploads, progress

### Data & State (4 patterns - ~600 lines)
- `09-shared-data.md` (150) - HandleInertiaRequests, global props
- `10-partial-reloads.md` (175) - only/except, lazy evaluation
- `11-deferred-props.md` (150) - Inertia::defer(), Deferred component
- `12-scroll-management.md` (125) - Scroll regions, preserveScroll

### Auth & Security (4 patterns - ~525 lines)
- `13-authentication.md` (150) - Auth patterns with Laravel Breeze/Sanctum
- `14-authorization.md` (125) - Passing policies/permissions to frontend
- `15-validation-errors.md` (150) - Error bags, displaying validation errors
- `16-csrf-protection.md` (100) - CSRF token handling

### Error Handling (2 patterns - ~250 lines)
- `17-error-handling.md` (150) - Error pages, 404/500/503
- `18-asset-versioning.md` (100) - Cache busting, version()

### Advanced (5 patterns - ~775 lines)
- `19-progress-indicators.md` (125) - NProgress, custom progress
- `20-remembering-state.md` (150) - remember(), preserveState deep-dive
- `21-events-lifecycle.md` (175) - before, success, error, finish events
- `22-ssr.md` (200) - Server-side rendering setup
- `23-testing.md` (125) - Testing Inertia responses in Laravel

### Extras (2 patterns - ~325 lines)
- `24-head-component.md` (125) - Head, title, meta tags
- `25-budtags-integration.md` (200) - BudTags-specific patterns

---

## BudTags-Specific Examples

### Modal with useForm

```typescript
// BudTags pattern: Modal + useForm + inertiaHandlers
import { useForm } from '@inertiajs/react';
import { handleInertiaSuccess, handleInertiaError } from '@/utils/inertiaHandlers';

function HarvestPlantsModal({ isOpen, onClose, selectedPlants }) {
  const { data, setData, post, reset } = useForm({
    harvest_name: '',
    harvest_weight: 0,
    plants: selectedPlants.map(p => p.Label),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    post('/harvest-plants', {
      preserveScroll: true,
      onSuccess: (page) => handleInertiaSuccess(page, onClose, reset),
      onError: (errors) => handleInertiaError(errors, 'Failed to harvest'),
    });
  };

  return (
    <Modal show={isOpen} onClose={onClose}>
      <form onSubmit={handleSubmit}>
        {/* Form fields */}
      </form>
    </Modal>
  );
}
```

### When to Use Inertia vs React Query

| Use Case | Use Inertia | Use React Query |
|----------|-------------|-----------------|
| Form submission | ✅ `useForm` | ❌ |
| Page navigation | ✅ `Link`, `router` | ❌ |
| Create/Update/Delete | ✅ `useForm` | ❌ |
| Metrc API fetches | ❌ | ✅ `useQuery` |
| Background polling | ❌ | ✅ `refetchInterval` |
| Complex caching | ❌ | ✅ Query keys |
| Optimistic updates | ⚠️ Limited | ✅ Full support |

### Accessing Shared Data

```typescript
// BudTags: usePage for global state
const { user, permissions, session } = usePage<PageProps>().props;

// Check organization features
const hasLabFeature = user?.active_org?.features
  .some(f => f.name === 'labs');

// Check permissions
const canManageUsers = permissions.includes('manage-users');

// Flash message from session (handled by MainLayout)
if (session.message) {
  toast.success(session.message);
}
```

---

## Key Differences from React Query

| Aspect | Inertia.js | React Query |
|--------|-----------|-------------|
| **Purpose** | Full-page SPA navigation | Server state caching |
| **Routing** | Server-side (Laravel) | Client-side (React Router) |
| **Data fetching** | Page props from controller | API calls with caching |
| **Mutations** | `useForm` with redirect | `useMutation` with invalidation |
| **Caching** | Browser history only | Intelligent query cache |
| **Best for** | CRUD pages, forms | Real-time data, complex queries |

---

## Next Steps

- **Start:** Read `01-installation-setup.md` for setup
- **Learn:** Read `02-core-concepts.md` for fundamentals
- **Forms:** Read `07-forms-useform.md` for form handling
- **BudTags:** Read `25-budtags-integration.md` for project patterns

## Resources

- **Official Docs:** https://inertiajs.com
- **GitHub (Laravel):** https://github.com/inertiajs/inertia-laravel
- **GitHub (React):** https://github.com/inertiajs/inertia/tree/master/packages/react
- **Discord:** https://discord.gg/inertiajs
