# Pattern 5: DevTools

## Installation

```bash
npm install @tanstack/react-query-devtools --save-dev
```

## Basic Setup

```typescript
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

DevTools are **automatically excluded from production bundles** (tree-shaken).

## Configuration Options

```typescript
<ReactQueryDevtools
  initialIsOpen={false}              // Start closed (default: false)
  position="bottom-right"            // Position (default: 'bottom-left')
  buttonPosition="bottom-right"      // Toggle button position
  panelPosition="bottom"             // Panel position: 'top' | 'bottom' | 'left' | 'right'
  client={queryClient}               // Specify client (auto-detected by default)
/>
```

### Available Positions

```typescript
// Toggle button position
buttonPosition="bottom-left" | "bottom-right" | "top-left" | "top-right"

// Panel position
panelPosition="top" | "bottom" | "left" | "right"

// BudTags recommended
<ReactQueryDevtools
  initialIsOpen={false}
  position="bottom-right"  // Out of the way
/>
```

## Production Build

### Lazy Loading (Recommended)

```typescript
import { lazy, Suspense, useState, useEffect } from 'react'

const ReactQueryDevtoolsProduction = lazy(() =>
  import('@tanstack/react-query-devtools/build/modern/production.js').then(
    (d) => ({
      default: d.ReactQueryDevtools,
    })
  )
)

function App() {
  const [showDevtools, setShowDevtools] = useState(false)

  useEffect(() => {
    // Expose global toggle
    // @ts-expect-error
    window.toggleDevtools = () => setShowDevtools((old) => !old)
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      {showDevtools && (
        <Suspense fallback={null}>
          <ReactQueryDevtoolsProduction />
        </Suspense>
      )}
    </QueryClientProvider>
  )
}

// In production console:
// window.toggleDevtools()
```

## DevTools Features

### Query Explorer

- **View all queries** in the cache
- **See query states**: success, error, fetching, stale
- **Inspect query data**: JSON viewer
- **See query metadata**: staleTime, gcTime, updatedAt, etc.

### Query Actions

Right-click any query to:
- **Refetch** - Manually trigger refetch
- **Invalidate** - Mark as stale and refetch
- **Reset** - Clear error state
- **Remove** - Remove from cache

### Cache Inspector

- **Live cache state**: See all data in cache
- **Data size**: Memory usage per query
- **Observer count**: How many components are using this query

### Query Timeline

- **Fetch events**: When queries were fetched
- **Invalidation events**: When queries were invalidated
- **Background updates**: Automatic refetches

### Settings

- **Show/hide observers**: Toggle query observer count
- **Show/hide query hashes**: Toggle internal hashes
- **Sticky queries**: Keep certain queries pinned

## Common Debugging Workflows

### 1. Why is my query not refetching?

```typescript
// Open DevTools
// 1. Find your query in the list
// 2. Check "Status" column: should show "stale" to trigger refetch
// 3. Check "Observers" column: should be > 0 (component mounted)
// 4. Check settings: refetchOnMount/refetchOnWindowFocus enabled?
```

### 2. Why is my query refetching too often?

```typescript
// Open DevTools
// 1. Watch the query timeline
// 2. Check when refetches are triggered
// 3. Likely causes:
//    - staleTime: 0 (default) → Set higher staleTime
//    - refetchOnWindowFocus: true → Disable
//    - Query key changes on every render → Memoize key
```

### 3. Why is my data not updating after mutation?

```typescript
// Open DevTools
// 1. Perform mutation
// 2. Check if query was invalidated (timeline)
// 3. Check if query refetched after invalidation
// 4. Common issue: Wrong queryKey in invalidateQueries
```

### 4. Memory leak investigation

```typescript
// Open DevTools
// 1. Check "Data" size for each query
// 2. Unmount components
// 3. Wait gcTime duration
// 4. Inactive queries should disappear
// 5. If queries persist → Check for lingering references
```

## DevTools Query States

### Status Colors

- 🟢 **Green**: Fresh (not stale)
- 🟡 **Yellow**: Stale (will refetch)
- 🔴 **Red**: Error state
- 🔵 **Blue**: Fetching (loading or background)
- ⚪ **Gray**: Inactive/paused

### Query Information

```
Queries (5)
┌────────────────────────────────────────────────────────────┐
│ ['metrc', 'packages', 'au-c-00001'] 🟡 Stale             │
│ Observers: 2 | Updated: 2 minutes ago                     │
│ Data: [{Id: 1, Label: "1A4..."}, ...]                     │
│ staleTime: 5m | gcTime: 10m | retry: 1                    │
└────────────────────────────────────────────────────────────┘
```

## Production DevTools Configuration

```typescript
// app.tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      {import.meta.env.DEV && (
        <ReactQueryDevtools
          initialIsOpen={false}
          position="bottom-right"
          buttonPosition="bottom-right"
        />
      )}
    </QueryClientProvider>
  )
}
```

## Keyboard Shortcuts

- **Esc**: Close DevTools
- **Click toggle button**: Open/close DevTools
- **Right-click query**: Context menu

## Next Steps
- **Core Concepts** → Read `02-core-concepts.md`
- **Basic Queries** → Read `07-basic-queries.md`
- **Testing** → Read `26-testing.md`
