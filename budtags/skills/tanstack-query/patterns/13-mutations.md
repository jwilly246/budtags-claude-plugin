# Pattern 13: Mutations

> **⚠️ BudTags Note:** Examples in this file show `confirm()` for simplicity. In BudTags, **NEVER use `confirm()` or `window.confirm()`**. Use a modal-based confirmation component or the `useConfirmDelete` hook instead.

## useMutation Hook

Use mutations for CREATE, UPDATE, DELETE operations:

```typescript
import { useMutation } from '@tanstack/react-query'

function CreatePackage() {
  const mutation = useMutation({
    mutationFn: (newPackage) => {
      return fetch('/api/packages', {
        method: 'POST',
        body: JSON.stringify(newPackage),
      })
    },
  })

  const handleCreate = () => {
    mutation.mutate({
      label: '1A4...',
      productId: 123,
    })
  }

  return (
    <button onClick={handleCreate} disabled={mutation.isPending}>
      {mutation.isPending ? 'Creating...' : 'Create Package'}
    </button>
  )
}
```

## Mutation States

```typescript
const mutation = useMutation({
  mutationFn: createPackage,
})

// States
mutation.status       // 'idle' | 'pending' | 'error' | 'success'
mutation.isPending    // status === 'pending'
mutation.isError      // status === 'error'
mutation.isSuccess    // status === 'success'
mutation.isIdle       // status === 'idle'

// Data
mutation.data         // Response data (if success)
mutation.error        // Error object (if error)
mutation.variables    // Variables passed to mutate()
```

## mutate vs mutateAsync

### mutate (Recommended)

```typescript
const mutation = useMutation({
  mutationFn: createPackage,
  onSuccess: (data) => {
    toast.success('Package created')
  },
  onError: (error) => {
    toast.error(error.message)
  },
})

// Fire and forget
mutation.mutate({ label: '1A4...' })
```

### mutateAsync

Returns a promise:

```typescript
const mutation = useMutation({
  mutationFn: createPackage,
})

const handleCreate = async () => {
  try {
    const data = await mutation.mutateAsync({ label: '1A4...' })
    toast.success('Package created')
  } catch (error) {
    toast.error(error.message)
  }
}
```

**When to use mutateAsync:**
- Need to await the result
- Complex async workflows
- Multiple sequential mutations

## Side Effects

### onSuccess

```typescript
const mutation = useMutation({
  mutationFn: createPackage,
  onSuccess: (data, variables, context) => {
    // data: API response
    // variables: Input passed to mutate()
    // context: Value returned from onMutate

    toast.success('Package created')
    queryClient.invalidateQueries({ queryKey: ['packages'] })
  },
})
```

### onError

```typescript
const mutation = useMutation({
  mutationFn: createPackage,
  onError: (error, variables, context) => {
    // error: Error object
    // variables: Input passed to mutate()
    // context: Value returned from onMutate

    toast.error(error.message)
  },
})
```

### onSettled

Runs after success OR error:

```typescript
const mutation = useMutation({
  mutationFn: createPackage,
  onSettled: (data, error, variables, context) => {
    // Always runs after mutation completes
    queryClient.invalidateQueries({ queryKey: ['packages'] })
  },
})
```

### onMutate

Runs before mutation function:

```typescript
const mutation = useMutation({
  mutationFn: updatePackage,
  onMutate: async (variables) => {
    // Cancel outgoing queries
    await queryClient.cancelQueries({ queryKey: ['packages'] })

    // Snapshot previous value
    const previousPackages = queryClient.getQueryData(['packages'])

    // Optimistically update
    queryClient.setQueryData(['packages'], (old) => {
      return old.map(pkg =>
        pkg.id === variables.id ? { ...pkg, ...variables } : pkg
      )
    })

    // Return context with snapshot
    return { previousPackages }
  },
  onError: (err, variables, context) => {
    // Rollback on error
    queryClient.setQueryData(['packages'], context.previousPackages)
  },
})
```

## Invalidating Queries After Mutation

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'

function CreatePackage() {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: createPackage,
    onSuccess: () => {
      // Invalidate and refetch packages
      queryClient.invalidateQueries({ queryKey: ['packages'] })
    },
  })

  return <button onClick={() => mutation.mutate(data)}>Create</button>
}
```

## Retry for Mutations

By default, mutations don't retry (unlike queries):

```typescript
const mutation = useMutation({
  mutationFn: createPackage,
  retry: 0, // Default: no retries
})

// Enable retries
const mutation = useMutation({
  mutationFn: createPackage,
  retry: 3, // Retry 3 times
})
```

## reset()

Clear mutation state:

```typescript
const mutation = useMutation({
  mutationFn: createPackage,
})

// After error or success
mutation.reset() // Clear to idle state
```

## BudTags Examples

### Create Metrc Package

```typescript
function CreatePackageForm() {
  const queryClient = useQueryClient()
  const { user } = usePage<PageProps>().props
  const license = usePage<PageProps>().props.session.license
  const { data, setData } = useForm({
    tag: '',
    quantity: 0,
    itemId: 0,
  })

  const mutation = useMutation({
    mutationFn: async (packageData) => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.create_package(license, packageData)
    },
    onSuccess: () => {
      // Invalidate packages list
      queryClient.invalidateQueries({ queryKey: ['metrc', 'packages', license] })

      // Show success
      toast.success('Package created successfully')

      // Reset form
      setData({ tag: '', quantity: 0, itemId: 0 })
    },
    onError: (error) => {
      toast.error(error.response?.data?.message || 'Failed to create package')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate(data)
  }

  return (
    <form onSubmit={handleSubmit}>
      <InputText value={data.tag} onChange={(e) => setData('tag', e.target.value)} />
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Creating...' : 'Create Package'}
      </button>
    </form>
  )
}
```

### Modal with Mutation

```typescript
function AdjustPackageModal({ pkg, isOpen, onClose }: Props) {
  const queryClient = useQueryClient()
  const { data, setData } = useForm({
    quantity: 0,
    reason: '',
  })

  const mutation = useMutation({
    mutationFn: (adjustData) =>
      axios.post(`/metrc/packages/${pkg.Id}/adjust`, adjustData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['metrc', 'packages'] })
      toast.success('Package adjusted')
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.message || 'Adjustment failed')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate(data)
  }

  return (
    <Modal show={isOpen} onClose={onClose}>
      <form onSubmit={handleSubmit}>
        <InputNumber
          value={data.quantity}
          onChange={(e) => setData('quantity', parseFloat(e.target.value))}
        />
        <InputSelect
          value={data.reason}
          onChange={(e) => setData('reason', e.target.value)}
        />
        <button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? 'Adjusting...' : 'Adjust Package'}
        </button>
      </form>
    </Modal>
  )
}
```

### Delete with Confirmation

```typescript
function DeletePackageButton({ pkg }: { pkg: Package }) {
  const queryClient = useQueryClient()

  const deleteMutation = useMutation({
    mutationFn: (id: number) => axios.delete(`/packages/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] })
      toast.success('Package deleted')
    },
    onError: () => {
      toast.error('Failed to delete package')
    },
  })

  const handleDelete = () => {
    if (confirm(`Delete package ${pkg.Label}?`)) {
      deleteMutation.mutate(pkg.Id)
    }
  }

  return (
    <button onClick={handleDelete} disabled={deleteMutation.isPending}>
      {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
    </button>
  )
}
```

### Bulk Mutation

```typescript
function FinishPackages({ packageIds }: { packageIds: number[] }) {
  const queryClient = useQueryClient()

  const finishMutation = useMutation({
    mutationFn: (ids: number[]) =>
      axios.post('/metrc/packages/finish', { ids }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['metrc', 'packages'] })
      toast.success(`Finished ${packageIds.length} packages`)
    },
    onError: () => {
      toast.error('Failed to finish packages')
    },
  })

  return (
    <button
      onClick={() => finishMutation.mutate(packageIds)}
      disabled={finishMutation.isPending}
    >
      {finishMutation.isPending
        ? 'Finishing...'
        : `Finish ${packageIds.length} Packages`}
    </button>
  )
}
```

## Next Steps
- **Invalidation** → Read `14-invalidation-refetching.md`
- **Optimistic Updates** → Read `15-optimistic-updates.md`
- **Error Handling** → Read error examples in this pattern
