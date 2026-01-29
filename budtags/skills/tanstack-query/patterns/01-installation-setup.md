# Pattern 1: Installation & Setup

## Installation

```bash
# NPM
npm install @tanstack/react-query

# Yarn
yarn add @tanstack/react-query

# PNPM
pnpm add @tanstack/react-query
```

### DevTools (Recommended)

```bash
npm install @tanstack/react-query-devtools --save-dev
```

## Requirements

- React 18+
- TypeScript 4.7+ (optional but recommended)
- Modern bundler (Vite, Webpack 5+, etc.)

## Basic Setup

### Create QueryClient

```typescript
import { QueryClient } from '@tanstack/react-query'

const queryClient = new QueryClient()
```

### Wrap App with QueryClientProvider

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
    </QueryClientProvider>
  )
}
```

## Production Setup with Custom Defaults

### app.tsx

```typescript
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import App from './App'

// Create QueryClient with custom defaults
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      gcTime: 5 * 60 * 1000, // 5 minutes (was cacheTime in v4)
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

const root = createRoot(document.getElementById('root')!)
root.render(
  <QueryClientProvider client={queryClient}>
    <App />
    <ReactQueryDevtools initialIsOpen={false} position="bottom-right" />
  </QueryClientProvider>
)
```

## Configuration Options

### Default Options

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Time until data is considered stale (default: 0)
      staleTime: 5 * 60 * 1000, // 5 minutes

      // Time until inactive queries are garbage collected (default: 5 minutes)
      gcTime: 10 * 60 * 1000, // 10 minutes

      // Number of retry attempts (default: 3)
      retry: 1,

      // Retry delay (default: exponential backoff)
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),

      // Refetch on window focus (default: true)
      refetchOnWindowFocus: false,

      // Refetch on reconnect (default: true)
      refetchOnReconnect: true,

      // Refetch on mount (default: true)
      refetchOnMount: true,
    },
    mutations: {
      retry: 0, // Don't retry mutations by default
    },
  },
})
```

### BudTags Recommended Configuration

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // Metrc data stale after 1 minute
      gcTime: 5 * 60 * 1000, // Keep cache for 5 minutes
      retry: 1, // Metrc API is rate-limited
      refetchOnWindowFocus: false, // Don't refetch when switching tabs
      refetchOnReconnect: true, // Refetch when network reconnects
    },
  },
})
```

## DevTools Setup

### Development Mode

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

### Production Lazy Loading

```typescript
import { lazy, Suspense } from 'react'

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

// In production console: window.toggleDevtools()
```

## Multiple QueryClients (Advanced)

For testing or isolated contexts:

```typescript
function MyComponent() {
  const [queryClient] = useState(() => new QueryClient())

  return (
    <QueryClientProvider client={queryClient}>
      <IsolatedContext />
    </QueryClientProvider>
  )
}
```

## Next Steps
- **Core Concepts** → Read `02-core-concepts.md`
- **Basic Queries** → Read `07-basic-queries.md`
- **Important Defaults** → Read `03-important-defaults.md`
