# Pattern 2: Core Concepts

## Server State vs Client State

### Client State
- Persisted in your app's memory
- Synchronously updated
- Always up-to-date
- Examples: form inputs, UI toggles, modals

### Server State
- Persisted remotely (API, database)
- Asynchronously updated
- Can become stale/outdated
- Examples: user data, package lists, Metrc data

**TanStack Query specializes in server state management.**

## The Problem TanStack Query Solves

Without TanStack Query, managing server state requires:
```typescript
// ❌ Manual implementation
const [data, setData] = useState(null)
const [isLoading, setIsLoading] = useState(false)
const [error, setError] = useState(null)

useEffect(() => {
  setIsLoading(true)
  fetch('/api/packages')
    .then(res => res.json())
    .then(data => {
      setData(data)
      setIsLoading(false)
    })
    .catch(err => {
      setError(err)
      setIsLoading(false)
    })
}, [])

// Problems:
// - No caching
// - No deduplication
// - No background updates
// - No optimistic updates
// - Boilerplate code
```

With TanStack Query:
```typescript
// ✅ Automatic caching, deduplication, background updates
const { data, isLoading, error } = useQuery({
  queryKey: ['packages'],
  queryFn: () => fetch('/api/packages').then(r => r.json()),
})
```

## Query Keys as Cache Identifiers

Query keys uniquely identify queries:

```typescript
// String key
useQuery({ queryKey: ['todos'], queryFn: fetchTodos })

// Array key
useQuery({ queryKey: ['todos', 5], queryFn: () => fetchTodo(5) })

// Array with object
useQuery({
  queryKey: ['todos', { status: 'active', page: 1 }],
  queryFn: fetchActiveTodos,
})
```

**Key Rule:** Same key = same cache entry

```typescript
// These share the same cache
useQuery({ queryKey: ['todos'], queryFn: fetchTodos }) // Component A
useQuery({ queryKey: ['todos'], queryFn: fetchTodos }) // Component B
// ✅ Only 1 network request!
```

## Query Lifecycle

### States

```typescript
const query = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})

// Status: Current state of the data
query.status // 'pending' | 'error' | 'success'

// Fetch Status: State of the query function
query.fetchStatus // 'fetching' | 'paused' | 'idle'
```

### Status Transitions

```
Initial State
    ↓
[pending, fetching] ← Query starts
    ↓
[success, idle]     ← Data received
    ↓
[success, fetching] ← Background refetch
    ↓
[success, idle]     ← Refetch complete
```

### Boolean Flags

```typescript
const {
  isPending,   // status === 'pending'
  isError,     // status === 'error'
  isSuccess,   // status === 'success'

  isFetching,  // fetchStatus === 'fetching'
  isPaused,    // fetchStatus === 'paused'
  isIdle,      // fetchStatus === 'idle'
} = useQuery(...)
```

## Stale-While-Revalidate Pattern

```typescript
const query = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  staleTime: 5 * 60 * 1000, // 5 minutes
})

// Timeline:
// 0s    → Query executes, data is fresh
// 5min  → Data becomes stale (but still shown)
// 5min+ → Next mount/focus triggers background refetch
// 5min+ → Old data shown while new data fetches
// 6min  → New data replaces old data
```

Benefits:
- ✅ Instant UI (old data shown immediately)
- ✅ Background updates (fresh data fetched)
- ✅ No loading spinners for cached data

## Automatic Refetching

TanStack Query automatically refetches stale data when:

1. **New component instance mounts**
2. **Window refocuses**
3. **Network reconnects**
4. **Configured refetch interval expires**

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  staleTime: 5 * 60 * 1000,

  // Control refetch behavior
  refetchOnMount: true,        // Refetch on mount if stale (default: true)
  refetchOnWindowFocus: false, // Refetch on window focus (default: true)
  refetchOnReconnect: true,    // Refetch on reconnect (default: true)
  refetchInterval: 30000,      // Poll every 30 seconds (default: false)
})
```

## Queries vs Mutations

### Queries (Read Operations)
```typescript
// GET requests - fetching data
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})
```

Characteristics:
- Declarative (runs automatically)
- Cached
- Deduplicated
- Background refetching
- Use for GET operations

### Mutations (Write Operations)
```typescript
// POST/PUT/DELETE - changing data
useMutation({
  mutationFn: createPackage,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['packages'] })
  },
})
```

Characteristics:
- Imperative (triggered manually)
- Not cached
- Not deduplicated
- Use for POST/PUT/DELETE operations

## Cache Behavior

### Garbage Collection

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  gcTime: 5 * 60 * 1000, // 5 minutes (default)
})

// Timeline:
// 0s   → Query active, data in cache
// 10s  → Component unmounts, query becomes inactive
// 5min → Garbage collector removes inactive data
```

### Structural Sharing

TanStack Query preserves referential equality when data doesn't change:

```typescript
const query1 = useQuery({ queryKey: ['todos'], queryFn: fetchTodos })
const query2 = useQuery({ queryKey: ['todos'], queryFn: fetchTodos })

// If data hasn't changed:
query1.data === query2.data // ✅ true (same reference)
```

Benefits:
- Prevents unnecessary re-renders
- Optimizes React performance

## BudTags Example: Metrc Packages

```typescript
function PackagesTable() {
  const { user } = usePage<PageProps>().props
  const license = usePage<PageProps>().props.session.license

  // Query packages from Metrc
  const {
    data: packages,
    isLoading,
    error,
    isFetching,
  } = useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages(license)
    },
    staleTime: 5 * 60 * 1000, // Metrc data stale after 5 minutes
    gcTime: 10 * 60 * 1000,   // Keep in cache for 10 minutes
    retry: 1,                 // Metrc API is rate-limited
  })

  if (isLoading) return <Spinner />
  if (error) return <ErrorMessage error={error} />

  return (
    <div>
      {isFetching && <RefreshIndicator />}
      <DataTable data={packages} />
    </div>
  )
}
```

## Next Steps
- **Important Defaults** → Read `03-important-defaults.md`
- **Query Keys** → Read `04-query-keys.md`
- **Basic Queries** → Read `07-basic-queries.md`
