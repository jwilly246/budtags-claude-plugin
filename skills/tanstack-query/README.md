# TanStack Query v5 Skill

Comprehensive documentation for **TanStack Query** (React Query) v5 - powerful server state management for React.

## What This Skill Covers

This skill provides complete patterns for:
- ✅ Data fetching and caching
- ✅ Mutations and optimistic updates
- ✅ Infinite queries and pagination
- ✅ Background synchronization
- ✅ TypeScript integration
- ✅ Server-side rendering
- ✅ Testing patterns
- ✅ React Suspense integration
- ✅ Error handling and retry strategies
- ✅ Real-time updates (polling, WebSockets, SSE)
- ✅ Offline-first patterns and cache persistence
- ✅ BudTags-specific integration

## Installation

```bash
npm install @tanstack/react-query

# DevTools (optional but recommended)
npm install @tanstack/react-query-devtools --save-dev
```

## File Structure

```
.claude/skills/tanstack-query/
├── SKILL.md                                    # Main entry point with auto-activation
├── README.md                                   # This file
└── patterns/
    ├── 01-installation-setup.md                # Installation and QueryClientProvider
    ├── 02-core-concepts.md                     # Server state, query lifecycle
    ├── 03-important-defaults.md                # Stale time, refetch behavior
    ├── 04-query-keys.md                        # Key structure and organization
    ├── 05-devtools.md                          # DevTools integration
    ├── 06-typescript.md                        # Type safety patterns
    ├── 07-basic-queries.md                     # useQuery fundamentals
    ├── 08-parallel-queries.md                  # Multiple queries, useQueries
    ├── 09-dependent-queries.md                 # Serial queries, enabled option
    ├── 10-query-functions.md                   # QueryFunctionContext, AbortSignal
    ├── 11-query-options.md                     # Complete options reference
    ├── 12-disabling-pausing-queries.md         # Lazy queries, conditional fetching
    ├── 13-mutations.md                         # useMutation, side effects
    ├── 14-invalidation-refetching.md           # Cache invalidation strategies
    ├── 15-optimistic-updates.md                # Optimistic UI patterns
    ├── 16-infinite-queries.md                  # Infinite scroll, pagination
    ├── 17-paginated-queries.md                 # Page-based pagination
    ├── 18-prefetching.md                       # Prefetch strategies
    ├── 19-initial-placeholder-data.md          # Initial vs placeholder data
    ├── 20-cache-updates.md                     # Manual cache manipulation
    ├── 21-cancellation.md                      # Request cancellation
    ├── 22-render-optimizations.md              # Performance optimization
    ├── 23-background-fetching-indicators.md    # Loading states
    ├── 24-network-mode.md                      # Network awareness
    ├── 25-ssr-hydration.md                     # Server-side rendering
    ├── 26-testing.md                           # Testing patterns
    ├── 27-suspense-integration.md              # React Suspense, error boundaries
    ├── 28-realtime-updates.md                  # Polling, WebSockets, Laravel Echo
    ├── 29-offline-first.md                     # Cache persistence, mutation queue
    └── 30-advanced-error-handling.md           # Retry strategies, global error handling
```

## Quick Start

### 1. Setup QueryClient

```typescript
// app.tsx or index.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

### 2. Basic Query

```typescript
import { useQuery } from '@tanstack/react-query'

function Packages() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['packages'],
    queryFn: () => fetch('/api/packages').then(r => r.json()),
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error!</div>

  return <DataTable data={data} />
}
```

### 3. Basic Mutation

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'

function CreatePackage() {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (data) => fetch('/api/packages', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] })
    }
  })

  return <button onClick={() => mutation.mutate(data)}>Create</button>
}
```

## When to Use TanStack Query

**✅ Use TanStack Query when you need:**
- Real-time data (polling, websockets)
- Optimistic UI updates
- Infinite scroll / pagination
- Background data syncing
- Multiple components sharing data
- Data persisting across route changes
- Client-side caching and synchronization

### Organization-Scoped Queries

```typescript
// Query key factory pattern
const packageKeys = {
  all: (orgId: number) => ['packages', orgId] as const,
  lists: (orgId: number) => [...packageKeys.all(orgId), 'list'] as const,
  list: (orgId: number, filters: string) => [...packageKeys.lists(orgId), { filters }] as const,
  details: (orgId: number) => [...packageKeys.all(orgId), 'detail'] as const,
  detail: (orgId: number, id: number) => [...packageKeys.details(orgId), id] as const,
}

// Usage
function usePackages(orgId: number, filters: string) {
  return useQuery({
    queryKey: packageKeys.list(orgId, filters),
    queryFn: () => fetchPackages(orgId, filters),
  })
}
```

### API Integration Example

```typescript
function usePackages(userId: string, license: string) {
  return useQuery({
    queryKey: ['packages', userId, license],
    queryFn: async () => {
      const response = await fetch(`/api/packages?license=${license}`)
      return response.json()
    },
    staleTime: 5 * 60 * 1000, // Data stale after 5 minutes
    retry: 1, // API is rate-limited
  })
}
```

### Modal + Mutation Pattern

```typescript
function AdjustPackageModal({ pkg, isOpen, onClose }: Props) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({ ... })

  const mutation = useMutation({
    mutationFn: (data) => axios.post('/api/packages/adjust', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] })
      toast.success('Package adjusted')
      onClose()
    },
    onError: (error) => {
      toast.error(error.message)
    }
  })

  return <Modal show={isOpen} onClose={onClose}>...</Modal>
}
```

## Progressive Learning Path

### Beginner (Start Here)
1. `01-installation-setup.md` - Setup QueryClient
2. `02-core-concepts.md` - Understand fundamentals
3. `07-basic-queries.md` - Your first query
4. `13-mutations.md` - Your first mutation

### Intermediate
5. `04-query-keys.md` - Organize your queries
6. `14-invalidation-refetching.md` - Keep data fresh
7. `08-parallel-queries.md` - Multiple requests
8. `09-dependent-queries.md` - Sequential requests

### Advanced
9. `15-optimistic-updates.md` - Instant UI updates
10. `16-infinite-queries.md` - Infinite scroll
11. `18-prefetching.md` - Preload data
12. `22-render-optimizations.md` - Performance

### Production
13. `06-typescript.md` - Type safety
14. `30-advanced-error-handling.md` - Error handling
15. `28-realtime-updates.md` - Real-time data
16. `25-ssr-hydration.md` - Server-side rendering
17. `26-testing.md` - Test your queries
18. `03-important-defaults.md` - Fine-tune defaults

### Advanced Features
19. `27-suspense-integration.md` - React Suspense patterns
20. `29-offline-first.md` - Offline-first and PWA

## Common Patterns

### Loading States
```typescript
const { data, isLoading, isFetching, error } = useQuery(...)

if (isLoading) return <Spinner />
if (error) return <Error error={error} />
return <div>{isFetching && <RefreshIndicator />}<DataTable data={data} /></div>
```

### Invalidation After Mutation
```typescript
const mutation = useMutation({
  mutationFn: updatePackage,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['packages'] })
  }
})
```

### Optimistic Update
```typescript
const mutation = useMutation({
  mutationFn: updatePackage,
  onMutate: async (newData) => {
    await queryClient.cancelQueries({ queryKey: ['packages', id] })
    const previous = queryClient.getQueryData(['packages', id])
    queryClient.setQueryData(['packages', id], newData)
    return { previous }
  },
  onError: (err, newData, context) => {
    queryClient.setQueryData(['packages', id], context.previous)
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['packages', id] })
  }
})
```

### Infinite Scroll
```typescript
const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
  queryKey: ['packages'],
  queryFn: ({ pageParam }) => fetchPackages(pageParam),
  initialPageParam: 0,
  getNextPageParam: (lastPage) => lastPage.nextCursor,
})
```

### React Suspense
```typescript
import { useSuspenseQuery } from '@tanstack/react-query'

function PackagesList() {
  const { data } = useSuspenseQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })
  // data is NEVER undefined!
  return <DataTable data={data} />
}

// Wrap with Suspense + ErrorBoundary
<ErrorBoundary fallback={<div>Error</div>}>
  <Suspense fallback={<Loading />}>
    <PackagesList />
  </Suspense>
</ErrorBoundary>
```

### Polling / Real-Time Updates
```typescript
// Basic polling
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  refetchInterval: 30000, // Poll every 30 seconds
})

// Laravel Echo integration
useEffect(() => {
  window.Echo.private(`org.${orgId}`)
    .listen('PackageUpdated', (e) => {
      queryClient.invalidateQueries({ queryKey: ['packages'] })
      toast.info(`Package ${e.label} updated`)
    })
}, [orgId])
```

### Error Handling with Retry
```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  retry: (failureCount, error) => {
    // Don't retry on 404
    if (error.response?.status === 404) return false
    // Retry server errors 3 times
    if (error.response?.status >= 500) return failureCount < 3
    return false
  },
  retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
})
```

### Offline-First with Cache Persistence
```typescript
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client'
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister'

const persister = createSyncStoragePersister({
  storage: window.localStorage,
})

<PersistQueryClientProvider
  client={queryClient}
  persistOptions={{ persister }}
>
  <App />
</PersistQueryClientProvider>
```

## Resources

- **Official Docs:** https://tanstack.com/query/latest
- **TK Dodo's Blog:** https://tkdodo.eu/blog/practical-react-query
- **GitHub:** https://github.com/TanStack/query
- **Discord:** https://tlinz.com/discord
- **Examples:** https://tanstack.com/query/latest/docs/framework/react/examples

## Next Steps

1. Read `SKILL.md` for complete overview
2. Start with `01-installation-setup.md` for setup
3. Learn fundamentals in `02-core-concepts.md`
4. Build queries with `07-basic-queries.md`
5. Create mutations with `13-mutations.md`
6. Optimize with `22-render-optimizations.md`
