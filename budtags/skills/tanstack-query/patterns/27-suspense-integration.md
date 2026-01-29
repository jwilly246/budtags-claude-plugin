# Pattern 27: Suspense Integration

## React Suspense Overview

React Suspense allows components to "wait" for asynchronous operations (like data fetching) and show fallback UI while waiting.

TanStack Query v5 provides first-class Suspense support with:

- **useSuspenseQuery** - Suspense version of useQuery
- **useSuspenseInfiniteQuery** - Suspense version of useInfiniteQuery
- **Type Safety** - Data is never undefined (no loading states needed)

## useSuspenseQuery vs useQuery

### Traditional useQuery

```typescript
function PackagesList() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  if (isLoading) return <LoadingSkeleton />
  if (isError) return <div>Error: {error.message}</div>

  return <DataTable data={data} /> // data might be undefined
}
```

### useSuspenseQuery

```typescript
import { useSuspenseQuery } from '@tanstack/react-query'

function PackagesList() {
  // No isLoading, isError - those are handled by Suspense + ErrorBoundary
  const { data } = useSuspenseQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  // data is NEVER undefined - TypeScript knows this!
  return <DataTable data={data} />
}

// Parent component provides Suspense + ErrorBoundary
function PackagesPage() {
  return (
    <ErrorBoundary fallback={<div>Failed to load packages</div>}>
      <Suspense fallback={<LoadingSkeleton />}>
        <PackagesList />
      </Suspense>
    </ErrorBoundary>
  )
}
```

## useSuspenseQuery Hook

### Basic Usage

```typescript
import { Suspense } from 'react'
import { useSuspenseQuery } from '@tanstack/react-query'

function User({ userId }: { userId: number }) {
  const { data: user } = useSuspenseQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  })

  // user is guaranteed to exist (not undefined)
  return <div>{user.name}</div>
}

function App() {
  return (
    <Suspense fallback={<div>Loading user...</div>}>
      <User userId={1} />
    </Suspense>
  )
}
```

### Type Safety Benefits

```typescript
// ❌ useQuery - data might be undefined
const { data } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})
data?.map(pkg => pkg.Label) // Need optional chaining

// ✅ useSuspenseQuery - data is NEVER undefined
const { data } = useSuspenseQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})
data.map(pkg => pkg.Label) // No optional chaining needed!
```

### Multiple Suspense Queries

All queries must resolve before rendering:

```typescript
function Dashboard() {
  const { data: packages } = useSuspenseQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  const { data: facilities } = useSuspenseQuery({
    queryKey: ['facilities'],
    queryFn: fetchFacilities,
  })

  const { data: strains } = useSuspenseQuery({
    queryKey: ['strains'],
    queryFn: fetchStrains,
  })

  // All data is guaranteed to exist
  return (
    <div>
      <h2>{packages.length} Packages</h2>
      <h2>{facilities.length} Facilities</h2>
      <h2>{strains.length} Strains</h2>
    </div>
  )
}

function App() {
  return (
    <Suspense fallback={<DashboardSkeleton />}>
      <Dashboard />
    </Suspense>
  )
}
```

## useSuspenseInfiniteQuery

### Infinite Scroll with Suspense

```typescript
import { useSuspenseInfiniteQuery } from '@tanstack/react-query'

function PackagesList() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useSuspenseInfiniteQuery({
    queryKey: ['packages'],
    queryFn: ({ pageParam }) => fetchPackages({ cursor: pageParam }),
    initialPageParam: 0,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  })

  // data.pages is guaranteed to exist
  const allPackages = data.pages.flatMap(page => page.packages)

  return (
    <div>
      {allPackages.map(pkg => (
        <PackageCard key={pkg.Id} package={pkg} />
      ))}

      {hasNextPage && (
        <button onClick={() => fetchNextPage()} disabled={isFetchingNextPage}>
          {isFetchingNextPage ? 'Loading more...' : 'Load More'}
        </button>
      )}
    </div>
  )
}

function App() {
  return (
    <Suspense fallback={<div>Loading packages...</div>}>
      <PackagesList />
    </Suspense>
  )
}
```

## Error Boundaries

### Basic Error Boundary

Catch errors from Suspense queries:

```typescript
import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="error-container">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
        </div>
      )
    }

    return this.props.children
  }
}

// Usage
<ErrorBoundary fallback={<div>Failed to load</div>}>
  <Suspense fallback={<div>Loading...</div>}>
    <PackagesList />
  </Suspense>
</ErrorBoundary>
```

### Error Boundary with Reset

```typescript
import { useQueryErrorResetBoundary } from '@tanstack/react-query'
import { ErrorBoundary as ReactErrorBoundary } from 'react-error-boundary'

function App() {
  const { reset } = useQueryErrorResetBoundary()

  return (
    <ReactErrorBoundary
      onReset={reset}
      fallbackRender={({ error, resetErrorBoundary }) => (
        <div>
          <h2>Error loading data</h2>
          <pre>{error.message}</pre>
          <button onClick={resetErrorBoundary}>Try Again</button>
        </div>
      )}
    >
      <Suspense fallback={<div>Loading...</div>}>
        <PackagesList />
      </Suspense>
    </ReactErrorBoundary>
  )
}
```

### Nested Error Boundaries

Granular error handling for different sections:

```typescript
function Dashboard() {
  const { reset } = useQueryErrorResetBoundary()

  return (
    <div className="grid grid-cols-3 gap-4">
      {/* Sidebar can fail independently */}
      <ReactErrorBoundary
        onReset={reset}
        fallback={<div>Sidebar failed to load</div>}
      >
        <Suspense fallback={<SidebarSkeleton />}>
          <Sidebar />
        </Suspense>
      </ReactErrorBoundary>

      {/* Main content can fail independently */}
      <ReactErrorBoundary
        onReset={reset}
        fallback={<div>Content failed to load</div>}
      >
        <Suspense fallback={<ContentSkeleton />}>
          <MainContent />
        </Suspense>
      </ReactErrorBoundary>

      {/* Stats can fail independently */}
      <ReactErrorBoundary
        onReset={reset}
        fallback={<div>Stats failed to load</div>}
      >
        <Suspense fallback={<StatsSkeleton />}>
          <Stats />
        </Suspense>
      </ReactErrorBoundary>
    </div>
  )
}
```

## Nested Suspense Boundaries

### Sequential Loading

Show parts of UI as they load:

```typescript
function PackageDetails({ packageId }: { packageId: number }) {
  return (
    <div>
      {/* Show package info first */}
      <Suspense fallback={<PackageSkeleton />}>
        <PackageInfo packageId={packageId} />

        {/* Show lab results after package loads */}
        <Suspense fallback={<LabResultsSkeleton />}>
          <LabResults packageId={packageId} />
        </Suspense>
      </Suspense>
    </div>
  )
}

function PackageInfo({ packageId }: { packageId: number }) {
  const { data: pkg } = useSuspenseQuery({
    queryKey: ['package', packageId],
    queryFn: () => fetchPackage(packageId),
  })

  return <div>{pkg.Label}</div>
}

function LabResults({ packageId }: { packageId: number }) {
  const { data: results } = useSuspenseQuery({
    queryKey: ['lab-results', packageId],
    queryFn: () => fetchLabResults(packageId),
  })

  return <div>{results.length} lab results</div>
}
```

### Parallel Loading

Wait for all sections to load:

```typescript
function Dashboard() {
  return (
    <Suspense fallback={<FullPageSkeleton />}>
      <div className="grid grid-cols-3">
        <Sidebar />
        <MainContent />
        <StatsPanel />
      </div>
    </Suspense>
  )
}

// All three components use useSuspenseQuery
// UI shows <FullPageSkeleton /> until ALL queries resolve
```

## BudTags Examples

### Metrc Packages with Suspense

```typescript
function PackagesPage() {
  const { reset } = useQueryErrorResetBoundary()
  const license = usePage<PageProps>().props.session.license

  return (
    <MainLayout>
      <div className="container mx-auto py-6">
        <h1 className="text-2xl font-bold mb-4">Packages</h1>

        <ErrorBoundary
          onReset={reset}
          fallbackRender={({ error, resetErrorBoundary }) => (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <h3 className="text-red-800 font-medium">
                Failed to load packages
              </h3>
              <p className="text-red-600 text-sm mt-1">{error.message}</p>
              <button
                onClick={resetErrorBoundary}
                className="mt-3 px-4 py-2 bg-red-100 text-red-800 rounded hover:bg-red-200"
              >
                Try Again
              </button>
            </div>
          )}
        >
          <Suspense fallback={<PackageTableSkeleton />}>
            <PackagesTable license={license} />
          </Suspense>
        </ErrorBoundary>
      </div>
    </MainLayout>
  )
}

function PackagesTable({ license }: { license: string }) {
  const { user } = usePage<PageProps>().props

  const { data: packages } = useSuspenseQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages(license, 'active')
    },
    staleTime: 30 * 1000,
  })

  return <DataTable data={packages} />
}

function PackageTableSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-10 bg-gray-200 rounded mb-4"></div>
      <div className="h-96 bg-gray-100 rounded"></div>
    </div>
  )
}
```

### Organization-Scoped Data with Suspense

```typescript
function OrganizationDashboard() {
  const { user } = usePage<PageProps>().props
  const orgId = user.active_org.id

  return (
    <div>
      <h1>{user.active_org.name} Dashboard</h1>

      <ErrorBoundary fallback={<div>Failed to load dashboard</div>}>
        <Suspense fallback={<DashboardSkeleton />}>
          <DashboardContent orgId={orgId} />
        </Suspense>
      </ErrorBoundary>
    </div>
  )
}

function DashboardContent({ orgId }: { orgId: number }) {
  const { data: labels } = useSuspenseQuery({
    queryKey: ['org', orgId, 'labels'],
    queryFn: () => axios.get(`/api/org/${orgId}/labels`).then(r => r.data),
  })

  const { data: templates } = useSuspenseQuery({
    queryKey: ['org', orgId, 'templates'],
    queryFn: () => axios.get(`/api/org/${orgId}/templates`).then(r => r.data),
  })

  const { data: strains } = useSuspenseQuery({
    queryKey: ['org', orgId, 'strains'],
    queryFn: () => axios.get(`/api/org/${orgId}/strains`).then(r => r.data),
  })

  return (
    <div className="grid grid-cols-3 gap-4">
      <StatsCard title="Labels" count={labels.length} />
      <StatsCard title="Templates" count={templates.length} />
      <StatsCard title="Strains" count={strains.length} />
    </div>
  )
}
```

### Nested Suspense: Licenses → Packages → Lab Results

```typescript
function LicenseView({ license }: { license: string }) {
  return (
    <div>
      {/* Show license info immediately */}
      <Suspense fallback={<LicenseSkeleton />}>
        <LicenseInfo license={license} />

        {/* Show packages after license loads */}
        <Suspense fallback={<PackagesSkeleton />}>
          <PackagesList license={license} />
        </Suspense>
      </Suspense>
    </div>
  )
}

function LicenseInfo({ license }: { license: string }) {
  const { user } = usePage<PageProps>().props

  const { data: facility } = useSuspenseQuery({
    queryKey: ['metrc', 'facility', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.facilities().then(facilities =>
        facilities.find(f => f.License.Number === license)
      )
    },
  })

  return (
    <div>
      <h2>{facility.Name}</h2>
      <p>{facility.License.Number}</p>
    </div>
  )
}

function PackagesList({ license }: { license: string }) {
  const { user } = usePage<PageProps>().props

  const { data: packages } = useSuspenseQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages(license, 'active')
    },
  })

  return (
    <div>
      {packages.map(pkg => (
        <div key={pkg.Id}>
          <span>{pkg.Label}</span>

          {/* Show lab results after package loads */}
          <Suspense fallback={<div>Loading lab results...</div>}>
            <LabResults packageId={pkg.Id} />
          </Suspense>
        </div>
      ))}
    </div>
  )
}

function LabResults({ packageId }: { packageId: number }) {
  const { data: results } = useSuspenseQuery({
    queryKey: ['lab-results', packageId],
    queryFn: () => fetchLabResults(packageId),
  })

  return <div>{results.length} results</div>
}
```

### Error Boundary with Toast Notification

```typescript
function PackagesPageWithToast() {
  const { reset } = useQueryErrorResetBoundary()

  return (
    <ReactErrorBoundary
      onReset={reset}
      onError={(error) => {
        // Show toast when error occurs
        toast.error(`Failed to load packages: ${error.message}`)
      }}
      fallbackRender={({ resetErrorBoundary }) => (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900">
            Unable to load packages
          </h3>
          <button
            onClick={() => {
              resetErrorBoundary()
              toast.info('Retrying...')
            }}
            className="mt-4"
          >
            Try Again
          </button>
        </div>
      )}
    >
      <Suspense fallback={<PackagesSkeleton />}>
        <PackagesTable />
      </Suspense>
    </ReactErrorBoundary>
  )
}
```

## When to Use Suspense

### ✅ Good Use Cases

- New applications built with React 18+
- Components that always need data (can't render without it)
- Simplified loading state management
- Better TypeScript type safety (no undefined checks)

### ❌ When Not to Use

- Need to show partial data while loading
- Complex loading states (progress bars, skeleton variants)
- Need to handle loading/error states inline
- Working with React < 18

## Next Steps

- **Error Handling** → Read `30-advanced-error-handling.md` for advanced error patterns
- **SSR** → Read `25-ssr-hydration.md` for Suspense with server-side rendering
- **Testing** → Read `26-testing.md` for testing Suspense queries
