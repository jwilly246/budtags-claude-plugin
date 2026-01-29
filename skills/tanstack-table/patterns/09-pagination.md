# Pattern 09: Pagination

## Enabling Pagination

To enable pagination, add the pagination row model to your table configuration:

```typescript
import { getPaginationRowModel } from '@tanstack/react-table'

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(), // ← Enable pagination
})
```

**Important:** Add this LAST in the row model pipeline (after sorting/filtering)!

## Pagination State

### Structure

```typescript
type PaginationState = {
  pageIndex: number  // Zero-based page number (0 = first page)
  pageSize: number   // Rows per page
}
```

### Automatic State

```typescript
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  // State managed internally
})
```

### Controlled State (Recommended)

```typescript
const [pagination, setPagination] = useState<PaginationState>({
  pageIndex: 0,
  pageSize: 10,
})

const table = useReactTable({
  data,
  columns,
  state: { pagination },
  onPaginationChange: setPagination,
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
})
```

### Initial State

```typescript
const table = useReactTable({
  data,
  columns,
  initialState: {
    pagination: {
      pageIndex: 0,
      pageSize: 25,
    },
  },
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
})
```

## Basic Pagination UI

### Previous/Next Buttons

```typescript
<div className="flex items-center gap-2">
  <button
    onClick={() => table.previousPage()}
    disabled={!table.getCanPreviousPage()}
    className="px-4 py-2 border rounded disabled:opacity-50"
  >
    Previous
  </button>
  <button
    onClick={() => table.nextPage()}
    disabled={!table.getCanNextPage()}
    className="px-4 py-2 border rounded disabled:opacity-50"
  >
    Next
  </button>
</div>
```

### First/Last Page Buttons

```typescript
<div className="flex items-center gap-2">
  <button
    onClick={() => table.firstPage()}
    disabled={!table.getCanPreviousPage()}
  >
    First
  </button>
  <button
    onClick={() => table.previousPage()}
    disabled={!table.getCanPreviousPage()}
  >
    Previous
  </button>
  <button
    onClick={() => table.nextPage()}
    disabled={!table.getCanNextPage()}
  >
    Next
  </button>
  <button
    onClick={() => table.lastPage()}
    disabled={!table.getCanNextPage()}
  >
    Last
  </button>
</div>
```

### Page Info

```typescript
<div className="flex items-center gap-2">
  <span>
    Page {table.getState().pagination.pageIndex + 1} of{' '}
    {table.getPageCount()}
  </span>
  <span>
    ({table.getRowModel().rows.length} rows)
  </span>
</div>
```

### Page Size Selector

```typescript
<select
  value={table.getState().pagination.pageSize}
  onChange={e => table.setPageSize(Number(e.target.value))}
  className="border rounded px-2 py-1"
>
  {[10, 20, 30, 40, 50].map(pageSize => (
    <option key={pageSize} value={pageSize}>
      Show {pageSize}
    </option>
  ))}
</select>
```

### Go to Page Input

```typescript
<div className="flex items-center gap-2">
  <span>Go to page:</span>
  <input
    type="number"
    min={1}
    max={table.getPageCount()}
    defaultValue={table.getState().pagination.pageIndex + 1}
    onChange={e => {
      const page = e.target.value ? Number(e.target.value) - 1 : 0
      table.setPageIndex(page)
    }}
    className="border rounded px-2 py-1 w-16"
  />
</div>
```

## Complete Pagination Controls

```typescript
function PaginationControls({ table }: { table: Table<any> }) {
  const { pageIndex, pageSize } = table.getState().pagination
  const pageCount = table.getPageCount()

  return (
    <div className="flex items-center justify-between px-4 py-3 border-t">
      {/* Left: Rows info */}
      <div className="text-sm text-gray-700">
        Showing {pageIndex * pageSize + 1} to{' '}
        {Math.min((pageIndex + 1) * pageSize, table.getRowCount())} of{' '}
        {table.getRowCount()} results
      </div>

      {/* Center: Page navigation */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => table.firstPage()}
          disabled={!table.getCanPreviousPage()}
          className="px-3 py-1 border rounded disabled:opacity-50"
        >
          «
        </button>
        <button
          onClick={() => table.previousPage()}
          disabled={!table.getCanPreviousPage()}
          className="px-3 py-1 border rounded disabled:opacity-50"
        >
          ‹
        </button>
        <span className="px-3 py-1">
          Page {pageIndex + 1} of {pageCount}
        </span>
        <button
          onClick={() => table.nextPage()}
          disabled={!table.getCanNextPage()}
          className="px-3 py-1 border rounded disabled:opacity-50"
        >
          ›
        </button>
        <button
          onClick={() => table.lastPage()}
          disabled={!table.getCanNextPage()}
          className="px-3 py-1 border rounded disabled:opacity-50"
        >
          »
        </button>
      </div>

      {/* Right: Page size selector */}
      <select
        value={pageSize}
        onChange={e => table.setPageSize(Number(e.target.value))}
        className="border rounded px-2 py-1"
      >
        {[10, 20, 30, 40, 50].map(size => (
          <option key={size} value={size}>
            {size} per page
          </option>
        ))}
      </select>
    </div>
  )
}
```

## Manual Pagination (Server-Side)

For server-side pagination, disable automatic pagination and manage page count:

```typescript
const [pagination, setPagination] = useState<PaginationState>({
  pageIndex: 0,
  pageSize: 25,
})

const { data: serverData } = useQuery({
  queryKey: ['packages', pagination],
  queryFn: () => fetchPackages({
    page: pagination.pageIndex,
    pageSize: pagination.pageSize,
  }),
})

const table = useReactTable({
  data: serverData?.data ?? [],
  columns,
  state: { pagination },
  onPaginationChange: setPagination,
  manualPagination: true, // ← YOU handle pagination
  pageCount: serverData?.pageCount ?? 0, // ← Total pages from server
  getCoreRowModel: getCoreRowModel(),
  // No getPaginationRowModel - server does the work!
})
```

### Alternative: Provide Row Count

```typescript
const table = useReactTable({
  data: serverData?.data ?? [],
  columns,
  state: { pagination },
  onPaginationChange: setPagination,
  manualPagination: true,
  rowCount: serverData?.totalRows ?? 0, // ← Total rows instead of pageCount
  getCoreRowModel: getCoreRowModel(),
})
```

## Configuration Options

### Auto-Reset Page Index

By default, `pageIndex` resets to 0 when data/filters/grouping changes:

```typescript
const table = useReactTable({
  data,
  columns,
  autoResetPageIndex: true, // ← Default behavior
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
})
```

Disable to maintain page position:

```typescript
const table = useReactTable({
  data,
  columns,
  autoResetPageIndex: false, // ← Don't reset on data changes
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
})
```

**Warning:** If disabled, you may need to manually reset to avoid empty pages!

## Pagination API Methods

### Navigation

```typescript
table.firstPage()            // Go to first page
table.lastPage()             // Go to last page
table.previousPage()         // Go to previous page
table.nextPage()             // Go to next page
table.setPageIndex(index)    // Go to specific page (0-based)
```

### Page Size

```typescript
table.setPageSize(size)      // Change rows per page
table.getState().pagination.pageSize // Get current page size
```

### State Checks

```typescript
table.getCanPreviousPage()   // boolean
table.getCanNextPage()       // boolean
table.getPageCount()         // Total number of pages
table.getRowCount()          // Total number of rows
```

### Reset

```typescript
table.resetPagination()      // Reset to initial state
table.resetPagination(true)  // Reset to default state
```

## Complete Pagination Example

```typescript
function PackagesTable({ data }: { data: Package[] }) {
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  })

  const columns = useMemo(() => [
    columnHelper.accessor('Label', { header: 'Package Tag' }),
    columnHelper.accessor('ProductName', { header: 'Product' }),
    columnHelper.accessor('Quantity', { header: 'Quantity' }),
  ], [])

  const table = useReactTable({
    data,
    columns,
    state: { pagination },
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  })

  return (
    <div>
      <table className="min-w-full">
        <thead>
          {table.getHeaderGroups().map(headerGroup => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map(header => (
                <th key={header.id}>
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map(row => (
            <tr key={row.id}>
              {row.getVisibleCells().map(cell => (
                <td key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination Controls */}
      <div className="flex items-center justify-between mt-4">
        <div className="text-sm text-gray-700">
          Showing {pagination.pageIndex * pagination.pageSize + 1} to{' '}
          {Math.min(
            (pagination.pageIndex + 1) * pagination.pageSize,
            table.getRowCount()
          )}{' '}
          of {table.getRowCount()} results
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="px-4 py-2 border rounded disabled:opacity-50"
          >
            Previous
          </button>
          <span className="px-3">
            Page {pagination.pageIndex + 1} of {table.getPageCount()}
          </span>
          <button
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="px-4 py-2 border rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>

        <select
          value={pagination.pageSize}
          onChange={e => table.setPageSize(Number(e.target.value))}
          className="border rounded px-2 py-1"
        >
          {[10, 20, 30, 40, 50].map(pageSize => (
            <option key={pageSize} value={pageSize}>
              Show {pageSize}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}
```

## Combined with Sorting and Filtering

```typescript
function PackagesTable({ data }: { data: Package[] }) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 25,
  })

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnFilters,
      pagination,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onPaginationChange: setPagination,
    // Row models in correct order
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),   // 1. Filter
    getSortedRowModel: getSortedRowModel(),       // 2. Sort
    getPaginationRowModel: getPaginationRowModel(), // 3. Paginate
  })

  return <div>{/* Table UI */}</div>
}
```

## Performance: Pagination vs Virtualization

### Use Pagination When:
- Dataset is manageable (< 100,000 rows)
- Users expect traditional page navigation
- Server-side implementation is available
- You want to reduce DOM nodes

### Use Virtualization When:
- Very large datasets (100,000+ rows)
- Users prefer scrolling over clicking
- You need to show all data at once
- Memory is not a constraint

**Virtualization Alternative:** Use [TanStack Virtual](https://tanstack.com/virtual/latest) to render only visible rows while scrolling through all data.

## BudTags Pattern: Flexible Pagination

**File:** `resources/js/Components/DataTable.tsx`

```typescript
interface DataTableProps<TData> {
  data: TData[]
  columns: ColumnDef<TData, any>[]
  enablePagination?: boolean
  defaultPageSize?: number
}

export function DataTable<TData>({
  data,
  columns,
  enablePagination = false,
  defaultPageSize = 25,
}: DataTableProps<TData>) {
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: defaultPageSize,
  })

  const table = useReactTable({
    data,
    columns,
    state: enablePagination ? { pagination } : {},
    onPaginationChange: enablePagination ? setPagination : undefined,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: enablePagination
      ? getPaginationRowModel()
      : undefined,
  })

  return (
    <BoxMain>
      <table>{/* ... */}</table>
      {enablePagination && <PaginationControls table={table} />}
    </BoxMain>
  )
}
```

## Common Mistakes

### ❌ Wrong Row Model Order

```typescript
// ❌ Paginate before filtering/sorting
const table = useReactTable({
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getSortedRowModel: getSortedRowModel(),
})

// ✅ Correct order
const table = useReactTable({
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),   // 1. Filter
  getSortedRowModel: getSortedRowModel(),       // 2. Sort
  getPaginationRowModel: getPaginationRowModel(), // 3. Paginate
})
```

### ❌ Using getPaginationRowModel with Manual Pagination

```typescript
// ❌ Conflicts
const table = useReactTable({
  manualPagination: true,
  getPaginationRowModel: getPaginationRowModel(), // ❌ Unnecessary
})

// ✅ Manual mode - no row model needed
const table = useReactTable({
  manualPagination: true,
  pageCount: totalPages,
  // Server handles pagination
})
```

### ❌ Not Providing pageCount for Manual Pagination

```typescript
// ❌ Missing pageCount
const table = useReactTable({
  data: serverData?.data ?? [],
  manualPagination: true,
  // Missing pageCount or rowCount!
})

// ✅ Provide total pages
const table = useReactTable({
  data: serverData?.data ?? [],
  manualPagination: true,
  pageCount: serverData?.pageCount ?? 0, // ✅
})
```

## Type Definitions

```typescript
type PaginationState = {
  pageIndex: number
  pageSize: number
}

type PaginationTableState = {
  pagination: PaginationState
}

type PaginationOptions = {
  pageCount?: number
  rowCount?: number
  manualPagination?: boolean
  autoResetPageIndex?: boolean
  onPaginationChange?: OnChangeFn<PaginationState>
  getPaginationRowModel?: (table: Table<any>) => () => RowModel<any>
}
```

## Next Steps

- **Row Selection** → See pattern 10
- **Column Visibility** → See pattern 11
- **Virtualization** → See pattern 19
- **Server-Side Data** → Combine manual sorting/filtering/pagination
