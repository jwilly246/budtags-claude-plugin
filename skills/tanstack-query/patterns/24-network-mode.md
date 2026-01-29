# Pattern 24: Network Mode

## Network Modes

Control how queries behave based on network connectivity:

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  networkMode: 'online', // 'online' | 'always' | 'offlineFirst'
})
```

## online (Default)

Only fetch when online:

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  networkMode: 'online', // Default
})

// Behavior:
// - Online: Fetch normally
// - Offline: Pause query, set fetchStatus: 'paused'
// - Reconnect: Resume and fetch
```

## always

Fetch regardless of network status:

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  networkMode: 'always',
})

// Behavior:
// - Always executes queryFn
// - Useful for reading from cache/localStorage
// - Ignores network status
```

### Use Case: Offline-First

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: async () => {
    // Try IndexedDB first
    const cached = await db.packages.toArray()
    if (cached.length > 0) return cached

    // Fallback to network (will throw if offline)
    return fetch('/api/packages').then(r => r.json())
  },
  networkMode: 'always',
})
```

## offlineFirst

Try fetch, use cache if fails:

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: async () => {
    // Try network first
    return fetch('/api/packages').then(r => r.json())
  },
  networkMode: 'offlineFirst',
})

// Behavior:
// - Try fetch
// - If fails (offline): Don't pause, mark as error
// - Service worker can intercept and return cached data
```

## fetchStatus Property

```typescript
const { fetchStatus } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})

// fetchStatus: 'fetching' | 'paused' | 'idle'
```

### State Combinations

```typescript
// Online, fetching
status: 'pending', fetchStatus: 'fetching'

// Offline, paused (networkMode: 'online')
status: 'pending', fetchStatus: 'paused'

// Offline, error (networkMode: 'offlineFirst')
status: 'error', fetchStatus: 'idle'
```

## Paused Queries Behavior

When networkMode is `'online'` and network is offline:

```typescript
const { fetchStatus } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  networkMode: 'online',
})

// Offline:
fetchStatus === 'paused'  // Query is paused

// invalidateQueries() called:
// - Query marked as stale
// - Will refetch when online

// Reconnect:
fetchStatus === 'fetching' // Automatically resumes
```

## BudTags Examples

### Standard Metrc Query (Online Only)

```typescript
function useMetrcPackages(license: string) {
  const { user } = usePage<PageProps>().props

  return useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages(license)
    },
    networkMode: 'online', // Default: only fetch when online
  })
}
```

### Offline-First with LocalStorage

```typescript
function usePackagesOfflineFirst() {
  const { user } = usePage<PageProps>().props
  const license = usePage<PageProps>().props.session.license

  return useQuery({
    queryKey: ['packages', license],
    queryFn: async () => {
      // Try network first
      try {
        const api = new MetrcApi()
        api.set_user(user)
        const packages = await api.packages(license)

        // Save to localStorage
        localStorage.setItem(
          `packages-${license}`,
          JSON.stringify(packages)
        )

        return packages
      } catch (error) {
        // Fallback to localStorage
        const cached = localStorage.getItem(`packages-${license}`)
        if (cached) {
          return JSON.parse(cached)
        }
        throw error
      }
    },
    networkMode: 'always', // Fetch even offline
  })
}
```

### Show Offline Indicator

```typescript
function OfflineIndicator() {
  const { fetchStatus } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
    networkMode: 'online',
  })

  if (fetchStatus === 'paused') {
    return (
      <div className="fixed bottom-4 right-4 bg-yellow-500 text-white px-4 py-2 rounded">
        You are offline. Data will sync when connection is restored.
      </div>
    )
  }

  return null
}
```

### Manual Network Detection

```typescript
import { onlineManager } from '@tanstack/react-query'

function NetworkStatus() {
  const [isOnline, setIsOnline] = useState(onlineManager.isOnline())

  useEffect(() => {
    return onlineManager.subscribe((online) => {
      setIsOnline(online)
    })
  }, [])

  return (
    <div className={`badge ${isOnline ? 'bg-green-500' : 'bg-red-500'}`}>
      {isOnline ? 'Online' : 'Offline'}
    </div>
  )
}
```

### Mock Offline for Testing

```typescript
// Temporarily set offline
onlineManager.setOnline(false)

// Re-enable
onlineManager.setOnline(true)

// In DevTools
onlineManager.setOnline(false) // Test offline behavior
```

## focusManager

Control refetch on window focus:

```typescript
import { focusManager } from '@tanstack/react-query'

// Disable focus refetching globally
focusManager.setFocused(false)

// Re-enable
focusManager.setFocused(true)

// Subscribe to focus events
focusManager.subscribe((isFocused) => {
  console.log('Window focused:', isFocused)
})
```

## Global Network Mode

Set default for all queries:

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      networkMode: 'offlineFirst', // Default for all queries
    },
  },
})
```

## Next Steps
- **Query Options** → Read `11-query-options.md`
- **Background Fetching** → Read `23-background-fetching-indicators.md`
- **Error Handling** → Read `13-mutations.md`
