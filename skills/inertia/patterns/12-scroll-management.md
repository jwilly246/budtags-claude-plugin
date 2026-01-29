# Pattern 12: Scroll Management

## Default Behavior

By default, Inertia scrolls to the top of the page on every navigation.

---

## preserveScroll

Maintain scroll position during navigation:

### With Link

```tsx
<Link href="/users?page=2" preserveScroll>
  Next Page
</Link>
```

### With router

```tsx
router.get('/users', { page: 2 }, {
  preserveScroll: true,
});

router.reload({
  preserveScroll: true,
});
```

### With useForm

```tsx
post('/users', {
  preserveScroll: true,
  onSuccess: () => toast.success('Created!'),
});
```

---

## Conditional Scroll Preservation

Preserve scroll only on certain conditions:

```tsx
router.get('/users', filters, {
  preserveScroll: (page) => {
    // Only preserve if staying on same component
    return page.component === 'Users/Index';
  },
});
```

---

## Scroll Regions

Define scrollable regions that maintain independent scroll positions:

### Setup in Layout

```tsx
export default function MainLayout({ children }) {
  return (
    <div className="flex h-screen">
      {/* Sidebar with independent scroll */}
      <aside
        scroll-region="sidebar"
        className="w-64 overflow-y-auto"
      >
        <Navigation />
      </aside>

      {/* Main content with independent scroll */}
      <main
        scroll-region="main"
        className="flex-1 overflow-y-auto"
      >
        {children}
      </main>
    </div>
  );
}
```

### How It Works

Each `scroll-region` attribute creates a region whose scroll position is:
- Saved when navigating away
- Restored when navigating back (via browser back/forward)

---

## Reset Scroll on Navigation

Force scroll to top even with preserveScroll:

```tsx
router.get('/users/1', {}, {
  preserveScroll: false, // Default behavior - scroll to top
});
```

---

## Scroll to Element

Scroll to a specific element after navigation:

```tsx
router.get('/users#user-form', {}, {
  onSuccess: () => {
    document.getElementById('user-form')?.scrollIntoView({
      behavior: 'smooth',
    });
  },
});
```

### With Hash in URL

```tsx
<Link href="/users#create-section">
  Create User
</Link>

// Inertia will scroll to #create-section after navigation
```

---

## Common Patterns

### Pagination Without Scroll Jump

```tsx
function handlePageChange(page: number) {
  router.get('/users', { page }, {
    preserveScroll: true,
    preserveState: true,
  });
}
```

### Form Submission Keep Position

```tsx
post('/users', {
  preserveScroll: true,
  onSuccess: () => {
    reset();
    toast.success('User created');
  },
});
```

### Filter Changes

```tsx
function handleFilterChange(filters: Filters) {
  router.get('/users', filters, {
    preserveScroll: true,
    preserveState: true,
    replace: true, // Don't add to history
  });
}
```

### Modal Actions

```tsx
function handleDelete(userId: number) {
  router.delete(`/users/${userId}`, {
    preserveScroll: true,
    onSuccess: () => {
      closeModal();
      toast.success('Deleted');
    },
  });
}
```

---

## BudTags Examples

### Data Table Actions

```tsx
function PackagesTable({ packages }) {
  const handleStatusChange = (pkgId: number, status: string) => {
    router.patch(`/packages/${pkgId}`, { status }, {
      preserveScroll: true, // Stay at current scroll position
      preserveState: true,  // Keep table state (sorting, selection)
      only: ['packages'],   // Only reload packages prop
    });
  };

  return (
    <table>
      {packages.map(pkg => (
        <tr key={pkg.id}>
          <td>{pkg.label}</td>
          <td>
            <select
              value={pkg.status}
              onChange={e => handleStatusChange(pkg.id, e.target.value)}
            >
              <option value="active">Active</option>
              <option value="finished">Finished</option>
            </select>
          </td>
        </tr>
      ))}
    </table>
  );
}
```

### Infinite Scroll Alternative

For lists where you want to preserve position across navigation:

```tsx
function PackagesList() {
  const { url } = usePage();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Restore scroll on mount
  useEffect(() => {
    const savedPosition = sessionStorage.getItem(`scroll:${url}`);
    if (savedPosition && scrollRef.current) {
      scrollRef.current.scrollTop = parseInt(savedPosition);
    }
  }, []);

  // Save scroll on navigation
  useEffect(() => {
    return router.on('before', () => {
      if (scrollRef.current) {
        sessionStorage.setItem(`scroll:${url}`, String(scrollRef.current.scrollTop));
      }
    });
  }, [url]);

  return (
    <div ref={scrollRef} className="overflow-y-auto h-[600px]">
      {/* List items */}
    </div>
  );
}
```

---

## Tips

1. **Always use preserveScroll for**:
   - Pagination
   - Filter changes
   - Inline edits
   - Modal actions
   - Form submissions

2. **Let scroll reset for**:
   - Navigation to different pages
   - Major context changes
   - Search result pages (new query)

3. **Combine with preserveState** to maintain both scroll and React state

---

## Next Steps

- **Remembering State** → Read `20-remembering-state.md`
- **Partial Reloads** → Read `10-partial-reloads.md`
- **Events** → Read `21-events-lifecycle.md`
