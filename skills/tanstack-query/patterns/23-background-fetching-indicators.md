# Pattern 23: Background Fetching Indicators

## isFetching vs isPending

### isPending
Query has no data yet (first load):

```typescript
const { isPending, data } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})

// isPending === true → No data, first fetch
// isPending === false → Has data (may be stale)
```

### isFetching
Query function is executing:

```typescript
const { isFetching, data } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})

// isFetching === true → Fetching (initial or background)
// isFetching === false → Not fetching
```

## State Combinations

```typescript
// Initial load
isPending: true, isFetching: true, data: undefined

// Background refetch
isPending: false, isFetching: true, data: Package[]

// Success (idle)
isPending: false, isFetching: false, data: Package[]
```

## Background Refetch Indicator

Show subtle indicator during background refetch:

```typescript
function Packages() {
  const { data, isFetching } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  return (
    <div>
      {isFetching && (
        <div className="absolute top-2 right-2">
          <RefreshIcon className="animate-spin" />
        </div>
      )}
      <DataTable data={data} />
    </div>
  )
}
```

## Global Fetching Indicator

Show indicator when ANY query is fetching:

```typescript
import { useIsFetching } from '@tanstack/react-query'

function GlobalLoadingIndicator() {
  const isFetching = useIsFetching()

  if (!isFetching) return null

  return (
    <div className="fixed top-0 left-0 right-0 h-1 bg-blue-500 animate-pulse" />
  )
}
```

### With Query Filters

```typescript
// Only show for specific queries
const isMetrcFetching = useIsFetching({ queryKey: ['metrc'] })

// Only show for package queries
const isPackagesFetching = useIsFetching({ queryKey: ['packages'] })
```

## BudTags Examples

### Metrc Packages with Refresh Indicator

```typescript
function MetrcPackages() {
  const { user } = usePage<PageProps>().props
  const license = usePage<PageProps>().props.session.license

  const {
    data: packages,
    isLoading,
    isFetching,
  } = useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages(license)
    },
    refetchOnWindowFocus: true, // Enable background refetch
  })

  if (isLoading) {
    return <Spinner />
  }

  return (
    <BoxMain>
      {/* Background refetch indicator */}
      {isFetching && (
        <div className="absolute top-2 right-2">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
            <span>Refreshing...</span>
          </div>
        </div>
      )}

      <DataTable data={packages} />
    </BoxMain>
  )
}
```

### Global Metrc Loading Bar

```typescript
function MetrcLoadingBar() {
  const isFetching = useIsFetching({ queryKey: ['metrc'] })

  if (!isFetching) return null

  return (
    <div className="fixed top-0 left-0 right-0 h-1 z-50">
      <div className="h-full bg-blue-600 animate-pulse" />
    </div>
  )
}

// In main layout
function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <MetrcLoadingBar />
      <Header />
      {children}
    </div>
  )
}
```

### Opacity During Refetch

```typescript
function Packages() {
  const { data, isFetching } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  return (
    <div className={isFetching ? 'opacity-50 transition-opacity' : ''}>
      <DataTable data={data} />
    </div>
  )
}
```

### Status Badge

```typescript
function PackagesSyncStatus() {
  const isFetching = useIsFetching({ queryKey: ['metrc', 'packages'] })

  return (
    <div className="flex items-center gap-2">
      <div
        className={`w-2 h-2 rounded-full ${
          isFetching ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'
        }`}
      />
      <span className="text-sm text-gray-600">
        {isFetching ? 'Syncing...' : 'Synced'}
      </span>
    </div>
  )
}
```

### Disabled Actions During Refetch

```typescript
function PackageActions({ pkg }: { pkg: Package }) {
  const isFetching = useIsFetching({
    queryKey: ['metrc', 'packages'],
  })

  return (
    <div>
      <button
        disabled={isFetching}
        onClick={() => handleFinish(pkg.Id)}
      >
        Finish Package
      </button>
    </div>
  )
}
```

### Progress Bar

```typescript
function ProgressBar() {
  const isFetching = useIsFetching()
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (isFetching) {
      // Simulate progress
      const interval = setInterval(() => {
        setProgress(old => Math.min(old + 10, 90))
      }, 100)

      return () => clearInterval(interval)
    } else {
      // Complete
      setProgress(100)
      setTimeout(() => setProgress(0), 300)
    }
  }, [isFetching])

  if (progress === 0) return null

  return (
    <div className="fixed top-0 left-0 right-0 h-1 bg-gray-200">
      <div
        className="h-full bg-blue-600 transition-all"
        style={{ width: `${progress}%` }}
      />
    </div>
  )
}
```

## Pagination Loading States

```typescript
function PaginatedPackages({ page }: { page: number }) {
  const { data, isLoading, isFetching, isPlaceholderData } = useQuery({
    queryKey: ['packages', page],
    queryFn: () => fetchPackages(page),
    placeholderData: (previousData) => previousData,
  })

  return (
    <div>
      {/* Initial load */}
      {isLoading && <Spinner />}

      {/* Page navigation */}
      <div>
        <button disabled={isPlaceholderData}>
          Previous
        </button>

        {/* Background fetch indicator for new page */}
        {isFetching && !isLoading && (
          <span className="ml-2 text-sm text-gray-500">
            Loading page {page}...
          </span>
        )}

        <button disabled={isPlaceholderData}>
          Next
        </button>
      </div>

      {/* Show old data with reduced opacity while loading new page */}
      <div className={isPlaceholderData ? 'opacity-50' : ''}>
        <DataTable data={data?.items} />
      </div>
    </div>
  )
}
```

## Query-Specific Indicators

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

  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <h2>
          Packages
          {packagesQuery.isFetching && <RefreshIcon />}
        </h2>
        <DataTable data={packagesQuery.data} />
      </div>

      <div>
        <h2>
          Plants
          {plantsQuery.isFetching && <RefreshIcon />}
        </h2>
        <DataTable data={plantsQuery.data} />
      </div>
    </div>
  )
}
```

## Manual Refetch Button

```typescript
function RefreshButton() {
  const queryClient = useQueryClient()
  const isFetching = useIsFetching({ queryKey: ['packages'] })

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['packages'] })
  }

  return (
    <button
      onClick={handleRefresh}
      disabled={isFetching}
      className="flex items-center gap-2"
    >
      <RefreshIcon className={isFetching ? 'animate-spin' : ''} />
      {isFetching ? 'Refreshing...' : 'Refresh'}
    </button>
  )
}
```

## Next Steps
- **Core Concepts** → Read `02-core-concepts.md`
- **Query States** → Read `07-basic-queries.md`
- **Network Mode** → Read `24-network-mode.md`
