# Pattern 7: Basic Queries

## useQuery Hook

The `useQuery` hook is the primary way to fetch data:

```typescript
import { useQuery } from '@tanstack/react-query'

function Packages() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['packages'],
    queryFn: () => fetch('/api/packages').then(r => r.json()),
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return <DataTable data={data} />
}
```

## Query States

### Status

```typescript
const { status } = useQuery(...)

// status: 'pending' | 'error' | 'success'
```

- **`pending`** - No data yet, first fetch in progress
- **`error`** - Query failed
- **`success`** - Query succeeded, data available

### Fetch Status

```typescript
const { fetchStatus } = useQuery(...)

// fetchStatus: 'fetching' | 'paused' | 'idle'
```

- **`fetching`** - Query function is executing
- **`paused`** - Query wants to fetch but is paused (offline, etc.)
- **`idle`** - Query is not fetching

### Boolean Flags

```typescript
const {
  isPending,   // status === 'pending'
  isError,     // status === 'error'
  isSuccess,   // status === 'success'

  isFetching,  // fetchStatus === 'fetching'
  isPaused,    // fetchStatus === 'paused'

  isLoading,   // isPending && isFetching (useful for initial load)
} = useQuery(...)
```

## Data and Error

```typescript
const { data, error } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})

// data: Package[] | undefined
// error: Error | null
```

### Type Narrowing

```typescript
if (status === 'pending') {
  // data is undefined
  // error is null
}

if (status === 'error') {
  // data is undefined
  // error is Error (not null)
  console.error(error.message)
}

if (status === 'success') {
  // data is Package[] (not undefined)
  // error is null
  return <DataTable data={data} />
}
```

## Common Patterns

### Loading State

```typescript
function Packages() {
  const { data, isLoading } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  if (isLoading) {
    return <Spinner />
  }

  return <DataTable data={data} />
}
```

### Error State

```typescript
function Packages() {
  const { data, error } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  if (error) {
    return <ErrorMessage error={error} />
  }

  return <DataTable data={data} />
}
```

### Loading + Error + Success

```typescript
function Packages() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  if (isLoading) return <Spinner />
  if (error) return <ErrorMessage error={error} />

  return <DataTable data={data} />
}
```

### Background Refetch Indicator

```typescript
function Packages() {
  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['packages'],
    queryFn: fetchPackages,
  })

  if (isLoading) return <Spinner />

  return (
    <div>
      {isFetching && <RefreshIndicator />}
      <DataTable data={data} />
    </div>
  )
}
```

## Query Function

### Inline Function

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: async () => {
    const response = await fetch('/api/packages')
    if (!response.ok) {
      throw new Error('Failed to fetch packages')
    }
    return response.json()
  },
})
```

### Named Function

```typescript
async function fetchPackages() {
  const response = await fetch('/api/packages')
  if (!response.ok) {
    throw new Error('Failed to fetch packages')
  }
  return response.json()
}

useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})
```

### Arrow Function with Parameters

```typescript
useQuery({
  queryKey: ['package', id],
  queryFn: () => fetchPackage(id),
})
```

## BudTags Examples

### Metrc Packages

```typescript
function MetrcPackages() {
  const { user } = usePage<PageProps>().props
  const license = usePage<PageProps>().props.session.license

  const {
    data: packages,
    isLoading,
    error,
    isFetching,
  } = useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages(license)
    },
    staleTime: 5 * 60 * 1000,
    retry: 1,
  })

  if (isLoading) {
    return (
      <BoxMain>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900" />
        </div>
      </BoxMain>
    )
  }

  if (error) {
    return (
      <BoxMain>
        <div className="text-red-600">
          Failed to load packages: {error.message}
        </div>
      </BoxMain>
    )
  }

  return (
    <BoxMain>
      {isFetching && (
        <div className="absolute top-2 right-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
        </div>
      )}
      <DataTable data={packages} />
    </BoxMain>
  )
}
```

### Organization Strains

```typescript
function Strains() {
  const { user } = usePage<PageProps>().props
  const orgId = user.active_org.id

  const { data: strains, isLoading } = useQuery({
    queryKey: ['strains', orgId],
    queryFn: () => axios.get(`/api/orgs/${orgId}/strains`).then(r => r.data),
  })

  if (isLoading) return <Spinner />

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {strains.map(strain => (
        <StrainCard key={strain.id} strain={strain} />
      ))}
    </div>
  )
}
```

### Labels with Filtering

```typescript
function Labels({ status }: { status: 'pending' | 'approved' | 'printed' }) {
  const { user } = usePage<PageProps>().props
  const orgId = user.active_org.id

  const { data: labels, isLoading } = useQuery({
    queryKey: ['labels', orgId, status],
    queryFn: () =>
      axios.get(`/api/orgs/${orgId}/labels`, { params: { status } }).then(r => r.data),
  })

  if (isLoading) return <Spinner />

  return <LabelList labels={labels} />
}
```

## Error Handling

### Throwing Errors

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: async () => {
    const response = await fetch('/api/packages')

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return response.json()
  },
})
```

### Custom Error Types

```typescript
type ApiError = {
  message: string
  statusCode: number
}

useQuery<Package[], ApiError>({
  queryKey: ['packages'],
  queryFn: async () => {
    const response = await fetch('/api/packages')

    if (!response.ok) {
      throw {
        message: await response.text(),
        statusCode: response.status,
      }
    }

    return response.json()
  },
})
```

## Default Data

### Fallback Data

```typescript
const { data = [] } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})

// data is always Package[] (never undefined)
return <DataTable data={data} />
```

## Next Steps
- **Parallel Queries** → Read `08-parallel-queries.md`
- **Query Options** → Read `11-query-options.md`
- **Mutations** → Read `13-mutations.md`
