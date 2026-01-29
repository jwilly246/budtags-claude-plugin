# Pattern 20: Remembering State

## Overview

Inertia can persist form data and component state in browser history, allowing users to return to previous states via back/forward navigation.

---

## Form Remember

### Basic Remember

Pass a key to `useForm` to remember form data:

```tsx
// Key identifies this form in history
const form = useForm('CreateUserForm', {
  name: '',
  email: '',
  role: 'user',
});

// Form data persists when:
// - Navigating away and back
// - Using browser back/forward
```

### Without Remember

```tsx
// No key = no remembering
const form = useForm({
  name: '',
  email: '',
});
```

---

## How It Works

1. Form data saved to browser's History API state
2. When navigating back, Inertia restores the state
3. useForm initializes with remembered values

---

## preserveState

Keep React component state during navigation:

### With Link

```tsx
<Link href="/users?page=2" preserveState>
  Next Page
</Link>
```

### With Router

```tsx
router.get('/users', filters, {
  preserveState: true,
});
```

### Conditional Preserve

```tsx
router.visit(url, {
  preserveState: (page) => {
    // Only preserve if same component
    return page.component === currentComponent;
  },
});
```

---

## Combined: preserveState + preserveScroll

```tsx
// Keep both React state AND scroll position
router.get('/users', { page: 2 }, {
  preserveState: true,
  preserveScroll: true,
});

// Common for pagination, filtering, sorting
```

---

## Replace vs Push

### Push (Default)

Adds new history entry:

```tsx
router.get('/users?page=2');
// Back button returns to page 1
```

### Replace

Replaces current entry:

```tsx
router.get('/users?page=2', {}, { replace: true });
// Back button skips to previous page (before pagination)
```

---

## Use Cases

### Search with History

```tsx
function SearchInput({ initialSearch }) {
  const [search, setSearch] = useState(initialSearch);

  const handleSearch = () => {
    router.get('/search', { q: search }, {
      preserveState: true,
      preserveScroll: true,
      // Don't replace - let users go back to previous searches
    });
  };
}
```

### Filters (Replace History)

```tsx
function Filters({ filters }) {
  const handleFilterChange = (newFilters) => {
    router.get('/users', newFilters, {
      preserveState: true,
      preserveScroll: true,
      replace: true,  // Don't bloat history with filter changes
    });
  };
}
```

### Tabs with State

```tsx
function TabbedContent() {
  const [activeTab, setActiveTab] = useState('details');

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    router.get(`/user?tab=${tab}`, {}, {
      preserveState: true,  // Keep local state
      preserveScroll: true, // Keep scroll
      replace: true,        // Don't add history entry
    });
  };
}
```

---

## Manual State Management

For complex state not in forms:

```tsx
function PackagesPage() {
  const { url } = usePage();
  const [selectedRows, setSelectedRows] = useState<string[]>([]);

  // Save to sessionStorage on change
  useEffect(() => {
    sessionStorage.setItem(`selection:${url}`, JSON.stringify(selectedRows));
  }, [selectedRows, url]);

  // Restore on mount
  useEffect(() => {
    const saved = sessionStorage.getItem(`selection:${url}`);
    if (saved) {
      setSelectedRows(JSON.parse(saved));
    }
  }, [url]);
}
```

---

## History-Based State

Access state from page object:

```tsx
import { usePage } from '@inertiajs/react';

function Component() {
  const { rememberedState } = usePage();
  // Access any state stored in history
}
```

---

## Clear History State

```tsx
router.visit('/users', {
  preserveState: false,  // Don't preserve
});

// Or manually clear
window.history.replaceState({}, '', window.location.href);
```

---

## BudTags Patterns

### Filter + Pagination State

```tsx
function PackagesPage({ packages, filters }) {
  const handlePageChange = (page: number) => {
    router.get('/packages', { ...filters, page }, {
      preserveState: true,
      preserveScroll: true,
      only: ['packages'],
    });
  };

  const handleFilterChange = (newFilters) => {
    router.get('/packages', { ...newFilters, page: 1 }, {
      preserveState: true,
      replace: true,  // Don't add filter changes to history
    });
  };
}
```

### Modal State Preservation

```tsx
function PackagesWithModal({ packages }) {
  const [editingPkg, setEditingPkg] = useState<Package | null>(null);

  // Inline edit doesn't navigate, state preserved naturally
  const handleSave = () => {
    router.patch(`/packages/${editingPkg.id}`, data, {
      preserveState: true,  // Keep modal state
      preserveScroll: true,
      onSuccess: () => setEditingPkg(null),
    });
  };
}
```

---

## Tips

1. **Use remember key** for forms you want to persist
2. **Use preserveState** for filter/pagination UI
3. **Use replace: true** for frequent changes (filters, sort)
4. **Let history push** for meaningful navigations (search queries)
5. **Combine with preserveScroll** for smooth UX

---

## Next Steps

- **Events & Lifecycle** → Read `21-events-lifecycle.md`
- **Scroll Management** → Read `12-scroll-management.md`
