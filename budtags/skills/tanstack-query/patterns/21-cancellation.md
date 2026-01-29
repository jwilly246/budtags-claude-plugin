# Pattern 21: Query Cancellation

## Automatic Cancellation

TanStack Query automatically cancels queries in these scenarios:

1. **Component unmounts** before query completes
2. **Query key changes** before previous query completes
3. **Manual cancelation** via `cancelQueries()`

## AbortSignal in Query Functions

Use the `signal` from context to support cancellation:

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: async ({ signal }) => {
    const response = await fetch('/api/packages', { signal })
    return response.json()
  },
})
```

## HTTP Client Integration

### With fetch

```typescript
queryFn: async ({ signal }) => {
  const response = await fetch('/api/packages', {
    signal, // ← Pass signal to fetch
  })

  if (!response.ok) throw new Error('Failed')
  return response.json()
}
```

### With Axios

```typescript
queryFn: async ({ signal }) => {
  const response = await axios.get('/api/packages', {
    signal, // ← Pass signal to axios
  })
  return response.data
}
```

### With XMLHttpRequest

```typescript
queryFn: ({ signal }) => {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    // Abort on signal
    signal?.addEventListener('abort', () => {
      xhr.abort()
      reject(new Error('Query was cancelled'))
    })

    xhr.open('GET', '/api/packages')
    xhr.onload = () => resolve(JSON.parse(xhr.responseText))
    xhr.onerror = () => reject(new Error('Network error'))
    xhr.send()
  })
}
```

## Manual Cancellation

### Cancel Specific Query

```typescript
const queryClient = useQueryClient()

// Cancel single query
await queryClient.cancelQueries({ queryKey: ['packages'] })
```

### Cancel Before Mutation

```typescript
const mutation = useMutation({
  mutationFn: updatePackage,
  onMutate: async (newPackage) => {
    // Cancel outgoing queries to prevent race conditions
    await queryClient.cancelQueries({ queryKey: ['packages'] })

    // Now safe to update cache
    queryClient.setQueryData(['packages'], newPackage)
  },
})
```

## Cancellation Options

### silent

Don't throw error when cancelled:

```typescript
await queryClient.cancelQueries({
  queryKey: ['packages'],
  silent: true, // Don't throw error
})
```

### revert

Revert query to previous state:

```typescript
await queryClient.cancelQueries({
  queryKey: ['packages'],
  revert: true, // Revert to previous data
})
```

## Long-Running Operations

Check signal periodically for long operations:

```typescript
queryFn: async ({ signal }) => {
  const items = []

  for (let i = 0; i < 1000; i++) {
    // Check if cancelled
    if (signal.aborted) {
      throw new Error('Operation cancelled')
    }

    // Process item
    items.push(await processItem(i))
  }

  return items
}
```

## BudTags Examples

### Metrc API with Cancellation

```typescript
function useMetrcPackages(license: string) {
  const { user } = usePage<PageProps>().props

  return useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: async ({ signal }) => {
      const api = new MetrcApi()
      api.set_user(user)

      // Pass signal to API call
      const packages = await api.packages(license, { signal })
      return packages
    },
  })
}

// If component unmounts or license changes, request is cancelled
```

### Search with Debounce + Cancellation

```typescript
function PackageSearch() {
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 300)

  const { data } = useQuery({
    queryKey: ['packages', 'search', debouncedSearch],
    queryFn: async ({ signal }) => {
      if (!debouncedSearch) return []

      // Cancelled automatically when search term changes
      const response = await fetch(
        `/api/packages/search?q=${debouncedSearch}`,
        { signal }
      )

      return response.json()
    },
    enabled: debouncedSearch.length > 0,
  })

  return (
    <div>
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search packages..."
      />
      <Results data={data} />
    </div>
  )
}
```

### Cancel Before Optimistic Update

```typescript
const updateMutation = useMutation({
  mutationFn: updatePackage,
  onMutate: async (newPackage) => {
    // Cancel to prevent race condition
    await queryClient.cancelQueries({
      queryKey: ['packages', newPackage.id],
    })

    const previousPackage = queryClient.getQueryData(['packages', newPackage.id])

    // Safe to update now
    queryClient.setQueryData(['packages', newPackage.id], newPackage)

    return { previousPackage }
  },
  onError: (err, newPackage, context) => {
    queryClient.setQueryData(['packages', newPackage.id], context.previousPackage)
  },
})
```

### Custom Cancellable Operation

```typescript
queryFn: async ({ signal }) => {
  const api = new MetrcApi()
  api.set_user(user)

  // Start fetch
  const packagesPromise = api.packages(license)

  // Create cancellation listener
  const cancelPromise = new Promise((_, reject) => {
    signal?.addEventListener('abort', () => {
      reject(new Error('Query cancelled'))
    })
  })

  // Race: fetch vs cancellation
  return await Promise.race([packagesPromise, cancelPromise])
}
```

## GraphQL Cancellation

### With Apollo Client

```typescript
import { useApolloClient } from '@apollo/client'

queryFn: async ({ signal }) => {
  const client = useApolloClient()

  const observable = client.watchQuery({
    query: PACKAGES_QUERY,
  })

  // Subscribe to abort
  signal?.addEventListener('abort', () => {
    observable.stopPolling()
  })

  const { data } = await observable.result()
  return data.packages
}
```

## Limitations with Suspense

Suspense mode doesn't support query cancellation:

```typescript
// ❌ Cancellation not supported
useQuery({
  queryKey: ['packages'],
  queryFn: ({ signal }) => fetchPackages({ signal }),
  suspense: true, // Cancellation disabled
})
```

## Race Condition Prevention

```typescript
// Without cancellation - race condition possible
const { data } = useQuery({
  queryKey: ['package', id],
  queryFn: () => fetchPackage(id),
})

// User clicks Package 1 → Request starts
// User clicks Package 2 → Request starts
// Request 2 completes → Shows Package 2
// Request 1 completes → Shows Package 1 (wrong!)

// With cancellation - race condition prevented
const { data } = useQuery({
  queryKey: ['package', id],
  queryFn: ({ signal }) => fetchPackage(id, { signal }),
})

// User clicks Package 1 → Request starts
// User clicks Package 2 → Request 1 cancelled, Request 2 starts
// Request 2 completes → Shows Package 2 (correct!)
```

## Best Practices

### ✅ DO

```typescript
// Pass signal to fetch/axios
queryFn: ({ signal }) => fetch('/api/data', { signal })

// Cancel before optimistic updates
onMutate: async () => {
  await queryClient.cancelQueries({ queryKey: ['data'] })
}

// Check signal in long operations
if (signal.aborted) throw new Error('Cancelled')
```

### ❌ DON'T

```typescript
// Ignore signal
queryFn: ({ signal }) => {
  // signal is ignored
  return fetch('/api/data')
}

// Don't catch cancellation errors unnecessarily
try {
  await query.refetch()
} catch (error) {
  // This will catch cancellation errors too
}
```

## Next Steps
- **Query Functions** → Read `10-query-functions.md`
- **Optimistic Updates** → Read `15-optimistic-updates.md`
- **Performance** → Read `22-render-optimizations.md`
