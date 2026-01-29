# Pattern 12: BudTags Integration

## Current Implementation in DataTable.tsx

BudTags uses TanStack Virtual in `resources/js/Components/DataTable.tsx`:

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'
import { Table, flexRender } from '@tanstack/react-table'

export function DataTable<T>({ table }: { table: Table<T> }) {
  const { rows } = table.getRowModel()
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50, // Row height estimate
    overscan: 10, // Render 10 extra rows for smooth scrolling
  })

  const virtualRows = virtualizer.getVirtualItems()

  return (
    <div
      ref={parentRef}
      className="overflow-auto"
      style={{ height: '600px' }}
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          position: 'relative'
        }}
      >
        {virtualRows.map((virtualRow) => {
          const row = rows[virtualRow.index]
          return (
            <div
              key={row.id}
              className="absolute top-0 left-0 w-full"
              style={{
                height: `${virtualRow.size}px`,
                transform: `translateY(${virtualRow.start}px)`,
              }}
            >
              {row.getVisibleCells().map((cell) => (
                <div key={cell.id} className="table-cell">
                  {flexRender(
                    cell.column.columnDef.cell,
                    cell.getContext()
                  )}
                </div>
              ))}
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

## Usage in Metrc Package Tables

### TablePackages.tsx

```typescript
import { DataTable } from '@/Components/DataTable'
import { createColumnHelper, useReactTable } from '@tanstack/react-table'
import { useMemo } from 'react'
import { Package } from '@/Types/types-metrc'

export function TablePackages({ packages }: { packages: Package[] }) {
  const columnHelper = createColumnHelper<Package>()

  // Memoized columns
  const columns = useMemo(
    () => [
      columnHelper.accessor('Label', {
        header: 'Label',
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor('ProductName', {
        header: 'Product',
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor('Quantity', {
        header: 'Quantity',
        cell: (info) => `${info.getValue()} ${info.row.original.UnitOfMeasureName}`,
      }),
    ],
    []
  )

  const table = useReactTable({
    data: packages,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  })

  // DataTable uses TanStack Virtual internally
  return <DataTable table={table} />
}
```

## Benefits for BudTags

### 1. Performance with Large Datasets

Without virtualization (1000+ Metrc packages):
- ❌ All 1000+ DOM nodes rendered
- ❌ 5-10 second initial render
- ❌ Laggy scrolling
- ❌ Browser tab freezes

With virtualization:
- ✅ Only ~20 DOM nodes rendered (visible + overscan)
- ✅ <100ms initial render
- ✅ Smooth 60fps scrolling
- ✅ Responsive UI

### 2. Real-World Performance

BudTags tables that benefit from virtualization:
- **Metrc Packages** - 500-2000 items (cultivation facilities)
- **Metrc Items** - 200-1000 items (product catalog)
- **Harvest Batches** - 100-500 items (large grows)
- **LeafLink Inventory** - 500+ items (wholesale)
- **QuickBooks Items** - 200+ items (accounting sync)

### 3. Memory Efficiency

| Without Virtualization | With Virtualization |
|------------------------|---------------------|
| 1000 rows = 1000 DOM nodes | 1000 rows = 20 DOM nodes |
| ~50MB memory | ~1MB memory |
| Garbage collection spikes | Minimal GC pressure |

## Advanced BudTags Patterns

### Dynamic Row Heights for Wrapped Text

```typescript
export function DataTableDynamic<T>({ table }: { table: Table<T> }) {
  const { rows } = table.getRowModel()
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 60, // Initial estimate
    measureElement: (element) => element.getBoundingClientRect().height,
    overscan: 5,
  })

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto">
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualRow) => {
          const row = rows[virtualRow.index]
          return (
            <div
              key={row.id}
              data-index={virtualRow.index}
              ref={virtualizer.measureElement}
              className="absolute top-0 left-0 w-full"
              style={{ transform: `translateY(${virtualRow.start}px)` }}
            >
              {/* Row content with variable height */}
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

### Scroll to Selected Package

```typescript
export function TablePackagesWithSelection({
  packages,
  selectedPackageId
}: {
  packages: Package[]
  selectedPackageId?: number
}) {
  const columnHelper = createColumnHelper<Package>()
  const parentRef = useRef<HTMLDivElement>(null)

  const columns = useMemo(() => [...], [])

  const table = useReactTable({
    data: packages,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  const { rows } = table.getRowModel()

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  })

  // Scroll to selected package on mount
  useEffect(() => {
    if (!selectedPackageId) return

    const index = packages.findIndex(pkg => pkg.Id === selectedPackageId)
    if (index !== -1) {
      virtualizer.scrollToIndex(index, { align: 'center' })
    }
  }, [selectedPackageId])

  return <DataTable table={table} parentRef={parentRef} virtualizer={virtualizer} />
}
```

### Preserve Scroll on Filter

```typescript
export function TablePackagesWithFilters() {
  const [filter, setFilter] = useState('active')
  const parentRef = useRef<HTMLDivElement>(null)

  // Don't reset scroll when filter changes
  const virtualizer = useVirtualizer({
    count: filteredPackages.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    // Scroll is preserved automatically
  })

  return (
    <>
      <div className="mb-4">
        <button onClick={() => setFilter('active')}>Active</button>
        <button onClick={() => setFilter('inactive')}>Inactive</button>
      </div>
      <DataTable table={table} parentRef={parentRef} virtualizer={virtualizer} />
    </>
  )
}
```

## Performance Monitoring

Check if virtualization is working:

```typescript
useEffect(() => {
  const virtualRows = virtualizer.getVirtualItems()
  console.log(`Rendering ${virtualRows.length} of ${rows.length} rows`)

  // Should see ~20-30 rendered rows even if 1000+ total
}, [virtualizer.getVirtualItems(), rows.length])
```

## Next Steps

- Review `DataTable.tsx` implementation
- Check table performance with 1000+ rows
- Consider dynamic heights for tables with variable content
- Add scroll restoration for better UX
