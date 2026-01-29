# Pattern 04: Table Instance

## Creating a Table Instance

The table instance is created with the `useReactTable` hook:

```typescript
import { useReactTable, getCoreRowModel } from '@tanstack/react-table'

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
})
```

## Required Options

### data (Required)

Your array of row data:

```typescript
const data: Package[] = [
  { Tag: 'PKG-001', ProductName: 'Product A', Quantity: 10 },
  { Tag: 'PKG-002', ProductName: 'Product B', Quantity: 20 },
]
```

**Must be memoized** to prevent unnecessary rerenders:

```typescript
const data = useMemo(() => packages, [packages])
```

### columns (Required)

Column definitions array:

```typescript
const columns = useMemo(() => [
  columnHelper.accessor('Tag', { header: 'Tag' }),
  columnHelper.accessor('ProductName', { header: 'Product' }),
], [])
```

### getCoreRowModel (Required)

Base row model - always required:

```typescript
getCoreRowModel: getCoreRowModel()
```

## Common Options

### State Management

#### Automatic State

```typescript
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  // State managed internally
})
```

#### Controlled State (Recommended)

```typescript
const [sorting, setSorting] = useState<SortingState>([])
const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
const [pagination, setPagination] = useState({
  pageIndex: 0,
  pageSize: 10,
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
  getCoreRowModel: getCoreRowModel(),
})
```

### Feature Row Models

Enable features by adding row models:

```typescript
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),           // Sorting
  getFilteredRowModel: getFilteredRowModel(),       // Filtering
  getPaginationRowModel: getPaginationRowModel(),   // Pagination
  getGroupedRowModel: getGroupedRowModel(),         // Grouping
  getExpandedRowModel: getExpandedRowModel(),       // Expansion
})
```

### Initial State

Set initial state values:

```typescript
const table = useReactTable({
  data,
  columns,
  initialState: {
    sorting: [{ id: 'ReceivedDateTime', desc: true }],
    pagination: { pageIndex: 0, pageSize: 25 },
    columnVisibility: { actions: false },
  },
  getCoreRowModel: getCoreRowModel(),
})
```

### Manual Modes

For server-side operations:

```typescript
const table = useReactTable({
  data,
  columns,
  manualSorting: true,        // You handle sorting
  manualFiltering: true,      // You handle filtering
  manualPagination: true,     // You handle pagination
  pageCount: totalPages,      // Total pages from server
  getCoreRowModel: getCoreRowModel(),
})
```

## Table Instance API

### Getting Data

```typescript
// Get all rows
table.getRowModel().rows

// Get pre-filtered rows
table.getPreFilteredRowModel().rows

// Get pre-grouped rows
table.getPreGroupedRowModel().rows

// Get selected rows
table.getSelectedRowModel().rows
```

### Getting Columns

```typescript
// All columns
table.getAllColumns()

// Leaf columns (no groups)
table.getAllLeafColumns()

// Visible columns
table.getVisibleLeafColumns()

// Specific column
table.getColumn('Tag')
```

### Getting Headers

```typescript
// Header groups
table.getHeaderGroups()

// Footer groups
table.getFooterGroups()

// Flattened headers
table.getFlatHeaders()

// Leaf headers (no groups)
table.getLeafHeaders()
```

### Getting State

```typescript
// Current state
table.getState()

// Specific state
table.getState().sorting
table.getState().columnFilters
table.getState().pagination
```

### Setting State

```typescript
// Set sorting
table.setSorting([{ id: 'ProductName', desc: false }])

// Set filters
table.setColumnFilters([{ id: 'ProductName', value: 'Product A' }])

// Set pagination
table.setPagination({ pageIndex: 1, pageSize: 25 })

// Set row selection
table.setRowSelection({ '0': true, '1': true })
```

### Reset Methods

```typescript
// Reset specific state
table.resetSorting()
table.resetColumnFilters()
table.resetPagination()

// Reset all state
table.resetRowSelection()
```

## Complete Example

```typescript
function PackagesTable({ data }: { data: Package[] }) {
  // State
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})
  const [rowSelection, setRowSelection] = useState({})
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  })

  // Memoize data and columns
  const memoData = useMemo(() => data, [data])
  const memoColumns = useMemo(() => columns, [])

  // Create table instance
  const table = useReactTable({
    data: memoData,
    columns: memoColumns,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
      pagination,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    enableRowSelection: true,
  })

  return (
    <div>
      {/* Table UI */}
    </div>
  )
}
```

## BudTags Pattern: Flexible DataTable

**File:** `resources/js/Components/DataTable.tsx`

```typescript
interface DataTableProps<TData> {
  data: TData[]
  columns: ColumnDef<TData, any>[]
  enableSorting?: boolean
  enableFiltering?: boolean
  enablePagination?: boolean
  enableRowSelection?: boolean
}

export function DataTable<TData>({
  data,
  columns,
  enableSorting = true,
  enableFiltering = false,
  enablePagination = false,
  enableRowSelection = false,
}: DataTableProps<TData>) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [rowSelection, setRowSelection] = useState({})

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnFilters,
      rowSelection,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: enableSorting ? getSortedRowModel() : undefined,
    getFilteredRowModel: enableFiltering ? getFilteredRowModel() : undefined,
    getPaginationRowModel: enablePagination ? getPaginationRowModel() : undefined,
    enableRowSelection,
  })

  return (
    <BoxMain>
      {/* Render table */}
    </BoxMain>
  )
}
```

## Common Patterns

### Pattern 1: Persist State to LocalStorage

```typescript
const [sorting, setSorting] = useState<SortingState>(() => {
  const saved = localStorage.getItem('tableSorting')
  return saved ? JSON.parse(saved) : []
})

useEffect(() => {
  localStorage.setItem('tableSorting', JSON.stringify(sorting))
}, [sorting])
```

### Pattern 2: Sync State with URL

```typescript
const [searchParams, setSearchParams] = useSearchParams()

const [sorting, setSorting] = useState<SortingState>(() => {
  const sort = searchParams.get('sort')
  return sort ? JSON.parse(sort) : []
})

useEffect(() => {
  if (sorting.length > 0) {
    setSearchParams({ sort: JSON.stringify(sorting) })
  }
}, [sorting])
```

### Pattern 3: Server-Side Table

```typescript
const [sorting, setSorting] = useState<SortingState>([])
const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 25 })

const { data: serverData } = useQuery({
  queryKey: ['packages', sorting, pagination],
  queryFn: () => fetchPackages({ sorting, pagination }),
})

const table = useReactTable({
  data: serverData?.data ?? [],
  columns,
  pageCount: serverData?.pageCount ?? 0,
  state: { sorting, pagination },
  onSortingChange: setSorting,
  onPaginationChange: setPagination,
  manualSorting: true,
  manualPagination: true,
  getCoreRowModel: getCoreRowModel(),
})
```

## Common Mistakes

### ❌ Not Memoizing Data

```typescript
// ❌ Recreates data array every render
const table = useReactTable({
  data: packages.filter(p => p.Quantity > 0),
  columns,
  getCoreRowModel: getCoreRowModel(),
})

// ✅ Memoized
const filteredData = useMemo(
  () => packages.filter(p => p.Quantity > 0),
  [packages]
)

const table = useReactTable({
  data: filteredData,
  columns,
  getCoreRowModel: getCoreRowModel(),
})
```

### ❌ Missing Row Model for Feature

```typescript
// ❌ Sorting won't work
const table = useReactTable({
  data,
  columns,
  state: { sorting },
  onSortingChange: setSorting,
  getCoreRowModel: getCoreRowModel(),
  // Missing getSortedRowModel!
})

// ✅ Includes row model
const table = useReactTable({
  data,
  columns,
  state: { sorting },
  onSortingChange: setSorting,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(), // ✅
})
```

## Type Definitions

```typescript
type TableOptions<TData> = {
  data: TData[]
  columns: ColumnDef<TData>[]
  getCoreRowModel: (table: Table<TData>) => () => RowModel<TData>
  state?: Partial<TableState>
  onStateChange?: OnChangeFn<TableState>
  initialState?: InitialTableState
  // Feature options
  enableSorting?: boolean
  enableFiltering?: boolean
  enableGrouping?: boolean
  enableRowSelection?: boolean | ((row: Row<TData>) => boolean)
  // Row models
  getSortedRowModel?: (table: Table<TData>) => () => RowModel<TData>
  getFilteredRowModel?: (table: Table<TData>) => () => RowModel<TData>
  getPaginationRowModel?: (table: Table<TData>) => () => RowModel<TData>
  // Manual modes
  manualSorting?: boolean
  manualFiltering?: boolean
  manualPagination?: boolean
  pageCount?: number
  // ... many more
}
```

## Next Steps

- **Row Models** → See pattern 05
- **Rendering** → See pattern 06
- **Add Sorting** → See pattern 07
- **Add Filtering** → See pattern 08
