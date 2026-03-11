---
name: tanstack-query
description: TanStack Query (React Query) v5 patterns for server state management, data fetching, caching, mutations, and optimistic updates
version: 1.1.0
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

### 3-Layer Architecture Overview

BudTags organizes React Query code into three layers per domain:

```
resources/js/Hooks/{domain}/
├── keys.ts         # Key factories (as const tuples)
├── queries.ts      # queryOptions() factories + private fetch functions
└── use*.ts         # Hook wrappers (spread queryOptions) + mutations
```

### Key Factories (keys.ts)
```typescript
// Flat pattern (Metrc reference data) — resources/js/Hooks/metrc/keys.ts
export const metrcPackageKeys = {
    all: () => ['metrc-packages'] as const,
    byLicense: (license: string | null) => [...metrcPackageKeys.all(), license] as const,
    paginatedPrefix: (license: string | null) => ['metrc-packages-paginated', license] as const,
};

// Hierarchical pattern (Marketplace) — resources/js/Hooks/marketplace/keys.ts
export const marketplaceOrderKeys = {
    all: (orgId: string, viewMode: 'seller' | 'buyer') =>
        ['marketplace-orders', orgId, viewMode] as const,
    lists: (orgId: string, viewMode: 'seller' | 'buyer') =>
        [...marketplaceOrderKeys.all(orgId, viewMode), 'list'] as const,
    detail: (orgId: string, viewMode: 'seller' | 'buyer', id: string) =>
        [...marketplaceOrderKeys.all(orgId, viewMode), 'detail', id] as const,
};
```

### queryOptions Factories (queries.ts)
```typescript
// resources/js/Hooks/metrc/queries.ts
import { queryOptions } from '@tanstack/react-query';
import { STALE_TIME } from '@/constants/query-config';
import { metrcPackageKeys } from './keys';

const fetchPackages = async (license: string, signal?: AbortSignal) => {
    const { data } = await axios.get(`/metrc/packages/${license}`, { signal });
    return data.packages;
};

export const metrcQueries = {
    packages: (license: string | null) => queryOptions({
        queryKey: metrcPackageKeys.byLicense(license),
        queryFn: ({ signal }) => fetchPackages(license!, signal),
        staleTime: STALE_TIME.DEFAULT,
    }),
};
```

### Hook Wrappers with Spread Pattern
```typescript
// resources/js/Hooks/metrc/useMetrcPackages.ts
export function useMetrcPackages(license: string | null, enabled = true) {
    return useQuery({
        ...metrcQueries.packages(license),  // spread queryOptions
        enabled: enabled && !!license,
    });
}
```

### Mutation with Optimistic Update
```typescript
// resources/js/Hooks/marketplace/useMarketplaceOrders.ts
export function useAcceptOrder() {
    const queryClient = useQueryClient();
    const orgId = usePage<PageProps>().props.user.active_org_id ?? '';

    return useMutation({
        mutationFn: async ({ id }: { id: string }) =>
            axios.post(`/marketplace/seller/orders/${id}/accept`),
        onMutate: async ({ id }) => {
            const opts = marketplaceOrderQueries.detail(orgId, 'seller', id);
            await queryClient.cancelQueries({ queryKey: opts.queryKey });
            const previous = queryClient.getQueryData(opts.queryKey);
            queryClient.setQueryData(opts.queryKey, (old: any) => ({ ...old, status: 'accepted' }));
            return { previous };
        },
        onError: (_err, { id }, context) => {
            queryClient.setQueryData(
                marketplaceOrderKeys.detail(orgId, 'seller', id),
                context?.previous,
            );
        },
        onSettled: (_data, _error, { id }) => {
            queryClient.invalidateQueries({ queryKey: marketplaceOrderKeys.all(orgId, 'seller') });
        },
    });
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
import { STALE_TIME } from '@/constants/query-config'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: STALE_TIME.DEFAULT,    // 5 min
      gcTime: STALE_TIME.LONG,          // 10 min
      refetchOnWindowFocus: false,
      retry: 1,
      retryDelay: 1000,
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
        {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
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
