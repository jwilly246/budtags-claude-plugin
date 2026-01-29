# Pattern 20: Cache Updates

## setQueryData

Manually update the cache:

```typescript
import { useQueryClient } from '@tanstack/react-query'

function Component() {
  const queryClient = useQueryClient()

  // Update cache
  queryClient.setQueryData(['packages'], (old: Package[]) => {
    return [...old, newPackage]
  })
}
```

## getQueryData

Read data from the cache:

```typescript
const packages = queryClient.getQueryData(['packages'])
```

## Update List After Create

```typescript
const createMutation = useMutation({
  mutationFn: createPackage,
  onSuccess: (newPackage) => {
    // Add to cache
    queryClient.setQueryData(['packages'], (old: Package[]) => {
      return [...old, newPackage]
    })
  },
})
```

## Update List After Update

```typescript
const updateMutation = useMutation({
  mutationFn: updatePackage,
  onSuccess: (updatedPackage) => {
    // Update in list
    queryClient.setQueryData(['packages'], (old: Package[]) =>
      old.map(pkg => pkg.id === updatedPackage.id ? updatedPackage : pkg)
    )

    // Update detail
    queryClient.setQueryData(['package', updatedPackage.id], updatedPackage)
  },
})
```

## Update List After Delete

```typescript
const deleteMutation = useMutation({
  mutationFn: deletePackage,
  onSuccess: (_, deletedId) => {
    // Remove from cache
    queryClient.setQueryData(['packages'], (old: Package[]) =>
      old.filter(pkg => pkg.id !== deletedId)
    )

    // Remove detail
    queryClient.removeQueries({ queryKey: ['package', deletedId] })
  },
})
```

## removeQueries

Remove queries from cache:

```typescript
// Remove specific query
queryClient.removeQueries({ queryKey: ['package', 5] })

// Remove all package queries
queryClient.removeQueries({ queryKey: ['packages'] })

// Remove with predicate
queryClient.removeQueries({
  predicate: (query) => query.state.status === 'error',
})
```

## resetQueries

Clear query error state and refetch:

```typescript
// Reset to initial state and refetch
queryClient.resetQueries({ queryKey: ['packages'] })
```

## Structural Sharing

TanStack Query preserves referential equality:

```typescript
const oldData = queryClient.getQueryData(['packages'])

queryClient.setQueryData(['packages'], (old: Package[]) => {
  // If nothing changed
  return old
})

const newData = queryClient.getQueryData(['packages'])

oldData === newData // ✅ true (same reference)
```

This prevents unnecessary re-renders.

## BudTags Examples

### Add Package to Cache After Creation

```typescript
const createMutation = useMutation({
  mutationFn: async (data) => {
    const api = new MetrcApi()
    api.set_user(user)
    return api.create_package(license, data)
  },
  onSuccess: (newPackage) => {
    // Add to list cache
    queryClient.setQueryData(
      ['metrc', 'packages', license],
      (old: Package[]) => [...(old ?? []), newPackage]
    )

    toast.success('Package created')
  },
})
```

### Update Package in Cache

```typescript
const adjustMutation = useMutation({
  mutationFn: (data) =>
    axios.post(`/metrc/packages/${data.id}/adjust`, data),
  onSuccess: (updatedPackage) => {
    // Update in list
    queryClient.setQueryData(
      ['metrc', 'packages', license],
      (old: Package[]) =>
        old?.map(pkg => pkg.Id === updatedPackage.Id ? updatedPackage : pkg)
    )

    // Update detail
    queryClient.setQueryData(
      ['metrc', 'package', license, updatedPackage.Id],
      updatedPackage
    )

    toast.success('Package adjusted')
  },
})
```

### Remove Package from Cache

```typescript
const deleteMutation = useMutation({
  mutationFn: (id: number) => axios.delete(`/packages/${id}`),
  onSuccess: (_, deletedId) => {
    // Remove from list
    queryClient.setQueryData(
      ['packages'],
      (old: Package[]) => old?.filter(pkg => pkg.id !== deletedId)
    )

    // Remove detail
    queryClient.removeQueries({ queryKey: ['package', deletedId] })

    toast.success('Package deleted')
  },
})
```

### Optimistic Update with Rollback

```typescript
const finishMutation = useMutation({
  mutationFn: (id: number) => axios.post(`/packages/${id}/finish`),
  onMutate: async (id) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['packages'] })

    // Snapshot
    const previous = queryClient.getQueryData(['packages'])

    // Optimistic update
    queryClient.setQueryData(['packages'], (old: Package[]) =>
      old.map(pkg =>
        pkg.id === id ? { ...pkg, FinishedDate: new Date().toISOString() } : pkg
      )
    )

    return { previous }
  },
  onError: (err, id, context) => {
    // Rollback
    queryClient.setQueryData(['packages'], context.previous)
  },
  onSettled: () => {
    // Refetch
    queryClient.invalidateQueries({ queryKey: ['packages'] })
  },
})
```

### Seed Detail Cache from List

```typescript
function PackagesList() {
  const queryClient = useQueryClient()

  const { data: packages } = useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: fetchPackages,
  })

  // Seed detail cache for each package
  useEffect(() => {
    packages?.forEach(pkg => {
      queryClient.setQueryData(
        ['metrc', 'package', license, pkg.Id],
        pkg
      )
    })
  }, [packages, license, queryClient])

  return <DataTable data={packages} />
}
```

### Update Multiple Queries

```typescript
const updateMutation = useMutation({
  mutationFn: updateStrain,
  onSuccess: (updatedStrain) => {
    // Update in all organization's queries
    queryClient.setQueryData(
      ['strains', orgId],
      (old: Strain[]) =>
        old?.map(s => s.id === updatedStrain.id ? updatedStrain : s)
    )

    // Update detail
    queryClient.setQueryData(['strain', updatedStrain.id], updatedStrain)

    // Update in labels query (if strain is used)
    queryClient.setQueryData(
      ['labels', orgId],
      (old: Label[]) =>
        old?.map(label =>
          label.strainId === updatedStrain.id
            ? { ...label, strainName: updatedStrain.name }
            : label
        )
    )
  },
})
```

## Cache Persistence

Persist cache to localStorage:

```typescript
import { persistQueryClient } from '@tanstack/react-query-persist-client'
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      gcTime: 1000 * 60 * 60 * 24, // 24 hours
    },
  },
})

const persister = createSyncStoragePersister({
  storage: window.localStorage,
})

persistQueryClient({
  queryClient,
  persister,
})
```

## Query Data Matchers

Update multiple queries at once:

```typescript
// Update all package queries
queryClient.setQueriesData(
  { queryKey: ['packages'] },
  (old: Package[]) => old.filter(pkg => !pkg.FinishedDate)
)
```

## Next Steps
- **Invalidation** → Read `14-invalidation-refetching.md`
- **Optimistic Updates** → Read `15-optimistic-updates.md`
- **Mutations** → Read `13-mutations.md`
