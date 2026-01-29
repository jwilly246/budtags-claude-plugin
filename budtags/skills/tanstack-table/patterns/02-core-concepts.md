# Pattern 02: Core Concepts

## Headless UI Philosophy

TanStack Table is a **headless** UI library - it provides logic, state, and API without any markup or styles.

### What "Headless" Means

**Headless libraries provide:**
- ✅ Business logic
- ✅ State management
- ✅ Data processing
- ✅ API methods

**Headless libraries DO NOT provide:**
- ❌ HTML markup
- ❌ CSS styles
- ❌ Pre-built components
- ❌ UI framework

### Benefits of Headless Architecture

1. **Full Design Control** - You own 100% of the markup and styling
2. **Small Bundle Size** - No unused UI code (10-15kb)
3. **Framework Agnostic** - Works with React, Vue, Solid, Angular, etc.
4. **Maximum Flexibility** - Works with any CSS framework (Tailwind, Bootstrap, etc.)
5. **Better Performance** - Only ship the logic you need

### Headless vs Component-Based

**Component-Based Libraries** (like AG Grid, MUI DataGrid):
```typescript
// ✅ Quick setup
<AGGridReact columnDefs={columns} rowData={data} />

// ❌ Limited customization
// ❌ Larger bundle (100kb+)
// ❌ Vendor lock-in
```

**Headless Libraries** (TanStack Table):
```typescript
// ❌ More setup required
const table = useReactTable({ data, columns })
// ...custom rendering

// ✅ Full control
// ✅ Tiny bundle (10-15kb)
// ✅ Framework portable
```

## Table Instance

The **table instance** is the core object that orchestrates everything.

### Creating a Table Instance

```typescript
import { useReactTable, getCoreRowModel } from '@tanstack/react-table'

const table = useReactTable({
  data,              // Your data array
  columns,           // Column definitions
  getCoreRowModel: getCoreRowModel(), // Required
})
```

### Table Instance Properties

```typescript
table.getHeaderGroups()    // Header structure
table.getRowModel()        // Processed rows
table.getAllColumns()      // All columns
table.getState()           // Current state
table.options              // Configuration
```

### Table Instance Methods

```typescript
table.setPageIndex(0)      // Set page
table.setSorting([...])    // Update sorting
table.setColumnFilters([...]) // Update filters
table.reset()              // Reset to defaults
```

## State Management

TanStack Table manages state for you, but you can also control it.

### Automatic State (Default)

```typescript
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  // State managed internally
})
```

### Controlled State (Recommended)

```typescript
const [sorting, setSorting] = useState<SortingState>([])
const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])

const table = useReactTable({
  data,
  columns,
  state: {
    sorting,           // ✅ You control the state
    columnFilters,
  },
  onSortingChange: setSorting,       // ✅ Notified of changes
  onColumnFiltersChange: setColumnFilters,
  getCoreRowModel: getCoreRowModel(),
})
```

**Benefits of Controlled State:**
- Persist state to localStorage
- Synchronize with URL query params
- Debug state changes
- Integrate with external state management

### State Types

```typescript
type TableState = {
  sorting: SortingState
  columnFilters: ColumnFiltersState
  columnVisibility: VisibilityState
  columnOrder: ColumnOrderState
  columnPinning: ColumnPinningState
  columnSizing: ColumnSizingState
  expanded: ExpandedState
  grouping: GroupingState
  pagination: PaginationState
  rowSelection: RowSelectionState
  rowPinning: RowPinningState
  globalFilter: any
}
```

## Row Models

Row models are functions that process your data through a pipeline.

### Core Row Model (Required)

```typescript
getCoreRowModel: getCoreRowModel()
```

**Always required** - provides base row processing.

### Feature Row Models

Add these for specific features:

```typescript
getSortedRowModel: getSortedRowModel()        // Sorting
getFilteredRowModel: getFilteredRowModel()    // Filtering
getPaginationRowModel: getPaginationRowModel() // Pagination
getGroupedRowModel: getGroupedRowModel()       // Grouping
getExpandedRowModel: getExpandedRowModel()     // Expansion
getFacetedRowModel: getFacetedRowModel()       // Faceted filtering
```

### Row Model Pipeline

Data flows through row models in order:

```
Raw Data
  ↓
getCoreRowModel (required)
  ↓
getFilteredRowModel (optional)
  ↓
getSortedRowModel (optional)
  ↓
getGroupedRowModel (optional)
  ↓
getExpandedRowModel (optional)
  ↓
getPaginationRowModel (optional)
  ↓
Final Rows
```

## Column Definitions

Columns define how data is accessed, displayed, and manipulated.

### Three Column Types

1. **Accessor Columns** - Has data model (can sort, filter, group)
2. **Display Columns** - No data model (buttons, checkboxes)
3. **Group Columns** - Organize other columns visually

```typescript
const columns = [
  // Accessor column
  columnHelper.accessor('firstName', {
    header: 'First Name',
  }),

  // Display column
  columnHelper.display({
    id: 'actions',
    cell: props => <button>Edit</button>
  }),

  // Group column
  columnHelper.group({
    id: 'name',
    header: 'Full Name',
    columns: [
      columnHelper.accessor('firstName'),
      columnHelper.accessor('lastName'),
    ],
  }),
]
```

## Rendering

TanStack Table doesn't render - you do!

### flexRender Helper

Use `flexRender` to render dynamic content:

```typescript
import { flexRender } from '@tanstack/react-table'

// ✅ Correct - handles functions and components
{flexRender(cell.column.columnDef.cell, cell.getContext())}

// ❌ Wrong - won't work if cell is a function
{cell.column.columnDef.cell}
```

### Basic Table Rendering Pattern

```typescript
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
            {flexRender(
              cell.column.columnDef.cell,
              cell.getContext()
            )}
          </td>
        ))}
      </tr>
    ))}
  </tbody>
</table>
```

## BudTags Pattern: Reusable DataTable

**File:** `resources/js/Components/DataTable.tsx`

```typescript
interface DataTableProps<TData> {
  data: TData[]
  columns: ColumnDef<TData, any>[]
  enableSorting?: boolean
  enableFiltering?: boolean
  enablePagination?: boolean
}

export function DataTable<TData>({
  data,
  columns,
  enableSorting = true,
  enableFiltering = true,
  enablePagination = true,
}: DataTableProps<TData>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: enableSorting ? getSortedRowModel() : undefined,
    getFilteredRowModel: enableFiltering ? getFilteredRowModel() : undefined,
    getPaginationRowModel: enablePagination ? getPaginationRowModel() : undefined,
  })

  return (
    <BoxMain>
      {/* Render table */}
    </BoxMain>
  )
}
```

## Key Takeaways

1. **Headless = Logic Only** - You provide the UI
2. **Table Instance = Controller** - Central orchestration object
3. **State Can Be Controlled** - For persistence and debugging
4. **Row Models = Data Pipeline** - Process data through features
5. **flexRender = Dynamic Rendering** - Handles functions and components
6. **You Own the Markup** - Complete design control

## Next Steps

- **Column Definitions** → See pattern 03
- **Table Instance Details** → See pattern 04
- **Row Models Deep Dive** → See pattern 05
- **Rendering Patterns** → See pattern 06
