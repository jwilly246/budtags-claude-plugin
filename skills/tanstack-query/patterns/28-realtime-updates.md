# Pattern 28: Real-Time Updates

## Real-Time Strategies Overview

Choose the right strategy for your use case:

| Strategy | When to Use | Pros | Cons |
|----------|------------|------|------|
| **Polling (refetchInterval)** | Data changes infrequently | Simple, works everywhere | Inefficient, polling delay |
| **WebSockets** | Real-time bidirectional | Instant updates, efficient | Complex setup, connection mgmt |
| **Server-Sent Events (SSE)** | Server pushes updates | Simpler than WebSockets | One-way only (server → client) |
| **Manual Invalidation** | User-triggered updates | Full control | Requires user action |

## Polling with refetchInterval

### Basic Polling

Automatically refetch at intervals:

```typescript
const { data } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  refetchInterval: 30000, // Poll every 30 seconds
})
```

### Stop Polling When Tab Inactive

Save resources when user is not viewing:

```typescript
const { data } = useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  refetchInterval: 30000, // Poll every 30s
  refetchIntervalInBackground: false, // Stop when tab inactive (default)
})
```

### Conditional Polling

Only poll when needed:

```typescript
const { data } = useQuery({
  queryKey: ['packages', filter],
  queryFn: () => fetchPackages(filter),
  refetchInterval: (query) => {
    const hasActivePackages = query.state.data?.some(pkg => !pkg.FinishedDate)

    // Poll every 30s if there are active packages, otherwise don't poll
    return hasActivePackages ? 30000 : false
  },
})
```

### Dynamic Polling Speed

Poll faster based on data state:

```typescript
const { data } = useQuery({
  queryKey: ['transfers', 'pending'],
  queryFn: fetchPendingTransfers,
  refetchInterval: (query) => {
    const transfers = query.state.data

    if (!transfers || transfers.length === 0) {
      return false // No pending transfers, stop polling
    }

    // Poll faster if there are many pending transfers
    if (transfers.length > 10) {
      return 10000 // 10 seconds
    }

    return 30000 // 30 seconds
  },
})
```

### Stop Polling on Condition

```typescript
const { data } = useQuery({
  queryKey: ['job', jobId],
  queryFn: () => fetchJobStatus(jobId),
  refetchInterval: (query) => {
    const job = query.state.data

    // Stop polling when job is complete
    if (job?.status === 'completed' || job?.status === 'failed') {
      return false
    }

    return 2000 // Poll every 2 seconds while running
  },
})
```

## WebSocket Integration

### Basic WebSocket Setup

Update cache on WebSocket messages:

```typescript
import { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'

function useWebSocketUpdates() {
  const queryClient = useQueryClient()

  useEffect(() => {
    const ws = new WebSocket('wss://api.example.com/ws')

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      const update = JSON.parse(event.data)

      // Update specific package
      if (update.type === 'PACKAGE_UPDATE') {
        queryClient.setQueryData(
          ['packages', update.packageId],
          update.data
        )

        // Invalidate list query
        queryClient.invalidateQueries({
          queryKey: ['packages'],
          refetchType: 'active', // Only refetch active queries
        })
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
    }

    return () => {
      ws.close()
    }
  }, [queryClient])
}
```

### WebSocket with Automatic Reconnection

```typescript
function useWebSocket(url: string) {
  const queryClient = useQueryClient()
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  useEffect(() => {
    let ws: WebSocket
    let reconnectTimeout: NodeJS.Timeout

    function connect() {
      ws = new WebSocket(url)

      ws.onopen = () => {
        console.log('WebSocket connected')
        reconnectAttempts.current = 0
      }

      ws.onmessage = (event) => {
        const update = JSON.parse(event.data)

        queryClient.setQueryData(
          ['packages', update.id],
          update.data
        )
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')

        // Attempt reconnection
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++
          const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 30000)

          console.log(`Reconnecting in ${delay}ms...`)
          reconnectTimeout = setTimeout(connect, delay)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        ws.close()
      }
    }

    connect()

    return () => {
      ws?.close()
      clearTimeout(reconnectTimeout)
    }
  }, [url, queryClient])
}
```

### Invalidate on WebSocket Event

Refetch queries when WebSocket receives update:

```typescript
function usePackageUpdates(license: string) {
  const queryClient = useQueryClient()

  useEffect(() => {
    const ws = new WebSocket(`wss://api.example.com/ws?license=${license}`)

    ws.onmessage = (event) => {
      const { type, packageId } = JSON.parse(event.data)

      if (type === 'PACKAGE_UPDATED') {
        // Invalidate specific package
        queryClient.invalidateQueries({
          queryKey: ['metrc', 'package', packageId],
        })

        // Invalidate package list
        queryClient.invalidateQueries({
          queryKey: ['metrc', 'packages', license],
        })

        toast.info('Package updated')
      }
    }

    return () => ws.close()
  }, [license, queryClient])

  return useQuery({
    queryKey: ['metrc', 'packages', license],
    queryFn: () => fetchPackages(license),
  })
}
```

## Server-Sent Events (SSE)

### Basic SSE Integration

```typescript
function useServerSentEvents(url: string) {
  const queryClient = useQueryClient()

  useEffect(() => {
    const eventSource = new EventSource(url)

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)

      queryClient.setQueryData(['realtime-data'], data)
    }

    eventSource.addEventListener('package-update', (event) => {
      const packageData = JSON.parse(event.data)

      queryClient.setQueryData(
        ['packages', packageData.id],
        packageData
      )
    })

    eventSource.onerror = (error) => {
      console.error('SSE error:', error)
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [url, queryClient])
}
```

### SSE with Reconnection

```typescript
function useSSE(endpoint: string) {
  const queryClient = useQueryClient()

  useEffect(() => {
    let eventSource: EventSource
    let reconnectTimeout: NodeJS.Timeout
    let reconnectAttempts = 0
    const maxReconnectAttempts = 5

    function connect() {
      eventSource = new EventSource(endpoint)

      eventSource.onopen = () => {
        console.log('SSE connected')
        reconnectAttempts = 0
      }

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data)
        queryClient.setQueryData(['sse-data'], data)
      }

      eventSource.onerror = () => {
        eventSource.close()

        if (reconnectAttempts < maxReconnectAttempts) {
          reconnectAttempts++
          const delay = Math.min(1000 * 2 ** reconnectAttempts, 30000)

          reconnectTimeout = setTimeout(connect, delay)
        }
      }
    }

    connect()

    return () => {
      eventSource?.close()
      clearTimeout(reconnectTimeout)
    }
  }, [endpoint, queryClient])
}
```

## BudTags Examples

### Polling Metrc Packages

Poll for active packages every 30 seconds:

```typescript
function useMetrcPackages(license: string, filter: 'active' | 'inactive') {
  const { user } = usePage<PageProps>().props

  return useQuery({
    queryKey: ['metrc', 'packages', license, filter],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages(license, filter)
    },
    refetchInterval: (query) => {
      // Only poll active packages
      if (filter !== 'active') return false

      // Stop polling if there's an error
      if (query.state.error) return false

      // Poll every 30 seconds
      return 30000
    },
    refetchIntervalInBackground: false, // Stop when tab inactive
    staleTime: 20 * 1000, // Consider data stale after 20 seconds
  })
}
```

### Laravel Echo Real-Time Label Approvals

```typescript
import Echo from 'laravel-echo'
import Pusher from 'pusher-js'

// Setup Echo (in App.tsx or similar)
window.Pusher = Pusher
window.Echo = new Echo({
  broadcaster: 'pusher',
  key: import.meta.env.VITE_PUSHER_APP_KEY,
  cluster: import.meta.env.VITE_PUSHER_APP_CLUSTER,
  forceTLS: true,
  authEndpoint: '/broadcasting/auth',
})

// Hook for real-time label updates
function useLabelApprovals(orgId: number) {
  const queryClient = useQueryClient()

  useEffect(() => {
    const channel = window.Echo.private(`org.${orgId}`)

    channel.listen('LabelApproved', (event: { labelId: number; approvedBy: string }) => {
      // Invalidate labels query
      queryClient.invalidateQueries({
        queryKey: ['labels', orgId],
      })

      // Show notification
      toast.success(`Label #${event.labelId} approved by ${event.approvedBy}`)
    })

    channel.listen('LabelRejected', (event: { labelId: number; reason: string }) => {
      queryClient.invalidateQueries({
        queryKey: ['labels', orgId],
      })

      toast.error(`Label #${event.labelId} rejected: ${event.reason}`)
    })

    return () => {
      window.Echo.leave(`org.${orgId}`)
    }
  }, [orgId, queryClient])

  return useQuery({
    queryKey: ['labels', orgId],
    queryFn: () => axios.get(`/api/org/${orgId}/labels`).then(r => r.data),
    // Fallback polling every 60 seconds
    refetchInterval: 60000,
  })
}
```

### Real-Time Transfer Check-In

```typescript
function useTransferCheckIn(transferId: number) {
  const queryClient = useQueryClient()
  const { user } = usePage<PageProps>().props
  const orgId = user.active_org.id

  useEffect(() => {
    // Subscribe to transfer updates
    window.Echo.private(`transfer.${transferId}`)
      .listen('PackageCheckedIn', (event: { packageId: number; label: string }) => {
        // Invalidate transfer data
        queryClient.invalidateQueries({
          queryKey: ['transfer', transferId],
        })

        toast.info(`Package ${event.label} checked in`)
      })
      .listen('TransferCompleted', (event: { transferId: number }) => {
        queryClient.invalidateQueries({
          queryKey: ['transfer', transferId],
        })

        toast.success('Transfer completed!')

        // Redirect to transfers list
        router.visit('/transfers/incoming')
      })

    return () => {
      window.Echo.leave(`transfer.${transferId}`)
    }
  }, [transferId, queryClient])

  return useQuery({
    queryKey: ['transfer', transferId],
    queryFn: () => fetchTransferDetails(transferId),
    refetchInterval: 10000, // Poll every 10 seconds as fallback
  })
}
```

### Conditional Polling Based on Filter

```typescript
function PackagesPage() {
  const [filter, setFilter] = useState<'active' | 'inactive'>('active')
  const license = usePage<PageProps>().props.session.license

  const { data, isFetching } = useQuery({
    queryKey: ['metrc', 'packages', license, filter],
    queryFn: () => fetchPackages(license, filter),
    refetchInterval: (query) => {
      // Only poll active packages
      if (filter === 'inactive') return false

      // Check if there are any active packages
      const hasActivePackages = query.state.data?.length > 0

      // Poll every 30 seconds if there are active packages
      return hasActivePackages ? 30000 : false
    },
    staleTime: 20 * 1000,
  })

  return (
    <div>
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setFilter('active')}
          className={filter === 'active' ? 'active' : ''}
        >
          Active {isFetching && filter === 'active' && '🔄'}
        </button>
        <button
          onClick={() => setFilter('inactive')}
          className={filter === 'inactive' ? 'active' : ''}
        >
          Inactive
        </button>
      </div>

      <DataTable data={data} />
    </div>
  )
}
```

### Real-Time Inventory Updates Across Licenses

```typescript
function useMultiLicenseUpdates(licenses: string[]) {
  const queryClient = useQueryClient()
  const { user } = usePage<PageProps>().props
  const orgId = user.active_org.id

  useEffect(() => {
    // Subscribe to organization-wide inventory updates
    const channel = window.Echo.private(`org.${orgId}.inventory`)

    channel.listen('InventoryUpdated', (event: {
      license: string
      packageId: number
      change: number
    }) => {
      // Invalidate packages for affected license
      queryClient.invalidateQueries({
        queryKey: ['metrc', 'packages', event.license],
      })

      // Show notification if it's one of our monitored licenses
      if (licenses.includes(event.license)) {
        toast.info(
          `Inventory updated for ${event.license}: Package #${event.packageId}`,
          { autoClose: 3000 }
        )
      }
    })

    return () => {
      window.Echo.leave(`org.${orgId}.inventory`)
    }
  }, [orgId, licenses, queryClient])
}
```

### Live Job Status Updates

```typescript
function useLabelGenerationJob(jobId: string) {
  const queryClient = useQueryClient()

  // Poll job status
  const { data: job } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => axios.get(`/api/jobs/${jobId}`).then(r => r.data),
    refetchInterval: (query) => {
      const job = query.state.data

      // Stop polling when job is complete
      if (job?.status === 'completed' || job?.status === 'failed') {
        return false
      }

      // Poll every 2 seconds while processing
      return 2000
    },
  })

  // Also listen via WebSocket for instant updates
  useEffect(() => {
    window.Echo.private(`job.${jobId}`)
      .listen('JobProgressUpdated', (event: { progress: number }) => {
        queryClient.setQueryData(['job', jobId], (old: any) => ({
          ...old,
          progress: event.progress,
        }))
      })
      .listen('JobCompleted', (event: { result: any }) => {
        queryClient.setQueryData(['job', jobId], (old: any) => ({
          ...old,
          status: 'completed',
          result: event.result,
        }))

        toast.success('Label generation completed!')
      })
      .listen('JobFailed', (event: { error: string }) => {
        queryClient.setQueryData(['job', jobId], (old: any) => ({
          ...old,
          status: 'failed',
          error: event.error,
        }))

        toast.error(`Label generation failed: ${event.error}`)
      })

    return () => {
      window.Echo.leave(`job.${jobId}`)
    }
  }, [jobId, queryClient])

  return job
}
```

## Next Steps

- **Background Fetching** → Read `23-background-fetching-indicators.md` for isFetching indicators
- **Network Mode** → Read `24-network-mode.md` for handling offline scenarios
- **Optimistic Updates** → Read `15-optimistic-updates.md` for instant UI updates
