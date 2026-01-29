# Pattern 9: Dependent Queries

## Serial Queries with enabled

Use the `enabled` option to make queries depend on previous results:

```typescript
function Package({ packageId }: { packageId: number }) {
  // Query 1: Get package
  const packageQuery = useQuery({
    queryKey: ['package', packageId],
    queryFn: () => fetchPackage(packageId),
  })

  // Query 2: Get lab results (depends on package data)
  const labQuery = useQuery({
    queryKey: ['lab', packageQuery.data?.LabTestId],
    queryFn: () => fetchLabResults(packageQuery.data!.LabTestId),
    enabled: !!packageQuery.data?.LabTestId, // Only run if LabTestId exists
  })

  if (packageQuery.isLoading) return <Spinner />
  if (labQuery.isLoading) return <div>Loading lab results...</div>

  return (
    <div>
      <PackageDetails pkg={packageQuery.data} />
      {labQuery.data && <LabResults results={labQuery.data} />}
    </div>
  )
}
```

## State Transitions

When `enabled: false`, the query goes to `idle` state:

```typescript
const query = useQuery({
  queryKey: ['data'],
  queryFn: fetchData,
  enabled: false,
})

// Initial state
query.status === 'pending'
query.fetchStatus === 'idle'  // ← Not fetching

// After enabled becomes true
query.status === 'pending'
query.fetchStatus === 'fetching'
```

## Multiple Dependencies

```typescript
function UserDashboard({ userId }: { userId: number }) {
  const userQuery = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  })

  const orgId = userQuery.data?.activeOrgId

  // Depends on user data
  const orgQuery = useQuery({
    queryKey: ['org', orgId],
    queryFn: () => fetchOrg(orgId!),
    enabled: !!orgId,
  })

  const license = orgQuery.data?.defaultLicense

  // Depends on org data
  const packagesQuery = useQuery({
    queryKey: ['packages', license],
    queryFn: () => fetchPackages(license!),
    enabled: !!license,
  })

  // All 3 queries run in sequence (waterfall)
  // User → Org → Packages
}
```

## Real-World Examples

### Package with Lab Results

```typescript
function PackageDetails({
  packageId,
  userId,
  license,
}: {
  packageId: number
  userId: string
  license: string
}) {
  // Get package details
  const packageQuery = useQuery({
    queryKey: ['package', license, packageId],
    queryFn: async () => {
      const response = await fetch(`/api/packages/${packageId}?license=${license}`)
      return response.json()
    },
  })

  const labTestId = packageQuery.data?.LabTestId

  // Get lab results (only if package has lab test)
  const labQuery = useQuery({
    queryKey: ['lab', labTestId],
    queryFn: async () => {
      const response = await fetch(`/api/lab-results/${labTestId}`)
      return response.json()
    },
    enabled: !!labTestId,
    staleTime: 10 * 60 * 1000, // Lab results rarely change
  })

  if (packageQuery.isLoading) return <Spinner />

  return (
    <div>
      <PackageInfo pkg={packageQuery.data} />

      {labTestId && (
        <div className="mt-4">
          {labQuery.isLoading && <div>Loading lab results...</div>}
          {labQuery.data && <LabResultsTable data={labQuery.data} />}
        </div>
      )}
    </div>
  )
}
```

### User Profile → Organization → Secrets

```typescript
function OrganizationSecrets({
  userId,
  orgId,
  hasPermission,
}: {
  userId: string
  orgId: number
  hasPermission: boolean
}) {
  // Fetch org details
  const orgQuery = useQuery({
    queryKey: ['org', orgId],
    queryFn: () => axios.get(`/api/orgs/${orgId}`).then(r => r.data),
  })

  // Only fetch secrets if user has permission
  const secretsQuery = useQuery({
    queryKey: ['secrets', orgId],
    queryFn: () =>
      axios.get(`/api/orgs/${orgId}/secrets`).then(r => r.data),
    enabled: hasPermission,
  })

  if (!hasPermission) {
    return <div>You don't have permission to view secrets</div>
  }

  if (secretsQuery.isLoading) return <Spinner />

  return <SecretsList secrets={secretsQuery.data} />
}
```

### Strain → Strain Images

```typescript
function StrainGallery({
  strainId,
  orgId,
}: {
  strainId: number
  orgId: number
}) {
  const strainQuery = useQuery({
    queryKey: ['strain', orgId, strainId],
    queryFn: () => axios.get(`/api/strains/${strainId}`).then(r => r.data),
  })

  const hasImages = (strainQuery.data?.image_count ?? 0) > 0

  const imagesQuery = useQuery({
    queryKey: ['strain-images', strainId],
    queryFn: () => axios.get(`/api/strains/${strainId}/images`).then(r => r.data),
    enabled: hasImages, // Only fetch if strain has images
  })

  if (strainQuery.isLoading) return <Spinner />

  return (
    <div>
      <StrainHeader strain={strainQuery.data} />

      {hasImages && (
        <div className="mt-4">
          {imagesQuery.isLoading ? (
            <div>Loading images...</div>
          ) : (
            <ImageGallery images={imagesQuery.data} />
          )}
        </div>
      )}
    </div>
  )
}
```

## Manual Refetch for Disabled Queries

Even when `enabled: false`, you can manually trigger a query:

```typescript
const query = useQuery({
  queryKey: ['data'],
  queryFn: fetchData,
  enabled: false,
})

// Later, manually fetch
<button onClick={() => query.refetch()}>
  Load Data
</button>
```

## Avoiding Request Waterfalls

### ❌ Bad: Sequential Dependencies

```typescript
// Takes 3 seconds total (1s + 1s + 1s)
const user = useQuery({ ... })       // 1 second
const org = useQuery({ ..., enabled: !!user.data })  // 1 second (waits for user)
const data = useQuery({ ..., enabled: !!org.data })  // 1 second (waits for org)
```

### ✅ Good: Parallel When Possible

```typescript
// Takes 1 second total (all parallel)
const user = useQuery({ ... })
const org = useQuery({ ..., queryKey: ['org', orgId] })  // Don't wait if orgId is known
const data = useQuery({ ..., queryKey: ['data', license] })  // Don't wait if license is known
```

**Rule:** Only use `enabled` when you truly need data from a previous query.

## skipToken for TypeScript

TypeScript helper to skip queries safely:

```typescript
import { skipToken } from '@tanstack/react-query'

function Package({ packageId }: { packageId: number | undefined }) {
  const query = useQuery({
    queryKey: ['package', packageId],
    queryFn: packageId ? () => fetchPackage(packageId) : skipToken,
  })

  // TypeScript knows query.data is Package | undefined
}
```

## Lazy Queries (User-Triggered)

```typescript
function Search() {
  const [query, setQuery] = useState('')

  const searchQuery = useQuery({
    queryKey: ['search', query],
    queryFn: () => search(query),
    enabled: false, // Don't run automatically
  })

  const handleSearch = () => {
    if (query.length > 0) {
      searchQuery.refetch()
    }
  }

  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <button onClick={handleSearch}>Search</button>

      {searchQuery.isFetching && <div>Searching...</div>}
      {searchQuery.data && <Results data={searchQuery.data} />}
    </div>
  )
}
```

## Next Steps
- **Query Options** → Read `11-query-options.md`
- **Prefetching** → Read `18-prefetching.md`
- **Performance** → Read `22-render-optimizations.md`
