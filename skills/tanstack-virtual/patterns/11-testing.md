# Pattern 11: Testing Virtualized Components

## Mock Virtualizer in Tests

```typescript
import { vi } from 'vitest'

vi.mock('@tanstack/react-virtual', () => ({
  useVirtualizer: vi.fn(() => ({
    getTotalSize: () => 1000,
    getVirtualItems: () => [
      { key: '0', index: 0, start: 0, size: 50, end: 50 },
      { key: '1', index: 1, start: 50, size: 50, end: 100 },
      { key: '2', index: 2, start: 100, size: 50, end: 150 },
    ],
    scrollToIndex: vi.fn(),
    scrollToOffset: vi.fn(),
    measure: vi.fn(),
    measureElement: null,
    scrollElement: null,
  })),
}))
```

## Test Virtual List Rendering

```typescript
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import VirtualList from './VirtualList'

describe('VirtualList', () => {
  it('renders virtual items', () => {
    const items = Array.from({ length: 100 }, (_, i) => ({
      id: i,
      name: `Item ${i}`
    }))

    render(<VirtualList items={items} />)

    // Should only render virtual items (not all 100)
    expect(screen.getByText('Item 0')).toBeInTheDocument()
    expect(screen.getByText('Item 1')).toBeInTheDocument()
    expect(screen.getByText('Item 2')).toBeInTheDocument()

    // Items outside viewport should not be rendered
    expect(screen.queryByText('Item 50')).not.toBeInTheDocument()
  })

  it('handles empty list', () => {
    render(<VirtualList items={[]} />)
    expect(screen.queryByRole('listitem')).not.toBeInTheDocument()
  })
})
```

## Test Scroll Behavior

```typescript
import { render, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'

it('scrolls to item on button click', () => {
  const scrollToIndexMock = vi.fn()

  vi.mock('@tanstack/react-virtual', () => ({
    useVirtualizer: () => ({
      scrollToIndex: scrollToIndexMock,
      getTotalSize: () => 1000,
      getVirtualItems: () => [],
    }),
  }))

  const { getByRole } = render(<VirtualListWithScroll items={items} />)

  fireEvent.click(getByRole('button', { name: /scroll to 50/i }))

  expect(scrollToIndexMock).toHaveBeenCalledWith(50, expect.any(Object))
})
```

## Test Dynamic Heights

```typescript
it('measures element height', async () => {
  const measureElementMock = vi.fn((element) =>
    element.getBoundingClientRect().height
  )

  vi.mock('@tanstack/react-virtual', () => ({
    useVirtualizer: vi.fn(() => ({
      getTotalSize: () => 5000,
      getVirtualItems: () => [
        { key: '0', index: 0, start: 0, size: 100 },
        { key: '1', index: 1, start: 100, size: 200 },
      ],
      measureElement: measureElementMock,
    })),
  }))

  render(<VirtualListWithDynamicHeights items={items} />)

  await waitFor(() => {
    expect(measureElementMock).toHaveBeenCalled()
  })
})
```

## Test TanStack Table + Virtual

```typescript
import { render, screen } from '@testing-library/react'
import { createColumnHelper } from '@tanstack/react-table'

it('renders virtual table rows', () => {
  const columnHelper = createColumnHelper<Package>()
  const columns = [
    columnHelper.accessor('Label', { header: 'Label' }),
    columnHelper.accessor('Quantity', { header: 'Quantity' }),
  ]

  const data = [
    { Id: 1, Label: '1A4...', Quantity: 10 },
    { Id: 2, Label: '1A4...', Quantity: 20 },
    { Id: 3, Label: '1A4...', Quantity: 30 },
  ]

  render(<VirtualTable data={data} columns={columns} />)

  // Headers should always be visible
  expect(screen.getByText('Label')).toBeInTheDocument()
  expect(screen.getByText('Quantity')).toBeInTheDocument()

  // Virtual rows should be rendered
  expect(screen.getByText('1A4...')).toBeInTheDocument()
})
```

## Snapshot Testing

```typescript
it('matches snapshot', () => {
  const items = Array.from({ length: 10 }, (_, i) => ({
    id: i,
    name: `Item ${i}`
  }))

  const { container } = render(<VirtualList items={items} />)
  expect(container).toMatchSnapshot()
})
```

## Integration Test (E2E)

```typescript
import { test, expect } from '@playwright/test'

test('virtual list scrolls smoothly', async ({ page }) => {
  await page.goto('/packages')

  // Check initial items are visible
  await expect(page.locator('[data-testid="package-0"]')).toBeVisible()

  // Scroll down
  await page.evaluate(() => {
    document.querySelector('[data-testid="virtual-list"]')?.scrollTo({
      top: 5000,
      behavior: 'smooth',
    })
  })

  // Check items at scroll position are visible
  await expect(page.locator('[data-testid="package-100"]')).toBeVisible()

  // First items should not be in DOM anymore
  await expect(page.locator('[data-testid="package-0"]')).not.toBeVisible()
})
```

## Next Steps
- Read `12-budtags-integration.md` for BudTags examples
- Read `09-performance-optimization.md` for optimization tips
