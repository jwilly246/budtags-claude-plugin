# Pattern 8: Parallel Queries

## Multiple useQuery Calls

The simplest way to fetch multiple queries in parallel:

```typescript
function Dashboard() {
  const packagesQuery = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  const plantsQuery = useQuery({
    queryKey: ['plants'],
    queryFn: fetchPlants,
  })

  const harvestsQuery = useQuery({
    queryKey: ['harvests'],
    queryFn: fetchHarvests,
  })

  // All queries execute in parallel automatically
  if (packagesQuery.isLoading || plantsQuery.isLoading || harvestsQuery.isLoading) {
    return <Spinner />
  }

  return (
    <div>
      <PackagesSummary data={packagesQuery.data} />
      <PlantsSummary data={plantsQuery.data} />
      <HarvestsSummary data={harvestsQuery.data} />
    </div>
  )
}
```

## useQueries for Dynamic Parallel Queries

When the number of queries is dynamic or comes from an array:

```typescript
import { useQueries } from '@tanstack/react-query'

function UserProfiles({ userIds }: { userIds: number[] }) {
  const queries = useQueries({
    queries: userIds.map(id => ({
      queryKey: ['user', id],
      queryFn: () => fetchUser(id),
      staleTime: 5 * 60 * 1000,
    })),
  })

  // queries is an array of query results
  const isLoading = queries.some(q => q.isLoading)
  const hasError = queries.some(q => q.isError)

  if (isLoading) return <Spinner />
  if (hasError) return <ErrorMessage />

  return (
    <div>
      {queries.map((query, i) => (
        <UserCard key={userIds[i]} user={query.data} />
      ))}
    </div>
  )
}
```

### Combining Results

```typescript
function MultiLicenseData({ licenses }: { licenses: string[] }) {
  const queries = useQueries({
    queries: licenses.map(license => ({
      queryKey: ['packages', license],
      queryFn: () => fetchPackages(license),
    })),
  })

  // Combine all results
  const allPackages = queries
    .filter(q => q.isSuccess)
    .flatMap(q => q.data ?? [])

  const totalCount = allPackages.length

  return (
    <div>
      <h2>Total Packages Across All Licenses: {totalCount}</h2>
      <DataTable data={allPackages} />
    </div>
  )
}
```

## Suspense Mode

When using React Suspense, all queries must succeed before rendering:

```typescript
function Dashboard() {
  const packagesQuery = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
    suspense: true,
  })

  const plantsQuery = useQuery({
    queryKey: ['plants'],
    queryFn: fetchPlants,
    suspense: true,
  })

  // No loading checks needed - Suspense handles it
  return (
    <div>
      <PackagesSummary data={packagesQuery.data} />
      <PlantsSummary data={plantsQuery.data} />
    </div>
  )
}

// Parent component
function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <Dashboard />
    </Suspense>
  )
}
```

## BudTags Examples

### Metrc Dashboard

```typescript
function MetrcDashboard() {
  const { user } = usePage<PageProps>().props
  const license = usePage<PageProps>().props.session.license

  // Parallel queries for all Metrc data
  const packagesQuery = useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages(license)
    },
  })

  const plantsQuery = useQuery({
    queryKey: ['metrc', 'plants', license],
    queryFn: () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.plants(license)
    },
  })

  const harvestsQuery = useQuery({
    queryKey: ['metrc', 'harvests', license],
    queryFn: () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.harvests(license)
    },
  })

  const locationsQuery = useQuery({
    queryKey: ['metrc', 'locations', license],
    queryFn: () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.locations(license)
    },
  })

  const isLoading =
    packagesQuery.isLoading ||
    plantsQuery.isLoading ||
    harvestsQuery.isLoading ||
    locationsQuery.isLoading

  if (isLoading) return <Spinner />

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <StatCard
        title="Packages"
        count={packagesQuery.data?.length ?? 0}
        icon={<PackageIcon />}
      />
      <StatCard
        title="Plants"
        count={plantsQuery.data?.length ?? 0}
        icon={<PlantIcon />}
      />
      <StatCard
        title="Harvests"
        count={harvestsQuery.data?.length ?? 0}
        icon={<HarvestIcon />}
      />
      <StatCard
        title="Locations"
        count={locationsQuery.data?.length ?? 0}
        icon={<LocationIcon />}
      />
    </div>
  )
}
```

### Multi-License Comparison

```typescript
function MultiLicenseComparison() {
  const { user } = usePage<PageProps>().props
  const licenses = usePage<PageProps>().props.session.licenses // Array of licenses

  const queries = useQueries({
    queries: licenses.map(license => ({
      queryKey: ['metrc', 'packages', license],
      queryFn: async () => {
        const api = new MetrcApi()
        api.set_user(user)
        return api.packages(license)
      },
      staleTime: 5 * 60 * 1000,
    })),
  })

  const isLoading = queries.some(q => q.isLoading)

  if (isLoading) return <Spinner />

  return (
    <div>
      {queries.map((query, i) => (
        <div key={licenses[i]}>
          <h3>{licenses[i]}</h3>
          <p>Packages: {query.data?.length ?? 0}</p>
        </div>
      ))}
    </div>
  )
}
```

### Combined Organization Data

```typescript
function OrganizationOverview() {
  const { user } = usePage<PageProps>().props
  const orgId = user.active_org.id

  // Parallel queries for org data
  const strainsQuery = useQuery({
    queryKey: ['strains', orgId],
    queryFn: () => axios.get(`/api/orgs/${orgId}/strains`).then(r => r.data),
  })

  const usersQuery = useQuery({
    queryKey: ['users', orgId],
    queryFn: () => axios.get(`/api/orgs/${orgId}/users`).then(r => r.data),
  })

  const labelsQuery = useQuery({
    queryKey: ['labels', orgId],
    queryFn: () => axios.get(`/api/orgs/${orgId}/labels`).then(r => r.data),
  })

  const secretsQuery = useQuery({
    queryKey: ['secrets', orgId],
    queryFn: () => axios.get(`/api/orgs/${orgId}/secrets`).then(r => r.data),
  })

  const isLoading =
    strainsQuery.isLoading ||
    usersQuery.isLoading ||
    labelsQuery.isLoading ||
    secretsQuery.isLoading

  if (isLoading) return <Spinner />

  return (
    <div className="grid grid-cols-2 gap-4">
      <div>Strains: {strainsQuery.data.length}</div>
      <div>Users: {usersQuery.data.length}</div>
      <div>Labels: {labelsQuery.data.length}</div>
      <div>API Keys: {secretsQuery.data.length}</div>
    </div>
  )
}
```

## useQueries with combine

Combine results into a single data structure:

```typescript
const result = useQueries({
  queries: [
    { queryKey: ['packages'], queryFn: fetchPackages },
    { queryKey: ['plants'], queryFn: fetchPlants },
  ],
  combine: (results) => ({
    data: {
      packages: results[0].data,
      plants: results[1].data,
    },
    isLoading: results.some(r => r.isLoading),
  }),
})

// result.data = { packages: Package[], plants: Plant[] }
// result.isLoading = boolean
```

## Performance Considerations

### Request Waterfall vs Parallel

```typescript
// ❌ BAD - Sequential (waterfall)
const user = useQuery({ queryKey: ['user'], queryFn: fetchUser })
const org = useQuery({
  queryKey: ['org', user.data?.orgId],
  queryFn: () => fetchOrg(user.data?.orgId),
  enabled: !!user.data?.orgId,
})

// ✅ GOOD - Parallel (if IDs are known)
const user = useQuery({ queryKey: ['user'], queryFn: fetchUser })
const org = useQuery({ queryKey: ['org', orgId], queryFn: () => fetchOrg(orgId) })
```

## Next Steps
- **Dependent Queries** → Read `09-dependent-queries.md`
- **Prefetching** → Read `18-prefetching.md`
- **Performance** → Read `22-render-optimizations.md`
