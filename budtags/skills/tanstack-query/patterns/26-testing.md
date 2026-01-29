# Pattern 26: Testing

## Test Setup

### QueryClientProvider Wrapper

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // Disable retries in tests
        gcTime: Infinity, // Prevent garbage collection during tests
      },
      mutations: {
        retry: false,
      },
    },
  })
}

function renderWithClient(ui: React.ReactElement) {
  const testQueryClient = createTestQueryClient()

  return render(
    <QueryClientProvider client={testQueryClient}>
      {ui}
    </QueryClientProvider>
  )
}
```

### Isolated QueryClient Per Test

```typescript
describe('PackagesList', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    // New QueryClient for each test
    queryClient = createTestQueryClient()
  })

  afterEach(() => {
    queryClient.clear() // Clean up
  })

  test('displays packages', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackagesList />
      </QueryClientProvider>
    )
  })
})
```

## Testing Queries

### Mock API

```typescript
import { rest } from 'msw'
import { setupServer } from 'msw/node'

const server = setupServer(
  rest.get('/api/packages', (req, res, ctx) => {
    return res(
      ctx.json([
        { id: 1, label: '1A4...', productName: 'Test Product' },
      ])
    )
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

### Test Loading State

```typescript
test('shows loading state', () => {
  const { getByText } = renderWithClient(<PackagesList />)

  expect(getByText('Loading...')).toBeInTheDocument()
})
```

### Test Success State

```typescript
import { waitFor } from '@testing-library/react'

test('displays packages after loading', async () => {
  const { getByText } = renderWithClient(<PackagesList />)

  await waitFor(() => {
    expect(getByText('1A4...')).toBeInTheDocument()
  })
})
```

### Test Error State

```typescript
test('displays error message', async () => {
  server.use(
    rest.get('/api/packages', (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({ message: 'Server error' }))
    })
  )

  const { getByText } = renderWithClient(<PackagesList />)

  await waitFor(() => {
    expect(getByText(/error/i)).toBeInTheDocument()
  })
})
```

## Testing Mutations

### Test Mutation Success

```typescript
import { userEvent } from '@testing-library/user-event'

test('creates package on submit', async () => {
  const user = userEvent.setup()
  const { getByRole, getByLabelText } = renderWithClient(<CreatePackageForm />)

  // Fill form
  await user.type(getByLabelText('Label'), '1A4...')
  await user.type(getByLabelText('Quantity'), '10')

  // Submit
  await user.click(getByRole('button', { name: /create/i }))

  // Wait for success
  await waitFor(() => {
    expect(getByText('Package created')).toBeInTheDocument()
  })
})
```

### Test Mutation Error

```typescript
test('shows error on failed creation', async () => {
  server.use(
    rest.post('/api/packages', (req, res, ctx) => {
      return res(ctx.status(400), ctx.json({ message: 'Invalid data' }))
    })
  )

  const user = userEvent.setup()
  const { getByRole, getByText } = renderWithClient(<CreatePackageForm />)

  await user.click(getByRole('button', { name: /create/i }))

  await waitFor(() => {
    expect(getByText('Invalid data')).toBeInTheDocument()
  })
})
```

## Testing Invalidation

```typescript
test('refetches after mutation', async () => {
  const { getByRole, queryByText } = renderWithClient(<PackagesPage />)

  // Initial data
  await waitFor(() => {
    expect(queryByText('Package 1')).toBeInTheDocument()
  })

  // Create new package
  server.use(
    rest.get('/api/packages', (req, res, ctx) => {
      return res(
        ctx.json([
          { id: 1, label: 'Package 1' },
          { id: 2, label: 'Package 2' }, // New package
        ])
      )
    })
  )

  const user = userEvent.setup()
  await user.click(getByRole('button', { name: /create/i }))

  // List refetched
  await waitFor(() => {
    expect(queryByText('Package 2')).toBeInTheDocument()
  })
})
```

## Testing Infinite Queries

```typescript
test('loads more packages', async () => {
  const { getByRole, queryByText } = renderWithClient(<InfinitePackages />)

  // First page loaded
  await waitFor(() => {
    expect(queryByText('Package 1')).toBeInTheDocument()
  })

  // Mock next page
  server.use(
    rest.get('/api/packages', (req, res, ctx) => {
      const page = req.url.searchParams.get('page')
      if (page === '2') {
        return res(ctx.json([{ id: 11, label: 'Package 11' }]))
      }
    })
  )

  // Load more
  const user = userEvent.setup()
  await user.click(getByRole('button', { name: /load more/i }))

  // Next page loaded
  await waitFor(() => {
    expect(queryByText('Package 11')).toBeInTheDocument()
  })
})
```

## Seeding Cache for Tests

```typescript
test('displays package detail', () => {
  const queryClient = createTestQueryClient()

  // Seed cache
  queryClient.setQueryData(['package', 1], {
    id: 1,
    label: '1A4...',
    productName: 'Test Product',
  })

  const { getByText } = render(
    <QueryClientProvider client={queryClient}>
      <PackageDetails packageId={1} />
    </QueryClientProvider>
  )

  expect(getByText('1A4...')).toBeInTheDocument()
})
```

## Testing with React Testing Library

### Custom Render with Query Client

```typescript
import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient
}

function customRender(
  ui: ReactElement,
  { queryClient, ...renderOptions }: CustomRenderOptions = {}
) {
  const testQueryClient = queryClient ?? createTestQueryClient()

  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={testQueryClient}>
        {children}
      </QueryClientProvider>
    )
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

export * from '@testing-library/react'
export { customRender as render }
```

## BudTags Test Examples

### Test Metrc Packages Query

```typescript
import { render, waitFor } from './test-utils'

describe('MetrcPackages', () => {
  test('displays packages from Metrc API', async () => {
    server.use(
      rest.get('/api/metrc/packages', (req, res, ctx) => {
        return res(
          ctx.json([
            { Id: 1, Label: '1A4...', ProductName: 'Flower' },
          ])
        )
      })
    )

    const { getByText } = render(<MetrcPackages />)

    await waitFor(() => {
      expect(getByText('1A4...')).toBeInTheDocument()
    })
  })
})
```

### Test Package Adjustment

```typescript
test('adjusts package quantity', async () => {
  const { getByRole, getByLabelText, getByText } = render(
    <AdjustPackageModal pkg={{ Id: 1, Label: '1A4...' }} isOpen onClose={jest.fn()} />
  )

  const user = userEvent.setup()

  // Fill form
  await user.type(getByLabelText('Quantity'), '5')
  await user.selectOptions(getByLabelText('Reason'), 'Waste')

  // Submit
  await user.click(getByRole('button', { name: /adjust/i }))

  // Success
  await waitFor(() => {
    expect(getByText('Package adjusted')).toBeInTheDocument()
  })
})
```

## Testing Best Practices

### ✅ DO

```typescript
// Disable retries
retry: false

// Isolate QueryClient per test
beforeEach(() => {
  queryClient = new QueryClient()
})

// Use waitFor for async queries
await waitFor(() => {
  expect(element).toBeInTheDocument()
})

// Mock network with MSW
server.use(rest.get(...))
```

### ❌ DON'T

```typescript
// Share QueryClient across tests
const globalQueryClient = new QueryClient() // ❌

// Forget to await
getByText('Data') // ❌ May not be loaded yet

// Use setTimeout instead of waitFor
setTimeout(() => expect(...), 1000) // ❌ Brittle
```

## Next Steps
- **Core Concepts** → Read `02-core-concepts.md`
- **Mutations** → Read `13-mutations.md`
- **Queries** → Read `07-basic-queries.md`
