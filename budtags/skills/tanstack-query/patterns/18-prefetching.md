# Pattern 18: Prefetching

## prefetchQuery

Manually fetch and cache data before it's needed:

```typescript
import { useQueryClient } from '@tanstack/react-query'

function Component() {
  const queryClient = useQueryClient()

  const handleHover = () => {
    // Prefetch on hover
    queryClient.prefetchQuery({
      queryKey: ['package', 5],
      queryFn: () => fetchPackage(5),
    })
  }

  return <button onMouseEnter={handleHover}>View Package</button>
}
```

## prefetchQuery vs ensureQueryData

### prefetchQuery
Fetches data if not in cache or stale:

```typescript
// Fetches if:
// - Not in cache, OR
// - In cache but stale
queryClient.prefetchQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})
```

### ensureQueryData
Only fetches if not in cache:

```typescript
// Only fetches if not in cache
// Uses cached data even if stale
const data = await queryClient.ensureQueryData({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})
```

## Prefetch Strategies

### 1. Hover Prefetch

```typescript
function PackageList({ packages }: { packages: Package[] }) {
  const queryClient = useQueryClient()

  const handleHover = (id: number) => {
    queryClient.prefetchQuery({
      queryKey: ['package', id],
      queryFn: () => fetchPackage(id),
      staleTime: 60 * 1000, // Don't refetch for 1 minute
    })
  }

  return (
    <div>
      {packages.map(pkg => (
        <div
          key={pkg.id}
          onMouseEnter={() => handleHover(pkg.id)}
        >
          <Link to={`/packages/${pkg.id}`}>{pkg.label}</Link>
        </div>
      ))}
    </div>
  )
}
```

### 2. Route Prefetch

```typescript
// Prefetch before navigation
const handleNavigate = async (id: number) => {
  // Prefetch package details
  await queryClient.prefetchQuery({
    queryKey: ['package', id],
    queryFn: () => fetchPackage(id),
  })

  // Then navigate
  router.visit(`/packages/${id}`)
}
```

### 3. Next Page Prefetch

```typescript
function PaginatedPackages({ page }: { page: number }) {
  const queryClient = useQueryClient()

  const { data } = useQuery({
    queryKey: ['packages', page],
    queryFn: () => fetchPackages(page),
  })

  // Prefetch next page
  useEffect(() => {
    if (data?.hasMore) {
      queryClient.prefetchQuery({
        queryKey: ['packages', page + 1],
        queryFn: () => fetchPackages(page + 1),
      })
    }
  }, [page, data, queryClient])

  return <DataTable data={data.items} />
}
```

### 4. Prefetch on Component Mount

```typescript
function Dashboard() {
  const queryClient = useQueryClient()

  useEffect(() => {
    // Prefetch data that will be needed soon
    queryClient.prefetchQuery({
      queryKey: ['packages'],
      queryFn: fetchPackages,
    })

    queryClient.prefetchQuery({
      queryKey: ['plants'],
      queryFn: fetchPlants,
    })
  }, [queryClient])

  return <div>Dashboard</div>
}
```

## Manual Cache Priming with setQueryData

Directly set cache without fetching:

```typescript
// Use list data to prime detail cache
const packages = queryClient.getQueryData(['packages'])

packages?.forEach(pkg => {
  queryClient.setQueryData(['package', pkg.id], pkg)
})
```

## BudTags Examples

### Prefetch Package Details on List Hover

```typescript
function PackagesList() {
  const queryClient = useQueryClient()
  const { user } = usePage<PageProps>().props
  const license = usePage<PageProps>().props.session.license

  const { data: packages } = useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages(license)
    },
  })

  const handleHover = (packageId: number) => {
    queryClient.prefetchQuery({
      queryKey: ['metrc', 'package', license, packageId],
      queryFn: async () => {
        const api = new MetrcApi()
        api.set_user(user)
        return api.package_by_id(license, packageId)
      },
      staleTime: 5 * 60 * 1000,
    })
  }

  return (
    <table>
      {packages?.map(pkg => (
        <tr
          key={pkg.Id}
          onMouseEnter={() => handleHover(pkg.Id)}
        >
          <td>
            <Link href={`/packages/${pkg.Id}`}>{pkg.Label}</Link>
          </td>
        </tr>
      ))}
    </table>
  )
}
```

### Prefetch Lab Results

```typescript
function PackageDetails({ packageId }: { packageId: number }) {
  const queryClient = useQueryClient()
  const { user } = usePage<PageProps>().props

  const { data: pkg } = useQuery({
    queryKey: ['package', packageId],
    queryFn: () => fetchPackage(packageId),
  })

  // Prefetch lab results when package loads
  useEffect(() => {
    if (pkg?.LabTestId) {
      queryClient.prefetchQuery({
        queryKey: ['lab', pkg.LabTestId],
        queryFn: async () => {
          const api = new ConfidentApi()
          api.set_user(user)
          return api.get_test(pkg.LabTestId)
        },
        staleTime: 10 * 60 * 1000, // Lab results rarely change
      })
    }
  }, [pkg?.LabTestId, user, queryClient])

  return <div>...</div>
}
```

### Prefetch Multiple Licenses on Org Load

```typescript
function OrganizationDashboard() {
  const queryClient = useQueryClient()
  const { user } = usePage<PageProps>().props
  const licenses = usePage<PageProps>().props.session.licenses

  useEffect(() => {
    // Prefetch all licenses' packages
    licenses.forEach(license => {
      queryClient.prefetchQuery({
        queryKey: ['metrc', 'packages', license],
        queryFn: async () => {
          const api = new MetrcApi()
          api.set_user(user)
          return api.packages(license)
        },
        staleTime: 5 * 60 * 1000,
      })
    })
  }, [licenses, user, queryClient])

  return <div>Dashboard</div>
}
```

### Prefetch Before Modal Open

```typescript
function PackageActions({ pkg }: { pkg: Package }) {
  const queryClient = useQueryClient()
  const [isOpen, setIsOpen] = useState(false)

  const handleOpenModal = async () => {
    // Prefetch additional package data before opening modal
    await queryClient.prefetchQuery({
      queryKey: ['package-history', pkg.Id],
      queryFn: () => fetchPackageHistory(pkg.Id),
    })

    setIsOpen(true)
  }

  return (
    <div>
      <button onClick={handleOpenModal}>View History</button>
      <HistoryModal isOpen={isOpen} packageId={pkg.Id} />
    </div>
  )
}
```

### Router Integration (Next.js)

```typescript
// Next.js App Router
async function PackagesPage() {
  const queryClient = getQueryClient()

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

## Prefetch Timing

### Aggressive (Hover)
```typescript
// Prefetch on hover
<Link
  onMouseEnter={() => prefetch()}
  to="/packages/5"
>
  View Package
</Link>
```

### Moderate (Focus)
```typescript
// Prefetch on focus
<Link
  onFocus={() => prefetch()}
  to="/packages/5"
>
  View Package
</Link>
```

### Conservative (Click)
```typescript
// Prefetch on click (before navigation)
const handleClick = async (e) => {
  e.preventDefault()
  await prefetch()
  router.visit('/packages/5')
}
```

## Prefetch Multiple Queries

```typescript
const prefetchAll = async () => {
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
}
```

## Next Steps
- **Initial Data** → Read `19-initial-placeholder-data.md`
- **SSR** → Read `25-ssr-hydration.md`
- **Cache Updates** → Read `20-cache-updates.md`
