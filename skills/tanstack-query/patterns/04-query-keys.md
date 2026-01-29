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

### Organization-Scoped Keys

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

// Usage
function Packages() {
  const { user } = usePage<PageProps>().props
  const orgId = user.active_org.id

  const { data } = useQuery({
    queryKey: packageKeys.list(orgId, { status: 'active' }),
    queryFn: () => fetchPackages(orgId, { status: 'active' }),
  })
}
```

### License-Specific Metrc Keys

```typescript
const metrcKeys = {
  all: (license: string) => ['metrc', license] as const,

  packages: (license: string) => [...metrcKeys.all(license), 'packages'] as const,
  package: (license: string, id: number) =>
    [...metrcKeys.packages(license), id] as const,

  plants: (license: string) => [...metrcKeys.all(license), 'plants'] as const,
  plant: (license: string, id: number) =>
    [...metrcKeys.plants(license), id] as const,

  harvests: (license: string) => [...metrcKeys.all(license), 'harvests'] as const,
  harvest: (license: string, id: number) =>
    [...metrcKeys.harvests(license), id] as const,
}

// Usage
function MetrcPackages() {
  const license = usePage<PageProps>().props.session.license

  const { data: packages } = useQuery({
    queryKey: metrcKeys.packages(license),
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages(license)
    },
  })

  const { data: package } = useQuery({
    queryKey: metrcKeys.package(license, packageId),
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.package_by_id(license, packageId)
    },
  })
}

// Switch license → invalidate all Metrc data
const handleLicenseChange = (newLicense: string) => {
  const oldLicense = session.license
  queryClient.invalidateQueries({ queryKey: metrcKeys.all(oldLicense) })
}
```

### Feature-Specific Keys

```typescript
const labelKeys = {
  all: (orgId: number) => ['labels', orgId] as const,
  pending: (orgId: number) => [...labelKeys.all(orgId), 'pending'] as const,
  approved: (orgId: number) => [...labelKeys.all(orgId), 'approved'] as const,
  printed: (orgId: number) => [...labelKeys.all(orgId), 'printed'] as const,
}

const strainKeys = {
  all: (orgId: number) => ['strains', orgId] as const,
  list: (orgId: number) => [...strainKeys.all(orgId), 'list'] as const,
  detail: (orgId: number, id: number) => [...strainKeys.all(orgId), 'detail', id] as const,
}

const userKeys = {
  all: (orgId: number) => ['users', orgId] as const,
  me: () => ['users', 'me'] as const,
  profile: (userId: number) => ['users', 'profile', userId] as const,
}
```

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
