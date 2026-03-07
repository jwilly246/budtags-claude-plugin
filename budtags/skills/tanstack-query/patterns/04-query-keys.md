# Pattern 4: Query Keys

## Query Keys are Cache Identifiers

Query keys uniquely identify queries in the cache:

```typescript
// Same key = same cache entry
useQuery({ queryKey: ['todos'], ... }) // Component A
useQuery({ queryKey: ['todos'], ... }) // Component B
// ✅ Both share the same data, only 1 network request
```

## Key Structure

### String Keys (Simple)

```typescript
useQuery({ queryKey: ['todos'], queryFn: fetchTodos })
```

### Array Keys with Variables

```typescript
// Detail query with ID
useQuery({
  queryKey: ['todo', 5],
  queryFn: () => fetchTodo(5),
})

// List query with filters
useQuery({
  queryKey: ['todos', { status: 'active', page: 1 }],
  queryFn: () => fetchTodos({ status: 'active', page: 1 }),
})
```

## Hierarchical Keys

Organize keys in a hierarchy for easy invalidation:

```typescript
// All todos
['todos']

// All active todos
['todos', 'list']

// Active todos with filters
['todos', 'list', { status: 'active' }]

// All todo details
['todos', 'detail']

// Specific todo detail
['todos', 'detail', 5]
```

### Benefits

```typescript
// Invalidate ALL todos (lists + details)
queryClient.invalidateQueries({ queryKey: ['todos'] })

// Invalidate only todo lists
queryClient.invalidateQueries({ queryKey: ['todos', 'list'] })

// Invalidate specific todo
queryClient.invalidateQueries({ queryKey: ['todos', 'detail', 5] })
```

## Deterministic Hashing

Object property order doesn't matter:

```typescript
// These are the SAME key
useQuery({ queryKey: ['todos', { status: 'active', page: 1 }], ... })
useQuery({ queryKey: ['todos', { page: 1, status: 'active' }], ... })
// ✅ TanStack Query normalizes object keys
```

**But array order DOES matter:**

```typescript
// These are DIFFERENT keys
useQuery({ queryKey: ['todos', 'active'], ... })
useQuery({ queryKey: ['active', 'todos'], ... })
// ❌ Different cache entries
```

## Query Key Factory Pattern

Create a factory for consistent keys:

```typescript
const todoKeys = {
  all: ['todos'] as const,
  lists: () => [...todoKeys.all, 'list'] as const,
  list: (filters: string) => [...todoKeys.lists(), { filters }] as const,
  details: () => [...todoKeys.all, 'detail'] as const,
  detail: (id: number) => [...todoKeys.details(), id] as const,
}

// Usage
useQuery({
  queryKey: todoKeys.list('active'),
  queryFn: () => fetchTodos('active'),
})

useQuery({
  queryKey: todoKeys.detail(5),
  queryFn: () => fetchTodo(5),
})

// Invalidation
queryClient.invalidateQueries({ queryKey: todoKeys.all })       // All todos
queryClient.invalidateQueries({ queryKey: todoKeys.lists() })   // All lists
queryClient.invalidateQueries({ queryKey: todoKeys.detail(5) }) // Specific todo
```

## Keys as Dependencies

Query keys are used as dependencies for refetching:

```typescript
function Todos({ filter }: { filter: string }) {
  const { data } = useQuery({
    queryKey: ['todos', filter],
    queryFn: () => fetchTodos(filter),
  })

  // When filter changes, queryKey changes, triggering new fetch
  // filter: 'active' → filter: 'completed' = automatic refetch
}
```

## BudTags Examples

BudTags uses two key factory patterns. Keys live in dedicated `keys.ts` files per domain (e.g., `Hooks/metrc/keys.ts`, `Hooks/marketplace/keys.ts`).

### Pattern A: Flat Keys (Metrc Reference Data)

Top-level string is kebab-case. Used for Metrc data where granular list/detail invalidation is rarely needed.

```typescript
// File: resources/js/Hooks/metrc/keys.ts

export const metrcPackageKeys = {
    all: () => ['metrc-packages'] as const,
    byLicense: (license: string | null) =>
        [...metrcPackageKeys.all(), license] as const,
    paginated: (license: string | null, page: number, perPage: number, search: string, dateFilter: string, sortBy: string, sortDir: string) =>
        ['metrc-packages-paginated', license, page, perPage, search, dateFilter, sortBy, sortDir] as const,
    paginatedPrefix: (license: string | null) =>
        ['metrc-packages-paginated', license] as const,  // for broad prefix invalidation
    suggestions: (search: string) =>
        ['metrc-package-suggestions', search] as const,
};

export const metrcItemKeys = {
    all: () => ['metrc-items'] as const,
    byLicense: (license: string | null) =>
        [...metrcItemKeys.all(), license] as const,
};

export const metrcStrainKeys = {
    all: () => ['metrc-strains'] as const,
    byLicense: (license: string | null) =>
        [...metrcStrainKeys.all(), license] as const,
};
```

**Why `paginatedPrefix`?** It matches all paginated variants for a license regardless of page/filter params:
```typescript
// Invalidates ALL paginated pages for this license at once
queryClient.invalidateQueries({ queryKey: metrcPackageKeys.paginatedPrefix(license) });
```

### Pattern B: Hierarchical Keys (Marketplace Entities)

Full `all → lists → list → details → detail` hierarchy. Used for marketplace entities that need granular invalidation (e.g., invalidate all lists but keep detail caches).

```typescript
// File: resources/js/Hooks/marketplace/keys.ts

export const marketplaceOrderKeys = {
    all: (orgId: string, viewMode: 'seller' | 'buyer') =>
        ['marketplace-orders', orgId, viewMode] as const,
    lists: (orgId: string, viewMode: 'seller' | 'buyer') =>
        [...marketplaceOrderKeys.all(orgId, viewMode), 'list'] as const,
    list: (orgId: string, viewMode: 'seller' | 'buyer', filters?: object) =>
        [...marketplaceOrderKeys.lists(orgId, viewMode), filters] as const,
    details: (orgId: string, viewMode: 'seller' | 'buyer') =>
        [...marketplaceOrderKeys.all(orgId, viewMode), 'detail'] as const,
    detail: (orgId: string, viewMode: 'seller' | 'buyer', id: string) =>
        [...marketplaceOrderKeys.details(orgId, viewMode), id] as const,
};

export const customerKeys = {
    all: (orgId: string) => ['marketplace-customers', orgId] as const,
    lists: (orgId: string) => [...customerKeys.all(orgId), 'list'] as const,
    list: (orgId: string, filters?: object) =>
        [...customerKeys.lists(orgId), filters] as const,
    details: (orgId: string) => [...customerKeys.all(orgId), 'detail'] as const,
    detail: (orgId: string, id: string) =>
        [...customerKeys.details(orgId), id] as const,
    stats: (orgId: string) => [...customerKeys.all(orgId), 'stats'] as const,
};
```

**Granular invalidation in action:**
```typescript
// After accepting an order:
// Invalidate all order lists (seller + buyer) but keep detail caches
queryClient.invalidateQueries({ queryKey: marketplaceOrderKeys.lists(orgId, 'seller') });

// Invalidate a specific order detail
queryClient.invalidateQueries({ queryKey: marketplaceOrderKeys.detail(orgId, 'seller', orderId) });

// Nuclear option: invalidate ALL order data for this org/view
queryClient.invalidateQueries({ queryKey: marketplaceOrderKeys.all(orgId, 'seller') });
```

### When to Use Which Pattern

| Pattern | Use When | Example Domains |
|---------|----------|-----------------|
| **Flat** | Data is mostly lists, no separate detail views, simple invalidation | Metrc reference data (items, strains, UOM, categories) |
| **Hierarchical** | Need granular list vs detail invalidation, CRUD operations on entities | Marketplace (orders, products, customers), QuickBooks |

## Variable Query Keys

Use variables from props/state in keys:

```typescript
function Package({ packageId }: { packageId: number }) {
  const { user } = usePage<PageProps>().props

  const { data } = useQuery({
    queryKey: ['packages', packageId], // ← Key includes variable
    queryFn: () => fetchPackage(packageId),
  })

  // When packageId changes (e.g., route param), new query executes
}
```

## Serialization

Query keys are serialized with JSON.stringify for storage:

```typescript
// Valid keys (JSON-serializable)
['todos']                                    // ✅
['todos', 5]                                 // ✅
['todos', { status: 'active', page: 1 }]    // ✅
['todos', ['tag1', 'tag2']]                  // ✅

// Invalid keys (not JSON-serializable)
['todos', new Date()]                        // ❌
['todos', () => {}]                          // ❌
['todos', Symbol('key')]                     // ❌
```

## Query Key Best Practices

### ✅ DO

```typescript
// Use factory pattern
const keys = {
  all: ['todos'] as const,
  list: (filter: string) => [...keys.all, 'list', filter] as const,
}

// Include dependencies in key
useQuery({
  queryKey: ['todos', filter, sortBy],
  queryFn: () => fetchTodos(filter, sortBy),
})

// Use objects for complex filters
useQuery({
  queryKey: ['todos', { status, priority, assignee }],
  queryFn: () => fetchTodos({ status, priority, assignee }),
})

// Scope by organization/user
useQuery({
  queryKey: ['packages', orgId, license],
  queryFn: () => fetchPackages(orgId, license),
})
```

### ❌ DON'T

```typescript
// Don't use random/dynamic keys
useQuery({
  queryKey: [Math.random()], // ❌ New query every render
  queryFn: fetchTodos,
})

// Don't forget dependencies
useQuery({
  queryKey: ['todos'], // ❌ Missing filter
  queryFn: () => fetchTodos(filter), // ← Uses filter but not in key
})

// Don't use non-serializable values
useQuery({
  queryKey: ['todos', new Date()], // ❌ Date object
  queryFn: fetchTodos,
})
```

## Next Steps
- **Query Functions** → Read `10-query-functions.md`
- **Invalidation** → Read `14-invalidation-refetching.md`
- **TypeScript** → Read `06-typescript.md`
