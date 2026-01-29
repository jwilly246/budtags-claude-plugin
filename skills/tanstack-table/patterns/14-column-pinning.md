# Pattern 14: Column Pinning

## Column Pinning State

Column pinning splits columns into three groups: left (pinned left), center (unpinned), and right (pinned right).

```typescript
type ColumnPinningState = {
  left?: string[]   // Column IDs pinned to left
  right?: string[]  // Column IDs pinned to right
}

// Example:
const columnPinning = {
  left: ['select', 'Label'],
  right: ['actions'],
}
```

## Enabling Column Pinning

```typescript
const [columnPinning, setColumnPinning] = useState<ColumnPinningState>({
  left: [],
  right: [],
})

const table = useReactTable({
  data,
  columns,
  state: { columnPinning },
  onColumnPinningChange: setColumnPinning,
  getCoreRowModel: getCoreRowModel(),
})
```

## Initial Pinned Columns

```typescript
const table = useReactTable({
  data,
  columns,
  initialState: {
    columnPinning: {
      left: ['select'],
      right: ['actions'],
    },
  },
  getCoreRowModel: getCoreRowModel(),
})
```

## Column Pinning Affects Order

Pinning takes precedence over manual column ordering:

1. **Column Pinning** - Splits into left/center/right
2. **Manual Column Ordering** - Only affects center (unpinned) columns
3. **Grouping** - If enabled

## Sticky CSS Implementation (Recommended)

Use sticky positioning for pinned columns:

```typescript
function StickyTable({ data }: { data: Package[] }) {
  const [columnPinning, setColumnPinning] = useState<ColumnPinningState>({
    left: ['select'],
    right: ['actions'],
  })

  const table = useReactTable({
    data,
    columns,
    state: { columnPinning },
    onColumnPinningChange: setColumnPinning,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div className="overflow-x-auto">
      <table>
        <thead>
          {table.getHeaderGroups().map(headerGroup => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map(header => {
                const isPinned = header.column.getIsPinned()

                return (
                  <th
                    key={header.id}
                    style={{
                      position: isPinned ? 'sticky' : 'relative',
                      left: isPinned === 'left' ? `${header.column.getStart('left')}px` : undefined,
                      right: isPinned === 'right' ? `${header.column.getAfter('right')}px` : undefined,
                      zIndex: isPinned ? 1 : 0,
                    }}
                    className={`
                      ${isPinned ? 'bg-white' : ''}
                      ${header.column.getIsLastColumn('left') ? 'shadow-r' : ''}
                      ${header.column.getIsFirstColumn('right') ? 'shadow-l' : ''}
                    `}
                  >
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
                  </th>
                )
              })}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map(row => (
            <tr key={row.id}>
              {row.getVisibleCells().map(cell => {
                const isPinned = cell.column.getIsPinned()

                return (
                  <td
                    key={cell.id}
                    style={{
                      position: isPinned ? 'sticky' : 'relative',
                      left: isPinned === 'left' ? `${cell.column.getStart('left')}px` : undefined,
                      right: isPinned === 'right' ? `${cell.column.getAfter('right')}px` : undefined,
                      zIndex: isPinned ? 1 : 0,
                    }}
                    className={`
                      ${isPinned ? 'bg-white' : ''}
                      ${cell.column.getIsLastColumn('left') ? 'shadow-r' : ''}
                      ${cell.column.getIsFirstColumn('right') ? 'shadow-l' : ''}
                    `}
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

### Tailwind Shadow Utilities

```css
/* Add to your Tailwind config or CSS */
.shadow-r {
  box-shadow: 4px 0 6px -1px rgba(0, 0, 0, 0.1);
}

.shadow-l {
  box-shadow: -4px 0 6px -1px rgba(0, 0, 0, 0.1);
}
```

## Split Table Implementation

Render separate tables for left/center/right sections:

```typescript
function SplitTable({ data }: { data: Package[] }) {
  const [columnPinning, setColumnPinning] = useState<ColumnPinningState>({
    left: ['select'],
    right: ['actions'],
  })

  const table = useReactTable({
    data,
    columns,
    state: { columnPinning },
    onColumnPinningChange: setColumnPinning,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div className="flex overflow-x-auto">
      {/* Left pinned columns */}
      {table.getLeftHeaderGroups().length > 0 && (
        <table className="border-r">
          <thead>
            {table.getLeftHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th key={header.id}>
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map(row => (
              <tr key={row.id}>
                {row.getLeftVisibleCells().map(cell => (
                  <td key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Center (unpinned) columns */}
      <table className="flex-1">
        <thead>
          {table.getCenterHeaderGroups().map(headerGroup => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map(header => (
                <th key={header.id}>
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map(row => (
            <tr key={row.id}>
              {row.getCenterVisibleCells().map(cell => (
                <td key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Right pinned columns */}
      {table.getRightHeaderGroups().length > 0 && (
        <table className="border-l">
          <thead>
            {table.getRightHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th key={header.id}>
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map(row => (
              <tr key={row.id}>
                {row.getRightVisibleCells().map(cell => (
                  <td key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
```

## Pin/Unpin UI Controls

```typescript
function ColumnPinControls({ column }: { column: Column<any> }) {
  const isPinned = column.getIsPinned()

  if (!column.getCanPin()) {
    return null
  }

  return (
    <div className="flex gap-1">
      <button
        onClick={() => column.pin('left')}
        disabled={isPinned === 'left'}
        className="text-xs px-2 py-1 border rounded disabled:opacity-50"
      >
        📌 Left
      </button>
      <button
        onClick={() => column.pin(false)}
        disabled={!isPinned}
        className="text-xs px-2 py-1 border rounded disabled:opacity-50"
      >
        Unpin
      </button>
      <button
        onClick={() => column.pin('right')}
        disabled={isPinned === 'right'}
        className="text-xs px-2 py-1 border rounded disabled:opacity-50"
      >
        Right 📌
      </button>
    </div>
  )
}
```

## Programmatic Pinning

```typescript
// Pin column to left
table.getColumn('Label')?.pin('left')

// Pin column to right
table.getColumn('actions')?.pin('right')

// Unpin column
table.getColumn('Label')?.pin(false)

// Set multiple pins at once
table.setColumnPinning({
  left: ['select', 'Label'],
  right: ['actions'],
})
```

## Disable Pinning

### Disable for Specific Column

```typescript
columnHelper.accessor('ProductName', {
  header: 'Product',
  enablePinning: false, // ← Can't pin this column
})
```

## Column Pinning API Methods

### Column Methods

```typescript
column.getCanPin()           // boolean
column.getIsPinned()         // 'left' | 'right' | false
column.pin(position)         // 'left' | 'right' | false

// Positioning helpers
column.getStart(position)    // Get CSS left value
column.getAfter(position)    // Get CSS right value

// Boundary checks
column.getIsLastColumn(position)  // Last in pinned group
column.getIsFirstColumn(position) // First in pinned group
```

### Table Methods

```typescript
// Get pinned header groups
table.getLeftHeaderGroups()
table.getCenterHeaderGroups()
table.getRightHeaderGroups()

// Set pinning
table.setColumnPinning({ left: [...], right: [...] })

// Reset pinning
table.resetColumnPinning()
table.resetColumnPinning(true) // Reset to initial state

// Get state
table.getState().columnPinning
```

### Row Methods

```typescript
// Get pinned cells
row.getLeftVisibleCells()
row.getCenterVisibleCells()
row.getRightVisibleCells()
```

## Complete Pinning Example

```typescript
function PackagesTable({ data }: { data: Package[] }) {
  const [columnPinning, setColumnPinning] = useState<ColumnPinningState>({
    left: ['select'],
    right: ['actions'],
  })

  const columns = useMemo(() => [
    columnHelper.display({
      id: 'select',
      header: ({ table }) => (
        <input
          type="checkbox"
          checked={table.getIsAllRowsSelected()}
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
    columnHelper.accessor('Label', { header: 'Package Tag' }),
    columnHelper.accessor('ProductName', { header: 'Product' }),
    columnHelper.accessor('Quantity', { header: 'Quantity' }),
    columnHelper.accessor('ItemCategory', { header: 'Category' }),
    columnHelper.display({
      id: 'actions',
      header: 'Actions',
      cell: () => <button>Edit</button>,
    }),
  ], [])

  const table = useReactTable({
    data,
    columns,
    state: { columnPinning },
    onColumnPinningChange: setColumnPinning,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div>
      <button
        onClick={() => table.resetColumnPinning()}
        className="mb-4 text-blue-600"
      >
        Reset Pinning
      </button>

      <div className="overflow-x-auto border rounded">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => {
                  const isPinned = header.column.getIsPinned()

                  return (
                    <th
                      key={header.id}
                      style={{
                        position: isPinned ? 'sticky' : 'relative',
                        left:
                          isPinned === 'left'
                            ? `${header.column.getStart('left')}px`
                            : undefined,
                        right:
                          isPinned === 'right'
                            ? `${header.column.getAfter('right')}px`
                            : undefined,
                        width: header.getSize(),
                        zIndex: isPinned ? 1 : 0,
                      }}
                      className={`
                        px-4 py-2 border-b
                        ${isPinned ? 'bg-gray-50' : ''}
                        ${header.column.getIsLastColumn('left') ? 'border-r-2 border-gray-300' : ''}
                        ${header.column.getIsFirstColumn('right') ? 'border-l-2 border-gray-300' : ''}
                      `}
                    >
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                    </th>
                  )
                })}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map(row => (
              <tr key={row.id} className="hover:bg-gray-50">
                {row.getVisibleCells().map(cell => {
                  const isPinned = cell.column.getIsPinned()

                  return (
                    <td
                      key={cell.id}
                      style={{
                        position: isPinned ? 'sticky' : 'relative',
                        left:
                          isPinned === 'left'
                            ? `${cell.column.getStart('left')}px`
                            : undefined,
                        right:
                          isPinned === 'right'
                            ? `${cell.column.getAfter('right')}px`
                            : undefined,
                        width: cell.column.getSize(),
                        zIndex: isPinned ? 1 : 0,
                      }}
                      className={`
                        px-4 py-2 border-b
                        ${isPinned ? 'bg-white' : ''}
                        ${cell.column.getIsLastColumn('left') ? 'border-r-2 border-gray-200' : ''}
                        ${cell.column.getIsFirstColumn('right') ? 'border-l-2 border-gray-200' : ''}
                      `}
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

## Common Patterns

### Pin Selection and Actions

```typescript
initialState: {
  columnPinning: {
    left: ['select'],
    right: ['actions'],
  },
}
```

### Pin ID Column

```typescript
initialState: {
  columnPinning: {
    left: ['id'],
  },
}
```

## Common Mistakes

### ❌ Forgetting z-index for Sticky Columns

```typescript
// ❌ Will appear behind other columns
style={{ position: 'sticky', left: 0 }}

// ✅ Correct with z-index
style={{ position: 'sticky', left: 0, zIndex: 1 }}
```

### ❌ Not Adding Background Color

```typescript
// ❌ Background shows through when scrolling
style={{ position: 'sticky', left: 0 }}

// ✅ Solid background
style={{ position: 'sticky', left: 0 }}
className="bg-white"
```

## Type Definitions

```typescript
type ColumnPinningState = {
  left?: string[]
  right?: string[]
}

type ColumnPinningPosition = 'left' | 'right' | false

type ColumnPinningColumn = {
  getCanPin: () => boolean
  getIsPinned: () => ColumnPinningPosition
  pin: (position: ColumnPinningPosition) => void
  getStart: (position?: ColumnPinningPosition) => number
  getAfter: (position?: ColumnPinningPosition) => number
  getIsLastColumn: (position: ColumnPinningPosition) => boolean
  getIsFirstColumn: (position: ColumnPinningPosition) => boolean
}
```

## Next Steps

- **Row Expansion** → See pattern 15
- **Column Ordering** → See pattern 12
- **Column Sizing** → See pattern 13
- **Combine Features** → Use pinning with sizing and ordering
