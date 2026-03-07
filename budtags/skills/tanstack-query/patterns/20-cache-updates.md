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
import { metrcQueries } from '@/Hooks/metrc/queries'

const createMutation = useMutation({
  mutationFn: (data: CreatePackageData) =>
    axios.post('/metrc/packages/create', { ...data, license }),
  onSuccess: (newPackage) => {
    // Use queryOptions factory for typed cache access
    const opts = metrcQueries.packages(license)
    queryClient.setQueryData(
      opts.queryKey,
      (old: Package[]) => [...(old ?? []), newPackage]
    )

    toast.success('Package created')
  },
})
```

### Update Package in Cache

```typescript
import { metrcPackageKeys } from '@/Hooks/metrc/keys'
import { metrcQueries } from '@/Hooks/metrc/queries'

const adjustMutation = useMutation({
  mutationFn: (data) =>
    axios.post(`/metrc/packages/${data.id}/adjust`, data),
  onSuccess: (updatedPackage) => {
    // Use queryOptions factory for typed cache access
    const listOpts = metrcQueries.packages(license)
    queryClient.setQueryData(
      listOpts.queryKey,
      (old: Package[]) =>
        old?.map(pkg => pkg.Id === updatedPackage.Id ? updatedPackage : pkg)
    )

    // Update detail — use queryOptions factory for the detail query
    const detailOpts = metrcQueries.packageDetail(license, updatedPackage.Id)
    queryClient.setQueryData(detailOpts.queryKey, updatedPackage)

    toast.success('Package adjusted')
  },
})
```

### Remove Package from Cache

```typescript
import { metrcPackageKeys } from '@/Hooks/metrc/keys'
import { metrcQueries } from '@/Hooks/metrc/queries'

const deleteMutation = useMutation({
  mutationFn: (id: number) => axios.delete(`/metrc/packages/${id}`),
  onSuccess: (_, deletedId) => {
    // Remove from list — use queryOptions factory for typed key
    const listOpts = metrcQueries.packages(license)
    queryClient.setQueryData(
      listOpts.queryKey,
      (old: Package[]) => old?.filter(pkg => pkg.Id !== deletedId)
    )

    // Remove detail
    const detailOpts = metrcQueries.packageDetail(license, deletedId)
    queryClient.removeQueries({ queryKey: detailOpts.queryKey })

    toast.success('Package deleted')
  },
})
```

### Optimistic Update with Rollback

```typescript
import { metrcQueries } from '@/Hooks/metrc/queries'

const finishMutation = useMutation({
  mutationFn: (id: number) => axios.post(`/metrc/packages/${id}/finish`),
  onMutate: async (id) => {
    const opts = metrcQueries.packages(license)

    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: opts.queryKey })

    // Snapshot — typed via queryOptions factory
    const previous = queryClient.getQueryData(opts.queryKey)

    // Optimistic update
    queryClient.setQueryData(opts.queryKey, (old: Package[]) =>
      old.map(pkg =>
        pkg.Id === id ? { ...pkg, FinishedDate: new Date().toISOString() } : pkg
      )
    )

    return { previous }
  },
  onError: (err, id, context) => {
    // Rollback
    const opts = metrcQueries.packages(license)
    queryClient.setQueryData(opts.queryKey, context.previous)
  },
  onSettled: () => {
    // Refetch
    const opts = metrcQueries.packages(license)
    queryClient.invalidateQueries({ queryKey: opts.queryKey })
  },
})
```

### Seed Detail Cache from List

```typescript
import { metrcQueries } from '@/Hooks/metrc/queries'

function PackagesList() {
  const queryClient = useQueryClient()

  // Use queryOptions factory for typed query + cache access
  const { data: packages } = useQuery(metrcQueries.packages(license))

  // Seed detail cache for each package
  useEffect(() => {
    packages?.forEach(pkg => {
      const detailOpts = metrcQueries.packageDetail(license, pkg.Id)
      queryClient.setQueryData(detailOpts.queryKey, pkg)
    })
  }, [packages, license, queryClient])

  return <DataTable data={packages} />
}
```

### Update Multiple Queries

```typescript
// For domains with key factories, use them for typed cache access.
// For simpler domains without factories, flat kebab-case keys are fine.
const updateMutation = useMutation({
  mutationFn: (data: UpdateStrainData) =>
    axios.put(`/strains/${data.id}`, data),
  onSuccess: (updatedStrain) => {
    // Update in list — flat kebab-case key
    queryClient.setQueryData(
      ['strains', orgId],
      (old: Strain[]) =>
        old?.map(s => s.id === updatedStrain.id ? updatedStrain : s)
    )

    // Update detail
    queryClient.setQueryData(['strain-detail', updatedStrain.id], updatedStrain)

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
