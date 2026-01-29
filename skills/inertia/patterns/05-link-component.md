# Pattern 5: Link Component

## Basic Usage

The `<Link>` component creates client-side navigation links:

```tsx
import { Link } from '@inertiajs/react';

// Basic link
<Link href="/users">Users</Link>

// With class
<Link href="/dashboard" className="text-blue-600 hover:underline">
  Dashboard
</Link>
```

---

## Link Props

### href (required)

The URL to navigate to:

```tsx
<Link href="/users">Users</Link>
<Link href={`/users/${user.id}`}>View User</Link>
<Link href={route('users.show', user.id)}>View User</Link> // With Ziggy
```

### method

HTTP method for the request (default: `get`):

```tsx
<Link href="/logout" method="post">Logout</Link>
<Link href={`/posts/${post.id}`} method="delete">Delete</Link>
```

### data

Data to include with the request:

```tsx
<Link href="/users" method="post" data={{ name: 'John' }}>
  Create John
</Link>

// With query parameters for GET
<Link href="/users" data={{ search: 'john', page: 2 }}>
  Search John
</Link>
```

### as

Render as a different element:

```tsx
<Link href="/logout" method="post" as="button" className="btn">
  Logout
</Link>
// Renders: <button>Logout</button>

<Link href="/download" as="button" download>
  Download
</Link>
```

---

## State Management Props

### preserveState

Keep local React state after navigation:

```tsx
<Link href="/users?page=2" preserveState>
  Next Page
</Link>

// Useful for:
// - Pagination
// - Filtering
// - Tab switching
```

### preserveScroll

Maintain scroll position after navigation:

```tsx
<Link href="/users" preserveScroll>
  Refresh
</Link>

// By default, Inertia scrolls to top
// preserveScroll keeps current position
```

### replace

Replace the current history entry instead of pushing:

```tsx
<Link href="/users?sort=name" replace>
  Sort by Name
</Link>

// Back button will skip this entry
```

---

## Prefetching

### prefetch

Preload page data on hover:

```tsx
<Link href="/dashboard" prefetch>
  Dashboard
</Link>
```

### prefetch with options

```tsx
<Link
  href="/users"
  prefetch="mount"      // Prefetch on mount
  cacheFor={30000}      // Cache for 30 seconds
>
  Users
</Link>

// prefetch options:
// - true / "hover" - Prefetch on hover
// - "mount" - Prefetch when component mounts
// - "click" - Prefetch on mousedown (just before click)
```

---

## Event Callbacks

### onBefore

Runs before the visit, return `false` to cancel:

```tsx
<Link
  href={`/posts/${post.id}`}
  method="delete"
  onBefore={() => confirm('Are you sure?')}
>
  Delete Post
</Link>
```

### onStart

Runs when the request starts:

```tsx
<Link
  href="/users"
  onStart={() => console.log('Loading...')}
>
  Users
</Link>
```

### onSuccess

Runs when the request succeeds:

```tsx
<Link
  href="/users"
  onSuccess={(page) => console.log('Loaded:', page.component)}
>
  Users
</Link>
```

### onError

Runs when the request fails:

```tsx
<Link
  href="/admin"
  onError={(errors) => console.error('Access denied')}
>
  Admin
</Link>
```

### onFinish

Runs when the request completes (success or error):

```tsx
<Link
  href="/users"
  onFinish={() => setLoading(false)}
>
  Users
</Link>
```

---

## Headers

Send custom headers with the request:

```tsx
<Link
  href="/api/action"
  headers={{ 'X-Custom-Header': 'value' }}
>
  Action
</Link>
```

---

## Partial Reloads with Link

### only

Only reload specific props:

```tsx
<Link href="/users" only={['users']}>
  Refresh Users
</Link>
```

### except

Reload all props except specified:

```tsx
<Link href="/dashboard" except={['notifications']}>
  Refresh Dashboard
</Link>
```

---

## Active Link Styling

Highlight the current page:

```tsx
import { Link, usePage } from '@inertiajs/react';

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  const { url } = usePage();
  const isActive = url.startsWith(href);

  return (
    <Link
      href={href}
      className={isActive ? 'text-blue-600 font-bold' : 'text-gray-600'}
    >
      {children}
    </Link>
  );
}

// Usage
<NavLink href="/dashboard">Dashboard</NavLink>
<NavLink href="/users">Users</NavLink>
```

---

## External Links

For external URLs, use regular `<a>` tags:

```tsx
// Internal - use Link
<Link href="/users">Users</Link>

// External - use <a>
<a href="https://example.com" target="_blank" rel="noopener noreferrer">
  External Site
</a>
```

For external redirects from server:

```php
return Inertia::location('https://example.com');
```

---

## BudTags Examples

### Navigation Menu

```tsx
import { Link, usePage } from '@inertiajs/react';
import { PageProps } from '@/Types/types';

function MainNav() {
  const { url } = usePage();
  const { permissions } = usePage<PageProps>().props;

  const links = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/packages', label: 'Packages' },
    { href: '/plants', label: 'Plants' },
    { href: '/harvests', label: 'Harvests' },
  ];

  return (
    <nav className="flex gap-4">
      {links.map(link => (
        <Link
          key={link.href}
          href={link.href}
          className={url.startsWith(link.href)
            ? 'text-orange-600 font-semibold'
            : 'text-gray-600 hover:text-gray-900'
          }
        >
          {link.label}
        </Link>
      ))}

      {permissions.includes('admin') && (
        <Link href="/admin">Admin</Link>
      )}
    </nav>
  );
}
```

### Delete with Confirmation

```tsx
<Link
  href={`/packages/${pkg.id}`}
  method="delete"
  as="button"
  className="text-red-600 hover:text-red-800"
  onBefore={() => confirm(`Delete package ${pkg.Label}?`)}
  preserveScroll
>
  Delete
</Link>
```

---

## Next Steps

- **Manual Visits** → Read `06-manual-visits.md`
- **Forms** → Read `07-forms-useform.md`
- **Scroll Management** → Read `12-scroll-management.md`
