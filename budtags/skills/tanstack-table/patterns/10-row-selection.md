# Pattern 10: Row Selection

## Enabling Row Selection

Row selection is enabled by default, but you need to manage the state:

```typescript
const [rowSelection, setRowSelection] = useState({})

const table = useReactTable({
  data,
  columns,
  state: { rowSelection },
  onRowSelectionChange: setRowSelection,
  getCoreRowModel: getCoreRowModel(),
  enableRowSelection: true, // ← Default is true
})
```

## Row Selection State

### Structure

```typescript
type RowSelectionState = Record<string, boolean>

// Example:
const rowSelection = {
  '0': true,    // Row at index 0 selected
  '1': false,   // Row at index 1 not selected
  '3': true,    // Row at index 3 selected
}
```

### Using Custom Row IDs

```typescript
const table = useReactTable({
  data,
  columns,
  getRowId: row => row.id, // ← Use custom ID instead of index
  state: { rowSelection },
  onRowSelectionChange: setRowSelection,
  getCoreRowModel: getCoreRowModel(),
})

// Now selection state uses your custom IDs:
// { 'user-123': true, 'user-456': true }
```

## Checkbox Selection UI

### Basic Checkbox Column

```typescript
const columns = [
  columnHelper.display({
    id: 'select',
    header: ({ table }) => (
      <input
        type="checkbox"
        checked={table.getIsAllRowsSelected()}
        indeterminate={table.getIsSomeRowsSelected()}
        onChange={table.getToggleAllRowsSelectedHandler()}
      />
    ),
    cell: ({ row }) => (
      <input
        type="checkbox"
        checked={row.getIsSelected()}
        onChange={row.getToggleSelectedHandler()}
      />
    ),
  }),
  // ... other columns
]
```

### Checkbox with Disabled State

```typescript
columnHelper.display({
  id: 'select',
  header: ({ table }) => (
    <input
      type="checkbox"
      checked={table.getIsAllRowsSelected()}
      indeterminate={table.getIsSomeRowsSelected()}
      onChange={table.getToggleAllRowsSelectedHandler()}
    />
  ),
  cell: ({ row }) => (
    <input
      type="checkbox"
      checked={row.getIsSelected()}
      disabled={!row.getCanSelect()} // ← Respect conditional selection
      onChange={row.getToggleSelectedHandler()}
    />
  ),
})
```

### Indeterminate Checkbox (Select All)

```typescript
function IndeterminateCheckbox({
  checked,
  indeterminate,
  onChange,
}: {
  checked: boolean
  indeterminate: boolean
  onChange: () => void
}) {
  const ref = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (ref.current) {
      ref.current.indeterminate = indeterminate
    }
  }, [indeterminate])

  return (
    <input
      type="checkbox"
      ref={ref}
      checked={checked}
      onChange={onChange}
    />
  )
}

// Usage
<IndeterminateCheckbox
  checked={table.getIsAllRowsSelected()}
  indeterminate={table.getIsSomeRowsSelected()}
  onChange={table.getToggleAllRowsSelectedHandler()}
/>
```

## Single Row Selection (Radio Buttons)

```typescript
const [rowSelection, setRowSelection] = useState({})

const table = useReactTable({
  data,
  columns,
  state: { rowSelection },
  onRowSelectionChange: setRowSelection,
  enableMultiRowSelection: false, // ← Only one row at a time
  getCoreRowModel: getCoreRowModel(),
})

// Radio button column
columnHelper.display({
  id: 'select',
  cell: ({ row }) => (
    <input
      type="radio"
      name="row-selection"
      checked={row.getIsSelected()}
      onChange={row.getToggleSelectedHandler()}
    />
  ),
})
```

## Conditional Row Selection

### Enable/Disable Selection Per Row

```typescript
const table = useReactTable({
  data,
  columns,
  state: { rowSelection },
  onRowSelectionChange: setRowSelection,
  enableRowSelection: row => row.original.Quantity > 0, // ← Only select if qty > 0
  getCoreRowModel: getCoreRowModel(),
})
```

### Common Conditional Patterns

```typescript
// Only active packages
enableRowSelection: row => !row.original.FinishedDate

// Only certain types
enableRowSelection: row => row.original.ItemCategory === 'Flower'

// Based on permission
enableRowSelection: row => hasPermission('edit-packages')

// Combined conditions
enableRowSelection: row =>
  !row.original.FinishedDate && row.original.Quantity > 0
```

## Sub-Row Selection

### Enable/Disable Sub-Row Selection

```typescript
const table = useReactTable({
  data,
  columns,
  state: { rowSelection },
  onRowSelectionChange: setRowSelection,
  enableSubRowSelection: true, // ← Default: selecting parent selects children
  getCoreRowModel: getCoreRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
})

// Disable sub-row selection
const table = useReactTable({
  enableSubRowSelection: false, // ← Parent selection doesn't affect children
  // ...
})
```

## Select All Variants

### Select All Rows

```typescript
<input
  type="checkbox"
  checked={table.getIsAllRowsSelected()}
  indeterminate={table.getIsSomeRowsSelected()}
  onChange={table.getToggleAllRowsSelectedHandler()}
/>
```

### Select All on Current Page

```typescript
<input
  type="checkbox"
  checked={table.getIsAllPageRowsSelected()}
  indeterminate={table.getIsSomePageRowsSelected()}
  onChange={table.getToggleAllPageRowsSelectedHandler()}
/>
```

## Programmatic Selection

### Select Specific Rows

```typescript
// Select by row ID
table.setRowSelection({ '0': true, '2': true })

// Select by custom ID
table.setRowSelection({ 'user-123': true, 'user-456': true })

// Clear selection
table.setRowSelection({})

// Toggle specific row
table.getRow('0').toggleSelected()

// Select all
table.toggleAllRowsSelected(true)

// Deselect all
table.toggleAllRowsSelected(false)
```

### Get Selected Rows

```typescript
// Get selection state object
const selection = table.getState().rowSelection
// { '0': true, '2': true }

// Get selected row instances
const selectedRows = table.getSelectedRowModel().rows

// Get selected row data
const selectedData = selectedRows.map(row => row.original)

// Get filtered selected rows
const filteredSelected = table.getFilteredSelectedRowModel().rows

// Get grouped selected rows
const groupedSelected = table.getGroupedSelectedRowModel().rows
```

## Row Selection API Methods

### Row Methods

```typescript
// Check selection
row.getIsSelected()          // boolean
row.getCanSelect()           // boolean
row.getIsSomeSelected()      // boolean (for parent rows with sub-rows)

// Toggle selection
row.toggleSelected()         // Toggle
row.toggleSelected(true)     // Force select
row.toggleSelected(false)    // Force deselect

// Get handler
row.getToggleSelectedHandler() // For onChange
```

### Table Methods

```typescript
// Check selection
table.getIsAllRowsSelected()      // boolean
table.getIsSomeRowsSelected()     // boolean
table.getIsAllPageRowsSelected()  // boolean
table.getIsSomePageRowsSelected() // boolean

// Toggle selection
table.toggleAllRowsSelected()
table.toggleAllRowsSelected(true)  // Select all
table.toggleAllRowsSelected(false) // Deselect all
table.toggleAllPageRowsSelected()

// Get handlers
table.getToggleAllRowsSelectedHandler()
table.getToggleAllPageRowsSelectedHandler()

// Reset selection
table.resetRowSelection()
table.resetRowSelection(true) // Reset to initial state

// Set selection
table.setRowSelection({ '0': true, '1': true })

// Get selected rows
table.getSelectedRowModel().rows
table.getFilteredSelectedRowModel().rows
table.getGroupedSelectedRowModel().rows
```

## Complete Selection Example

```typescript
function PackagesTable({ data }: { data: Package[] }) {
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({})

  const columns = useMemo(() => [
    columnHelper.display({
      id: 'select',
      header: ({ table }) => (
        <input
          type="checkbox"
          checked={table.getIsAllPageRowsSelected()}
          indeterminate={table.getIsSomePageRowsSelected()}
          onChange={table.getToggleAllPageRowsSelectedHandler()}
        />
      ),
      cell: ({ row }) => (
        <input
          type="checkbox"
          checked={row.getIsSelected()}
          disabled={!row.getCanSelect()}
          onChange={row.getToggleSelectedHandler()}
        />
      ),
    }),
    columnHelper.accessor('Label', { header: 'Package Tag' }),
    columnHelper.accessor('ProductName', { header: 'Product' }),
    columnHelper.accessor('Quantity', { header: 'Quantity' }),
  ], [])

  const table = useReactTable({
    data,
    columns,
    state: { rowSelection },
    onRowSelectionChange: setRowSelection,
    enableRowSelection: row => row.original.Quantity > 0,
    getCoreRowModel: getCoreRowModel(),
  })

  const selectedPackages = table
    .getSelectedRowModel()
    .rows.map(row => row.original)

  return (
    <div>
      {/* Selection info */}
      <div className="mb-4">
        Selected {selectedPackages.length} package(s)
        {selectedPackages.length > 0 && (
          <button
            onClick={() => table.resetRowSelection()}
            className="ml-4 text-blue-600"
          >
            Clear Selection
          </button>
        )}
      </div>

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
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Actions for selected rows */}
      {selectedPackages.length > 0 && (
        <div className="mt-4">
          <button onClick={() => console.log(selectedPackages)}>
            Process {selectedPackages.length} Selected
          </button>
        </div>
      )}
    </div>
  )
}
```

## BudTags Pattern: Checkbox Column Helper

**File:** `resources/js/Components/TableHelpers.tsx`

```typescript
export function createCheckboxColumn<TData>(): ColumnDef<TData> {
  return {
    id: 'select',
    header: ({ table }) => (
      <input
        type="checkbox"
        checked={table.getIsAllPageRowsSelected()}
        indeterminate={table.getIsSomePageRowsSelected()}
        onChange={table.getToggleAllPageRowsSelectedHandler()}
        className="cursor-pointer"
      />
    ),
    cell: ({ row }) => (
      <input
        type="checkbox"
        checked={row.getIsSelected()}
        disabled={!row.getCanSelect()}
        onChange={row.getToggleSelectedHandler()}
        className="cursor-pointer"
      />
    ),
  }
}

// Usage
const columns = [
  createCheckboxColumn<Package>(),
  columnHelper.accessor('Label', { header: 'Package Tag' }),
  // ...
]
```

## Common Patterns

### Persist Selection Across Pages

```typescript
const [rowSelection, setRowSelection] = useState<RowSelectionState>({})

// Selection persists across page changes because state is external
const table = useReactTable({
  data,
  columns,
  state: { rowSelection, pagination },
  onRowSelectionChange: setRowSelection,
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
})
```

### Bulk Actions on Selected Rows

```typescript
function BulkActions({ table }: { table: Table<Package> }) {
  const selectedRows = table.getSelectedRowModel().rows

  const handleBulkDelete = () => {
    const ids = selectedRows.map(row => row.original.Id)
    // Delete packages with these IDs
  }

  const handleBulkUpdate = () => {
    const packages = selectedRows.map(row => row.original)
    // Update packages
  }

  if (selectedRows.length === 0) return null

  return (
    <div className="flex gap-2">
      <button onClick={handleBulkDelete}>
        Delete {selectedRows.length} items
      </button>
      <button onClick={handleBulkUpdate}>
        Update {selectedRows.length} items
      </button>
    </div>
  )
}
```

## Common Mistakes

### ❌ Forgetting to Set Selection State

```typescript
// ❌ Won't work - no state
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
})

// ✅ Correct
const [rowSelection, setRowSelection] = useState({})
const table = useReactTable({
  data,
  columns,
  state: { rowSelection },
  onRowSelectionChange: setRowSelection,
  getCoreRowModel: getCoreRowModel(),
})
```

### ❌ Not Handling Indeterminate State

```typescript
// ❌ Missing indeterminate
<input
  type="checkbox"
  checked={table.getIsAllRowsSelected()}
  onChange={table.getToggleAllRowsSelectedHandler()}
/>

// ✅ Correct
<input
  type="checkbox"
  checked={table.getIsAllRowsSelected()}
  indeterminate={table.getIsSomeRowsSelected()}
  onChange={table.getToggleAllRowsSelectedHandler()}
/>
```

## Type Definitions

```typescript
type RowSelectionState = Record<string, boolean>

type RowSelectionOptions = {
  enableRowSelection?: boolean | ((row: Row<any>) => boolean)
  enableMultiRowSelection?: boolean
  enableSubRowSelection?: boolean
  onRowSelectionChange?: OnChangeFn<RowSelectionState>
}

type RowSelectionRow = {
  getIsSelected: () => boolean
  getIsSomeSelected: () => boolean
  getCanSelect: () => boolean
  toggleSelected: (value?: boolean) => void
  getToggleSelectedHandler: () => (event: unknown) => void
}
```

## Next Steps

- **Column Visibility** → See pattern 11
- **Column Ordering** → See pattern 12
- **Row Expansion** → See pattern 15
- **Bulk Actions** → Combine with selection state
