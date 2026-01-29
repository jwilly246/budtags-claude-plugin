# Pattern 29: Offline-First Patterns

## Offline-First Overview

Offline-first applications work without an internet connection by:

1. **Cache Persistence** - Save query cache to local storage
2. **Mutation Queue** - Queue mutations when offline, sync when online
3. **Background Sync** - Sync pending operations via Service Worker
4. **Optimistic Updates** - Update UI immediately, sync in background

**When to use in BudTags:**
- Mobile devices with unreliable connections
- Field workers (cultivation, harvest) needing offline access
- Viewing cached Metrc data when API is down
- Creating labels offline, syncing later

## Cache Persistence (localStorage)

### Basic Setup

Persist queries to localStorage:

```typescript
import { QueryClient } from '@tanstack/react-query'
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client'
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister'

// Create persister
const persister = createSyncStoragePersister({
  storage: window.localStorage,
  key: 'REACT_QUERY_OFFLINE_CACHE',
})

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      gcTime: 1000 * 60 * 60 * 24, // 24 hours
    },
  },
})

// Wrap app
function App() {
  return (
    <PersistQueryClientProvider
      client={queryClient}
      persistOptions={{ persister }}
    >
      <YourApp />
    </PersistQueryClientProvider>
  )
}
```

### Selective Persistence

Exclude sensitive data from cache:

```typescript
const persister = createSyncStoragePersister({
  storage: window.localStorage,
  serialize: (data) => {
    // Filter out sensitive queries
    const filtered = {
      ...data,
      clientState: {
        ...data.clientState,
        queries: data.clientState.queries.filter((query) => {
          const queryKey = query.queryKey

          // Exclude secrets and API keys
          if (queryKey.includes('secrets')) return false
          if (queryKey.includes('api-keys')) return false
          if (queryKey.includes('auth')) return false

          return true
        }),
      },
    }
    return JSON.stringify(filtered)
  },
  deserialize: (cachedString) => {
    return JSON.parse(cachedString)
  },
})
```

### Cache Versioning

Migrate cache when schema changes:

```typescript
const CACHE_VERSION = 2

const persister = createSyncStoragePersister({
  storage: window.localStorage,
  key: `REACT_QUERY_CACHE_V${CACHE_VERSION}`,
})

// Clear old cache versions
function clearOldCaches() {
  for (let i = 1; i < CACHE_VERSION; i++) {
    window.localStorage.removeItem(`REACT_QUERY_CACHE_V${i}`)
  }
}

clearOldCaches()
```

### Max Cache Size

Limit cache size to prevent storage quota errors:

```typescript
const MAX_CACHE_SIZE = 5 * 1024 * 1024 // 5MB

const persister = createSyncStoragePersister({
  storage: window.localStorage,
  serialize: (data) => {
    const serialized = JSON.stringify(data)

    if (serialized.length > MAX_CACHE_SIZE) {
      console.warn('Cache too large, clearing old queries')

      // Keep only recent queries
      const filtered = {
        ...data,
        clientState: {
          ...data.clientState,
          queries: data.clientState.queries.slice(-50), // Keep last 50 queries
        },
      }

      return JSON.stringify(filtered)
    }

    return serialized
  },
})
```

## Cache Persistence (IndexedDB)

### Async Persistence with IndexedDB

Better for large datasets:

```typescript
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister'
import { get, set, del } from 'idb-keyval'

const persister = createAsyncStoragePersister({
  storage: {
    getItem: async (key) => await get(key),
    setItem: async (key, value) => await set(key, value),
    removeItem: async (key) => await del(key),
  },
  key: 'REACT_QUERY_OFFLINE_CACHE',
})

// Use with PersistQueryClientProvider
<PersistQueryClientProvider
  client={queryClient}
  persistOptions={{ persister }}
>
  <App />
</PersistQueryClientProvider>
```

### IndexedDB with Compression

Compress large datasets:

```typescript
import { get, set, del } from 'idb-keyval'
import pako from 'pako'

const persister = createAsyncStoragePersister({
  storage: {
    getItem: async (key) => {
      const compressed = await get(key)
      if (!compressed) return null

      // Decompress
      const decompressed = pako.inflate(compressed, { to: 'string' })
      return JSON.parse(decompressed)
    },
    setItem: async (key, value) => {
      // Compress before storing
      const json = JSON.stringify(value)
      const compressed = pako.deflate(json)
      await set(key, compressed)
    },
    removeItem: async (key) => await del(key),
  },
})
```

## Mutation Queue (Offline Sync)

### Basic Mutation Queue

Queue mutations when offline:

```typescript
import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'

interface QueuedMutation {
  id: string
  url: string
  method: string
  data: any
  timestamp: number
}

function useMutationQueue() {
  const [queue, setQueue] = useState<QueuedMutation[]>([])
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const queryClient = useQueryClient()

  // Listen for online/offline events
  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Load queue from localStorage
  useEffect(() => {
    const savedQueue = localStorage.getItem('mutation-queue')
    if (savedQueue) {
      setQueue(JSON.parse(savedQueue))
    }
  }, [])

  // Save queue to localStorage
  useEffect(() => {
    localStorage.setItem('mutation-queue', JSON.stringify(queue))
  }, [queue])

  // Add mutation to queue
  const enqueueMutation = (mutation: Omit<QueuedMutation, 'id' | 'timestamp'>) => {
    const queuedMutation: QueuedMutation = {
      ...mutation,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
    }

    setQueue((prev) => [...prev, queuedMutation])

    if (!isOnline) {
      toast.info('Queued for sync when online')
    }
  }

  // Process queued mutations
  const processMutation = useMutation({
    mutationFn: async (mutations: QueuedMutation[]) => {
      const results = []

      for (const mutation of mutations) {
        try {
          const response = await fetch(mutation.url, {
            method: mutation.method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(mutation.data),
          })

          if (!response.ok) throw new Error('Request failed')

          results.push({ id: mutation.id, success: true })
        } catch (error) {
          results.push({ id: mutation.id, success: false, error })
        }
      }

      return results
    },
    onSuccess: (results) => {
      // Remove successful mutations from queue
      const successfulIds = results
        .filter((r) => r.success)
        .map((r) => r.id)

      setQueue((prev) => prev.filter((m) => !successfulIds.includes(m.id)))

      const successCount = successfulIds.length
      const failCount = results.length - successCount

      if (successCount > 0) {
        toast.success(`Synced ${successCount} change${successCount > 1 ? 's' : ''}`)
      }

      if (failCount > 0) {
        toast.error(`Failed to sync ${failCount} change${failCount > 1 ? 's' : ''}`)
      }

      // Invalidate queries
      queryClient.invalidateQueries()
    },
  })

  // Auto-process queue when coming online
  useEffect(() => {
    if (isOnline && queue.length > 0) {
      toast.info(`Syncing ${queue.length} queued change${queue.length > 1 ? 's' : ''}...`)
      processMutation.mutate(queue)
    }
  }, [isOnline])

  return {
    queue,
    isOnline,
    enqueueMutation,
    processQueue: () => processMutation.mutate(queue),
    clearQueue: () => setQueue([]),
  }
}
```

### Optimistic Updates with Queue

Update UI immediately, queue for sync:

```typescript
function useOptimisticMutation() {
  const queryClient = useQueryClient()
  const { enqueueMutation, isOnline } = useMutationQueue()

  return useMutation({
    mutationFn: async (data) => {
      if (!isOnline) {
        // Queue for later
        enqueueMutation({
          url: '/api/packages',
          method: 'POST',
          data,
        })
        return { queued: true, data }
      }

      // Online: execute immediately
      return axios.post('/api/packages', data)
    },
    onMutate: async (data) => {
      // Cancel outgoing queries
      await queryClient.cancelQueries({ queryKey: ['packages'] })

      // Snapshot previous value
      const previousPackages = queryClient.getQueryData(['packages'])

      // Optimistically update
      queryClient.setQueryData(['packages'], (old: any[]) => [
        ...old,
        { ...data, id: 'temp-' + Date.now(), _queued: !isOnline },
      ])

      return { previousPackages }
    },
    onError: (err, data, context) => {
      // Rollback on error
      queryClient.setQueryData(['packages'], context.previousPackages)
      toast.error('Failed to create package')
    },
    onSuccess: () => {
      toast.success(isOnline ? 'Package created' : 'Package queued for sync')
    },
  })
}
```

## Background Sync API

### Service Worker Background Sync

Sync pending operations via Service Worker:

```typescript
// In your service worker (service-worker.js)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-mutations') {
    event.waitUntil(syncMutations())
  }
})

async function syncMutations() {
  const queue = await getQueueFromIndexedDB()

  for (const mutation of queue) {
    try {
      await fetch(mutation.url, {
        method: mutation.method,
        body: JSON.stringify(mutation.data),
      })

      await removeFromQueue(mutation.id)
    } catch (error) {
      console.error('Sync failed:', error)
    }
  }
}

// In your React app
function useBackgroundSync() {
  const registerSync = async () => {
    if ('serviceWorker' in navigator && 'sync' in registration) {
      const registration = await navigator.serviceWorker.ready
      await registration.sync.register('sync-mutations')
    }
  }

  return { registerSync }
}
```

## BudTags Examples

### Offline Metrc Package Viewing

Cache packages for offline viewing:

```typescript
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client'
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister'

const persister = createSyncStoragePersister({
  storage: window.localStorage,
  key: 'BUDTAGS_CACHE',
  serialize: (data) => {
    // Only cache Metrc packages, not secrets
    const filtered = {
      ...data,
      clientState: {
        ...data.clientState,
        queries: data.clientState.queries.filter((query) => {
          const key = query.queryKey
          // Cache Metrc data
          if (key.includes('metrc')) return true
          // Cache facilities
          if (key.includes('facilities')) return true
          // Cache strains
          if (key.includes('strains')) return true
          // Don't cache secrets
          if (key.includes('secrets')) return false
          return true
        }),
      },
    }
    return JSON.stringify(filtered)
  },
})

function App() {
  return (
    <PersistQueryClientProvider
      client={queryClient}
      persistOptions={{ persister }}
    >
      <BudTagsApp />
    </PersistQueryClientProvider>
  )
}
```

### Offline Label Creation

Create labels offline, sync when online:

```typescript
function CreateLabelModal({ packages, isOpen, onClose }: Props) {
  const { enqueueMutation, isOnline } = useMutationQueue()
  const { data, setData } = useForm({
    templateId: 0,
    packageIds: [],
  })

  const createLabels = useMutation({
    mutationFn: async (labelData) => {
      if (!isOnline) {
        // Queue for later
        enqueueMutation({
          url: '/api/labels',
          method: 'POST',
          data: labelData,
        })
        return { queued: true }
      }

      // Online: create immediately
      return axios.post('/api/labels', labelData)
    },
    onSuccess: (response) => {
      if (response.queued) {
        toast.info('Labels queued. Will sync when online.')
      } else {
        toast.success('Labels created')
      }
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createLabels.mutate(data)
  }

  return (
    <Modal show={isOpen} onClose={onClose}>
      <form onSubmit={handleSubmit}>
        {!isOnline && (
          <div className="bg-yellow-100 p-3 rounded mb-4">
            ⚠️ Offline mode: Labels will be queued for sync
          </div>
        )}

        <InputSelect
          label="Template"
          value={data.templateId}
          onChange={(e) => setData('templateId', parseInt(e.target.value))}
        />

        <button type="submit" disabled={createLabels.isPending}>
          {createLabels.isPending ? 'Creating...' : 'Create Labels'}
        </button>
      </form>
    </Modal>
  )
}
```

### Offline Indicator with Sync Queue

Show offline status and queued changes:

```typescript
function OfflineIndicator() {
  const { queue, isOnline, processQueue } = useMutationQueue()

  if (isOnline && queue.length === 0) {
    return null // Hide when online and queue is empty
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {!isOnline && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded-lg shadow-lg flex items-center gap-3">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6z" />
          </svg>
          <div>
            <p className="font-medium">Offline Mode</p>
            {queue.length > 0 && (
              <p className="text-sm">
                {queue.length} change{queue.length > 1 ? 's' : ''} queued
              </p>
            )}
          </div>
        </div>
      )}

      {isOnline && queue.length > 0 && (
        <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded-lg shadow-lg">
          <p className="font-medium">
            {queue.length} change{queue.length > 1 ? 's' : ''} ready to sync
          </p>
          <button
            onClick={processQueue}
            className="mt-2 w-full px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Sync Now
          </button>
        </div>
      )}
    </div>
  )
}
```

### License Data Persistence

Cache license data across sessions:

```typescript
function useLicenseData(license: string) {
  const { user } = usePage<PageProps>().props

  return useQuery({
    queryKey: ['metrc', 'facility', license],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.facilities().then(facilities =>
        facilities.find(f => f.License.Number === license)
      )
    },
    staleTime: 60 * 60 * 1000, // 1 hour
    gcTime: 24 * 60 * 60 * 1000, // 24 hours (persisted)
    networkMode: 'offlineFirst', // Try cache first, then network
  })
}
```

### Strain Images Offline Cache

Cache strain images for offline viewing:

```typescript
function useStrainWithImages(strainId: number) {
  const { data: strain } = useQuery({
    queryKey: ['strain', strainId],
    queryFn: () => axios.get(`/api/strains/${strainId}`).then(r => r.data),
    gcTime: 24 * 60 * 60 * 1000, // Cache for 24 hours
  })

  // Prefetch images
  const { data: images } = useQuery({
    queryKey: ['strain', strainId, 'images'],
    queryFn: async () => {
      const imageUrls = strain.images || []

      // Download and cache images
      const cachedImages = await Promise.all(
        imageUrls.map(async (url) => {
          const response = await fetch(url)
          const blob = await response.blob()
          return URL.createObjectURL(blob)
        })
      )

      return cachedImages
    },
    enabled: !!strain,
    gcTime: 24 * 60 * 60 * 1000,
  })

  return { strain, images }
}
```

## Network Mode Options

Control how queries behave offline:

```typescript
// Always try to fetch (default)
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  networkMode: 'online', // Only fetch when online
})

// Try cache first, then network
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  networkMode: 'offlineFirst', // Prefer cache over network
})

// Always fetch, even offline (will fail offline)
useQuery({
  queryKey: ['packages'],
  queryFn: fetchPackages,
  networkMode: 'always', // Attempt fetch even if offline
})
```

## Next Steps

- **Network Mode** → Read `24-network-mode.md` for detailed network mode options
- **Error Handling** → Read `30-advanced-error-handling.md` for offline error handling
- **Optimistic Updates** → Read `15-optimistic-updates.md` for instant UI updates
