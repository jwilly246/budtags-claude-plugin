# Pattern 25: SSR & Hydration

## Server-Side Rendering

TanStack Query supports SSR with Next.js, Remix, and other frameworks.

## Basic SSR Pattern

### 1. Prefetch on Server

```typescript
import { dehydrate, HydrationBoundary, QueryClient } from '@tanstack/react-query'

// Server Component (Next.js App Router)
export default async function PackagesPage() {
  const queryClient = new QueryClient()

  // Prefetch on server
  await queryClient.prefetchQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <PackagesList />
    </HydrationBoundary>
  )
}
```

### 2. Use in Client Component

```typescript
'use client'

function PackagesList() {
  // Data is already in cache from server
  const { data } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  return <DataTable data={data} />
}
```

## Per-Request QueryClient

**Important:** Create a new QueryClient for each request:

```typescript
// ❌ BAD - Shared across requests
const queryClient = new QueryClient()

export default async function Page() {
  await queryClient.prefetchQuery(...)
  // Data leaks between users!
}

// ✅ GOOD - New instance per request
export default async function Page() {
  const queryClient = new QueryClient()
  await queryClient.prefetchQuery(...)
  // Isolated to this request
}
```

## Next.js App Router

### Server Component

```typescript
// app/packages/page.tsx
import { dehydrate, HydrationBoundary, QueryClient } from '@tanstack/react-query'
import { PackagesList } from './PackagesList'

export default async function PackagesPage() {
  const queryClient = new QueryClient()

  await queryClient.prefetchQuery({
    queryKey: ['packages'],
    queryFn: async () => {
      const response = await fetch('https://api.example.com/packages')
      return response.json()
    },
  })

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <PackagesList />
    </HydrationBoundary>
  )
}
```

### Client Component

```typescript
// app/packages/PackagesList.tsx
'use client'

import { useQuery } from '@tanstack/react-query'

export function PackagesList() {
  const { data } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  return <div>{data?.map(pkg => <div key={pkg.id}>{pkg.label}</div>)}</div>
}
```

## Next.js Pages Router

### getServerSideProps

```typescript
import { dehydrate, QueryClient } from '@tanstack/react-query'

export async function getServerSideProps() {
  const queryClient = new QueryClient()

  await queryClient.prefetchQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  return {
    props: {
      dehydratedState: dehydrate(queryClient),
    },
  }
}

function PackagesPage() {
  const { data } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  return <DataTable data={data} />
}
```

### _app.tsx

```typescript
import { HydrationBoundary, QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

export default function App({ Component, pageProps }) {
  const [queryClient] = useState(() => new QueryClient())

  return (
    <QueryClientProvider client={queryClient}>
      <HydrationBoundary state={pageProps.dehydratedState}>
        <Component {...pageProps} />
      </HydrationBoundary>
    </QueryClientProvider>
  )
}
```

## SSR Example with Next.js

### Server Component

```typescript
// app/packages/page.tsx
export default async function PackagesPage() {
  const packages = await fetchPackages()

  return <PackagesClient initialPackages={packages} />
}
```

### Client Component

```typescript
// app/packages/PackagesClient.tsx
'use client'

import { useQuery } from '@tanstack/react-query'

export function PackagesClient({ initialPackages }) {
  const { data: packages } = useQuery({
    queryKey: ['packages'],
    queryFn: async () => {
      const response = await fetch('/api/packages')
      return response.json()
    },
    initialData: initialPackages, // Use server data as initial
    staleTime: 5 * 60 * 1000,
  })

  return <DataTable data={packages} />
}
```

## initialData vs SSR

### Using initialData

```typescript
// Traditional SSR
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  initialData: serverData, // From props
})
```

### Using Hydration

```typescript
// Modern SSR (Next.js, Remix)
// Server: prefetchQuery + dehydrate
// Client: HydrationBoundary
```

## Security: Serialization

**Warning:** XSS vulnerability with dehydrate

```typescript
// ❌ BAD - Vulnerable to XSS
<script>
  window.__REACT_QUERY_STATE__ = {dehydrate(queryClient)}
</script>

// ✅ GOOD - Use Next.js built-in serialization
// Or serialize manually with DOMPurify
```

## Server-Side gcTime

Set to Infinity on server to prevent garbage collection during SSR:

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      gcTime: typeof window === 'undefined' ? Infinity : 5 * 60 * 1000,
    },
  },
})
```

## Streaming (Experimental)

```typescript
import { dehydrate, HydrationBoundary, QueryClient } from '@tanstack/react-query'
import { experimental_renderToPipeableStream } from 'react-dom/server'

const queryClient = new QueryClient()

const { pipe } = experimental_renderToPipeableStream(
  <QueryClientProvider client={queryClient}>
    <HydrationBoundary state={dehydrate(queryClient)}>
      <App />
    </HydrationBoundary>
  </QueryClientProvider>
)
```

## Prefetch Multiple Queries

```typescript
export default async function Dashboard() {
  const queryClient = new QueryClient()

  await Promise.all([
    queryClient.prefetchQuery({
      queryKey: ['packages'],
      queryFn: fetchPackages,
    }),
    queryClient.prefetchQuery({
      queryKey: ['plants'],
      queryFn: fetchPlants,
    }),
    queryClient.prefetchQuery({
      queryKey: ['harvests'],
      queryFn: fetchHarvests,
    }),
  ])

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <Dashboard />
    </HydrationBoundary>
  )
}
```

## SSR Best Practices

### ✅ DO

```typescript
// Create new QueryClient per request
const queryClient = new QueryClient()

// Set gcTime to Infinity on server
gcTime: typeof window === 'undefined' ? Infinity : 5 * 60 * 1000

// Prefetch critical data on server
await queryClient.prefetchQuery({ ... })
```

### ❌ DON'T

```typescript
// Share QueryClient across requests
const sharedClient = new QueryClient() // ❌ Data leaks

// Render before prefetch completes
// Missing await
queryClient.prefetchQuery({ ... }) // ❌ Not awaited
```

## Next Steps
- **Prefetching** → Read `18-prefetching.md`
- **Initial Data** → Read `19-initial-placeholder-data.md`
- **Testing** → Read `26-testing.md`
