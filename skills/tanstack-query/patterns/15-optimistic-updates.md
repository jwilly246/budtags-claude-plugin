# Pattern 15: Optimistic Updates

## What are Optimistic Updates?

Update the UI immediately before the server responds, making the app feel instant.

## Two Approaches

### 1. UI Variables (Simple)

Use mutation variables to show optimistic state:

```typescript
function ToggleTodo({ todo }: { todo: Todo }) {
  const mutation = useMutation({
    mutationFn: (id: number) => toggleTodo(id),
  })

  return (
    <div>
      <input
        type="checkbox"
        checked={mutation.isPending ? !todo.done : todo.done}
        onChange={() => mutation.mutate(todo.id)}
      />
      {todo.text}
    </div>
  )
}
```

### 2. Cache Manipulation (Advanced)

Directly update the cache for complex UIs:

```typescript
const mutation = useMutation({
  mutationFn: updatePackage,
  onMutate: async (newPackage) => {
    // Cancel outgoing queries
    await queryClient.cancelQueries({ queryKey: ['packages'] })

    // Snapshot previous value
    const previousPackages = queryClient.getQueryData(['packages'])

    // Optimistically update cache
    queryClient.setQueryData(['packages'], (old: Package[]) =>
      old.map(pkg => pkg.id === newPackage.id ? { ...pkg, ...newPackage } : pkg)
    )

    // Return context with snapshot
    return { previousPackages }
  },
  onError: (err, newPackage, context) => {
    // Rollback on error
    queryClient.setQueryData(['packages'], context.previousPackages)
    toast.error('Update failed')
  },
  onSettled: () => {
    // Always refetch after error or success
    queryClient.invalidateQueries({ queryKey: ['packages'] })
  },
})
```

## Complete Optimistic Update Pattern

```typescript
const updateMutation = useMutation({
  mutationFn: (pkg: Package) => axios.put(`/packages/${pkg.id}`, pkg),

  // Step 1: Before mutation (optimistic update)
  onMutate: async (newPackage) => {
    // Cancel outgoing refetches (prevent race conditions)
    await queryClient.cancelQueries({ queryKey: ['packages', newPackage.id] })

    // Snapshot current value
    const previousPackage = queryClient.getQueryData(['packages', newPackage.id])

    // Optimistically update cache
    queryClient.setQueryData(['packages', newPackage.id], newPackage)

    // Return context
    return { previousPackage }
  },

  // Step 2a: If mutation fails (rollback)
  onError: (err, newPackage, context) => {
    queryClient.setQueryData(['packages', newPackage.id], context.previousPackage)
    toast.error('Update failed')
  },

  // Step 2b: If mutation succeeds (optional: update with server data)
  onSuccess: (data, variables) => {
    queryClient.setQueryData(['packages', variables.id], data)
    toast.success('Package updated')
  },

  // Step 3: Always run (refetch to ensure sync)
  onSettled: (data, error, variables) => {
    queryClient.invalidateQueries({ queryKey: ['packages', variables.id] })
  },
})
```

## BudTags Examples

### Finish Package Optimistically

```typescript
function useFinishPackage() {
  const queryClient = useQueryClient()
  const license = usePage<PageProps>().props.session.license

  return useMutation({
    mutationFn: (id: number) => axios.post(`/metrc/packages/${id}/finish`),
    onMutate: async (id) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['metrc', 'packages', license] })

      // Snapshot previous packages
      const previousPackages = queryClient.getQueryData(['metrc', 'packages', license])

      // Optimistically update
      queryClient.setQueryData(['metrc', 'packages', license], (old: Package[]) =>
        old.map(pkg =>
          pkg.Id === id
            ? { ...pkg, FinishedDate: new Date().toISOString() }
            : pkg
        )
      )

      return { previousPackages }
    },
    onError: (err, id, context) => {
      // Rollback on error
      queryClient.setQueryData(
        ['metrc', 'packages', license],
        context.previousPackages
      )
      toast.error('Failed to finish package')
    },
    onSettled: () => {
      // Always refetch
      queryClient.invalidateQueries({ queryKey: ['metrc', 'packages', license] })
    },
  })
}

// Usage
function PackageRow({ pkg }: { pkg: Package }) {
  const finishMutation = useFinishPackage()

  return (
    <tr className={pkg.FinishedDate ? 'opacity-50' : ''}>
      <td>{pkg.Label}</td>
      <td>
        <button
          onClick={() => finishMutation.mutate(pkg.Id)}
          disabled={!!pkg.FinishedDate}
        >
          {pkg.FinishedDate ? 'Finished' : 'Finish'}
        </button>
      </td>
    </tr>
  )
}
```

### Toggle Active/Inactive

```typescript
function useToggleActive() {
  const queryClient = useQueryClient()
  const { user } = usePage<PageProps>().props
  const orgId = user.active_org.id

  return useMutation({
    mutationFn: ({ id, active }: { id: number; active: boolean }) =>
      axios.put(`/strains/${id}`, { active }),
    onMutate: async ({ id, active }) => {
      await queryClient.cancelQueries({ queryKey: ['strains', orgId] })

      const previousStrains = queryClient.getQueryData(['strains', orgId])

      // Optimistically toggle
      queryClient.setQueryData(['strains', orgId], (old: Strain[]) =>
        old.map(strain =>
          strain.id === id ? { ...strain, active } : strain
        )
      )

      return { previousStrains }
    },
    onError: (err, variables, context) => {
      queryClient.setQueryData(['strains', orgId], context.previousStrains)
      toast.error('Failed to toggle strain')
    },
    onSuccess: () => {
      toast.success('Strain updated')
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['strains', orgId] })
    },
  })
}
```

### Inline Edit with Optimistic Update

```typescript
function EditableCell({ package, field }: { package: Package; field: keyof Package }) {
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [value, setValue] = useState(package[field])

  const updateMutation = useMutation({
    mutationFn: (data) => axios.put(`/packages/${package.id}`, data),
    onMutate: async (newData) => {
      await queryClient.cancelQueries({ queryKey: ['packages'] })

      const previousPackages = queryClient.getQueryData(['packages'])

      queryClient.setQueryData(['packages'], (old: Package[]) =>
        old.map(pkg =>
          pkg.id === package.id ? { ...pkg, ...newData } : pkg
        )
      )

      return { previousPackages }
    },
    onError: (err, newData, context) => {
      queryClient.setQueryData(['packages'], context.previousPackages)
      setValue(package[field]) // Reset to original
      toast.error('Update failed')
    },
    onSuccess: () => {
      setIsEditing(false)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] })
    },
  })

  const handleSave = () => {
    updateMutation.mutate({ [field]: value })
  }

  if (isEditing) {
    return (
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onBlur={handleSave}
        autoFocus
      />
    )
  }

  return <span onClick={() => setIsEditing(true)}>{value}</span>
}
```

### Bulk Selection with Optimistic UI

```typescript
function useBulkFinish() {
  const queryClient = useQueryClient()
  const license = usePage<PageProps>().props.session.license

  return useMutation({
    mutationFn: (ids: number[]) =>
      axios.post('/metrc/packages/bulk-finish', { ids }),
    onMutate: async (ids) => {
      await queryClient.cancelQueries({ queryKey: ['metrc', 'packages', license] })

      const previousPackages = queryClient.getQueryData(['metrc', 'packages', license])

      const finishedDate = new Date().toISOString()

      queryClient.setQueryData(['metrc', 'packages', license], (old: Package[]) =>
        old.map(pkg =>
          ids.includes(pkg.Id)
            ? { ...pkg, FinishedDate: finishedDate }
            : pkg
        )
      )

      return { previousPackages }
    },
    onError: (err, ids, context) => {
      queryClient.setQueryData(
        ['metrc', 'packages', license],
        context.previousPackages
      )
      toast.error('Failed to finish packages')
    },
    onSuccess: (data, ids) => {
      toast.success(`Finished ${ids.length} packages`)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['metrc', 'packages', license] })
    },
  })
}
```

## Race Condition Prevention

Always cancel outgoing queries before optimistic updates:

```typescript
onMutate: async (newData) => {
  // ✅ Prevent race condition
  await queryClient.cancelQueries({ queryKey: ['packages'] })

  // Now safe to update
  queryClient.setQueryData(['packages'], newData)
}
```

Without cancellation:
```
1. User updates package → Optimistic update
2. Background refetch starts (from previous invalidation)
3. Optimistic update completes
4. Background refetch completes → Overwrites optimistic update
5. User sees old data briefly (race condition)
```

## useMutationState for Cross-Component Updates

Access mutation state from other components:

```typescript
import { useMutationState } from '@tanstack/react-query'

function PendingMutations() {
  const pending = useMutationState({
    filters: { status: 'pending' },
  })

  return <div>{pending.length} mutations pending...</div>
}
```

## Next Steps
- **Mutations** → Read `13-mutations.md`
- **Invalidation** → Read `14-invalidation-refetching.md`
- **Cache Updates** → Read `20-cache-updates.md`
