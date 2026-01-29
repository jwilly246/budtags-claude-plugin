# Pattern 05: Row Models

## What Are Row Models?

Row models are functions that process your data through a pipeline. Each row model adds a specific feature to your table.

## Row Model Pipeline

Data flows through row models in this order:

```
Raw Data
  ↓
getCoreRowModel() ← REQUIRED
  ↓
getFilteredRowModel() ← Optional (filtering)
  ↓
getSortedRowModel() ← Optional (sorting)
  ↓
getGroupedRowModel() ← Optional (grouping)
  ↓
getExpandedRowModel() ← Optional (expansion)
  ↓
getPaginationRowModel() ← Optional (pagination)
  ↓
Final Displayed Rows
```

## Core Row Model (Required)

**Always required** - provides base row processing.

```typescript
import { getCoreRowModel } from '@tanstack/react-table'

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(), // ← Required
})
```

**What it does:**
- Creates row objects from raw data
- Assigns row IDs
- Creates initial row hierarchy

## Sorted Row Model

Enables sorting functionality.

```typescript
import { getSortedRowModel } from '@tanstack/react-table'

const [sorting, setSorting] = useState<SortingState>([])

const table = useReactTable({
  data,
  columns,
  state: { sorting },
  onSortingChange: setSorting,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(), // ← Add this
})
```

**What it does:**
- Sorts rows based on `sorting` state
- Supports multi-column sorting
- Uses column `sortingFn` or default algorithm

**Without this:** Sorting won't work even if you have sorting state!

## Filtered Row Model

Enables filtering functionality.

```typescript
import { getFilteredRowModel } from '@tanstack/react-table'

const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
const [globalFilter, setGlobalFilter] = useState('')

const table = useReactTable({
  data,
  columns,
  state: { columnFilters, globalFilter },
  onColumnFiltersChange: setColumnFilters,
  onGlobalFilterChange: setGlobalFilter,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(), // ← Add this
})
```

**What it does:**
- Filters rows based on column filters
- Applies global filter
- Uses column `filterFn` or default algorithm

## Paginated Row Model

Enables pagination functionality.

```typescript
import { getPaginationRowModel } from '@tanstack/react-table'

const [pagination, setPagination] = useState({
  pageIndex: 0,
  pageSize: 10,
})

const table = useReactTable({
  data,
  columns,
  state: { pagination },
  onPaginationChange: setPagination,
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(), // ← Add this
})
```

**What it does:**
- Splits rows into pages
- Manages `pageIndex` and `pageSize`
- Provides pagination helper methods

**Note:** Add this LAST in the pipeline (after sorting/filtering)!

## Grouped Row Model

Enables row grouping/aggregation.

```typescript
import { getGroupedRowModel } from '@tanstack/react-table'

const [grouping, setGrouping] = useState<GroupingState>(['status'])

const table = useReactTable({
  data,
  columns,
  state: { grouping },
  onGroupingChange: setGrouping,
  getCoreRowModel: getCoreRowModel(),
  getGroupedRowModel: getGroupedRowModel(), // ← Add this
})
```

**What it does:**
- Groups rows by column values
- Creates group headers
- Enables aggregation functions

## Expanded Row Model

Enables row expansion for nested data.

```typescript
import { getExpandedRowModel } from '@tanstack/react-table'

const [expanded, setExpanded] = useState<ExpandedState>({})

const table = useReactTable({
  data,
  columns,
  state: { expanded },
  onExpandedChange: setExpanded,
  getCoreRowModel: getCoreRowModel(),
  getExpandedRowModel: getExpandedRowModel(), // ← Add this
  getSubRows: row => row.subRows, // Define how to get sub-rows
})
```

**What it does:**
- Manages expanded state
- Renders nested/hierarchical data
- Provides expand/collapse methods

## Faceted Row Models

Enable faceted filtering metadata.

```typescript
import {
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFacetedMinMaxValues,
} from '@tanstack/react-table'

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getFacetedRowModel: getFacetedRowModel(), // ← Unique values for filtering
  getFacetedUniqueValues: getFacetedUniqueValues(), // ← Unique value counts
  getFacetedMinMaxValues: getFacetedMinMaxValues(), // ← Min/max for ranges
})
```

**What they do:**
- `getFacetedRowModel()` - Pre-computes unique values
- `getFacetedUniqueValues()` - Counts for each unique value
- `getFacetedMinMaxValues()` - Min/max values for numeric columns

**Use for:** Dynamic filter UI (checkboxes, range sliders)

## Complete Example with Multiple Row Models

```typescript
function PackagesTable({ data }: { data: Package[] }) {
  // State
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter] = useState('')
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 25,
  })

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnFilters,
      globalFilter,
      pagination,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    onPaginationChange: setPagination,

    // Row models in pipeline order
    getCoreRowModel: getCoreRowModel(),           // 1. Required
    getFilteredRowModel: getFilteredRowModel(),   // 2. Filter first
    getSortedRowModel: getSortedRowModel(),       // 3. Then sort
    getPaginationRowModel: getPaginationRowModel(), // 4. Then paginate
  })

  return <div>{/* Table UI */}</div>
}
```

## Manual Row Models (Server-Side)

For server-side operations, skip row models and manage data externally:

```typescript
const { data: serverData } = useQuery({
  queryKey: ['packages', sorting, columnFilters, pagination],
  queryFn: () => fetchPackages({ sorting, columnFilters, pagination }),
})

const table = useReactTable({
  data: serverData?.data ?? [],
  columns,
  state: { sorting, columnFilters, pagination },
  onSortingChange: setSorting,
  onColumnFiltersChange: setColumnFilters,
  onPaginationChange: setPagination,

  // Manual modes - YOU handle the processing
  manualSorting: true,
  manualFiltering: true,
  manualPagination: true,
  pageCount: serverData?.pageCount ?? 0,

  // Only core row model needed
  getCoreRowModel: getCoreRowModel(),
  // No other row models - server does the work!
})
```

## Accessing Row Models

### Get Current Rows

```typescript
// After all processing (filtered, sorted, paginated)
const rows = table.getRowModel().rows
```

### Get Pre-Filtered Rows

```typescript
// Before filtering was applied
const preFilteredRows = table.getPreFilteredRowModel().rows
```

### Get Pre-Grouped Rows

```typescript
// Before grouping was applied
const preGroupedRows = table.getPreGroupedRowModel().rows
```

### Get Pre-Paginated Rows

```typescript
// Before pagination was applied (all rows on all pages)
const allRows = table.getPrePaginationRowModel().rows
```

## Performance Considerations

### Memoization

Row models are automatically memoized - they only recalculate when dependencies change:

```typescript
// getSortedRowModel only recalculates when:
// - data changes
// - columns change
// - sorting state changes
getSortedRowModel: getSortedRowModel()
```

### Conditional Row Models

Only add row models for features you're using:

```typescript
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),

  // ✅ Only add if sorting is enabled
  getSortedRowModel: enableSorting ? getSortedRowModel() : undefined,

  // ✅ Only add if filtering is enabled
  getFilteredRowModel: enableFiltering ? getFilteredRowModel() : undefined,
})
```

## Common Mistakes

### ❌ Wrong Row Model Order

```typescript
// ❌ Paginate before sorting - wrong order!
const table = useReactTable({
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  getSortedRowModel: getSortedRowModel(),
})

// ✅ Correct order: filter → sort → paginate
const table = useReactTable({
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
})
```

### ❌ Missing Row Model for Feature

```typescript
// ❌ Has sorting state but no getSortedRowModel
const table = useReactTable({
  state: { sorting },
  getCoreRowModel: getCoreRowModel(),
  // Sorting won't work!
})

// ✅ Includes row model
const table = useReactTable({
  state: { sorting },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(), // ✅
})
```

### ❌ Using Row Models with Manual Mode

```typescript
// ❌ Conflicts - manual mode means server handles it
const table = useReactTable({
  manualSorting: true,
  getSortedRowModel: getSortedRowModel(), // ❌ Unnecessary
})

// ✅ Manual mode - no row model needed
const table = useReactTable({
  manualSorting: true,
  // Server handles sorting, no getSortedRowModel
})
```

## BudTags Pattern: Flexible Row Models

**File:** `resources/js/Components/DataTable.tsx`

```typescript
export function DataTable<TData>({
  enableSorting = true,
  enableFiltering = false,
  enablePagination = false,
  ...
}: DataTableProps<TData>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: enableSorting ? getSortedRowModel() : undefined,
    getFilteredRowModel: enableFiltering ? getFilteredRowModel() : undefined,
    getPaginationRowModel: enablePagination ? getPaginationRowModel() : undefined,
  })
}
```

## Type Definitions

```typescript
type RowModel<TData> = {
  rows: Row<TData>[]
  flatRows: Row<TData>[]
  rowsById: Record<string, Row<TData>>
}

type Row<TData> = {
  id: string
  index: number
  original: TData
  depth: number
  subRows: Row<TData>[]
  getVisibleCells(): Cell<TData, unknown>[]
  getAllCells(): Cell<TData, unknown>[]
  // ... many more
}
```

## Next Steps

- **Rendering Rows** → See pattern 06
- **Enable Sorting** → See pattern 07
- **Enable Filtering** → See pattern 08
- **Enable Pagination** → See pattern 09
