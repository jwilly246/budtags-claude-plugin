# Pattern 15: Row Expansion

## Enabling Row Expansion

To enable row expansion, add the expanded row model:

```typescript
import { getExpandedRowModel } from '@tanstack/react-table'

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getExpandedRowModel: getExpandedRowModel(), // ← Enable expansion
})
```

## Two Expansion Use Cases

1. **Sub-Rows Expansion** - Hierarchical data with child rows
2. **Custom UI Expansion** - Detail panels, additional information

## Sub-Rows Expansion

### Define Sub-Rows

```typescript
type Package = {
  Id: number
  Label: string
  ProductName: string
  children?: Package[] // ← Sub-rows
}

const table = useReactTable({
  data,
  columns,
  getSubRows: row => row.children, // ← Tell table where sub-rows are
  getCoreRowModel: getCoreRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
})
```

### Expansion State

```typescript
type ExpandedState = Record<string, boolean> | true

const [expanded, setExpanded] = useState<ExpandedState>({})

const table = useReactTable({
  data,
  columns,
  state: { expanded },
  onExpandedChange: setExpanded,
  getSubRows: row => row.children,
  getCoreRowModel: getCoreRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
})

// Examples:
// {} - All collapsed
// { '0': true } - Row 0 expanded
// { '0': true, '0.1': true } - Row 0 and its first child expanded
// true - All rows expanded
```

### Render Sub-Rows

```typescript
<tbody>
  {table.getRowModel().rows.map(row => (
    <Fragment key={row.id}>
      {/* Main row */}
      <tr>
        {row.getVisibleCells().map(cell => (
          <td key={cell.id}>
            {flexRender(cell.column.columnDef.cell, cell.getContext())}
          </td>
        ))}
      </tr>

      {/* Sub-rows render automatically through getRowModel() */}
    </Fragment>
  ))}
</tbody>
```

### Expand/Collapse Button

```typescript
columnHelper.display({
  id: 'expander',
  header: () => null,
  cell: ({ row }) =>
    row.getCanExpand() ? (
      <button
        onClick={row.getToggleExpandedHandler()}
        style={{ paddingLeft: `${row.depth * 2}rem` }}
      >
        {row.getIsExpanded() ? '👇' : '👉'}
      </button>
    ) : null,
})
```

### Visual Hierarchy (Indentation)

```typescript
columnHelper.accessor('Label', {
  header: 'Package Tag',
  cell: ({ row, getValue }) => (
    <div style={{ paddingLeft: `${row.depth * 2}rem` }}>
      {getValue()}
    </div>
  ),
})
```

## Custom UI Expansion

### Enable All Rows to Expand

```typescript
const table = useReactTable({
  data,
  columns,
  state: { expanded },
  onExpandedChange: setExpanded,
  getRowCanExpand: () => true, // ← All rows can expand
  getCoreRowModel: getCoreRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
})
```

### Render Expanded Content

```typescript
<tbody>
  {table.getRowModel().rows.map(row => (
    <Fragment key={row.id}>
      {/* Main row */}
      <tr>
        <td>
          <button onClick={row.getToggleExpandedHandler()}>
            {row.getIsExpanded() ? '−' : '+'}
          </button>
        </td>
        {row.getVisibleCells().map(cell => (
          <td key={cell.id}>
            {flexRender(cell.column.columnDef.cell, cell.getContext())}
          </td>
        ))}
      </tr>

      {/* Expanded content */}
      {row.getIsExpanded() && (
        <tr>
          <td colSpan={row.getAllCells().length}>
            <div className="p-4 bg-gray-50">
              {/* Custom expanded UI */}
              <h3>Details for {row.original.Label}</h3>
              <p>Additional information...</p>
            </div>
          </td>
        </tr>
      )}
    </Fragment>
  ))}
</tbody>
```

## Programmatic Expansion

### Expand/Collapse Specific Rows

```typescript
// Expand row
row.toggleExpanded(true)

// Collapse row
row.toggleExpanded(false)

// Toggle row
row.toggleExpanded()

// Expand all rows
table.toggleAllRowsExpanded(true)

// Collapse all rows
table.toggleAllRowsExpanded(false)

// Set specific expansion state
table.setExpanded({ '0': true, '1': true })

// Expand all
table.setExpanded(true)

// Collapse all
table.setExpanded({})
```

## Filtering with Sub-Rows

### Filter from Leaf Rows

```typescript
const table = useReactTable({
  data,
  columns,
  state: { expanded, columnFilters },
  onExpandedChange: setExpanded,
  onColumnFiltersChange: setColumnFilters,
  getSubRows: row => row.children,
  filterFromLeafRows: true, // ← Filter from children upward
  maxLeafRowFilterDepth: 0, // ← 0 = unlimited depth
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
})
```

## Pagination with Expansion

### Include Expanded Rows in Pagination

```typescript
const table = useReactTable({
  data,
  columns,
  state: { expanded, pagination },
  onExpandedChange: setExpanded,
  onPaginationChange: setPagination,
  paginateExpandedRows: true, // ← Default: true (count expanded rows)
  getCoreRowModel: getCoreRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
})
```

### Exclude Expanded Rows from Pagination

```typescript
const table = useReactTable({
  paginateExpandedRows: false, // ← Only count top-level rows
  // ...
})
```

## Manual Expansion (Server-Side)

```typescript
const [expanded, setExpanded] = useState<ExpandedState>({})

const { data: serverData } = useQuery({
  queryKey: ['packages', expanded],
  queryFn: () => fetchPackagesWithChildren({ expanded }),
})

const table = useReactTable({
  data: serverData?.data ?? [],
  columns,
  state: { expanded },
  onExpandedChange: setExpanded,
  manualExpanding: true, // ← YOU handle expansion
  getCoreRowModel: getCoreRowModel(),
  // No getExpandedRowModel - server provides expanded data
})
```

## Row Expansion API Methods

### Row Methods

```typescript
row.getCanExpand()           // boolean
row.getIsExpanded()          // boolean
row.toggleExpanded()         // Toggle
row.toggleExpanded(true)     // Force expand
row.toggleExpanded(false)    // Force collapse
row.getToggleExpandedHandler() // For onClick

row.depth                    // Number (nesting level)
row.getParentRow()           // Parent row instance
row.subRows                  // Child rows array
```

### Table Methods

```typescript
table.toggleAllRowsExpanded()
table.toggleAllRowsExpanded(true)  // Expand all
table.toggleAllRowsExpanded(false) // Collapse all

table.setExpanded({ ... })
table.setExpanded(true)            // Expand all
table.setExpanded({})              // Collapse all

table.resetExpanded()
table.resetExpanded(true)          // Reset to initial state

table.getState().expanded

table.getExpandedRowModel().rows   // All expanded rows
table.getIsAllRowsExpanded()       // boolean
table.getIsSomeRowsExpanded()      // boolean
```

## Complete Sub-Rows Example

```typescript
type Package = {
  Id: number
  Label: string
  ProductName: string
  Quantity: number
  children?: Package[]
}

function HierarchicalTable({ data }: { data: Package[] }) {
  const [expanded, setExpanded] = useState<ExpandedState>({})

  const columns = useMemo(() => [
    columnHelper.display({
      id: 'expander',
      cell: ({ row }) => (
        row.getCanExpand() ? (
          <button
            onClick={row.getToggleExpandedHandler()}
            style={{ paddingLeft: `${row.depth}rem` }}
          >
            {row.getIsExpanded() ? '−' : '+'}
          </button>
        ) : null
      ),
    }),
    columnHelper.accessor('Label', {
      header: 'Package Tag',
      cell: ({ row, getValue }) => (
        <div style={{ paddingLeft: `${row.depth * 2}rem` }}>
          {getValue()}
        </div>
      ),
    }),
    columnHelper.accessor('ProductName', {
      header: 'Product',
    }),
    columnHelper.accessor('Quantity', {
      header: 'Quantity',
    }),
  ], [])

  const table = useReactTable({
    data,
    columns,
    state: { expanded },
    onExpandedChange: setExpanded,
    getSubRows: row => row.children,
    getCoreRowModel: getCoreRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
  })

  return (
    <div>
      <div className="mb-4 flex gap-2">
        <button
          onClick={() => table.toggleAllRowsExpanded(true)}
          className="px-4 py-2 border rounded"
        >
          Expand All
        </button>
        <button
          onClick={() => table.toggleAllRowsExpanded(false)}
          className="px-4 py-2 border rounded"
        >
          Collapse All
        </button>
      </div>

      <table className="min-w-full border">
        <thead>
          {table.getHeaderGroups().map(headerGroup => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map(header => (
                <th key={header.id} className="border px-4 py-2 bg-gray-50">
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
            <tr
              key={row.id}
              className={`
                hover:bg-gray-50
                ${row.depth > 0 ? 'bg-gray-50' : ''}
              `}
            >
              {row.getVisibleCells().map(cell => (
                <td key={cell.id} className="border px-4 py-2">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

## Complete Custom UI Example

```typescript
function DetailPanelTable({ data }: { data: Package[] }) {
  const [expanded, setExpanded] = useState<ExpandedState>({})

  const columns = useMemo(() => [
    columnHelper.display({
      id: 'expander',
      cell: ({ row }) => (
        <button
          onClick={row.getToggleExpandedHandler()}
          className="text-blue-600"
        >
          {row.getIsExpanded() ? '−' : '+'}
        </button>
      ),
    }),
    columnHelper.accessor('Label', { header: 'Package Tag' }),
    columnHelper.accessor('ProductName', { header: 'Product' }),
    columnHelper.accessor('Quantity', { header: 'Quantity' }),
  ], [])

  const table = useReactTable({
    data,
    columns,
    state: { expanded },
    onExpandedChange: setExpanded,
    getRowCanExpand: () => true,
    getCoreRowModel: getCoreRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
  })

  return (
    <table className="min-w-full border">
      <thead>
        {table.getHeaderGroups().map(headerGroup => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map(header => (
              <th key={header.id} className="border px-4 py-2 bg-gray-50">
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
          <Fragment key={row.id}>
            {/* Main row */}
            <tr className="hover:bg-gray-50">
              {row.getVisibleCells().map(cell => (
                <td key={cell.id} className="border px-4 py-2">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>

            {/* Expanded detail panel */}
            {row.getIsExpanded() && (
              <tr>
                <td colSpan={row.getAllCells().length} className="border">
                  <div className="p-4 bg-gray-50">
                    <h3 className="font-bold mb-2">
                      Package Details: {row.original.Label}
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <strong>Product:</strong> {row.original.ProductName}
                      </div>
                      <div>
                        <strong>Quantity:</strong> {row.original.Quantity}
                      </div>
                      <div>
                        <strong>Category:</strong> {row.original.ItemCategory}
                      </div>
                      <div>
                        <strong>Received:</strong>{' '}
                        {new Date(
                          row.original.ReceivedDateTime
                        ).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            )}
          </Fragment>
        ))}
      </tbody>
    </table>
  )
}
```

## Common Mistakes

### ❌ Forgetting getExpandedRowModel

```typescript
// ❌ Expansion won't work
const table = useReactTable({
  getSubRows: row => row.children,
  getCoreRowModel: getCoreRowModel(),
  // Missing getExpandedRowModel!
})

// ✅ Correct
const table = useReactTable({
  getSubRows: row => row.children,
  getCoreRowModel: getCoreRowModel(),
  getExpandedRowModel: getExpandedRowModel(), // ✅
})
```

### ❌ Not Providing getSubRows for Hierarchical Data

```typescript
// ❌ Won't know where to find sub-rows
const table = useReactTable({
  getCoreRowModel: getCoreRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
})

// ✅ Tell table where sub-rows are
const table = useReactTable({
  getSubRows: row => row.children, // ✅
  getCoreRowModel: getCoreRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
})
```

## Type Definitions

```typescript
type ExpandedState = Record<string, boolean> | true

type ExpandedTableState = {
  expanded: ExpandedState
}

type ExpandedOptions<TData> = {
  manualExpanding?: boolean
  onExpandedChange?: OnChangeFn<ExpandedState>
  paginateExpandedRows?: boolean
  filterFromLeafRows?: boolean
  maxLeafRowFilterDepth?: number
  getSubRows?: (row: TData, index: number) => TData[] | undefined
  getRowCanExpand?: (row: Row<TData>) => boolean
  getExpandedRowModel?: (table: Table<any>) => () => RowModel<TData>
}
```

## Next Steps

- **Row Grouping** → See pattern 16
- **Custom Expansion UI** → Detail panels, sub-tables
- **Filtering with Sub-Rows** → Filter from leaf rows
- **Pagination** → Control expanded row pagination
