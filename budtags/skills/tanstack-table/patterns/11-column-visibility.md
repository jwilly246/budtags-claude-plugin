# Pattern 11: Column Visibility

## Enabling Column Visibility

Column visibility is managed through dedicated state:

```typescript
const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})

const table = useReactTable({
  data,
  columns,
  state: { columnVisibility },
  onColumnVisibilityChange: setColumnVisibility,
  getCoreRowModel: getCoreRowModel(),
})
```

## Column Visibility State

### Structure

```typescript
type VisibilityState = Record<string, boolean>

// Example:
const columnVisibility = {
  'ProductName': true,   // Visible
  'Quantity': false,     // Hidden
  'actions': true,       // Visible
}
```

### Initial State

```typescript
const table = useReactTable({
  data,
  columns,
  initialState: {
    columnVisibility: {
      'ItemCategory': false,  // Hidden by default
      'actions': false,        // Hidden by default
    },
  },
  getCoreRowModel: getCoreRowModel(),
})
```

**Don't combine `initialState.columnVisibility` and `state.columnVisibility` - choose one!**

## Prevent Column from Being Hidden

```typescript
columnHelper.accessor('Label', {
  header: 'Package Tag',
  enableHiding: false, // ← Can't be hidden
})

columnHelper.display({
  id: 'select',
  enableHiding: false, // ← Checkbox column always visible
  // ...
})
```

## Column Visibility Toggle UI

### Basic Toggle for Single Column

```typescript
<label className="flex items-center gap-2">
  <input
    type="checkbox"
    checked={column.getIsVisible()}
    disabled={!column.getCanHide()}
    onChange={column.getToggleVisibilityHandler()}
  />
  <span>{column.columnDef.header}</span>
</label>
```

### All Columns Toggle List

```typescript
function ColumnVisibilityMenu({ table }: { table: Table<any> }) {
  return (
    <div className="p-4 border rounded">
      <div className="font-bold mb-2">Toggle Columns</div>
      {table.getAllColumns().map(column => {
        return (
          <label
            key={column.id}
            className="flex items-center gap-2 py-1"
          >
            <input
              type="checkbox"
              checked={column.getIsVisible()}
              disabled={!column.getCanHide()}
              onChange={column.getToggleVisibilityHandler()}
              className="cursor-pointer disabled:cursor-not-allowed"
            />
            <span className={!column.getCanHide() ? 'opacity-50' : ''}>
              {typeof column.columnDef.header === 'string'
                ? column.columnDef.header
                : column.id}
            </span>
          </label>
        )
      })}
    </div>
  )
}
```

### Dropdown Menu for Column Visibility

```typescript
function ColumnVisibilityDropdown({ table }: { table: Table<any> }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-4 py-2 border rounded"
      >
        Columns ▼
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white border rounded shadow-lg z-10">
          <div className="p-2 border-b font-semibold">Show Columns</div>
          <div className="p-2 max-h-64 overflow-y-auto">
            {table.getAllLeafColumns().map(column => (
              <label
                key={column.id}
                className="flex items-center gap-2 py-1 hover:bg-gray-50 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={column.getIsVisible()}
                  disabled={!column.getCanHide()}
                  onChange={column.getToggleVisibilityHandler()}
                />
                <span className="text-sm">
                  {typeof column.columnDef.header === 'string'
                    ? column.columnDef.header
                    : column.id}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
```

## Programmatic Column Visibility

### Hide/Show Specific Columns

```typescript
// Hide column
table.getColumn('Quantity')?.toggleVisibility(false)

// Show column
table.getColumn('Quantity')?.toggleVisibility(true)

// Toggle column
table.getColumn('Quantity')?.toggleVisibility()
```

### Set Multiple Columns

```typescript
// Hide multiple columns
table.setColumnVisibility({
  Quantity: false,
  ItemCategory: false,
  actions: false,
})

// Show all columns
table.setColumnVisibility({})
```

### Reset to Initial State

```typescript
table.resetColumnVisibility()
table.resetColumnVisibility(true) // Reset to initial state
```

## Visibility-Aware Rendering

Use visibility-aware methods when rendering:

```typescript
<thead>
  <tr>
    {/* ✅ Only renders visible columns */}
    {table.getVisibleLeafColumns().map(column => (
      <th key={column.id}>{column.columnDef.header}</th>
    ))}
  </tr>
</thead>
<tbody>
  {table.getRowModel().rows.map(row => (
    <tr key={row.id}>
      {/* ✅ Only renders visible cells */}
      {row.getVisibleCells().map(cell => (
        <td key={cell.id}>
          {flexRender(cell.column.columnDef.cell, cell.getContext())}
        </td>
      ))}
    </tr>
  ))}
</tbody>
```

**Don't use `getAllColumns()` or `getAllCells()` for rendering - use visibility-aware methods!**

## Column Visibility Presets

### Save/Load Presets

```typescript
function ColumnPresets({ table }: { table: Table<any> }) {
  const savePreset = () => {
    const visibility = table.getState().columnVisibility
    localStorage.setItem('columnPreset', JSON.stringify(visibility))
  }

  const loadPreset = () => {
    const saved = localStorage.getItem('columnPreset')
    if (saved) {
      table.setColumnVisibility(JSON.parse(saved))
    }
  }

  const resetToDefault = () => {
    table.resetColumnVisibility(true)
  }

  return (
    <div className="flex gap-2">
      <button onClick={savePreset}>Save Preset</button>
      <button onClick={loadPreset}>Load Preset</button>
      <button onClick={resetToDefault}>Reset to Default</button>
    </div>
  )
}
```

### Common Presets

```typescript
function QuickPresets({ table }: { table: Table<Package> }) {
  const showAll = () => {
    table.setColumnVisibility({})
  }

  const showEssential = () => {
    table.setColumnVisibility({
      Label: true,
      ProductName: true,
      Quantity: true,
      // All others hidden
      ItemCategory: false,
      UnitOfMeasureName: false,
      ReceivedDateTime: false,
      actions: true,
    })
  }

  const showDetails = () => {
    table.setColumnVisibility({
      Label: true,
      ProductName: true,
      Quantity: true,
      ItemCategory: true,
      UnitOfMeasureName: true,
      ReceivedDateTime: true,
      FinishedDate: true,
      actions: true,
    })
  }

  return (
    <div className="flex gap-2">
      <button onClick={showAll}>Show All</button>
      <button onClick={showEssential}>Essential</button>
      <button onClick={showDetails}>Detailed</button>
    </div>
  )
}
```

## Column Visibility API Methods

### Column Methods

```typescript
// Check visibility
column.getIsVisible()        // boolean
column.getCanHide()          // boolean

// Toggle visibility
column.toggleVisibility()
column.toggleVisibility(true)  // Force show
column.toggleVisibility(false) // Force hide

// Get handler
column.getToggleVisibilityHandler() // For onChange
```

### Table Methods

```typescript
// Get columns
table.getAllColumns()        // All columns
table.getAllLeafColumns()    // All leaf columns (no groups)
table.getVisibleLeafColumns() // Only visible leaf columns

// Set visibility
table.setColumnVisibility({ columnId: boolean })

// Reset visibility
table.resetColumnVisibility()
table.resetColumnVisibility(true) // Reset to initial state

// Get state
table.getState().columnVisibility
```

## Complete Visibility Example

```typescript
function PackagesTable({ data }: { data: Package[] }) {
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({
    ItemCategory: false, // Hidden by default
  })

  const columns = useMemo(() => [
    columnHelper.accessor('Label', {
      header: 'Package Tag',
      enableHiding: false, // Always visible
    }),
    columnHelper.accessor('ProductName', {
      header: 'Product',
    }),
    columnHelper.accessor('Quantity', {
      header: 'Quantity',
    }),
    columnHelper.accessor('ItemCategory', {
      header: 'Category',
    }),
    columnHelper.accessor('UnitOfMeasureName', {
      header: 'Unit',
    }),
    columnHelper.accessor('ReceivedDateTime', {
      header: 'Received',
      cell: info => new Date(info.getValue()).toLocaleDateString(),
    }),
  ], [])

  const table = useReactTable({
    data,
    columns,
    state: { columnVisibility },
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div>
      {/* Column visibility controls */}
      <div className="mb-4 flex gap-4">
        <ColumnVisibilityDropdown table={table} />
        <button
          onClick={() => table.resetColumnVisibility()}
          className="text-blue-600"
        >
          Reset Columns
        </button>
      </div>

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

      {/* Show hidden column count */}
      <div className="mt-2 text-sm text-gray-600">
        {table.getAllLeafColumns().length -
          table.getVisibleLeafColumns().length}{' '}
        column(s) hidden
      </div>
    </div>
  )
}
```

## Responsive Column Visibility

### Hide Columns on Small Screens

```typescript
function ResponsiveTable({ data }: { data: Package[] }) {
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        // Mobile: hide non-essential columns
        setColumnVisibility({
          ItemCategory: false,
          UnitOfMeasureName: false,
          ReceivedDateTime: false,
        })
      } else {
        // Desktop: show all
        setColumnVisibility({})
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const table = useReactTable({
    data,
    columns,
    state: { columnVisibility },
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
  })

  return <table>{/* ... */}</table>
}
```

## Persist Column Visibility

### Save to LocalStorage

```typescript
function PackagesTable({ data }: { data: Package[] }) {
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>(
    () => {
      const saved = localStorage.getItem('packageTableColumns')
      return saved ? JSON.parse(saved) : {}
    }
  )

  useEffect(() => {
    localStorage.setItem(
      'packageTableColumns',
      JSON.stringify(columnVisibility)
    )
  }, [columnVisibility])

  const table = useReactTable({
    data,
    columns,
    state: { columnVisibility },
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
  })

  return <table>{/* ... */}</table>
}
```

## Common Mistakes

### ❌ Using getAllCells Instead of getVisibleCells

```typescript
// ❌ Renders hidden columns
{row.getAllCells().map(cell => <td>...</td>)}

// ✅ Only renders visible columns
{row.getVisibleCells().map(cell => <td>...</td>)}
```

### ❌ Combining initialState and state

```typescript
// ❌ Conflicts - don't do both
const table = useReactTable({
  initialState: {
    columnVisibility: { Quantity: false },
  },
  state: {
    columnVisibility: { ItemCategory: false },
  },
})

// ✅ Choose one
const table = useReactTable({
  state: { columnVisibility },
  onColumnVisibilityChange: setColumnVisibility,
})
```

## Type Definitions

```typescript
type VisibilityState = Record<string, boolean>

type ColumnVisibilityOptions = {
  enableHiding?: boolean
  onColumnVisibilityChange?: OnChangeFn<VisibilityState>
}

type ColumnVisibilityColumn = {
  getCanHide: () => boolean
  getIsVisible: () => boolean
  toggleVisibility: (value?: boolean) => void
  getToggleVisibilityHandler: () => (event: unknown) => void
}
```

## Next Steps

- **Column Ordering** → See pattern 12
- **Column Sizing** → See pattern 13
- **Column Pinning** → See pattern 14
- **Save User Preferences** → Combine with localStorage
