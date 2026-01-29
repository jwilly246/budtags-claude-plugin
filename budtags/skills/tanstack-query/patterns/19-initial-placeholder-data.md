# Pattern 19: Initial & Placeholder Data

## initialData vs placeholderData

### initialData
- Persists to cache
- Treated as real data
- Can become stale
- Affects `dataUpdatedAt`

### placeholderData
- Doesn't persist to cache
- Only shown while loading
- Doesn't become stale
- Doesn't affect `dataUpdatedAt`

## initialData

### Static Initial Data

```typescript
useQuery({
  queryKey: ['package', 5],
  queryFn: () => fetchPackage(5),
  initialData: {
    id: 5,
    label: 'Loading...',
    // ... default values
  },
})
```

### Dynamic Initial Data from Cache

```typescript
useQuery({
  queryKey: ['package', id],
  queryFn: () => fetchPackage(id),
  initialData: () => {
    // Use list data as initial detail data
    const packages = queryClient.getQueryData(['packages'])
    return packages?.find(pkg => pkg.id === id)
  },
  // When to consider initial data stale
  initialDataUpdatedAt: () =>
    queryClient.getQueryState(['packages'])?.dataUpdatedAt,
})
```

## placeholderData

### Static Placeholder

```typescript
useQuery({
  queryKey: ['package', id],
  queryFn: () => fetchPackage(id),
  placeholderData: {
    id,
    label: 'Loading...',
    // ... skeleton data
  },
})
```

### Keep Previous Data (Pagination)

```typescript
useQuery({
  queryKey: ['packages', page],
  queryFn: () => fetchPackages(page),
  placeholderData: (previousData) => previousData,
})

// While loading page 2:
// - Shows page 1 data
// - isPlaceholderData: true

// When page 2 loads:
// - Shows page 2 data
// - isPlaceholderData: false
```

## When to Use Each

### Use initialData When:
- Seeding from cache
- Default state that should be cached
- Data should be considered "real"

### Use placeholderData When:
- Showing skeleton/loading states
- Keeping previous page during pagination
- Temporary UI filler

## BudTags Examples

### Package Detail from List

```typescript
function PackageDetails({ packageId }: { packageId: number }) {
  const queryClient = useQueryClient()
  const license = usePage<PageProps>().props.session.license

  const { data: pkg } = useQuery({
    queryKey: ['metrc', 'package', license, packageId],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.package_by_id(license, packageId)
    },
    // Use list data as initial data
    initialData: () => {
      const packages = queryClient.getQueryData(['metrc', 'packages', license])
      return packages?.find((p: Package) => p.Id === packageId)
    },
    // Mark when list was fetched
    initialDataUpdatedAt: () =>
      queryClient.getQueryState(['metrc', 'packages', license])?.dataUpdatedAt,
  })

  return <PackageDetailsView pkg={pkg} />
}
```

### Paginated Packages with Previous Data

```typescript
function PaginatedPackages() {
  const [page, setPage] = useState(1)
  const license = usePage<PageProps>().props.session.license

  const { data, isPlaceholderData } = useQuery({
    queryKey: ['metrc', 'packages', license, page],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages_paginated(license, page)
    },
    placeholderData: (previousData) => previousData,
  })

  return (
    <div>
      <DataTable data={data.items} opacity={isPlaceholderData ? 0.5 : 1} />

      <button
        onClick={() => setPage(p => p + 1)}
        disabled={isPlaceholderData}
      >
        Next
      </button>
    </div>
  )
}
```

### Skeleton Placeholder

```typescript
function StrainDetails({ strainId }: { strainId: number }) {
  const { data: strain } = useQuery({
    queryKey: ['strain', strainId],
    queryFn: () => fetchStrain(strainId),
    placeholderData: {
      id: strainId,
      name: '████████',
      type: '████',
      // Skeleton data
    },
  })

  return (
    <div>
      <h1>{strain.name}</h1>
      <p>Type: {strain.type}</p>
    </div>
  )
}
```

### Conditional Initial Data

```typescript
function PackageHistory({ packageId }: { packageId: number }) {
  const queryClient = useQueryClient()

  const { data } = useQuery({
    queryKey: ['package-history', packageId],
    queryFn: () => fetchPackageHistory(packageId),
    initialData: () => {
      // Only use cached detail as initial if it exists AND is fresh
      const pkg = queryClient.getQueryData(['package', packageId])
      const state = queryClient.getQueryState(['package', packageId])

      const isFresh = state?.dataUpdatedAt &&
        Date.now() - state.dataUpdatedAt < 60000 // Less than 1 minute old

      return isFresh ? pkg : undefined
    },
  })

  return <HistoryList data={data} />
}
```

### Cache-First Approach

```typescript
function useCachedThenFresh<T>(
  queryKey: unknown[],
  queryFn: () => Promise<T>
) {
  return useQuery({
    queryKey,
    queryFn,
    // Use any cached data as initial, even if stale
    initialData: () => queryClient.getQueryData(queryKey),
    // But immediately refetch if stale
    staleTime: 0,
  })
}

// Usage
const { data } = useCachedThenFresh(
  ['packages'],
  fetchPackages
)
// Shows cached data immediately, refetches in background
```

## initialDataUpdatedAt

Tell TanStack Query when initial data was fetched:

```typescript
useQuery({
  queryKey: ['package', id],
  queryFn: () => fetchPackage(id),
  initialData: () => {
    const packages = queryClient.getQueryData(['packages'])
    return packages?.find(p => p.id === id)
  },
  // Tell when initial data was fetched
  initialDataUpdatedAt: () => {
    const state = queryClient.getQueryState(['packages'])
    return state?.dataUpdatedAt
  },
  // If initial data is older than 5 minutes, refetch
  staleTime: 5 * 60 * 1000,
})
```

## Persistence Comparison

```typescript
// initialData persists
useQuery({
  queryKey: ['data'],
  queryFn: fetchData,
  initialData: { id: 1, name: 'Default' },
})
// Cache: { data: { id: 1, name: 'Default' } }
// Component unmounts
// Cache: Still has { id: 1, name: 'Default' }

// placeholderData doesn't persist
useQuery({
  queryKey: ['data'],
  queryFn: fetchData,
  placeholderData: { id: 1, name: 'Loading' },
})
// Cache: undefined (until fetch completes)
// Component unmounts
// Cache: undefined (placeholder never cached)
```

## Next Steps
- **Prefetching** → Read `18-prefetching.md`
- **Cache Updates** → Read `20-cache-updates.md`
- **Query Options** → Read `11-query-options.md`
