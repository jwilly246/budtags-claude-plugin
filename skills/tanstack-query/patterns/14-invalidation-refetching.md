# Pattern 14: Invalidation & Refetching

## Query Invalidation

Mark queries as stale and optionally refetch them:

```typescript
import { useQueryClient } from '@tanstack/react-query'

function Component() {
  const queryClient = useQueryClient()

  // Invalidate single query
  queryClient.invalidateQueries({ queryKey: ['packages'] })

  // Invalidate multiple queries
  queryClient.invalidateQueries({ queryKey: ['packages'] })
  queryClient.invalidateQueries({ queryKey: ['plants'] })
}
```

## Query Matching Strategies

### Exact Match

```typescript
// Only invalidates ['packages']
queryClient.invalidateQueries({
  queryKey: ['packages'],
  exact: true,
})

// Does NOT invalidate:
// ['packages', 5]
// ['packages', { status: 'active' }]
```

### Prefix Match (Default)

```typescript
// Invalidates ALL queries starting with ['packages']
queryClient.invalidateQueries({ queryKey: ['packages'] })

// Invalidates:
// ['packages']
// ['packages', 5]
// ['packages', { status: 'active' }]
// ['packages', 'detail', 10]
```

### Predicate Match

```typescript
// Invalidate all queries with stale data
queryClient.invalidateQueries({
  predicate: (query) => query.isStale(),
})

// Invalidate all error queries
queryClient.invalidateQueries({
  predicate: (query) => query.state.status === 'error',
})

// Invalidate by custom logic
queryClient.invalidateQueries({
  predicate: (query) => {
    return query.queryKey[0] === 'packages' && query.state.data.length > 0
  },
})
```

## invalidateQueries vs refetchQueries

### invalidateQueries (Common)

Marks queries as stale, refetches active queries:

```typescript
// Mark as stale, refetch if active
queryClient.invalidateQueries({ queryKey: ['packages'] })

// Behavior:
// - Active queries: Marked stale, refetch in background
// - Inactive queries: Marked stale, refetch on next mount
```

### refetchQueries

Immediately refetch matching queries:

```typescript
// Refetch now, regardless of stale state
queryClient.refetchQueries({ queryKey: ['packages'] })

// Behavior:
// - Active queries: Refetch immediately
// - Inactive queries: Not refetched
```

## After Mutations

### Common Pattern

```typescript
const mutation = useMutation({
  mutationFn: createPackage,
  onSuccess: () => {
    // Invalidate package list
    queryClient.invalidateQueries({ queryKey: ['packages'] })
  },
})
```

### Multiple Invalidations

```typescript
const mutation = useMutation({
  mutationFn: updatePackage,
  onSuccess: () => {
    // Invalidate list
    queryClient.invalidateQueries({ queryKey: ['packages'] })

    // Invalidate specific detail
    queryClient.invalidateQueries({ queryKey: ['packages', data.id] })

    // Invalidate related data
    queryClient.invalidateQueries({ queryKey: ['inventory'] })
  },
})
```

## Selective Invalidation

### Hierarchical Keys

```typescript
const packageKeys = {
  all: ['packages'] as const,
  lists: () => [...packageKeys.all, 'list'] as const,
  list: (filters: string) => [...packageKeys.lists(), filters] as const,
  details: () => [...packageKeys.all, 'detail'] as const,
  detail: (id: number) => [...packageKeys.details(), id] as const,
}

// Invalidate ALL package queries
queryClient.invalidateQueries({ queryKey: packageKeys.all })

// Invalidate only package lists
queryClient.invalidateQueries({ queryKey: packageKeys.lists() })

// Invalidate specific detail
queryClient.invalidateQueries({ queryKey: packageKeys.detail(5) })
```

## When to Invalidate vs Update

### Use Invalidation When:
- Simple CRUD operations
- Data structure might change
- Lazy approach (let queries refetch when needed)

```typescript
const deleteMutation = useMutation({
  mutationFn: deletePackage,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['packages'] })
  },
})
```

### Use setQueryData When:
- You know exact shape of updated data
- Want immediate UI update (no loading state)
- Response includes updated data

```typescript
const updateMutation = useMutation({
  mutationFn: updatePackage,
  onSuccess: (updatedPackage) => {
    // Update cache directly
    queryClient.setQueryData(['packages', updatedPackage.id], updatedPackage)

    // Update list
    queryClient.setQueryData(['packages'], (old) =>
      old.map(pkg => pkg.id === updatedPackage.id ? updatedPackage : pkg)
    )
  },
})
```

## BudTags Examples

### After Creating Package

```typescript
const createMutation = useMutation({
  mutationFn: async (data) => {
    const api = new MetrcApi()
    api.set_user(user)
    return api.create_package(license, data)
  },
  onSuccess: () => {
    // Invalidate package list for this license
    queryClient.invalidateQueries({
      queryKey: ['metrc', 'packages', license],
    })

    toast.success('Package created')
  },
})
```

### After Adjusting Package

```typescript
const adjustMutation = useMutation({
  mutationFn: (data) => axios.post(`/metrc/packages/adjust`, data),
  onSuccess: () => {
    // Invalidate package lists
    queryClient.invalidateQueries({
      queryKey: ['metrc', 'packages'],
    })

    // Invalidate specific package detail
    queryClient.invalidateQueries({
      queryKey: ['metrc', 'package', license, data.id],
    })

    toast.success('Package adjusted')
  },
})
```

### After Organization Switch

```typescript
const handleOrgChange = (newOrgId: number) => {
  // Invalidate all queries for new org
  queryClient.invalidateQueries({
    predicate: (query) => {
      // Invalidate queries that include orgId
      return query.queryKey.includes(newOrgId)
    },
  })

  // Navigate to new org
  router.visit(`/orgs/${newOrgId}`)
}
```

### After License Switch

```typescript
const handleLicenseChange = (newLicense: string) => {
  const oldLicense = session.license

  // Remove old license data
  queryClient.removeQueries({
    queryKey: ['metrc', 'packages', oldLicense],
  })
  queryClient.removeQueries({
    queryKey: ['metrc', 'plants', oldLicense],
  })

  // Prefetch new license data
  queryClient.prefetchQuery({
    queryKey: ['metrc', 'packages', newLicense],
    queryFn: () => fetchPackages(newLicense),
  })
}
```

### Selective Invalidation by Status

```typescript
const finishMutation = useMutation({
  mutationFn: (id: number) => axios.post(`/packages/${id}/finish`),
  onSuccess: () => {
    // Invalidate active packages list
    queryClient.invalidateQueries({
      queryKey: ['packages', { status: 'active' }],
    })

    // Invalidate finished packages list
    queryClient.invalidateQueries({
      queryKey: ['packages', { status: 'finished' }],
    })
  },
})
```

## Background Refetching

Invalidation triggers background refetch (no loading spinner):

```typescript
const mutation = useMutation({
  mutationFn: updatePackage,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['packages'] })
  },
})

// In component:
const { data, isFetching } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
})

// When mutation succeeds:
// - data still shows old data
// - isFetching becomes true
// - New data fetched in background
// - data updates when fetch completes
// - No loading spinner shown
```

## Stale Time Override

Force immediate refetch regardless of staleTime:

```typescript
queryClient.invalidateQueries({
  queryKey: ['packages'],
  refetchType: 'active', // 'active' | 'inactive' | 'all' | 'none'
})
```

## Next Steps
- **Optimistic Updates** → Read `15-optimistic-updates.md`
- **Cache Updates** → Read `20-cache-updates.md`
- **Mutations** → Read `13-mutations.md`
