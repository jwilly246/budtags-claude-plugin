# Pattern 2: Core Concepts

## How Inertia Works

Inertia.js is a **protocol** that sits between your server-side framework (Laravel) and your client-side framework (React). It enables SPA-like experiences without building a separate API.

### The Protocol

1. **Initial Page Load**: Full HTML response (like traditional apps)
2. **Subsequent Navigations**: XHR requests that return JSON
3. **Page Component Swap**: React updates the component without full page reload

```
┌─────────────┐     Full HTML      ┌─────────────┐
│   Browser   │ ◄──────────────────│   Laravel   │
│   (React)   │                    │  Controller │
└─────────────┘                    └─────────────┘
       │                                  ▲
       │  XHR (X-Inertia: true)          │
       └──────────────────────────────────┘
              Returns JSON:
              {
                component: "Users/Index",
                props: { users: [...] },
                url: "/users",
                version: "abc123"
              }
```

### Initial Page Load Response

On first visit, Laravel returns a full HTML page:

```html
<!DOCTYPE html>
<html>
<head>...</head>
<body>
  <div id="app" data-page='{"component":"Users/Index","props":{"users":[...]},"url":"/users","version":"abc123"}'></div>
  <script src="/js/app.js"></script>
</body>
</html>
```

### Subsequent XHR Response

Inertia adds `X-Inertia: true` header. Server responds with JSON:

```json
{
  "component": "Users/Show",
  "props": {
    "user": { "id": 1, "name": "John" }
  },
  "url": "/users/1",
  "version": "abc123"
}
```

---

## Server State vs Client State

### Inertia's Philosophy

Inertia treats **the server as the source of truth**. Unlike SPAs with client-side routing:

| Aspect | Traditional SPA | Inertia.js |
|--------|-----------------|------------|
| Routing | Client-side (React Router) | Server-side (Laravel routes) |
| Data fetching | API calls + caching | Page props from controller |
| State | Client-managed | Server-provided |
| Navigation | Client renders | Server dictates component |

### Page Props Flow

```
Controller → Inertia::render() → HandleInertiaRequests → React Component
```

```php
// Laravel Controller
public function show(User $user)
{
    return Inertia::render('Users/Show', [
        'user' => $user,
        'can' => [
            'edit' => auth()->user()->can('update', $user),
            'delete' => auth()->user()->can('delete', $user),
        ],
    ]);
}
```

```tsx
// React Page Component
interface Props {
  user: User;
  can: {
    edit: boolean;
    delete: boolean;
  };
}

export default function Show({ user, can }: Props) {
  return (
    <div>
      <h1>{user.name}</h1>
      {can.edit && <EditButton userId={user.id} />}
      {can.delete && <DeleteButton userId={user.id} />}
    </div>
  );
}
```

---

## The Page Object

Every Inertia request includes a page object:

```typescript
interface Page<Props = {}> {
  component: string;        // "Users/Index"
  props: Props;            // { users: [...] }
  url: string;             // "/users"
  version: string | null;  // Asset version for cache busting
  scrollRegions: ScrollRegion[];
  rememberedState: Record<string, unknown>;
  clearHistory: boolean;
  encryptHistory: boolean;
}
```

Access via `usePage()`:

```typescript
import { usePage } from '@inertiajs/react';

function Layout({ children }) {
  const page = usePage();

  console.log(page.component);  // Current page component name
  console.log(page.url);        // Current URL
  console.log(page.props);      // All props (including shared)
}
```

---

## Shared Data

Data available on **every** page request:

```php
// HandleInertiaRequests middleware
public function share(Request $request): array
{
    return array_merge(parent::share($request), [
        'user' => fn() => $request->user(),
        'flash' => fn() => $request->session()->get('message'),
    ]);
}
```

Accessed via `usePage().props`:

```typescript
const { user, flash } = usePage<PageProps>().props;
```

---

## Redirects & Flash Messages

After form submissions, Inertia follows redirects automatically:

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

The flash message is available via shared data:

```typescript
const { session } = usePage<PageProps>().props;
// session.message = "User created successfully!"
```

---

## History State

Inertia uses browser history for navigation:

- **Back/Forward**: Works as expected
- **preserveState**: Keeps local component state during navigation
- **preserveScroll**: Maintains scroll position
- **replace**: Replaces history entry instead of pushing

```typescript
router.visit('/users', {
  preserveState: true,   // Keep React state
  preserveScroll: true,  // Keep scroll position
  replace: true,         // Don't add to history
});
```

---

## Asset Versioning

Inertia tracks asset versions to force full page reloads when assets change:

```php
// HandleInertiaRequests
public function version(Request $request): ?string
{
    return parent::version($request);
    // Or custom: return md5_file(public_path('mix-manifest.json'));
}
```

When version changes, Inertia forces a full page reload to get fresh assets.

---

## Key Concepts Summary

| Concept | Description |
|---------|-------------|
| **Protocol** | XHR-based page swapping |
| **Page Props** | Data passed from controller to component |
| **Shared Data** | Props available on every request |
| **Redirects** | Followed automatically, flash messages preserved |
| **History** | Browser history managed by Inertia |
| **Versioning** | Cache busting for assets |

---

## Next Steps

- **Creating Responses** → Read `03-creating-responses.md`
- **Page Components** → Read `04-pages-components.md`
- **Shared Data** → Read `09-shared-data.md`
