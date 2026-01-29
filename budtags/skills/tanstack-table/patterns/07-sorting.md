# Pattern 07: Sorting

## Enabling Sorting

To enable sorting, add the sorted row model to your table configuration:

```typescript
import { getSortedRowModel } from '@tanstack/react-table'

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(), // ← Enable sorting
})
```

**Without this row model, sorting won't work!**

## Sorting State

### Automatic State

```typescript
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  // State managed internally
})
```

### Controlled State (Recommended)

```typescript
const [sorting, setSorting] = useState<SortingState>([])

const table = useReactTable({
  data,
  columns,
  state: { sorting },
  onSortingChange: setSorting,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
})
```

### Initial State

```typescript
const table = useReactTable({
  data,
  columns,
  initialState: {
    sorting: [
      { id: 'ReceivedDateTime', desc: true }, // Sort by date descending
    ],
  },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
})
```

**Don't combine `initialState` and `state` - `state` takes precedence!**

## Sorting State Structure

```typescript
type SortingState = ColumnSort[]

type ColumnSort = {
  id: string    // Column ID
  desc: boolean // true = descending, false = ascending
}

// Example:
const sorting = [
  { id: 'ProductName', desc: false }, // A → Z
  { id: 'Quantity', desc: true },     // High → Low
]
```

## Basic Sorting UI

### Clickable Headers

```typescript
<th
  key={header.id}
  onClick={header.column.getToggleSortingHandler()}
  className="cursor-pointer select-none"
>
  {flexRender(header.column.columnDef.header, header.getContext())}
  {header.column.getIsSorted() === 'asc' && ' 🔼'}
  {header.column.getIsSorted() === 'desc' && ' 🔽'}
</th>
```

### With Better Indicators

```typescript
<th
  key={header.id}
  onClick={header.column.getToggleSortingHandler()}
  className="cursor-pointer"
>
  <div className="flex items-center gap-2">
    {flexRender(header.column.columnDef.header, header.getContext())}
    {{
      asc: <ChevronUpIcon className="w-4 h-4" />,
      desc: <ChevronDownIcon className="w-4 h-4" />,
    }[header.column.getIsSorted() as string] ?? (
      <ChevronUpDownIcon className="w-4 h-4 opacity-40" />
    )}
  </div>
</th>
```

## Multi-Column Sorting

By default, users can Shift+click to sort by multiple columns.

### Enable Multi-Sort

```typescript
const table = useReactTable({
  data,
  columns,
  enableMultiSort: true, // ← Default is true
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
})
```

### Disable Multi-Sort

```typescript
const table = useReactTable({
  data,
  columns,
  enableMultiSort: false, // ← Only single column sorting
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
})
```

### Limit Multi-Sort Columns

```typescript
const table = useReactTable({
  data,
  columns,
  maxMultiSortColCount: 3, // ← Max 3 columns sorted at once
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
})
```

### Custom Multi-Sort Trigger

```typescript
const table = useReactTable({
  data,
  columns,
  isMultiSortEvent: (e) => e.ctrlKey, // ← Use Ctrl+click instead of Shift+click
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
})
```

### Show Sort Index

```typescript
<th onClick={header.column.getToggleSortingHandler()}>
  {flexRender(header.column.columnDef.header, header.getContext())}
  {header.column.getIsSorted() && (
    <span className="ml-1 text-xs">
      {header.column.getSortIndex() + 1}
    </span>
  )}
  {header.column.getIsSorted() === 'asc' && ' 🔼'}
  {header.column.getIsSorted() === 'desc' && ' 🔽'}
</th>
```

## Built-in Sorting Functions

TanStack Table provides 6 built-in sorting functions:

```typescript
// Alphanumeric (natural number sorting)
sortingFn: 'alphanumeric'        // "1" < "2" < "10" (case-insensitive)
sortingFn: 'alphanumericCaseSensitive' // Case-sensitive version

// Text (standard string comparison)
sortingFn: 'text'                // Standard sorting (case-insensitive)
sortingFn: 'textCaseSensitive'   // Case-sensitive version

// Date
sortingFn: 'datetime'            // For Date objects

// Basic
sortingFn: 'basic'               // Fastest but least accurate
```

### Usage

```typescript
columnHelper.accessor('ProductName', {
  header: 'Product',
  sortingFn: 'text', // ← Use text sorting
})

columnHelper.accessor('Quantity', {
  header: 'Quantity',
  sortingFn: 'basic', // ← Use basic sorting for numbers
})

columnHelper.accessor('ReceivedDateTime', {
  header: 'Received',
  cell: info => new Date(info.getValue()).toLocaleDateString(),
  sortingFn: 'datetime', // ← Use datetime sorting
})
```

## Custom Sorting Functions

### Column-Level Custom Sort

```typescript
columnHelper.accessor('ReceivedDateTime', {
  header: 'Received',
  cell: info => new Date(info.getValue()).toLocaleDateString(),
  sortingFn: (rowA, rowB, columnId) => {
    const dateA = new Date(rowA.getValue(columnId))
    const dateB = new Date(rowB.getValue(columnId))
    return dateA.getTime() - dateB.getTime()
  },
})
```

### Reusable Sorting Functions

```typescript
// Define reusable sorting function
const dateSortingFn = (rowA, rowB, columnId) => {
  const dateA = new Date(rowA.getValue(columnId))
  const dateB = new Date(rowB.getValue(columnId))
  return dateA.getTime() - dateB.getTime()
}

const table = useReactTable({
  data,
  columns,
  sortingFns: {
    customDateSort: dateSortingFn, // ← Register custom function
  },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
})

// Use in column definition
columnHelper.accessor('ReceivedDateTime', {
  header: 'Received',
  sortingFn: 'customDateSort', // ← Reference by name
})
```

### Sorting Function Return Values

```typescript
sortingFn: (rowA, rowB, columnId) => {
  const a = rowA.getValue(columnId)
  const b = rowB.getValue(columnId)

  // Return -1 if a < b
  // Return 0 if a === b
  // Return 1 if a > b

  if (a < b) return -1
  if (a > b) return 1
  return 0
}
```

## Disabling Sorting

### Disable for Specific Column

```typescript
columnHelper.display({
  id: 'actions',
  header: 'Actions',
  enableSorting: false, // ← Can't sort this column
  cell: props => <button>Edit</button>,
})
```

### Disable for All Columns

```typescript
const table = useReactTable({
  data,
  columns,
  enableSorting: false, // ← Disable sorting globally
  getCoreRowModel: getCoreRowModel(),
})
```

## Advanced Sorting Options

### Initial Sort Direction

```typescript
columnHelper.accessor('Quantity', {
  header: 'Quantity',
  sortDescFirst: true, // ← First click sorts descending
})
```

### Invert Sorting (for Rankings)

```typescript
columnHelper.accessor('Rank', {
  header: 'Rank',
  invertSorting: true, // ← Lower numbers rank higher
})
```

### Undefined Value Handling

```typescript
columnHelper.accessor('OptionalField', {
  header: 'Optional',
  sortUndefined: 'last',  // Options: 'first', 'last', 1, -1, false
})
```

### Disable Sort Removal

```typescript
columnHelper.accessor('ProductName', {
  header: 'Product',
  enableSortingRemoval: false, // ← Can't remove sorting, only toggle direction
})
```

## Manual Sorting (Server-Side)

For server-side sorting, disable automatic sorting:

```typescript
const [sorting, setSorting] = useState<SortingState>([])

const { data: serverData } = useQuery({
  queryKey: ['packages', sorting],
  queryFn: () => fetchPackages({ sorting }), // Server handles sorting
})

const table = useReactTable({
  data: serverData?.data ?? [],
  columns,
  state: { sorting },
  onSortingChange: setSorting,
  manualSorting: true, // ← YOU handle sorting
  getCoreRowModel: getCoreRowModel(),
  // No getSortedRowModel - server does the work!
})
```

## Sorting API Methods

### Column Methods

```typescript
// Toggle sorting
column.toggleSorting(desc?: boolean)
column.toggleSorting() // Cycle: none → asc → desc
column.toggleSorting(true) // Force descending

// Get sort handler for onClick
column.getToggleSortingHandler()

// Check sorting state
column.getIsSorted()        // false | 'asc' | 'desc'
column.getCanSort()         // boolean
column.getSortIndex()       // number (position in multi-sort)
column.getAutoSortDir()     // 'asc' | 'desc'
column.getAutoSortingFn()   // Function
column.getSortingFn()       // Function

// Clear sorting
column.clearSorting()
```

### Table Methods

```typescript
// Reset sorting
table.resetSorting()
table.resetSorting(true) // Reset to initial state

// Set sorting
table.setSorting([{ id: 'ProductName', desc: false }])

// Get state
table.getState().sorting

// Get pre-sorted rows
table.getPreSortedRowModel().rows
```

## Complete Sorting Example

```typescript
function PackagesTable({ data }: { data: Package[] }) {
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'ReceivedDateTime', desc: true },
  ])

  const columns = useMemo(() => [
    columnHelper.accessor('Label', {
      header: 'Package Tag',
      enableSorting: true,
    }),
    columnHelper.accessor('ProductName', {
      header: 'Product',
      sortingFn: 'text',
    }),
    columnHelper.accessor('Quantity', {
      header: 'Quantity',
      sortingFn: 'basic',
    }),
    columnHelper.accessor('ReceivedDateTime', {
      header: 'Received',
      cell: info => new Date(info.getValue()).toLocaleDateString(),
      sortingFn: (rowA, rowB, columnId) => {
        const dateA = new Date(rowA.getValue(columnId))
        const dateB = new Date(rowB.getValue(columnId))
        return dateA.getTime() - dateB.getTime()
      },
    }),
  ], [])

  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    enableMultiSort: true,
  })

  return (
    <table>
      <thead>
        {table.getHeaderGroups().map(headerGroup => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map(header => (
              <th
                key={header.id}
                onClick={header.column.getToggleSortingHandler()}
                className="cursor-pointer select-none"
              >
                <div className="flex items-center gap-2">
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )}
                  {header.column.getIsSorted() && (
                    <span className="text-xs">
                      {header.column.getSortIndex() + 1}
                    </span>
                  )}
                  {{
                    asc: ' 🔼',
                    desc: ' 🔽',
                  }[header.column.getIsSorted() as string] ?? null}
                </div>
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
  )
}
```

## BudTags Pattern: Date Sorting Helper

**File:** `resources/js/Components/TableHelpers.tsx`

```typescript
export function createDateSortingFn<TData>() {
  return (rowA: Row<TData>, rowB: Row<TData>, columnId: string) => {
    const dateA = new Date(rowA.getValue(columnId) as string)
    const dateB = new Date(rowB.getValue(columnId) as string)
    return dateA.getTime() - dateB.getTime()
  }
}

// Usage
columnHelper.accessor('ReceivedDateTime', {
  header: 'Received',
  sortingFn: createDateSortingFn(),
})
```

## Common Mistakes

### ❌ Missing getSortedRowModel

```typescript
// ❌ Sorting won't work
const table = useReactTable({
  state: { sorting },
  onSortingChange: setSorting,
  getCoreRowModel: getCoreRowModel(),
  // Missing getSortedRowModel!
})

// ✅ Correct
const table = useReactTable({
  state: { sorting },
  onSortingChange: setSorting,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(), // ✅
})
```

### ❌ Using getSortedRowModel with Manual Sorting

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

### ❌ Not Memoizing Sorting Functions

```typescript
// ❌ Recreates function every render
const table = useReactTable({
  sortingFns: {
    mySort: (a, b) => { /* ... */ }, // ❌ New function each render
  },
})

// ✅ Memoized
const sortingFns = useMemo(() => ({
  mySort: (a, b) => { /* ... */ },
}), [])

const table = useReactTable({
  sortingFns, // ✅
})
```

## Type Definitions

```typescript
type SortingState = ColumnSort[]

type ColumnSort = {
  id: string
  desc: boolean
}

type SortingFn<TData> = (
  rowA: Row<TData>,
  rowB: Row<TData>,
  columnId: string
) => number

type ColumnDefSorting<TData> = {
  enableSorting?: boolean
  sortingFn?: SortingFn<TData> | keyof SortingFns | string
  sortDescFirst?: boolean
  invertSorting?: boolean
  sortUndefined?: 'first' | 'last' | 1 | -1 | false
  enableSortingRemoval?: boolean
}
```

## Next Steps

- **Add Filtering** → See pattern 08
- **Add Pagination** → See pattern 09
- **Row Selection** → See pattern 10
- **Column Visibility** → See pattern 11
