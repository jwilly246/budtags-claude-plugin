# Pattern 22: Render Optimizations

## Structural Sharing

TanStack Query automatically optimizes referential equality:

```typescript
const query1 = useQuery({ queryKey: ['packages'], queryFn: fetchPackages })
const query2 = useQuery({ queryKey: ['packages'], queryFn: fetchPackages })

// If data hasn't changed:
query1.data === query2.data // ✅ true (same reference)
```

This prevents unnecessary re-renders when data is structurally the same.

## Tracked Properties (Proxies)

Only re-render when accessed properties change:

```typescript
// Component only re-renders when data or error changes
function Component() {
  const { data, error } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  // isFetching changes don't cause re-render
  return <DataTable data={data} error={error} />
}
```

## notifyOnChangeProps

Control which property changes trigger re-renders:

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  notifyOnChangeProps: ['data'], // Only re-render when data changes
})
```

### Track All Properties

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  notifyOnChangeProps: 'all', // Re-render on any property change
})
```

## select for Subset Subscriptions

Transform data and only re-render when selected subset changes:

```typescript
// Only re-render when package count changes, not when packages themselves change
const { data: count } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  select: (packages) => packages.length,
})
```

### More Examples

```typescript
// Only re-render when labels change
const { data: labels } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  select: (packages) => packages.map(p => p.Label),
})

// Only re-render when active packages change
const { data: activePackages } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  select: (packages) => packages.filter(p => !p.FinishedDate),
})
```

## Memoization Best Practices

### Memoize Query Options

```typescript
// ❌ BAD - New object every render
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})

// ✅ GOOD - Memoized options
const queryOptions = useMemo(
  () => ({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  }),
  []
)

useQuery(queryOptions)
```

### Memoize Query Key

```typescript
// ❌ BAD - New array every render
useQuery({
  queryKey: ['packages', { status, location }],
  queryFn: fetchPackages,
})

// ✅ GOOD - Memoized key
const queryKey = useMemo(
  () => ['packages', { status, location }],
  [status, location]
)

useQuery({
  queryKey,
  queryFn: fetchPackages,
})
```

### Memoize Query Function

```typescript
// ❌ BAD - New function every render
useQuery({
  queryKey: ['package', id],
  queryFn: () => fetchPackage(id),
})

// ✅ GOOD - Memoized function
const queryFn = useCallback(
  () => fetchPackage(id),
  [id]
)

useQuery({
  queryKey: ['package', id],
  queryFn,
})
```

## Object Rest Destructuring Warning

```typescript
// ❌ BAD - Breaks tracked properties
const query = useQuery({ queryKey: ['packages'], queryFn: fetchPackages })
const { ...rest } = query
// All properties accessed, will re-render on any change

// ✅ GOOD - Destructure only what you need
const { data, error } = useQuery({ queryKey: ['packages'], queryFn: fetchPackages })
```

## BudTags Examples

### Optimized Package List

```typescript
function PackagesList() {
  const { user } = usePage<PageProps>().props
  const license = usePage<PageProps>().props.session.license

  // Memoize query options
  const queryOptions = useMemo(
    () => ({
      queryKey: ['metrc', 'packages', license],
      queryFn: async () => {
        const api = new MetrcApi()
        api.set_user(user)
        return api.packages(license)
      },
      staleTime: 5 * 60 * 1000,
    }),
    [license, user]
  )

  // Only destructure what we need
  const { data: packages } = useQuery(queryOptions)

  return <DataTable data={packages} />
}
```

### Select Optimization

```typescript
function PackageCount() {
  // Only re-renders when count changes, not when packages change
  const { data: count } = useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: fetchPackages,
    select: (packages) => packages.length,
  })

  return <div>Total: {count}</div>
}
```

### Memoized Filter

```typescript
function ActivePackages() {
  const [showActive, setShowActive] = useState(true)

  const { data: packages } = useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: fetchPackages,
    // Only re-render when filtered result changes
    select: useCallback(
      (packages: Package[]) => {
        return packages.filter(pkg =>
          showActive ? !pkg.FinishedDate : !!pkg.FinishedDate
        )
      },
      [showActive]
    ),
  })

  return <DataTable data={packages} />
}
```

### Tracked Properties Example

```typescript
function PackageStatus() {
  // Only accesses isPending and error
  // Won't re-render when isFetching or data changes
  const { isPending, error } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  if (isPending) return <Spinner />
  if (error) return <Error error={error} />

  return <div>Ready</div>
}
```

## ESLint Rule for Optimization

Install and configure the ESLint plugin:

```bash
npm install @tanstack/eslint-plugin-query --save-dev
```

```json
{
  "extends": ["plugin:@tanstack/eslint-plugin-query/recommended"]
}
```

Catches common mistakes like:
- Missing memoization
- Inefficient destructuring
- Stale dependencies

## React.memo for Query Components

```typescript
const PackageCard = memo(({ pkg }: { pkg: Package }) => {
  return (
    <div>
      <h3>{pkg.Label}</h3>
      <p>{pkg.ProductName}</p>
    </div>
  )
})

function PackagesList() {
  const { data: packages } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  return (
    <div>
      {packages?.map(pkg => (
        <PackageCard key={pkg.Id} pkg={pkg} />
      ))}
    </div>
  )
}
```

## Avoid Inline Objects in Dependencies

```typescript
// ❌ BAD - New object every render
useQuery({
  queryKey: ['packages', { status: 'active' }],
  queryFn: fetchPackages,
})

// ✅ GOOD - Separate variables
const status = 'active'
useQuery({
  queryKey: ['packages', status],
  queryFn: fetchPackages,
})

// ✅ ALSO GOOD - Memoized object
const filters = useMemo(() => ({ status: 'active' }), [])
useQuery({
  queryKey: ['packages', filters],
  queryFn: fetchPackages,
})
```

## Performance Checklist

- ✅ Use `select` to subscribe to subset of data
- ✅ Destructure only needed properties from useQuery
- ✅ Memoize query keys with variables
- ✅ Memoize query functions with closures
- ✅ Use `notifyOnChangeProps` for fine-grained control
- ✅ Leverage structural sharing (automatic)
- ✅ Use React.memo for expensive components
- ✅ Install ESLint plugin

## Profiling

Use React DevTools Profiler to identify:
- Components re-rendering unnecessarily
- Expensive renders
- Query performance issues

## Next Steps
- **Core Concepts** → Read `02-core-concepts.md`
- **Query Options** → Read `11-query-options.md`
- **Testing** → Read `26-testing.md`
