# Pattern 12: Disabling & Pausing Queries

## enabled: false

Disable a query from running automatically:

```typescript
const query = useQuery({
  queryKey: ['data'],
  queryFn: fetchData,
  enabled: false, // ← Query will not run automatically
})

// Query state when disabled:
query.status === 'pending'
query.fetchStatus === 'idle'  // Not fetching
query.data === undefined
```

## Lazy Queries

Queries that only run when manually triggered:

```typescript
function Search() {
  const [searchTerm, setSearchTerm] = useState('')

  const searchQuery = useQuery({
    queryKey: ['search', searchTerm],
    queryFn: () => search(searchTerm),
    enabled: false, // Don't run automatically
  })

  const handleSearch = () => {
    searchQuery.refetch()
  }

  return (
    <div>
      <input
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      <button onClick={handleSearch}>Search</button>

      {searchQuery.isFetching && <div>Searching...</div>}
      {searchQuery.data && <Results data={searchQuery.data} />}
    </div>
  )
}
```

## Conditional Queries

Enable queries based on dependencies:

```typescript
function Package({ packageId }: { packageId: number | undefined }) {
  const query = useQuery({
    queryKey: ['package', packageId],
    queryFn: () => fetchPackage(packageId!),
    enabled: !!packageId, // Only run if packageId exists
  })

  // When packageId is undefined:
  // - Query doesn't run
  // - status: 'pending', fetchStatus: 'idle'

  // When packageId becomes defined:
  // - Query automatically runs
}
```

## skipToken for TypeScript

Type-safe way to skip queries:

```typescript
import { skipToken } from '@tanstack/react-query'

function Package({ packageId }: { packageId: number | undefined }) {
  const query = useQuery({
    queryKey: ['package', packageId],
    queryFn: packageId !== undefined
      ? () => fetchPackage(packageId)
      : skipToken, // ← Type-safe skip
  })

  // TypeScript knows query.data is Package | undefined
}
```

## Behavior When Disabled

### Invalidation is Ignored

```typescript
const query = useQuery({
  queryKey: ['data'],
  queryFn: fetchData,
  enabled: false,
})

// This does NOT trigger a refetch
queryClient.invalidateQueries({ queryKey: ['data'] })

// Manual refetch still works
query.refetch()
```

### No Automatic Refetching

```typescript
const query = useQuery({
  queryKey: ['data'],
  queryFn: fetchData,
  enabled: false,
})

// These events don't trigger refetch when disabled:
// - Component mount
// - Window focus
// - Network reconnect
```

## Manual Refetch

Even when disabled, you can manually refetch:

```typescript
const query = useQuery({
  queryKey: ['data'],
  queryFn: fetchData,
  enabled: false,
})

// Manually trigger
<button onClick={() => query.refetch()}>
  Load Data
</button>

// With async/await
const handleLoad = async () => {
  await query.refetch()
  toast.success('Data loaded')
}
```

## BudTags Examples

### Permission-Based Query

```typescript
function OrganizationSecrets() {
  const { user } = usePage<PageProps>().props
  const hasPermission = user.permissions.includes('edit-secrets')

  const secretsQuery = useQuery({
    queryKey: ['secrets', user.active_org.id],
    queryFn: () =>
      axios.get(`/api/orgs/${user.active_org.id}/secrets`).then(r => r.data),
    enabled: hasPermission, // Only run if user has permission
  })

  if (!hasPermission) {
    return <div>You don't have permission to view secrets</div>
  }

  if (secretsQuery.isLoading) return <Spinner />

  return <SecretsList secrets={secretsQuery.data} />
}
```

### License-Specific Plant Query

```typescript
function MetrcPlants() {
  const { user } = usePage<PageProps>().props
  const license = usePage<PageProps>().props.session.license

  // Only cultivation licenses can access plants
  const isCultivation = license?.startsWith('au-c-')

  const plantsQuery = useQuery({
    queryKey: ['metrc', 'plants', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.plants(license!)
    },
    enabled: isCultivation, // Only run for cultivation licenses
  })

  if (!isCultivation) {
    return (
      <div>Plants are only available for cultivation licenses</div>
    )
  }

  if (plantsQuery.isLoading) return <Spinner />

  return <PlantsTable data={plantsQuery.data} />
}
```

### Modal with Lazy Loading

```typescript
function PackageDetailsModal({ isOpen, packageId }: Props) {
  const query = useQuery({
    queryKey: ['package', packageId],
    queryFn: () => fetchPackage(packageId),
    enabled: isOpen, // Only fetch when modal is open
  })

  return (
    <Modal show={isOpen} onClose={onClose}>
      {query.isLoading && <Spinner />}
      {query.data && <PackageDetails pkg={query.data} />}
    </Modal>
  )
}
```

### Filter Form

```typescript
function FilteredPackages() {
  const [filters, setFilters] = useState({
    status: '',
    location: '',
  })
  const [applied, setApplied] = useState(false)

  const packagesQuery = useQuery({
    queryKey: ['packages', filters],
    queryFn: () => fetchPackages(filters),
    enabled: applied, // Only run when user applies filters
  })

  const handleApplyFilters = () => {
    setApplied(true)
  }

  return (
    <div>
      <FilterForm value={filters} onChange={setFilters} />
      <button onClick={handleApplyFilters}>Apply Filters</button>

      {packagesQuery.isFetching && <Spinner />}
      {packagesQuery.data && <DataTable data={packagesQuery.data} />}
    </div>
  )
}
```

### Data Source Toggle

```typescript
function Inventory({ dataSource }: { dataSource: 'packages' | 'plants' }) {
  const { user } = usePage<PageProps>().props
  const license = usePage<PageProps>().props.session.license

  const packagesQuery = useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages(license)
    },
    enabled: dataSource === 'packages',
  })

  const plantsQuery = useQuery({
    queryKey: ['metrc', 'plants', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.plants(license)
    },
    enabled: dataSource === 'plants',
  })

  if (dataSource === 'packages') {
    if (packagesQuery.isLoading) return <Spinner />
    return <PackagesTable data={packagesQuery.data} />
  }

  if (dataSource === 'plants') {
    if (plantsQuery.isLoading) return <Spinner />
    return <PlantsTable data={plantsQuery.data} />
  }
}
```

## Toggling enabled

```typescript
function ToggleableQuery() {
  const [enabled, setEnabled] = useState(false)

  const query = useQuery({
    queryKey: ['data'],
    queryFn: fetchData,
    enabled,
  })

  return (
    <div>
      <button onClick={() => setEnabled(!enabled)}>
        {enabled ? 'Disable' : 'Enable'} Query
      </button>

      {query.isFetching && <div>Loading...</div>}
      {query.data && <div>Data: {query.data}</div>}
    </div>
  )
}
```

## Permanently Disabled Queries

```typescript
// Query that never runs automatically
const query = useQuery({
  queryKey: ['manual-data'],
  queryFn: fetchData,
  enabled: false,
  staleTime: Infinity, // Never becomes stale
})

// Only way to fetch is manual refetch
<button onClick={() => query.refetch()}>
  Fetch Data
</button>
```

## Next Steps
- **Dependent Queries** → Read `09-dependent-queries.md`
- **Query Options** → Read `11-query-options.md`
- **TypeScript** → Read `06-typescript.md`
