# Pattern 18: Virtualization

## Why Virtualize?

Virtualization renders only visible rows, dramatically improving performance for large datasets.

**Use virtualization when:**
- Dataset > 1,000 rows
- User prefers scrolling over pagination
- Memory/performance is critical

**Benefits:**
- Renders only ~20 rows instead of 10,000+
- Smooth scrolling performance
- Reduced memory usage
- Better mobile performance

## Installation

```bash
npm install @tanstack/react-virtual
```

## Basic Virtualization

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'

function VirtualizedTable({ data }: { data: Package[] }) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  const tableContainerRef = useRef<HTMLDivElement>(null)

  const rowVirtualizer = useVirtualizer({
    count: table.getRowModel().rows.length,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => 50, // Estimated row height
    overscan: 5, // Render 5 extra rows outside viewport
  })

  return (
    <div
      ref={tableContainerRef}
      style={{
        height: '600px',
        overflow: 'auto',
      }}
    >
      <table style={{ display: 'grid' }}>
        <thead style={{ display: 'grid', position: 'sticky', top: 0, zIndex: 1 }}>
          {table.getHeaderGroups().map(headerGroup => (
            <tr key={headerGroup.id} style={{ display: 'flex', width: '100%' }}>
              {headerGroup.headers.map(header => (
                <th
                  key={header.id}
                  style={{
                    display: 'flex',
                    width: header.getSize(),
                  }}
                >
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody
          style={{
            display: 'grid',
            height: `${rowVirtualizer.getTotalSize()}px`,
            position: 'relative',
          }}
        >
          {rowVirtualizer.getVirtualItems().map(virtualRow => {
            const row = table.getRowModel().rows[virtualRow.index]
            return (
              <tr
                key={row.id}
                style={{
                  display: 'flex',
                  position: 'absolute',
                  transform: `translateY(${virtualRow.start}px)`,
                  width: '100%',
                }}
              >
                {row.getVisibleCells().map(cell => (
                  <td
                    key={cell.id}
                    style={{
                      display: 'flex',
                      width: cell.column.getSize(),
                    }}
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
```

## Dynamic Row Heights

For tables with variable row heights:

```typescript
const rowVirtualizer = useVirtualizer({
  count: table.getRowModel().rows.length,
  getScrollElement: () => tableContainerRef.current,
  estimateSize: () => 50,
  measureElement:
    typeof window !== 'undefined' &&
    navigator.userAgent.indexOf('Firefox') === -1
      ? element => element?.getBoundingClientRect().height
      : undefined,
  overscan: 5,
})
```

## With Sorting, Filtering, and Pagination

```typescript
function VirtualizedTable({ data }: { data: Package[] }) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])

  const table = useReactTable({
    data,
    columns,
    state: { sorting, columnFilters },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  })

  const rowVirtualizer = useVirtualizer({
    count: table.getRowModel().rows.length, // Uses filtered/sorted count
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => 50,
    overscan: 10,
  })

  return (
    <div>
      {/* Filters */}
      <input
        value={columnFilters.find(f => f.id === 'ProductName')?.value as string ?? ''}
        onChange={e =>
          table.getColumn('ProductName')?.setFilterValue(e.target.value)
        }
        placeholder="Search products..."
      />

      {/* Virtualized table */}
      <div ref={tableContainerRef} style={{ height: '600px', overflow: 'auto' }}>
        {/* ... */}
      </div>

      <div className="mt-2 text-sm text-gray-600">
        Showing {rowVirtualizer.getVirtualItems().length} of{' '}
        {table.getRowModel().rows.length} rows
      </div>
    </div>
  )
}
```

## Virtualization Performance Tips

### 1. Keep Virtualizer in Lowest Component

```typescript
// ✅ GOOD - Virtualizer in table component
function DataTable() {
  const rowVirtualizer = useVirtualizer({...})
  return <table>{/* ... */}</table>
}

// ❌ BAD - Virtualizer in parent causes re-renders
function Page() {
  const rowVirtualizer = useVirtualizer({...})
  return <DataTable virtualizer={rowVirtualizer} />
}
```

### 2. Memoize Row Rendering

```typescript
const VirtualRow = memo(({ virtualRow, row }: { virtualRow: VirtualItem; row: Row<Package> }) => (
  <tr
    style={{
      display: 'flex',
      position: 'absolute',
      transform: `translateY(${virtualRow.start}px)`,
      width: '100%',
    }}
  >
    {row.getVisibleCells().map(cell => (
      <td key={cell.id} style={{ display: 'flex', width: cell.column.getSize() }}>
        {flexRender(cell.column.columnDef.cell, cell.getContext())}
      </td>
    ))}
  </tr>
))
```

### 3. Use CSS Grid/Flexbox

```css
table {
  display: grid;
}

thead, tbody, tr {
  display: contents;
}

th, td {
  overflow: hidden;
}
```

## Infinite Scrolling with Virtualization

```typescript
function InfiniteTable() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useInfiniteQuery({
      queryKey: ['packages'],
      queryFn: ({ pageParam = 0 }) => fetchPackages(pageParam),
      getNextPageParam: (lastPage, pages) => lastPage.nextCursor,
    })

  const flatData = useMemo(
    () => data?.pages?.flatMap(page => page.data) ?? [],
    [data]
  )

  const table = useReactTable({
    data: flatData,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  const rowVirtualizer = useVirtualizer({
    count: hasNextPage
      ? table.getRowModel().rows.length + 1
      : table.getRowModel().rows.length,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => 50,
    overscan: 5,
  })

  useEffect(() => {
    const [lastItem] = [...rowVirtualizer.getVirtualItems()].reverse()

    if (!lastItem) return

    if (
      lastItem.index >= table.getRowModel().rows.length - 1 &&
      hasNextPage &&
      !isFetchingNextPage
    ) {
      fetchNextPage()
    }
  }, [
    hasNextPage,
    fetchNextPage,
    table.getRowModel().rows.length,
    isFetchingNextPage,
    rowVirtualizer.getVirtualItems(),
  ])

  return (
    <div ref={tableContainerRef} style={{ height: '600px', overflow: 'auto' }}>
      {/* Virtualized table */}
      {isFetchingNextPage && <div>Loading more...</div>}
    </div>
  )
}
```

## Column Virtualization

For tables with many columns:

```typescript
const columnVirtualizer = useVirtualizer({
  horizontal: true,
  count: table.getAllLeafColumns().length,
  getScrollElement: () => tableContainerRef.current,
  estimateSize: index => table.getAllLeafColumns()[index].getSize(),
  overscan: 3,
})
```

## Complete Example

```typescript
function VirtualizedPackagesTable({ data }: { data: Package[] }) {
  const tableContainerRef = useRef<HTMLDivElement>(null)

  const columns = useMemo(() => [
    columnHelper.accessor('Label', {
      header: 'Package Tag',
      size: 200,
    }),
    columnHelper.accessor('ProductName', {
      header: 'Product',
      size: 300,
    }),
    columnHelper.accessor('Quantity', {
      header: 'Quantity',
      size: 100,
    }),
  ], [])

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  const rowVirtualizer = useVirtualizer({
    count: table.getRowModel().rows.length,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => 50,
    overscan: 10,
  })

  return (
    <div
      ref={tableContainerRef}
      className="border rounded"
      style={{
        height: '600px',
        overflow: 'auto',
      }}
    >
      <table style={{ display: 'grid' }}>
        <thead
          style={{
            display: 'grid',
            position: 'sticky',
            top: 0,
            zIndex: 1,
            background: 'white',
          }}
        >
          {table.getHeaderGroups().map(headerGroup => (
            <tr
              key={headerGroup.id}
              style={{ display: 'flex', width: '100%' }}
            >
              {headerGroup.headers.map(header => (
                <th
                  key={header.id}
                  style={{
                    display: 'flex',
                    width: header.getSize(),
                  }}
                  className="border-b px-4 py-2 bg-gray-50"
                >
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody
          style={{
            display: 'grid',
            height: `${rowVirtualizer.getTotalSize()}px`,
            position: 'relative',
          }}
        >
          {rowVirtualizer.getVirtualItems().map(virtualRow => {
            const row = table.getRowModel().rows[virtualRow.index]
            return (
              <tr
                key={row.id}
                style={{
                  display: 'flex',
                  position: 'absolute',
                  transform: `translateY(${virtualRow.start}px)`,
                  width: '100%',
                }}
              >
                {row.getVisibleCells().map(cell => (
                  <td
                    key={cell.id}
                    style={{
                      display: 'flex',
                      width: cell.column.getSize(),
                    }}
                    className="border-b px-4 py-2"
                  >
                    {flexRender(
                      cell.column.columnDef.cell,
                      cell.getContext()
                    )}
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
```

## Virtualization vs Pagination

| Feature | Virtualization | Pagination |
|---------|----------------|------------|
| **Best for** | 10,000+ rows, scrolling | < 10,000 rows, navigation |
| **Memory** | Very low | Moderate |
| **UX** | Seamless scrolling | Click to navigate |
| **Complexity** | Higher | Lower |
| **Mobile** | Excellent | Good |

## Type Definitions

```typescript
type VirtualizerOptions = {
  count: number
  getScrollElement: () => HTMLElement | null
  estimateSize: (index: number) => number
  overscan?: number
  horizontal?: boolean
  measureElement?: (element: Element) => number
}
```

## Next Steps
- **Infinite Scrolling** → Combine with TanStack Query
- **Column Virtualization** → For wide tables
- **Performance Optimization** → Memoization techniques
