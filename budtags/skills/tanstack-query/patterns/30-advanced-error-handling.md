# Pattern 30: Advanced Error Handling

## Error Handling Overview

TanStack Query provides comprehensive error handling at multiple levels:

```typescript
// Query-level errors
const { error, isError } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})

// Mutation-level errors
const mutation = useMutation({
  mutationFn: createPackage,
  onError: (error) => {
    toast.error(error.message)
  },
})

// Global-level errors
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error) => console.error(error),
  }),
})
```

## Error Types

Common error scenarios:

- **Network errors**: Connection failed, timeout
- **API errors**: 4xx, 5xx status codes
- **Parsing errors**: Invalid JSON response
- **Validation errors**: Invalid request data
- **Rate limiting**: 429 Too Many Requests

## Retry Strategies

### Default Retry Behavior

Queries retry 3 times by default with exponential backoff:

```typescript
const { data } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  // Default behavior (built-in):
  retry: 3,
  retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
})
```

### Custom Retry Logic

Conditional retries based on error type:

```typescript
const { data } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  retry: (failureCount, error) => {
    // Don't retry on 404 (resource not found)
    if (error.response?.status === 404) return false

    // Don't retry on auth errors
    if (error.response?.status === 401 || error.response?.status === 403) {
      return false
    }

    // Retry up to 5 times for rate limiting
    if (error.response?.status === 429) {
      return failureCount < 5
    }

    // Retry up to 3 times for server errors
    if (error.response?.status >= 500) {
      return failureCount < 3
    }

    // Don't retry other errors
    return false
  },
})
```

### Custom Retry Delay

Exponential backoff with custom timing:

```typescript
const { data } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  retry: 3,
  retryDelay: (attemptIndex, error) => {
    // Rate limit: wait longer
    if (error.response?.status === 429) {
      return Math.min(5000 * 2 ** attemptIndex, 60000) // 5s, 10s, 20s, 40s, 60s max
    }

    // Server error: normal backoff
    if (error.response?.status >= 500) {
      return Math.min(1000 * 2 ** attemptIndex, 10000) // 1s, 2s, 4s, 8s, 10s max
    }

    // Default backoff
    return Math.min(1000 * 2 ** attemptIndex, 30000)
  },
})
```

### Mutation Retry

Mutations don't retry by default:

```typescript
const mutation = useMutation({
  mutationFn: createPackage,
  retry: 3, // Enable retries for mutations
  retryDelay: 1000, // 1 second between retries
})
```

## Error Boundaries

### Basic Error Boundary

Catch and display query errors:

```typescript
import { ErrorBoundary } from 'react-error-boundary'

function App() {
  return (
    <ErrorBoundary
      fallbackRender={({ error, resetErrorBoundary }) => (
        <div className="error-container">
          <h2>Something went wrong</h2>
          <pre>{error.message}</pre>
          <button onClick={resetErrorBoundary}>Try Again</button>
        </div>
      )}
    >
      <PackagesList />
    </ErrorBoundary>
  )
}
```

### Error Boundary with Query Reset

Reset queries when error boundary resets:

```typescript
import { useQueryErrorResetBoundary } from '@tanstack/react-query'
import { ErrorBoundary } from 'react-error-boundary'

function App() {
  const { reset } = useQueryErrorResetBoundary()

  return (
    <ErrorBoundary
      onReset={reset}
      fallbackRender={({ error, resetErrorBoundary }) => (
        <div>
          <h2>Error loading data</h2>
          <p>{error.message}</p>
          <button onClick={resetErrorBoundary}>
            Retry
          </button>
        </div>
      )}
    >
      <PackagesList />
    </ErrorBoundary>
  )
}
```

### Nested Error Boundaries

Granular error handling:

```typescript
function Dashboard() {
  return (
    <div>
      <ErrorBoundary fallback={<div>Sidebar failed to load</div>}>
        <Sidebar />
      </ErrorBoundary>

      <ErrorBoundary fallback={<div>Packages failed to load</div>}>
        <PackagesList />
      </ErrorBoundary>

      <ErrorBoundary fallback={<div>Stats failed to load</div>}>
        <Stats />
      </ErrorBoundary>
    </div>
  )
}
```

### Error Boundary Component

Reusable error boundary:

```typescript
import { useQueryErrorResetBoundary } from '@tanstack/react-query'
import { ErrorBoundary as ReactErrorBoundary } from 'react-error-boundary'

interface Props {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export function QueryErrorBoundary({ children, fallback }: Props) {
  const { reset } = useQueryErrorResetBoundary()

  return (
    <ReactErrorBoundary
      onReset={reset}
      fallbackRender={({ error, resetErrorBoundary }) => {
        if (fallback) return <>{fallback}</>

        return (
          <div className="rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  Error loading data
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error.message}</p>
                </div>
                <div className="mt-4">
                  <button
                    type="button"
                    onClick={resetErrorBoundary}
                    className="rounded-md bg-red-50 px-2 py-1.5 text-sm font-medium text-red-800 hover:bg-red-100"
                  >
                    Try again
                  </button>
                </div>
              </div>
            </div>
          </div>
        )
      }}
    >
      {children}
    </ReactErrorBoundary>
  )
}
```

## Fallback UI Patterns

### Show Cached Data on Error

Display stale data with warning:

```typescript
function PackagesList() {
  const { data, error, isError, refetch, isFetching } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  if (isError && !data) {
    // No cached data, show error
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load packages</p>
        <button onClick={() => refetch()}>Retry</button>
      </div>
    )
  }

  if (isError && data) {
    // Show stale data with warning
    return (
      <>
        <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-4">
          <div className="flex items-center">
            <p className="text-yellow-700">
              ⚠️ Showing cached data. Unable to fetch updates.
            </p>
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              className="ml-auto"
            >
              {isFetching ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>
        <DataTable data={data} />
      </>
    )
  }

  return <DataTable data={data} />
}
```

### Empty State vs Error State

```typescript
function PackagesList() {
  const { data, error, isError, isLoading } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  if (isLoading) return <LoadingSkeleton />

  if (isError) {
    return (
      <div className="text-center py-12">
        <svg className="mx-auto h-12 w-12 text-red-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">
          Failed to load packages
        </h3>
        <p className="mt-1 text-sm text-gray-500">{error.message}</p>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12">
        <svg className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">
          No packages found
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by creating a new package.
        </p>
      </div>
    )
  }

  return <DataTable data={data} />
}
```

### Retry Button

```typescript
function PackagesList() {
  const { data, isError, refetch, isRefetching } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  if (isError) {
    return (
      <div className="text-center">
        <p>Failed to load packages</p>
        <button
          onClick={() => refetch()}
          disabled={isRefetching}
          className="mt-4"
        >
          {isRefetching ? 'Retrying...' : 'Retry'}
        </button>
      </div>
    )
  }

  return <DataTable data={data} />
}
```

## Global Error Handling

### QueryCache onError

Global query error handler:

```typescript
import { QueryCache, QueryClient } from '@tanstack/react-query'

const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error, query) => {
      // Log to monitoring service (e.g., Sentry)
      console.error('Query error:', {
        error,
        queryKey: query.queryKey,
        queryHash: query.queryHash,
      })

      // Show user-facing notification
      if (error.response?.status >= 500) {
        toast.error('Server error. Please try again later.')
      }
    },
  }),
})
```

### MutationCache onError

Global mutation error handler:

```typescript
import { MutationCache, QueryClient } from '@tanstack/react-query'

const queryClient = new QueryClient({
  mutationCache: new MutationCache({
    onError: (error, variables, context, mutation) => {
      // Log error
      console.error('Mutation error:', {
        error,
        variables,
        mutationKey: mutation.options.mutationKey,
      })

      // Show error toast
      const message = error.response?.data?.message || 'Operation failed'
      toast.error(message)
    },
  }),
})
```

### Combined Global Handlers

```typescript
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error, query) => {
      if (error.response?.status === 401) {
        // Redirect to login
        window.location.href = '/login'
      } else if (error.response?.status >= 500) {
        toast.error('Server error')
      }
    },
  }),
  mutationCache: new MutationCache({
    onError: (error) => {
      if (error.response?.status === 401) {
        window.location.href = '/login'
      } else {
        toast.error(error.response?.data?.message || 'Operation failed')
      }
    },
  }),
  defaultOptions: {
    queries: {
      // Global query defaults
      retry: 3,
      staleTime: 30 * 1000,
    },
    mutations: {
      // Global mutation defaults
      retry: 0,
    },
  },
})
```

## BudTags Examples

> ⚠️ **v5 Breaking Change**: `onError` callbacks were **removed from `useQuery`** in TanStack Query v5.
> - For per-query error handling: Check `error` from the query result
> - For global error handling: Use `QueryCache.onError`
> - `onError` **still works** in `useMutation`

### Metrc API Error Handling

```typescript
// ✅ v5-compliant: No onError in useQuery, handle errors from result
function useMetrcPackages(license: string) {
  const { user } = usePage<PageProps>().props

  return useQuery<Package[], Error>({
    queryKey: ['metrc', 'packages', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages(license, 'active')
    },
    retry: (failureCount, error) => {
      const status = (error as any).response?.status

      // Don't retry auth errors - redirect instead
      if (status === 401 || status === 403) return false

      // Retry rate limit errors with longer backoff
      if (status === 429) return failureCount < 5

      // Retry server errors
      if (status >= 500) return failureCount < 3

      return false
    },
    retryDelay: (attemptIndex, error) => {
      const status = (error as any).response?.status

      // Rate limit: wait progressively longer
      if (status === 429) {
        return Math.min(5000 * 2 ** attemptIndex, 60000)
      }

      // Server error: normal backoff
      return Math.min(1000 * 2 ** attemptIndex, 10000)
    },
    staleTime: 30 * 1000, // 30 seconds
    gcTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Handle errors in component using the error from query result
function PackagesContainer() {
  const { data, error, isError } = useMetrcPackages(license)

  useEffect(() => {
    if (error) {
      const status = (error as any).response?.status
      if (status === 401) {
        toast.error('Invalid Metrc API key.')
        router.visit('/secrets')
      } else if (status === 403) {
        toast.error('License permission denied.')
        router.visit('/pick-license')
      }
    }
  }, [error])

  // ... rest of component
}
```

### License Permission Error Recovery

```typescript
function PackagesPage() {
  const license = usePage<PageProps>().props.session.license
  const { data, error, isError } = useMetrcPackages(license)

  if (isError) {
    const status = error.response?.status

    // Permission error - show helpful message
    if (status === 403) {
      return (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900">
            License Access Required
          </h3>
          <p className="mt-2 text-sm text-gray-500">
            Your current license ({license}) does not have access to packages.
          </p>
          <button
            onClick={() => router.visit('/pick-license')}
            className="mt-4"
          >
            Switch License
          </button>
        </div>
      )
    }

    // API key error
    if (status === 401) {
      return (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900">
            API Key Required
          </h3>
          <p className="mt-2 text-sm text-gray-500">
            Please configure your Metrc API key to continue.
          </p>
          <button
            onClick={() => router.visit('/secrets')}
            className="mt-4"
          >
            Add API Key
          </button>
        </div>
      )
    }

    // Generic error
    return <div>Error loading packages: {error.message}</div>
  }

  return <DataTable data={data} />
}
```

### Organization-Scoped Error Handling

```typescript
// ✅ v5-compliant: Use generic types, no onError
function useOrgData<T>(endpoint: string) {
  const { user } = usePage<PageProps>().props
  const orgId = user.active_org.id

  return useQuery<T, Error>({
    queryKey: ['org', orgId, endpoint],
    queryFn: async () => {
      const response = await axios.get(`/api/org/${orgId}/${endpoint}`)
      return response.data as T
    },
    retry: (failureCount, error) => {
      // Don't retry permission errors
      if ((error as any).response?.status === 403) return false
      return failureCount < 3
    },
  })
}

// Handle errors in the consuming component
function OrgStrains() {
  const { data, error, isError } = useOrgData<Strain[]>('strains')

  // Show toast on error (via useEffect or global handler)
  useEffect(() => {
    if (error) {
      const status = (error as any).response?.status
      if (status === 403) {
        toast.error('You do not have permission to access this data.')
      } else if (status === 401) {
        toast.error('Session expired. Please log in again.')
        router.visit('/login')
      }
    }
  }, [error])

  if (isError) return <div>Error loading data</div>
  return <StrainsList data={data} />
}
```

### Stale Data with Error Toast

```typescript
function TransfersList() {
  const license = usePage<PageProps>().props.session.license
  const { data, error, isError, refetch, isFetching } = useQuery({
    queryKey: ['metrc', 'transfers', license],
    queryFn: () => fetchMetrcTransfers(license),
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 5 * 60 * 1000, // Poll every 5 minutes
  })

  // Show error toast but keep displaying cached data
  useEffect(() => {
    if (isError && data) {
      toast.error('Unable to fetch latest transfers. Showing cached data.', {
        toastId: 'transfers-error', // Prevent duplicate toasts
      })
    }
  }, [isError, data])

  if (isError && !data) {
    return <div>Error loading transfers</div>
  }

  return (
    <>
      {isError && data && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-yellow-700">
              ⚠️ Showing cached data from {new Date().toLocaleTimeString()}
            </p>
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              className="text-sm font-medium text-yellow-700 hover:text-yellow-800"
            >
              {isFetching ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>
      )}
      <DataTable data={data} />
    </>
  )
}
```

## Next Steps

- **Suspense** → Read `27-suspense-integration.md` for React Suspense error boundaries
- **Testing Errors** → Read `26-testing.md` for testing error scenarios
- **Network Modes** → Read `24-network-mode.md` for offline error handling
