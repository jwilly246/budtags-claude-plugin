# Pattern 10: Query Functions

## QueryFunctionContext

Query functions receive a context object with helpful properties:

```typescript
function queryFn(context: QueryFunctionContext) {
  const { queryKey, signal, meta, pageParam } = context

  // Use context properties
  console.log(queryKey)   // ['todos', { status: 'active' }]
  console.log(signal)     // AbortSignal for cancellation
  console.log(pageParam)  // Page parameter (infinite queries)
}
```

## Using Query Keys in Query Functions

Access query key parameters inside the function:

```typescript
useQuery({
  queryKey: ['package', packageId],
  queryFn: ({ queryKey }) => {
    const [_key, id] = queryKey
    return fetchPackage(id)
  },
})
```

### Destructuring Query Keys

```typescript
useQuery({
  queryKey: ['packages', { status: 'active', page: 1 }],
  queryFn: ({ queryKey }) => {
    const [_key, filters] = queryKey
    return fetchPackages(filters)
  },
})
```

## AbortSignal for Cancellation

The `signal` property allows query functions to be cancelled:

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: async ({ signal }) => {
    const response = await fetch('/api/packages', { signal })
    return response.json()
  },
})

// Query automatically cancelled on unmount or key change
```

### With Axios

```typescript
useQuery({
  queryKey: ['packages'],
  queryFn: async ({ signal }) => {
    const response = await axios.get('/api/packages', { signal })
    return response.data
  },
})
```

### Custom Cancellation

```typescript
useQuery({
  queryKey: ['long-running'],
  queryFn: async ({ signal }) => {
    // Check if cancelled
    if (signal.aborted) {
      throw new Error('Query was cancelled')
    }

    const data = await fetchData()

    // Check again before expensive operation
    if (signal.aborted) {
      throw new Error('Query was cancelled')
    }

    return processData(data)
  },
})
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
  errors?: Record<string, string[]>
}

useQuery<Package[], ApiError>({
  queryKey: ['packages'],
  queryFn: async () => {
    const response = await fetch('/api/packages')

    if (!response.ok) {
      const errorData = await response.json()
      throw {
        message: errorData.message,
        statusCode: response.status,
        errors: errorData.errors,
      }
    }

    return response.json()
  },
})
```

## BudTags Examples

### Metrc API with Error Handling

```typescript
function useMetrcPackages(license: string) {
  const { user } = usePage<PageProps>().props

  return useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: async ({ signal }) => {
      const api = new MetrcApi()
      api.set_user(user)

      try {
        const packages = await api.packages(license, signal)
        return packages
      } catch (error) {
        if (error.response?.status === 401) {
          throw new Error('Invalid Metrc API key. Please check your secrets.')
        }
        if (error.response?.status === 429) {
          throw new Error('Metrc rate limit exceeded. Please try again later.')
        }
        throw error
      }
    },
    retry: 1, // Don't retry aggressively due to rate limits
  })
}
```

### Organization Query with Context

```typescript
useQuery({
  queryKey: ['packages', orgId, { status, location }],
  queryFn: async ({ queryKey, signal }) => {
    const [_key, orgId, filters] = queryKey

    const response = await axios.get(`/api/orgs/${orgId}/packages`, {
      params: filters,
      signal,
    })

    return response.data
  },
})
```

### Search with Debounce

```typescript
function SearchPackages() {
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 300)

  const { data, isFetching } = useQuery({
    queryKey: ['packages', 'search', debouncedSearch],
    queryFn: async ({ queryKey, signal }) => {
      const [_key, _type, searchTerm] = queryKey

      if (!searchTerm) return []

      const response = await fetch(`/api/packages/search?q=${searchTerm}`, {
        signal,
      })

      return response.json()
    },
    enabled: debouncedSearch.length > 0,
  })

  return (
    <div>
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search packages..."
      />
      {isFetching && <Spinner />}
      {data && <Results data={data} />}
    </div>
  )
}
```

### Paginated Query

```typescript
useQuery({
  queryKey: ['packages', { page, perPage }],
  queryFn: async ({ queryKey, signal }) => {
    const [_key, params] = queryKey

    const response = await fetch(
      `/api/packages?page=${params.page}&per_page=${params.perPage}`,
      { signal }
    )

    return response.json()
  },
})
```

## Query Function Best Practices

### ✅ DO

```typescript
// Use signal for cancellation
queryFn: async ({ signal }) => {
  return fetch('/api/data', { signal })
}

// Throw errors for failure cases
queryFn: async () => {
  const res = await fetch('/api/data')
  if (!res.ok) throw new Error('Failed')
  return res.json()
}

// Use queryKey for dynamic parameters
queryFn: ({ queryKey }) => {
  const [_key, id] = queryKey
  return fetchItem(id)
}
```

### ❌ DON'T

```typescript
// Don't ignore errors
queryFn: async () => {
  const res = await fetch('/api/data')
  return res.json() // ❌ Doesn't check res.ok
}

// Don't use external variables (use queryKey instead)
let externalId = 5
queryFn: () => fetchItem(externalId) // ❌ Won't refetch when externalId changes

// Use queryKey instead:
queryFn: ({ queryKey }) => {
  const [_key, id] = queryKey
  return fetchItem(id)
}
```

## Async/Await Patterns

### Sequential Operations

```typescript
queryFn: async () => {
  const user = await fetchUser()
  const org = await fetchOrg(user.orgId)
  const data = await fetchData(org.license)
  return data
}
```

### Parallel Operations

```typescript
queryFn: async () => {
  const [packages, plants, harvests] = await Promise.all([
    fetchPackages(),
    fetchPlants(),
    fetchHarvests(),
  ])

  return { packages, plants, harvests }
}
```

## Next Steps
- **Query Options** → Read `11-query-options.md`
- **Cancellation** → Read `21-cancellation.md`
- **Error Handling** → Read `13-mutations.md` (onError patterns)
