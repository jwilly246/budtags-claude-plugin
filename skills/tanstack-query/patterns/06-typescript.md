# Pattern 6: TypeScript

## Type Inference from queryFn

TanStack Query automatically infers types from your `queryFn`:

```typescript
const { data } = useQuery({
  queryKey: ['packages'],
  queryFn: async () => {
    const response = await fetch('/api/packages')
    return response.json() as Package[]
  },
})

// data is inferred as Package[] | undefined
```

## Generic Types

### Explicit Type Parameters

```typescript
const { data } = useQuery<Package[]>({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})

// data: Package[] | undefined
```

### Full Generic Signature

```typescript
useQuery<TData, TError, TQueryFnData, TQueryKey>({
  queryKey,
  queryFn,
})

// TData = The type of data returned (same as TQueryFnData by default)
// TError = The type of error (default: Error)
// TQueryFnData = The type returned by queryFn
// TQueryKey = The type of the query key (auto-inferred)
```

## Type Narrowing with Status Checks

```typescript
const { data, status, error } = useQuery({
  queryKey: ['package', id],
  queryFn: () => fetchPackage(id),
})

// Before narrowing
data // Package | undefined
error // Error | null

// After narrowing
if (status === 'pending') {
  data // undefined
}

if (status === 'error') {
  error // Error (not null)
  data // undefined
}

if (status === 'success') {
  data // Package (not undefined)
}
```

## Error Typing

### Default Error Type

```typescript
const { error } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})

// error: Error | null (default)
```

### Custom Error Type

```typescript
type ApiError = {
  message: string
  statusCode: number
}

const { error } = useQuery<Package[], ApiError>({
  queryKey: ['packages'],
  queryFn: async () => {
    const response = await fetch('/api/packages')
    if (!response.ok) {
      throw {
        message: 'Failed to fetch packages',
        statusCode: response.status,
      }
    }
    return response.json()
  },
})

// error: ApiError | null
if (error) {
  toast.error(`Error ${error.statusCode}: ${error.message}`)
}
```

## queryOptions Helper for Type Safety

```typescript
import { queryOptions, useQuery } from '@tanstack/react-query'

const packagesQueryOptions = queryOptions({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  staleTime: 5 * 60 * 1000,
})

// Use in component
const { data } = useQuery(packagesQueryOptions)

// Use in prefetch
queryClient.prefetchQuery(packagesQueryOptions)

// Use in loader
const data = await queryClient.ensureQueryData(packagesQueryOptions)

// ✅ Benefits:
// - Single source of truth
// - Full type inference
// - Reusable across components
```

## select Option Type Transformations

```typescript
type Package = {
  Id: number
  Label: string
  ProductName: string
}

const { data } = useQuery({
  queryKey: ['packages'],
  queryFn: () => fetchPackages(),
  select: (packages) => packages.map((p) => p.Label),
})

// data: string[] | undefined (not Package[])
```

### Typed select

```typescript
const { data } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  select: (packages: Package[]) => ({
    total: packages.length,
    labels: packages.map((p) => p.Label),
  }),
})

// data: { total: number; labels: string[] } | undefined
```

## Global Type Registration

Register default types for your entire app:

```typescript
// types/react-query.d.ts
import '@tanstack/react-query'

declare module '@tanstack/react-query' {
  interface Register {
    defaultError: ApiError
  }
}

type ApiError = {
  message: string
  statusCode: number
  errors?: Record<string, string[]>
}
```

Now all queries default to `ApiError`:

```typescript
const { error } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})

// error: ApiError | null (not Error | null)
```

## useMutation TypeScript

```typescript
type CreatePackageData = {
  label: string
  productId: number
}

const mutation = useMutation<
  Package,            // TData - success response
  ApiError,           // TError - error type
  CreatePackageData,  // TVariables - mutation input
  unknown             // TContext - onMutate context
>({
  mutationFn: (data) => createPackage(data),
})

// mutation.mutate accepts CreatePackageData
mutation.mutate({
  label: '1A4...',
  productId: 123,
})
```

## BudTags Type Patterns

### Metrc API Types

```typescript
// types-metrc.tsx (shared types)
export type Package = {
  Id: number
  Label: string
  ProductName: string
  Quantity: number
  UnitOfMeasureName: string
  ReceivedDateTime: string
  FinishedDate?: string
}

export type Plant = {
  Id: number
  Label: string
  StrainName: string
  PlantedDate: string
}

// Use in queries
function useMetrcPackages(license: string) {
  return useQuery<Package[]>({
    queryKey: ['metrc', 'packages', license],
    queryFn: async () => {
      const api = new MetrcApi()
      return api.packages(license)
    },
  })
}
```

### Query Key Types

```typescript
const packageKeys = {
  all: (orgId: number) => ['packages', orgId] as const,
  lists: (orgId: number) => [...packageKeys.all(orgId), 'list'] as const,
  list: (orgId: number, filters: PackageFilters) =>
    [...packageKeys.lists(orgId), filters] as const,
  details: (orgId: number) => [...packageKeys.all(orgId), 'detail'] as const,
  detail: (orgId: number, id: number) =>
    [...packageKeys.details(orgId), id] as const,
}

// Type: readonly ["packages", number, "detail", number]
type PackageDetailKey = ReturnType<typeof packageKeys.detail>
```

### Generic DataTable with React Query

```typescript
interface DataTableProps<TData> {
  queryKey: unknown[]
  queryFn: () => Promise<TData[]>
  columns: ColumnDef<TData, any>[]
}

function DataTable<TData>({ queryKey, queryFn, columns }: DataTableProps<TData>) {
  const { data, isLoading, error } = useQuery({
    queryKey,
    queryFn,
  })

  if (isLoading) return <Spinner />
  if (error) return <ErrorMessage error={error} />

  const table = useReactTable({
    data: data ?? [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return <table>...</table>
}

// Usage with full type safety
<DataTable<Package>
  queryKey={['packages']}
  queryFn={fetchPackages}
  columns={packageColumns}
/>
```

### Mutation with Form Data

```typescript
import { useState } from 'react'

type AdjustPackageData = {
  packageId: number
  quantity: number
  reason: string
}

function AdjustPackageModal({ pkg }: { pkg: Package }) {
  const [data, setData] = useState<AdjustPackageData>({
    packageId: pkg.Id,
    quantity: 0,
    reason: '',
  })

  const mutation = useMutation<void, ApiError, AdjustPackageData>({
    mutationFn: (data) => axios.post('/api/packages/adjust', data),
    onSuccess: () => {
      toast.success('Package adjusted')
    },
    onError: (error) => {
      toast.error(error.message)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate(data)
  }

  return <form onSubmit={handleSubmit}>...</form>
}
```

## Type Guards for Status

```typescript
function isSuccess<T>(query: { status: string; data: T | undefined }): query is { status: 'success'; data: T } {
  return query.status === 'success'
}

const query = useQuery({
  queryKey: ['package', id],
  queryFn: () => fetchPackage(id),
})

if (isSuccess(query)) {
  query.data // Package (not undefined)
}
```

## Common Type Errors

### ❌ Type Mismatch

```typescript
// ❌ Error: Type 'Package[]' is not assignable to type 'string'
const { data } = useQuery<string>({
  queryKey: ['packages'],
  queryFn: () => fetchPackages(), // Returns Package[]
})

// ✅ Fix: Correct type or use select
const { data } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  select: (packages) => packages.map(p => p.Label).join(', '),
})
```

### ❌ Mutation Variables Type

```typescript
// ❌ Error: Argument of type 'number' is not assignable to parameter of type '{ id: number }'
const mutation = useMutation({
  mutationFn: (id: number) => deletePackage(id),
})
mutation.mutate({ id: 5 }) // Wrong shape

// ✅ Fix: Match mutationFn signature
mutation.mutate(5)
```

## Type Safety Checklist

- ✅ Use `queryOptions` helper for reusable queries
- ✅ Explicitly type custom errors
- ✅ Use `as const` for query key factories
- ✅ Type `select` transformations
- ✅ Register global error type with module augmentation
- ✅ Import shared types from `types-metrc.tsx`
- ✅ Use type guards for status narrowing

## Next Steps
- **Query Options** → Read `11-query-options.md`
- **Basic Queries** → Read `07-basic-queries.md`
- **Mutations** → Read `13-mutations.md`
