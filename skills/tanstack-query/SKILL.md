---
name: tanstack-query
description: TanStack Query (React Query) v5 patterns for server state management, data fetching, caching, mutations, and optimistic updates
version: 1.0.0
category: project
agent: tanstack-specialist
auto_activate:
  patterns:
    - "**/*.{ts,tsx,js,jsx}"
  keywords:
    - "useQuery"
    - "useMutation"
    - "QueryClient"
    - "useInfiniteQuery"
    - "invalidateQueries"
    - "react-query"
    - "tanstack query"
    - "server state"
    - "data fetching"
    - "cache management"
    - "useSuspenseQuery"
    - "useSuspenseInfiniteQuery"
    - "error boundary"
    - "ErrorBoundary"
    - "refetchInterval"
    - "polling"
    - "websocket"
    - "realtime"
    - "offline"
    - "offline-first"
    - "cache persistence"
    - "mutation queue"
    - "retry"
    - "error handling"
---

# TanStack Query v5 Skill

Comprehensive patterns for **TanStack Query** (formerly React Query) - a powerful data synchronization library for React applications.

## What is TanStack Query?

TanStack Query makes **fetching, caching, synchronizing, and updating server state** in React applications a breeze. It handles the complex and often misunderstood parts of server state management automatically:

- ✅ **Caching** - Intelligent caching with automatic garbage collection
- ✅ **Deduplication** - Multiple components requesting the same data get a single request
- ✅ **Background Updates** - Data updates in the background to stay fresh
- ✅ **Optimistic Updates** - UI updates before server confirms
- ✅ **Pagination & Infinite Scroll** - Built-in support for complex data loading
- ✅ **Request Cancellation** - Automatic cleanup on component unmount
- ✅ **DevTools** - Powerful debugging and cache inspection

## When to Use TanStack Query

**Use TanStack Query when you need:**
- ✅ Real-time updates (polling, websockets)
- ✅ Optimistic UI updates
- ✅ Complex data dependencies (infinite scroll, pagination)
- ✅ Background data syncing
- ✅ Client-side search/filtering with server validation
- ✅ Multiple components sharing the same data
- ✅ Data to persist across route changes
- ✅ Automatic caching and deduplication
- ✅ Request cancellation and retry logic

## Progressive Loading Strategy

Load only the patterns you need:

### Quick Start (~300 lines)
```
patterns/01-installation-setup.md       (150 lines)
patterns/07-basic-queries.md            (175 lines)
```

### Mutations (~400 lines)
```
patterns/13-mutations.md                (200 lines)
patterns/14-invalidation-refetching.md  (200 lines)
```

### Advanced Features (~600 lines)
```
patterns/15-optimistic-updates.md       (225 lines)
patterns/16-infinite-queries.md         (200 lines)
patterns/18-prefetching.md              (200 lines)
```

### Production Readiness (~1,000 lines)
```
patterns/06-typescript.md               (200 lines)
patterns/22-render-optimizations.md     (200 lines)
patterns/25-ssr-hydration.md            (225 lines)
patterns/26-testing.md                  (200 lines)
patterns/27-suspense-integration.md     (225 lines)
patterns/30-advanced-error-handling.md  (250 lines)
```

### Real-Time & Polling (~500 lines)
```
patterns/28-realtime-updates.md         (250 lines)
patterns/23-background-fetching-indicators.md (150 lines)
patterns/24-network-mode.md             (175 lines)
```

### Offline & PWA (~275 lines)
```
patterns/29-offline-first.md            (275 lines)
```

## All Pattern Files (30 Total)

### Foundation (6 patterns - ~1,075 lines)
- `01-installation-setup.md` (150 lines) - Installation, QueryClientProvider setup
- `02-core-concepts.md` (200 lines) - Server state vs client state, query lifecycle
- `03-important-defaults.md` (175 lines) - Stale time, refetch behavior, retries
- `04-query-keys.md` (200 lines) - Key structure, hierarchical organization, factory pattern
- `05-devtools.md` (150 lines) - DevTools installation, debugging, cache inspection
- `06-typescript.md` (200 lines) - Type inference, generic types, type safety

### Queries (6 patterns - ~1,100 lines)
- `07-basic-queries.md` (175 lines) - useQuery hook, query states, basic patterns
- `08-parallel-queries.md` (150 lines) - Multiple queries, useQueries hook
- `09-dependent-queries.md` (175 lines) - enabled option, serial queries, waterfalls
- `10-query-functions.md` (150 lines) - QueryFunctionContext, AbortSignal, error handling
- `11-query-options.md` (200 lines) - staleTime, gcTime, refetch options, complete reference
- `12-disabling-pausing-queries.md` (150 lines) - Lazy queries, enabled: false patterns

### Mutations (3 patterns - ~625 lines)
- `13-mutations.md` (200 lines) - useMutation, mutate vs mutateAsync, side effects
- `14-invalidation-refetching.md` (200 lines) - invalidateQueries, matching strategies
- `15-optimistic-updates.md` (225 lines) - onMutate, rollback, cache manipulation

### Advanced Queries (4 patterns - ~775 lines)
- `16-infinite-queries.md` (200 lines) - useInfiniteQuery, pagination params, bi-directional
- `17-paginated-queries.md` (175 lines) - Page-based pagination, keepPreviousData
- `18-prefetching.md` (200 lines) - prefetchQuery, cache priming, router integration
- `19-initial-placeholder-data.md` (200 lines) - initialData vs placeholderData

### Cache & Performance (3 patterns - ~525 lines)
- `20-cache-updates.md` (175 lines) - setQueryData, getQueryData, cache cleanup
- `21-cancellation.md` (150 lines) - AbortSignal, automatic cancellation, HTTP clients
- `22-render-optimizations.md` (200 lines) - Structural sharing, tracked properties, select

### Background & Network (3 patterns - ~575 lines)
- `23-background-fetching-indicators.md` (150 lines) - isFetching vs isPending, global indicators
- `24-network-mode.md` (175 lines) - online/always/offlineFirst modes, network awareness
- `28-realtime-updates.md` (250 lines) - Polling, WebSockets, SSE, Laravel Echo integration

### Integration & Testing (4 patterns - ~900 lines)
- `25-ssr-hydration.md` (225 lines) - Server-side rendering, Next.js integration, dehydrate/hydrate
- `26-testing.md` (200 lines) - Test setup, mocking, async testing, RTL integration
- `27-suspense-integration.md` (225 lines) - useSuspenseQuery, Error Boundaries, React 18+ patterns
- `30-advanced-error-handling.md` (250 lines) - Retry strategies, error boundaries, global error handling

### Offline & PWA (1 pattern - ~275 lines)
- `29-offline-first.md` (275 lines) - Cache persistence, mutation queue, background sync, IndexedDB

## BudTags Integration Examples

### Organization-Scoped Query Keys
```typescript
const packageKeys = {
  all: (orgId: number) => ['packages', orgId] as const,
  lists: (orgId: number) => [...packageKeys.all(orgId), 'list'] as const,
  list: (orgId: number, filters: string) => [...packageKeys.lists(orgId), { filters }] as const,
  details: (orgId: number) => [...packageKeys.all(orgId), 'detail'] as const,
  detail: (orgId: number, id: number) => [...packageKeys.details(orgId), id] as const,
}
```

### License-Specific Metrc Queries
```typescript
function usePackages(license: string) {
  return useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages(license)
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000,   // 10 minutes
  })
}
```

### Modal + Mutation Pattern
```typescript
function AdjustPackageModal({ pkg, isOpen, onClose }: Props) {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (data: AdjustData) => axios.post('/metrc/adjust', data),
    onSuccess: () => {
      // Invalidate package list
      queryClient.invalidateQueries({ queryKey: ['metrc', 'packages'] })

      // Show success toast
      toast.success('Package adjusted successfully')

      // Close modal
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.message || 'Failed to adjust package')
    }
  })

  return (
    <Modal show={isOpen} onClose={onClose}>
      <form onSubmit={(e) => {
        e.preventDefault()
        mutation.mutate(formData)
      }}>
        {/* ... */}
      </form>
    </Modal>
  )
}
```

### Real-Time Updates with Background Refetch
```typescript
function PackagesTable() {
  const { data: packages } = useQuery({
    queryKey: ['metrc', 'packages'],
    queryFn: fetchPackages,
    refetchInterval: 30000, // Poll every 30 seconds
    refetchOnWindowFocus: true,
  })

  return <DataTable data={packages} />
}
```

### Optimistic Update for Quick Actions
```typescript
function useFinishPackage() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => axios.post(`/packages/${id}/finish`),
    onMutate: async (id) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['packages'] })

      // Snapshot previous value
      const previous = queryClient.getQueryData(['packages'])

      // Optimistically update
      queryClient.setQueryData(['packages'], (old: Package[]) =>
        old.map(pkg => pkg.Id === id ? { ...pkg, FinishedDate: new Date().toISOString() } : pkg)
      )

      return { previous }
    },
    onError: (err, id, context) => {
      // Rollback on error
      queryClient.setQueryData(['packages'], context.previous)
      toast.error('Failed to finish package')
    },
    onSettled: () => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: ['packages'] })
    },
  })
}
```

## Quick Start Guide

### 1. Install TanStack Query
```bash
npm install @tanstack/react-query
npm install @tanstack/react-query-devtools --save-dev
```

### 2. Setup QueryClient
```typescript
// app.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      gcTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
})

createInertiaApp({
  resolve: (name) => resolvePageComponent(`./Pages/${name}.tsx`, import.meta.glob('./Pages/**/*.tsx')),
  setup({ el, App, props }) {
    const root = createRoot(el)
    root.render(
      <QueryClientProvider client={queryClient}>
        <App {...props} />
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    )
  },
})
```

### 3. Use in Components
```typescript
import { useQuery } from '@tanstack/react-query'

function Packages() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['packages'],
    queryFn: () => fetch('/api/packages').then(r => r.json()),
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return <DataTable data={data} />
}
```

## Next Steps
- **Start:** Read `01-installation-setup.md` for setup
- **Learn:** Read `02-core-concepts.md` for fundamentals
- **Build:** Read `07-basic-queries.md` and `13-mutations.md`
- **Optimize:** Read `22-render-optimizations.md` and `06-typescript.md`
- **Test:** Read `26-testing.md` for testing patterns

## Resources
- **Official Docs:** https://tanstack.com/query/latest
- **GitHub:** https://github.com/TanStack/query
- **Discord:** https://tlinz.com/discord
- **TK Dodo's Blog:** https://tkdodo.eu/blog/practical-react-query (highly recommended)
