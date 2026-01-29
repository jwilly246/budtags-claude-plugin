# React 19 Suspense & Hydration Improvements

Improvements to Suspense, useDeferredValue, hydration, and third-party compatibility.

## useDeferredValue Initial Value

New in React 19: `useDeferredValue` accepts an optional initial value.

### Before (React 18)

```typescript
function Search({ query }) {
  // No initial value - renders with query immediately
  const deferredQuery = useDeferredValue(query);

  return <SearchResults query={deferredQuery} />;
}
```

### After (React 19)

```typescript
function Search({ query }) {
  // Initial render uses '' (empty string)
  // Then re-renders with actual query in background
  const deferredQuery = useDeferredValue(query, '');

  return <SearchResults query={deferredQuery} />;
}
```

### Use Case: Faster Initial Render

```typescript
function FilteredList({ items, filter }) {
  // First render: show all items (filter = '')
  // Background: apply actual filter
  const deferredFilter = useDeferredValue(filter, '');

  const filteredItems = useMemo(() => {
    if (!deferredFilter) return items;
    return items.filter(item =>
      item.name.toLowerCase().includes(deferredFilter.toLowerCase())
    );
  }, [items, deferredFilter]);

  return (
    <ul>
      {filteredItems.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}
```

### BudTags Example: Package Search

```typescript
function PackageSearch({ packages }) {
  const [search, setSearch] = useState('');

  // Initial render shows all packages
  // Filtering happens in background as user types
  const deferredSearch = useDeferredValue(search, '');

  const isStale = search !== deferredSearch;

  const filteredPackages = useMemo(() => {
    if (!deferredSearch) return packages;
    return packages.filter(pkg =>
      pkg.Label.toLowerCase().includes(deferredSearch.toLowerCase())
    );
  }, [packages, deferredSearch]);

  return (
    <div>
      <input
        value={search}
        onChange={e => setSearch(e.target.value)}
        placeholder="Search packages..."
      />

      <div style={{ opacity: isStale ? 0.7 : 1 }}>
        <PackageTable packages={filteredPackages} />
      </div>
    </div>
  );
}
```

---

## Suspense Boundary Batching (React 19.2)

React 19.2 batches Suspense boundary reveals during SSR for a smoother experience.

### Before (Could be jarring)
- Boundaries revealed one at a time as data loaded
- Content could pop in incrementally

### After (Smoother)
- Multiple boundaries revealed together when possible
- Better matches client-side rendering behavior
- React uses heuristics to avoid impacting Core Web Vitals

```typescript
// These might now reveal together if they load around the same time
<Suspense fallback={<Skeleton />}>
  <Header />  {/* Might wait for Sidebar */}
</Suspense>

<Suspense fallback={<Skeleton />}>
  <Sidebar />  {/* Might reveal with Header */}
</Suspense>
```

---

## Third-Party Script Compatibility

React 19 handles third-party modifications (browser extensions, injected scripts) more gracefully.

### What Changed

- Unexpected tags in `<head>` and `<body>` are skipped during hydration
- No more hydration errors from browser extensions
- Injected stylesheets are preserved on re-render

### Before (React 18)

```
Warning: Expected server HTML to contain a matching <div> in <body>
// Caused by browser extension injecting elements
```

### After (React 19)

No error - React skips unexpected elements and hydrates correctly.

### What This Means for BudTags

- Users with ad blockers, password managers, etc. won't see hydration errors
- Browser DevTools extensions work better
- More resilient production experience

---

## Custom Elements Support

React 19 fully supports Web Components (Custom Elements).

### Server-Side Rendering

```typescript
// Renders correctly on server
<my-custom-element attr="value" />
```

### Client-Side Property Handling

```typescript
// React 19 correctly distinguishes:
// - Primitive values → attributes
// - Objects/functions → properties

<my-datepicker
  value="2024-01-01"           // Attribute (string)
  onchange={handleChange}      // Property (function)
  config={{ theme: 'dark' }}   // Property (object)
/>
```

### BudTags Example: Third-Party Components

```typescript
// If using a web component for label preview
function LabelPreview({ zpl }) {
  return (
    <zebra-label-viewer
      zpl-content={zpl}
      dpmm={8}
      width={4}
      height={6}
      onrender={handleRender}
    />
  );
}
```

---

## Hydration Best Practices

### 1. Avoid Dynamic Content Mismatches

```typescript
// ❌ Causes hydration mismatch
function BadComponent() {
  return <div>{Date.now()}</div>;
}

// ✅ Use useEffect for client-only content
function GoodComponent() {
  const [time, setTime] = useState<number | null>(null);

  useEffect(() => {
    setTime(Date.now());
  }, []);

  return <div>{time ?? 'Loading...'}</div>;
}
```

### 2. Use Suspense for Async Data

```typescript
// ✅ Suspense handles the loading state consistently
function DataComponent({ dataPromise }) {
  const data = use(dataPromise);
  return <div>{data.value}</div>;
}

function Page() {
  return (
    <Suspense fallback={<Skeleton />}>
      <DataComponent dataPromise={fetchData()} />
    </Suspense>
  );
}
```

### 3. Handle Browser-Only APIs

```typescript
// ✅ Check for browser environment
function WindowSize() {
  const [size, setSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const updateSize = () => {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  return <div>{size.width} x {size.height}</div>;
}
```

---

## BudTags Context: Inertia SSR

If using Inertia SSR:

```typescript
// Inertia handles SSR, but React 19 improvements help:
// - Better hydration error messages if mismatches occur
// - Third-party scripts don't cause issues
// - useDeferredValue for expensive filtering
```

### With React Query Suspense Mode

```typescript
function PackagesPage() {
  return (
    <Suspense fallback={<PackagesSkeleton />}>
      <PackagesContent />
    </Suspense>
  );
}

function PackagesContent() {
  const { data: packages } = useSuspenseQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  });

  const [filter, setFilter] = useState('');
  const deferredFilter = useDeferredValue(filter, '');

  const filtered = useMemo(() =>
    packages.filter(p => p.Label.includes(deferredFilter)),
    [packages, deferredFilter]
  );

  return (
    <div>
      <input value={filter} onChange={e => setFilter(e.target.value)} />
      <PackageTable packages={filtered} />
    </div>
  );
}
```

---

## Summary

| Feature | Benefit |
|---------|---------|
| `useDeferredValue` initial | Faster first render |
| Suspense batching | Smoother SSR reveals |
| Third-party tolerance | No extension errors |
| Custom Elements | Web Component support |

## Next Steps

- Read `04-use-api.md` for `use()` with Suspense
- Read `09-error-handling.md` for hydration error handling
- Read `11-activity-component.md` for UI state management
