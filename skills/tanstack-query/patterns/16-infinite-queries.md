# Pattern 16: Infinite Queries

## useInfiniteQuery

For infinite scroll and "load more" patterns:

```typescript
import { useInfiniteQuery } from '@tanstack/react-query'

function Packages() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['packages'],
    queryFn: ({ pageParam }) => fetchPackages(pageParam),
    initialPageParam: 0,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  })

  return (
    <div>
      {data.pages.map((page) => (
        page.items.map(pkg => <PackageCard key={pkg.id} pkg={pkg} />)
      ))}

      <button
        onClick={() => fetchNextPage()}
        disabled={!hasNextPage || isFetchingNextPage}
      >
        {isFetchingNextPage ? 'Loading...' : 'Load More'}
      </button>
    </div>
  )
}
```

## Data Structure

```typescript
{
  pages: [
    { items: [...], nextCursor: 2 },  // Page 1
    { items: [...], nextCursor: 3 },  // Page 2
    { items: [...], nextCursor: null }, // Page 3 (last)
  ],
  pageParams: [0, 2, 3]
}
```

## Required Options

### initialPageParam (Required)

```typescript
useInfiniteQuery({
  queryKey: ['packages'],
  queryFn: ({ pageParam }) => fetchPackages(pageParam),
  initialPageParam: 0, // ← Required in v5
  getNextPageParam: (lastPage) => lastPage.nextCursor,
})
```

### getNextPageParam

Determine next page parameter:

```typescript
// Cursor-based
getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined

// Offset-based
getNextPageParam: (lastPage, allPages) => {
  return lastPage.items.length > 0 ? allPages.length : undefined
}

// Return undefined when no more pages
getNextPageParam: (lastPage) => {
  if (lastPage.isLast) return undefined
  return lastPage.nextPage
}
```

## Methods

```typescript
const query = useInfiniteQuery(...)

query.fetchNextPage()       // Load next page
query.fetchPreviousPage()   // Load previous page
query.hasNextPage           // boolean - more pages available
query.hasPreviousPage       // boolean - previous pages available
query.isFetchingNextPage    // boolean - loading next page
query.isFetchingPreviousPage // boolean - loading previous page
```

## Bi-Directional Scrolling

```typescript
useInfiniteQuery({
  queryKey: ['packages'],
  queryFn: ({ pageParam }) => fetchPackages(pageParam),
  initialPageParam: 0,
  getNextPageParam: (lastPage) => lastPage.nextCursor,
  getPreviousPageParam: (firstPage) => firstPage.prevCursor,
})
```

## BudTags Examples

### Metrc Packages with Infinite Scroll

```typescript
function InfinitePackages() {
  const { user } = usePage<PageProps>().props
  const license = usePage<PageProps>().props.session.license

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteQuery({
    queryKey: ['metrc', 'packages', license, 'infinite'],
    queryFn: async ({ pageParam }) => {
      const api = new MetrcApi()
      api.set_user(user)
      // Metrc API uses lastModifiedStart/lastModifiedEnd for pagination
      return api.packages_paginated(license, pageParam)
    },
    initialPageParam: new Date('2020-01-01').toISOString(),
    getNextPageParam: (lastPage) => {
      // If we got a full page, there might be more
      if (lastPage.length === 100) {
        const lastPackage = lastPage[lastPage.length - 1]
        return lastPackage.LastModified
      }
      return undefined
    },
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) return <Spinner />

  return (
    <div>
      <div className="grid grid-cols-1 gap-4">
        {data.pages.map((page, i) => (
          <React.Fragment key={i}>
            {page.map(pkg => (
              <PackageCard key={pkg.Id} pkg={pkg} />
            ))}
          </React.Fragment>
        ))}
      </div>

      {hasNextPage && (
        <button
          onClick={() => fetchNextPage()}
          disabled={isFetchingNextPage}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
        >
          {isFetchingNextPage ? 'Loading more...' : 'Load More'}
        </button>
      )}
    </div>
  )
}
```

### Auto-Loading on Scroll

```typescript
function AutoLoadPackages() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
    queryKey: ['packages'],
    queryFn: ({ pageParam }) => fetchPackages({ page: pageParam }),
    initialPageParam: 1,
    getNextPageParam: (lastPage, allPages) => {
      return lastPage.hasMore ? allPages.length + 1 : undefined
    },
  })

  // Intersection Observer for auto-loading
  const loadMoreRef = useRef(null)

  useEffect(() => {
    if (!hasNextPage || isFetchingNextPage) return

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          fetchNextPage()
        }
      },
      { threshold: 1 }
    )

    if (loadMoreRef.current) {
      observer.observe(loadMoreRef.current)
    }

    return () => observer.disconnect()
  }, [hasNextPage, isFetchingNextPage, fetchNextPage])

  return (
    <div>
      {data.pages.map((page) =>
        page.items.map(pkg => <PackageCard key={pkg.id} pkg={pkg} />)
      )}

      <div ref={loadMoreRef} className="h-10">
        {isFetchingNextPage && <Spinner />}
      </div>
    </div>
  )
}
```

### Chat Messages (Reverse Infinite)

```typescript
function ChatMessages() {
  const {
    data,
    fetchPreviousPage,
    hasPreviousPage,
    isFetchingPreviousPage,
  } = useInfiniteQuery({
    queryKey: ['messages'],
    queryFn: ({ pageParam }) => fetchMessages(pageParam),
    initialPageParam: undefined,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    getPreviousPageParam: (firstPage) => firstPage.prevCursor,
    select: (data) => ({
      pages: [...data.pages].reverse(),
      pageParams: [...data.pageParams].reverse(),
    }),
  })

  return (
    <div>
      {hasPreviousPage && (
        <button onClick={() => fetchPreviousPage()}>
          {isFetchingPreviousPage ? 'Loading...' : 'Load Older'}
        </button>
      )}

      {data.pages.map((page) =>
        page.messages.map(msg => <Message key={msg.id} msg={msg} />)
      )}
    </div>
  )
}
```

## Flattening Pages

Get all items in a flat array:

```typescript
const allPackages = data?.pages.flatMap(page => page.items) ?? []

// Use in components
<DataTable data={allPackages} />
```

## Refetching Infinite Queries

Refetches all loaded pages:

```typescript
query.refetch() // Refetches page 1, page 2, page 3, etc.
```

## Selecting Data

Transform infinite query data:

```typescript
useInfiniteQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  initialPageParam: 0,
  getNextPageParam: (lastPage) => lastPage.nextCursor,
  select: (data) => ({
    pages: data.pages.map(page => ({
      ...page,
      items: page.items.filter(pkg => !pkg.FinishedDate),
    })),
    pageParams: data.pageParams,
  }),
})
```

## Prefetching Next Page

```typescript
const query = useInfiniteQuery({
  queryKey: ['packages'],
  queryFn: ({ pageParam }) => fetchPackages(pageParam),
  initialPageParam: 0,
  getNextPageParam: (lastPage) => lastPage.nextCursor,
})

// Prefetch next page when user scrolls near bottom
useEffect(() => {
  if (query.hasNextPage && !query.isFetchingNextPage) {
    queryClient.prefetchInfiniteQuery({
      queryKey: ['packages'],
      queryFn: ({ pageParam }) => fetchPackages(pageParam),
      initialPageParam: 0,
      getNextPageParam: (lastPage) => lastPage.nextCursor,
    })
  }
}, [query.hasNextPage, query.isFetchingNextPage])
```

## Pagination vs Infinite Queries

### Use Infinite Queries:
- Infinite scroll
- "Load more" buttons
- Chat/feed interfaces
- Unknown total pages

### Use Paginated Queries:
- Page numbers (1, 2, 3...)
- Fixed page size
- Known total pages
- Jump to specific page

## Next Steps
- **Paginated Queries** → Read `17-paginated-queries.md`
- **Prefetching** → Read `18-prefetching.md`
- **Performance** → Read `22-render-optimizations.md`
