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

## queryOptions Helper for Type Safety (Primary BudTags Pattern)

> **BudTags:** `queryOptions` is the primary pattern for all query definitions. Every
> query should be defined in a `queries.ts` file using `queryOptions`, consumed via
> spread in components or wrapped in a hook. Do not inline `queryKey`/`queryFn`/`staleTime`
> directly into `useQuery` calls — centralise them here.

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

### Metrc API Types and 3-Layer Architecture

The BudTags frontend never calls the Metrc API directly. All Metrc data flows through
Laravel backend routes (e.g. `/metrc/items`, `/metrc/packages/{license}`). The frontend
calls those Laravel routes via axios.

The 3-layer pattern is: **`queries.ts` (queryOptions factory) → hook wrapper → component**.

```typescript
// ── queryOptions provides end-to-end type inference ──
// File: Hooks/metrc/queries.ts
import { queryOptions } from '@tanstack/react-query';
import { STALE_TIME } from '@/constants/query-config';
import { metrcItemKeys } from './keys';

type Item = { Id: number; Name: string; ProductCategoryName: string };

const fetchItems = async (signal?: AbortSignal): Promise<Item[]> => {
    const { data } = await axios.get('/metrc/items', { signal });
    return data.items || [];
};

export const metrcQueries = {
    items: (license: string | null) => queryOptions({
        queryKey: metrcItemKeys.byLicense(license),
        queryFn: ({ signal }) => fetchItems(signal),
        staleTime: STALE_TIME.REFERENCE,
    }),
};

// ── Hook wrapper — type inference flows through spread ──
export function useMetrcItems(enabled = true) {
    const license = usePage<PageProps>().props.session?.license ?? null;
    return useQuery({ ...metrcQueries.items(license), enabled });
    // Return type is UseQueryResult<Item[], Error> — fully inferred
}

// ── Typed cache access via queryOptions ──
const cached = queryClient.getQueryData(metrcQueries.items(license).queryKey);
// Type: Item[] | undefined — no manual cast needed!

queryClient.setQueryData(metrcQueries.items(license).queryKey, (old) => {
    // old: Item[] | undefined — fully typed
    return old?.filter(item => item.Name !== 'Removed');
});
```

Shared Metrc types live in `types-metrc.tsx`:

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
