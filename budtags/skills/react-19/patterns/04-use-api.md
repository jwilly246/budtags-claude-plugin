# React 19 use() API

The `use()` API lets you read resources like Promises and Context during render.

## Overview

```typescript
import { use } from 'react';

// Read a promise (suspends until resolved)
const data = use(promise);

// Read context (can be conditional!)
const theme = use(ThemeContext);
```

## Reading Promises

### Basic Usage

```typescript
import { use, Suspense } from 'react';

function Comments({ commentsPromise }) {
  // Suspends until promise resolves
  const comments = use(commentsPromise);

  return (
    <ul>
      {comments.map(comment => (
        <li key={comment.id}>{comment.text}</li>
      ))}
    </ul>
  );
}

function Page() {
  // Promise created in parent, passed to child
  const commentsPromise = fetchComments();

  return (
    <Suspense fallback={<div>Loading comments...</div>}>
      <Comments commentsPromise={commentsPromise} />
    </Suspense>
  );
}
```

### Important: Promise Creation Location

```typescript
// ✅ Promise created OUTSIDE render (in parent, event handler, etc.)
function Parent() {
  const dataPromise = fetchData(); // Created here
  return <Child dataPromise={dataPromise} />;
}

function Child({ dataPromise }) {
  const data = use(dataPromise); // OK - promise from props
  return <div>{data}</div>;
}

// ❌ Promise created DURING render - NOT supported
function Bad() {
  const dataPromise = fetchData(); // Created in render!
  const data = use(dataPromise); // This won't work correctly
  return <div>{data}</div>;
}
```

---

## Reading Context Conditionally

Unlike `useContext`, `use()` can be called after conditionals and early returns:

```typescript
function Heading({ children }) {
  // Can return early BEFORE reading context
  if (children == null) {
    return null;
  }

  // use() works after early return!
  const theme = use(ThemeContext);

  return (
    <h1 style={{ color: theme.color }}>
      {children}
    </h1>
  );
}
```

### Comparison

```typescript
// ❌ useContext - must be at top level
function BadComponent({ show }) {
  if (!show) return null;
  const theme = useContext(ThemeContext); // ERROR: Called conditionally
  return <div>{theme.name}</div>;
}

// ✅ use() - can be conditional
function GoodComponent({ show }) {
  if (!show) return null;
  const theme = use(ThemeContext); // OK!
  return <div>{theme.name}</div>;
}
```

---

## BudTags Examples

### With React Query (Complementary Use)

```typescript
// React Query is still preferred for most data fetching
// But use() can be helpful in specific scenarios

function PackageDetails({ packagePromise }) {
  // If you already have a promise from somewhere
  const pkg = use(packagePromise);

  return (
    <div>
      <h2>{pkg.Label}</h2>
      <p>Quantity: {pkg.Quantity}</p>
    </div>
  );
}

// vs React Query (usually preferred)
function PackageDetailsWithQuery({ packageId }) {
  const { data: pkg, isLoading } = useQuery({
    queryKey: ['package', packageId],
    queryFn: () => fetchPackage(packageId),
  });

  if (isLoading) return <Spinner />;

  return (
    <div>
      <h2>{pkg.Label}</h2>
      <p>Quantity: {pkg.Quantity}</p>
    </div>
  );
}
```

### When to Use use() vs React Query

| Scenario | Recommendation |
|----------|----------------|
| Data fetching with caching | React Query |
| Mutations with invalidation | React Query |
| One-time data load | use() can work |
| Promise from parent prop | use() |
| Conditional context access | use() |
| Background refetching | React Query |

### Conditional Context in Modals

```typescript
function OptionalThemeComponent({ useTheme }) {
  // Only read theme context if needed
  if (!useTheme) {
    return <div className="default-style">Content</div>;
  }

  const theme = use(ThemeContext);

  return (
    <div style={{ background: theme.background }}>
      Content
    </div>
  );
}
```

---

## Error Handling

### With Error Boundaries

```typescript
function DataDisplay({ dataPromise }) {
  // If promise rejects, Error Boundary catches it
  const data = use(dataPromise);
  return <div>{data.message}</div>;
}

function Page() {
  return (
    <ErrorBoundary fallback={<div>Failed to load</div>}>
      <Suspense fallback={<div>Loading...</div>}>
        <DataDisplay dataPromise={fetchData()} />
      </Suspense>
    </ErrorBoundary>
  );
}
```

### Manual Error Handling

If you need more control, handle errors before passing the promise:

```typescript
function Parent() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData()
      .then(setData)
      .catch(setError);
  }, []);

  if (error) return <ErrorMessage error={error} />;
  if (!data) return <Loading />;

  return <Child data={data} />;
}
```

---

## Patterns

### Server Data Loading

```typescript
// In a framework like Next.js
async function Page() {
  const dataPromise = fetchFromServer();

  return (
    <Suspense fallback={<Skeleton />}>
      <DataConsumer dataPromise={dataPromise} />
    </Suspense>
  );
}

function DataConsumer({ dataPromise }) {
  const data = use(dataPromise);
  return <DataView data={data} />;
}
```

### Multiple Promises

```typescript
function Dashboard({ userPromise, statsPromise }) {
  const user = use(userPromise);
  const stats = use(statsPromise);

  return (
    <div>
      <h1>Welcome, {user.name}</h1>
      <StatsDisplay stats={stats} />
    </div>
  );
}

function Page() {
  return (
    <Suspense fallback={<DashboardSkeleton />}>
      <Dashboard
        userPromise={fetchUser()}
        statsPromise={fetchStats()}
      />
    </Suspense>
  );
}
```

---

## Limitations

1. **No render-created promises:** Promise must come from outside the render function
2. **Requires Suspense:** Must be wrapped in a Suspense boundary
3. **No caching:** Unlike React Query, doesn't cache results
4. **No background updates:** Doesn't refetch or sync

## When to Use

| Use Case | use() | React Query |
|----------|-------|-------------|
| Simple promise consumption | ✅ | ✅ |
| Conditional context | ✅ | N/A |
| Caching needed | ❌ | ✅ |
| Background sync | ❌ | ✅ |
| Mutations | ❌ | ✅ |
| SSR data | ✅ | ✅ |

## Next Steps

- Read `02-new-hooks.md` for other new hooks
- Read `10-suspense-hydration.md` for Suspense patterns
