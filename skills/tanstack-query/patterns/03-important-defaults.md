# Pattern 3: Important Defaults

## Default Behavior

TanStack Query has opinionated defaults designed for most use cases:

```typescript
// These are the defaults (you don't need to specify them)
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,

  // Defaults:
  staleTime: 0,                    // Data is stale immediately
  gcTime: 5 * 60 * 1000,           // 5 minutes
  retry: 3,                        // 3 retry attempts
  retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
  refetchOnMount: true,            // Refetch on mount if stale
  refetchOnWindowFocus: true,      // Refetch on window focus if stale
  refetchOnReconnect: true,        // Refetch on reconnect if stale
  refetchInterval: false,          // No polling
})
```

## Stale Time (staleTime: 0)

**Default:** Data is considered stale immediately after fetching.

```typescript
// Default behavior
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  // staleTime: 0 (default)
})

// Timeline:
// 0s   → Query fetches, data is fresh
// 0.1s → Data becomes stale
// Next mount/focus/reconnect → Refetch triggers
```

### When to Override

```typescript
// Static data that rarely changes
useQuery({
  queryKey: ['app-config'],
  queryFn: fetchConfig,
  staleTime: Infinity, // Never stale
})

// Data that changes slowly
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  staleTime: 5 * 60 * 1000, // Stale after 5 minutes
})

// Real-time data
useQuery({
  queryKey: ['stock-price'],
  queryFn: fetchStockPrice,
  staleTime: 0, // Always stale (default)
  refetchInterval: 1000, // Poll every second
})
```

## Garbage Collection Time (gcTime: 5 minutes)

**Default:** Inactive queries are garbage collected after 5 minutes.

```typescript
// Timeline
// 0s    → Query active, data in cache
// 10s   → Component unmounts, query becomes inactive
// 5min  → Data removed from cache
// 5min+ → Remounting component refetches from scratch
```

### When to Override

```typescript
// Keep data longer for frequently revisited pages
useQuery({
  queryKey: ['user-profile'],
  queryFn: fetchProfile,
  gcTime: 30 * 60 * 1000, // 30 minutes
})

// Aggressively clean up memory
useQuery({
  queryKey: ['large-dataset'],
  queryFn: fetchLargeData,
  gcTime: 0, // Remove immediately when inactive
})

// Keep forever (use sparingly)
useQuery({
  queryKey: ['app-constants'],
  queryFn: fetchConstants,
  staleTime: Infinity,
  gcTime: Infinity,
})
```

## Retry (retry: 3)

**Default:** Failed queries retry 3 times with exponential backoff.

```typescript
// Default retry behavior
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  // retry: 3 (default)
  // retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000)
})

// Timeline on failure:
// 0s    → First attempt fails
// 1s    → Retry 1 (2^0 * 1000ms = 1s delay)
// 3s    → Retry 2 (2^1 * 1000ms = 2s delay)
// 7s    → Retry 3 (2^2 * 1000ms = 4s delay)
// 7s+   → Give up, show error
```

### When to Override

```typescript
// No retries for user actions
useQuery({
  queryKey: ['search', query],
  queryFn: () => search(query),
  retry: false, // Don't retry failed searches
})

// More retries for unreliable APIs
useQuery({
  queryKey: ['external-api'],
  queryFn: fetchExternalData,
  retry: 5,
})

// Custom retry logic
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  retry: (failureCount, error) => {
    // Don't retry on 404
    if (error.response?.status === 404) return false
    // Retry up to 3 times for other errors
    return failureCount < 3
  },
  retryDelay: (attemptIndex) => {
    // Custom delay: 1s, 3s, 5s
    return (attemptIndex + 1) * 1000
  },
})
```

## Refetch on Mount (refetchOnMount: true)

**Default:** Stale queries refetch when component mounts.

```typescript
// Component A mounts
useQuery({ queryKey: ['packages'], queryFn: fetchPackages })
// → Fetches packages

// 10 seconds later, Component B mounts
useQuery({ queryKey: ['packages'], queryFn: fetchPackages })
// → Data is stale (staleTime: 0), refetches in background
// → Shows old data while fetching
```

### When to Override

```typescript
// Never refetch on mount
useQuery({
  queryKey: ['static-data'],
  queryFn: fetchStaticData,
  staleTime: Infinity,
  refetchOnMount: false,
})

// Conditional refetch
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  refetchOnMount: (query) => {
    // Only refetch if data is older than 1 minute
    return Date.now() - query.state.dataUpdatedAt > 60000
  },
})
```

## Refetch on Window Focus (refetchOnWindowFocus: true)

**Default:** Stale queries refetch when window regains focus.

```typescript
// User switches to another tab, then back
// → Stale queries automatically refetch
```

### When to Override (Common for BudTags)

```typescript
// Disable for internal apps where users frequently switch tabs
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false, // ← BudTags default
    },
  },
})

// Or per-query
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  refetchOnWindowFocus: false,
})
```

## Refetch on Reconnect (refetchOnReconnect: true)

**Default:** Stale queries refetch when network reconnects.

```typescript
// User loses internet, then reconnects
// → Stale queries automatically refetch
```

Usually keep this enabled.

## Global Defaults vs Per-Query

### Set Global Defaults

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,        // 1 minute
      gcTime: 5 * 60 * 1000,       // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false, // Disable for BudTags
    },
    mutations: {
      retry: 0, // Never retry mutations
    },
  },
})
```

### Override Per-Query

```typescript
// This query overrides global defaults
useQuery({
  queryKey: ['real-time-data'],
  queryFn: fetchRealTimeData,
  staleTime: 0,              // Override global 1 minute
  refetchInterval: 5000,     // Poll every 5 seconds
})
```

## BudTags Recommended Defaults

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,         // Metrc data stale after 1 minute
      gcTime: 5 * 60 * 1000,        // Keep cache for 5 minutes
      retry: 1,                     // Metrc API is rate-limited, don't retry aggressively
      refetchOnWindowFocus: false,  // Users switch tabs frequently
      refetchOnReconnect: true,     // Refetch on network reconnect
      refetchOnMount: true,         // Refetch stale data on mount
    },
    mutations: {
      retry: 0, // Never retry mutations (user should retry manually)
    },
  },
})
```

## Next Steps
- **Query Keys** → Read `04-query-keys.md`
- **Query Options** → Read `11-query-options.md`
- **Basic Queries** → Read `07-basic-queries.md`
