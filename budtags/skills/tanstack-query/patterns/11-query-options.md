# Pattern 11: Query Options

## Complete Options Reference

```typescript
useQuery({
  // Required
  queryKey: ['packages'],
  queryFn: fetchPackages,

  // Stale & Cache
  staleTime: 5 * 60 * 1000,           // Data fresh for 5 minutes (default: 0)
  gcTime: 10 * 60 * 1000,             // Cache for 10 minutes (default: 5 min)

  // Retry
  retry: 3,                           // Retry 3 times (default: 3)
  retryDelay: (attemptIndex) =>
    Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff (default)

  // Refetch
  refetchOnMount: true,               // Refetch on mount if stale (default: true)
  refetchOnWindowFocus: false,        // Refetch on window focus (default: true)
  refetchOnReconnect: true,           // Refetch on reconnect (default: true)
  refetchInterval: false,             // Poll interval (default: false)
  refetchIntervalInBackground: false, // Poll when tab inactive (default: false)

  // Enable/Disable
  enabled: true,                      // Enable query (default: true)

  // Initial Data
  initialData: undefined,             // Initial data (default: undefined)
  initialDataUpdatedAt: undefined,    // When initial data was fetched
  placeholderData: undefined,         // Placeholder while loading

  // Select
  select: (data) => data,             // Transform data (default: identity)

  // Other
  networkMode: 'online',              // 'online' | 'always' | 'offlineFirst'
  notifyOnChangeProps: undefined,     // Which props trigger re-render
  meta: undefined,                    // Metadata object
})
```

## staleTime

How long until data is considered stale:

```typescript
// Always stale (refetch on every mount/focus)
useQuery({
  queryKey: ['real-time-data'],
  queryFn: fetchData,
  staleTime: 0, // Default
})

// Fresh for 5 minutes
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  staleTime: 5 * 60 * 1000,
})

// Never stale
useQuery({
  queryKey: ['constants'],
  queryFn: fetchConstants,
  staleTime: Infinity,
})
```

## gcTime (Garbage Collection Time)

How long inactive queries stay in cache:

```typescript
// Remove immediately when inactive
useQuery({
  queryKey: ['temporary-data'],
  queryFn: fetchData,
  gcTime: 0,
})

// Keep for 10 minutes (default: 5 minutes)
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  gcTime: 10 * 60 * 1000,
})

// Keep forever
useQuery({
  queryKey: ['app-config'],
  queryFn: fetchConfig,
  gcTime: Infinity,
})
```

## retry

Control retry behavior:

```typescript
// No retries
useQuery({
  queryKey: ['search'],
  queryFn: search,
  retry: false,
})

// Custom retry logic
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  retry: (failureCount, error) => {
    // Don't retry on 404
    if (error.response?.status === 404) return false

    // Max 3 retries
    return failureCount < 3
  },
})

// Custom retry delay
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  retryDelay: (attemptIndex) => {
    // 1s, 2s, 4s, 8s
    return Math.min(1000 * 2 ** attemptIndex, 30000)
  },
})
```

## refetchInterval (Polling)

Automatically refetch at intervals:

```typescript
// Poll every 10 seconds
useQuery({
  queryKey: ['stock-price'],
  queryFn: fetchStockPrice,
  refetchInterval: 10000,
})

// Poll only while tab is active
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  refetchInterval: 30000,
  refetchIntervalInBackground: false, // Default
})

// Poll even when tab is inactive
useQuery({
  queryKey: ['notifications'],
  queryFn: fetchNotifications,
  refetchInterval: 60000,
  refetchIntervalInBackground: true,
})

// Dynamic polling based on data
useQuery({
  queryKey: ['task', taskId],
  queryFn: () => fetchTask(taskId),
  refetchInterval: (data) => {
    // Poll every 1s while task is running
    if (data?.status === 'running') return 1000
    // Stop polling when complete
    return false
  },
})
```

## enabled

Conditionally enable queries:

```typescript
// Lazy query (never auto-fetches)
useQuery({
  queryKey: ['data'],
  queryFn: fetchData,
  enabled: false,
})

// Conditional query
useQuery({
  queryKey: ['user-data', userId],
  queryFn: () => fetchUserData(userId),
  enabled: !!userId, // Only run if userId exists
})

// Permission-based
useQuery({
  queryKey: ['secrets', orgId],
  queryFn: () => fetchSecrets(orgId),
  enabled: hasPermission('edit-secrets'),
})
```

## select

Transform data without affecting cache:

```typescript
// Select specific fields
const { data: labels } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  select: (packages) => packages.map(p => p.Label),
})
// data: string[]

// Aggregate data
const { data: count } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  select: (packages) => packages.length,
})
// data: number

// Filter data
const { data: activePackages } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  select: (packages) => packages.filter(p => !p.FinishedDate),
})
```

## initialData vs placeholderData

### initialData

Persists to cache, treated as real data:

```typescript
useQuery({
  queryKey: ['package', id],
  queryFn: () => fetchPackage(id),
  initialData: () => {
    // Use cached list data for initial package data
    const packages = queryClient.getQueryData(['packages'])
    return packages?.find(p => p.Id === id)
  },
  // Mark when initial data was fetched
  initialDataUpdatedAt: () =>
    queryClient.getQueryState(['packages'])?.dataUpdatedAt,
})
```

### placeholderData

Doesn't persist, just shows while loading:

```typescript
useQuery({
  queryKey: ['package', id],
  queryFn: () => fetchPackage(id),
  placeholderData: {
    Id: id,
    Label: 'Loading...',
    ProductName: 'Loading...',
  },
})

// Keep previous data while refetching
useQuery({
  queryKey: ['packages', page],
  queryFn: () => fetchPackages(page),
  placeholderData: (previousData) => previousData,
})
```

## BudTags Configuration Examples

### Metrc Packages Query

```typescript
useQuery({
  queryKey: ['metrc', 'packages', license],
  queryFn: async () => {
    const api = new MetrcApi()
    api.set_user(user)
    return api.packages(license)
  },
  staleTime: 5 * 60 * 1000,    // Metrc data fresh for 5 minutes
  gcTime: 10 * 60 * 1000,      // Keep in cache for 10 minutes
  retry: 1,                     // Metrc is rate-limited, don't retry aggressively
  refetchOnWindowFocus: false,  // Users switch tabs frequently
})
```

### Real-Time Polling

```typescript
useQuery({
  queryKey: ['transfer-status', transferId],
  queryFn: () => fetchTransferStatus(transferId),
  refetchInterval: (data) => {
    // Poll every 5 seconds while pending
    if (data?.status === 'pending') return 5000
    // Stop when complete
    return false
  },
  refetchIntervalInBackground: false,
})
```

### Conditional Metrc Query

```typescript
useQuery({
  queryKey: ['metrc', 'plants', license],
  queryFn: async () => {
    const api = new MetrcApi()
    api.set_user(user)
    return api.plants(license)
  },
  // Only run for cultivation licenses
  enabled: license?.startsWith('au-c-'),
  staleTime: 5 * 60 * 1000,
})
```

### Transform Package Data

```typescript
const { data: packageLabels } = useQuery({
  queryKey: ['metrc', 'packages', license],
  queryFn: async () => {
    const api = new MetrcApi()
    api.set_user(user)
    return api.packages(license)
  },
  // Transform to just labels for dropdown
  select: (packages) => packages.map(p => ({
    value: p.Id,
    label: p.Label,
  })),
})
```

## Next Steps
- **Important Defaults** → Read `03-important-defaults.md`
- **Performance** → Read `22-render-optimizations.md`
- **Initial Data** → Read `19-initial-placeholder-data.md`
