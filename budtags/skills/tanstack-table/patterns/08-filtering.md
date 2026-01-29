# Pattern 08: Filtering

## Enabling Filtering

To enable filtering, add the filtered row model to your table configuration:

```typescript
import { getFilteredRowModel } from '@tanstack/react-table'

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(), // ← Enable filtering
})
```

**Without this row model, filtering won't work!**

## Two Types of Filtering

1. **Column Filtering** - Filter individual columns
2. **Global Filtering** - Search across all columns

## Column Filtering

### Column Filter State

```typescript
type ColumnFiltersState = ColumnFilter[]

type ColumnFilter = {
  id: string      // Column ID
  value: unknown  // Filter value (any type)
}

// Example:
const columnFilters = [
  { id: 'ProductName', value: 'Product A' },
  { id: 'Quantity', value: { min: 10, max: 100 } },
]
```

### Controlled State (Recommended)

```typescript
const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])

const table = useReactTable({
  data,
  columns,
  state: { columnFilters },
  onColumnFiltersChange: setColumnFilters,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})
```

### Initial State

```typescript
const table = useReactTable({
  data,
  columns,
  initialState: {
    columnFilters: [
      { id: 'ProductName', value: 'Product A' },
    ],
  },
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})
```

### Basic Column Filter UI

```typescript
function ColumnFilter({ column }: { column: Column<any, any> }) {
  const filterValue = column.getFilterValue()

  return (
    <input
      type="text"
      value={(filterValue ?? '') as string}
      onChange={e => column.setFilterValue(e.target.value)}
      placeholder={`Search ${column.id}...`}
      className="border rounded px-2 py-1"
    />
  )
}

// Usage
<th>
  {flexRender(header.column.columnDef.header, header.getContext())}
  {header.column.getCanFilter() && (
    <ColumnFilter column={header.column} />
  )}
</th>
```

## Global Filtering

### Global Filter State

```typescript
const [globalFilter, setGlobalFilter] = useState('')

const table = useReactTable({
  data,
  columns,
  state: { globalFilter },
  onGlobalFilterChange: setGlobalFilter,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})
```

### Global Filter UI

```typescript
function GlobalFilter({ table }: { table: Table<any> }) {
  const globalFilter = table.getState().globalFilter

  return (
    <input
      type="text"
      value={globalFilter ?? ''}
      onChange={e => table.setGlobalFilter(String(e.target.value))}
      placeholder="Search all columns..."
      className="border rounded px-4 py-2 mb-4"
    />
  )
}

// Usage
<div>
  <GlobalFilter table={table} />
  <table>{/* ... */}</table>
</div>
```

## Built-in Filter Functions

TanStack Table provides 10 built-in filter functions:

```typescript
// String filters
'includesString'              // Case-insensitive contains
'includesStringSensitive'     // Case-sensitive contains
'equalsString'                // Case-insensitive equals
'equalsStringSensitive'       // Case-sensitive equals

// Array filters
'arrIncludes'                 // Array includes value
'arrIncludesAll'              // Array includes all values
'arrIncludesSome'             // Array includes some values

// Equality filters
'equals'                      // Strict equality (===)
'weakEquals'                  // Weak equality (==)

// Number filters
'inNumberRange'               // Number in range [min, max]
```

### Usage

```typescript
columnHelper.accessor('ProductName', {
  header: 'Product',
  filterFn: 'includesString', // ← Case-insensitive search
})

columnHelper.accessor('Status', {
  header: 'Status',
  filterFn: 'arrIncludes', // ← For multi-select filter
})

columnHelper.accessor('Quantity', {
  header: 'Quantity',
  filterFn: 'inNumberRange', // ← For range filter
})
```

## Custom Filter Functions

### Simple Custom Filter

```typescript
columnHelper.accessor('ProductName', {
  header: 'Product',
  filterFn: (row, columnId, filterValue) => {
    const value = row.getValue(columnId) as string
    return value.toLowerCase().includes(filterValue.toLowerCase())
  },
})
```

### Filter Function Signature

```typescript
type FilterFn<TData> = (
  row: Row<TData>,
  columnId: string,
  filterValue: any
) => boolean
```

### Advanced Custom Filter with Auto-Remove

```typescript
const customFilter = (row, columnId, filterValue) => {
  const value = row.getValue(columnId) as string
  return value.toLowerCase().includes(filterValue.toLowerCase())
}

// Auto-remove filter when value is empty
customFilter.autoRemove = (val) => !val || val === ''

columnHelper.accessor('ProductName', {
  header: 'Product',
  filterFn: customFilter,
})
```

### Reusable Filter Functions

```typescript
const filterFns = {
  fuzzy: (row, columnId, filterValue) => {
    // Fuzzy search implementation
    const value = row.getValue(columnId) as string
    return value.toLowerCase().includes(filterValue.toLowerCase())
  },
}

const table = useReactTable({
  data,
  columns,
  filterFns, // ← Register custom functions
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})

// Use in column definition
columnHelper.accessor('ProductName', {
  header: 'Product',
  filterFn: 'fuzzy', // ← Reference by name
})
```

## Filter UI Components

### Text Filter

```typescript
function TextFilter({ column }: { column: Column<any> }) {
  return (
    <input
      type="text"
      value={(column.getFilterValue() ?? '') as string}
      onChange={e => column.setFilterValue(e.target.value)}
      placeholder="Filter..."
      className="border rounded px-2 py-1 w-full"
    />
  )
}
```

### Select Filter

```typescript
function SelectFilter({ column, options }: {
  column: Column<any>
  options: string[]
}) {
  return (
    <select
      value={(column.getFilterValue() ?? '') as string}
      onChange={e => column.setFilterValue(e.target.value || undefined)}
      className="border rounded px-2 py-1 w-full"
    >
      <option value="">All</option>
      {options.map(option => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  )
}
```

### Number Range Filter

```typescript
function NumberRangeFilter({ column }: { column: Column<any> }) {
  const [min, max] = (column.getFilterValue() as [number, number]) ?? [
    undefined,
    undefined,
  ]

  return (
    <div className="flex gap-2">
      <input
        type="number"
        value={min ?? ''}
        onChange={e =>
          column.setFilterValue((old: [number, number]) => [
            e.target.value ? Number(e.target.value) : undefined,
            old?.[1],
          ])
        }
        placeholder="Min"
        className="border rounded px-2 py-1 w-20"
      />
      <input
        type="number"
        value={max ?? ''}
        onChange={e =>
          column.setFilterValue((old: [number, number]) => [
            old?.[0],
            e.target.value ? Number(e.target.value) : undefined,
          ])
        }
        placeholder="Max"
        className="border rounded px-2 py-1 w-20"
      />
    </div>
  )
}

// Usage with inNumberRange filter
columnHelper.accessor('Quantity', {
  header: 'Quantity',
  filterFn: 'inNumberRange',
  cell: info => info.getValue(),
})
```

### Debounced Filter

```typescript
function DebouncedFilter({ column }: { column: Column<any> }) {
  const [value, setValue] = useState('')

  useEffect(() => {
    const timeout = setTimeout(() => {
      column.setFilterValue(value)
    }, 300)

    return () => clearTimeout(timeout)
  }, [value, column])

  return (
    <input
      type="text"
      value={value}
      onChange={e => setValue(e.target.value)}
      placeholder="Search..."
      className="border rounded px-2 py-1"
    />
  )
}
```

## Disabling Filters

### Disable for Specific Column

```typescript
columnHelper.display({
  id: 'actions',
  header: 'Actions',
  enableColumnFilter: false, // ← Can't filter this column
  enableGlobalFilter: false, // ← Excluded from global search
  cell: props => <button>Edit</button>,
})
```

### Disable All Filtering

```typescript
const table = useReactTable({
  data,
  columns,
  enableFilters: false, // ← Disable all filtering
  getCoreRowModel: getCoreRowModel(),
})
```

### Disable Global Filter Only

```typescript
const table = useReactTable({
  data,
  columns,
  enableGlobalFilter: false, // ← Disable global filter
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})
```

## Manual Filtering (Server-Side)

For server-side filtering, disable automatic filtering:

```typescript
const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
const [globalFilter, setGlobalFilter] = useState('')

const { data: serverData } = useQuery({
  queryKey: ['packages', columnFilters, globalFilter],
  queryFn: () => fetchPackages({ columnFilters, globalFilter }),
})

const table = useReactTable({
  data: serverData?.data ?? [],
  columns,
  state: { columnFilters, globalFilter },
  onColumnFiltersChange: setColumnFilters,
  onGlobalFilterChange: setGlobalFilter,
  manualFiltering: true, // ← YOU handle filtering
  getCoreRowModel: getCoreRowModel(),
  // No getFilteredRowModel - server does the work!
})
```

## Filtering API Methods

### Column Methods

```typescript
// Set/get filter value
column.setFilterValue(value)
column.getFilterValue()

// Check filter state
column.getCanFilter()       // boolean
column.getIsFiltered()      // boolean
column.getFilterIndex()     // number (order applied)
```

### Table Methods

```typescript
// Column filters
table.setColumnFilters([...])
table.resetColumnFilters()
table.getState().columnFilters

// Global filter
table.setGlobalFilter(value)
table.resetGlobalFilter()
table.getState().globalFilter

// Get pre-filtered rows
table.getPreFilteredRowModel().rows
```

## Complete Filtering Example

```typescript
function PackagesTable({ data }: { data: Package[] }) {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter] = useState('')

  const columns = useMemo(() => [
    columnHelper.accessor('Label', {
      header: 'Package Tag',
      filterFn: 'includesString',
    }),
    columnHelper.accessor('ProductName', {
      header: 'Product',
      filterFn: 'includesString',
    }),
    columnHelper.accessor('Quantity', {
      header: 'Quantity',
      filterFn: 'inNumberRange',
    }),
    columnHelper.accessor('ItemCategory', {
      header: 'Category',
      filterFn: 'arrIncludes',
    }),
  ], [])

  const table = useReactTable({
    data,
    columns,
    state: {
      columnFilters,
      globalFilter,
    },
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  })

  return (
    <div>
      {/* Global filter */}
      <input
        type="text"
        value={globalFilter ?? ''}
        onChange={e => table.setGlobalFilter(e.target.value)}
        placeholder="Search all columns..."
        className="border rounded px-4 py-2 mb-4 w-full"
      />

      <table>
        <thead>
          {table.getHeaderGroups().map(headerGroup => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map(header => (
                <th key={header.id}>
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )}
                  {/* Column filter */}
                  {header.column.getCanFilter() && (
                    <input
                      type="text"
                      value={
                        (header.column.getFilterValue() ?? '') as string
                      }
                      onChange={e =>
                        header.column.setFilterValue(e.target.value)
                      }
                      placeholder="Filter..."
                      className="border rounded px-2 py-1 mt-1 w-full"
                    />
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

      {/* Show filtered count */}
      <div className="mt-4 text-sm text-gray-600">
        Showing {table.getRowModel().rows.length} of{' '}
        {table.getPreFilteredRowModel().rows.length} rows
      </div>
    </div>
  )
}
```

## BudTags Pattern: Filter Button Cell

**File:** `resources/js/Components/TableHelpers.tsx`

```typescript
export function createFilterButtonCell<TData, TValue>(
  filterKey: string
) {
  return {
    cell: ({ getValue, table }) => {
      const value = getValue() as TValue
      return (
        <button
          onClick={() => {
            table.getColumn(filterKey)?.setFilterValue(value)
          }}
          className="text-blue-600 hover:underline"
        >
          {String(value)}
        </button>
      )
    },
  }
}

// Usage
columnHelper.accessor('ProductName', {
  header: 'Product',
  ...createFilterButtonCell('ProductName'),
})
```

## Performance Considerations

**Client-Side Performance:**
- Works well up to ~100,000 rows
- Consider pagination for better UX
- Use debounced inputs for large datasets

**When to Use Server-Side:**
- Dataset > 100,000 rows
- Complex filter logic
- Security/privacy requirements
- Reduce payload size

## Common Mistakes

### ❌ Missing getFilteredRowModel

```typescript
// ❌ Filtering won't work
const table = useReactTable({
  state: { columnFilters },
  onColumnFiltersChange: setColumnFilters,
  getCoreRowModel: getCoreRowModel(),
  // Missing getFilteredRowModel!
})

// ✅ Correct
const table = useReactTable({
  state: { columnFilters },
  onColumnFiltersChange: setColumnFilters,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(), // ✅
})
```

### ❌ Using getFilteredRowModel with Manual Filtering

```typescript
// ❌ Conflicts
const table = useReactTable({
  manualFiltering: true,
  getFilteredRowModel: getFilteredRowModel(), // ❌ Unnecessary
})

// ✅ Manual mode - no row model needed
const table = useReactTable({
  manualFiltering: true,
  // Server handles filtering
})
```

### ❌ Not Handling Empty Filter Values

```typescript
// ❌ Filter stays active with empty string
column.setFilterValue('')

// ✅ Remove filter with undefined
column.setFilterValue(value || undefined)
```

## Type Definitions

```typescript
type ColumnFiltersState = ColumnFilter[]

type ColumnFilter = {
  id: string
  value: unknown
}

type FilterFn<TData> = {
  (row: Row<TData>, columnId: string, filterValue: any): boolean
  resolveFilterValue?: (value: any) => any
  autoRemove?: (value: any) => boolean
}

type ColumnDefFiltering<TData> = {
  enableColumnFilter?: boolean
  enableGlobalFilter?: boolean
  filterFn?: FilterFn<TData> | keyof FilterFns | string
}
```

## Next Steps

- **Add Pagination** → See pattern 09
- **Row Selection** → See pattern 10
- **Faceted Filtering** → See pattern 20
- **Column Visibility** → See pattern 11
