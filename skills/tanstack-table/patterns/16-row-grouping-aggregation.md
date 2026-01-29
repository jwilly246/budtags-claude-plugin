# Pattern 16: Row Grouping & Aggregation

## Enabling Grouping

```typescript
import { getGroupedRowModel, getExpandedRowModel } from '@tanstack/react-table'

const [grouping, setGrouping] = useState<GroupingState>([])
const [expanded, setExpanded] = useState<ExpandedState>({})

const table = useReactTable({
  data,
  columns,
  state: { grouping, expanded },
  onGroupingChange: setGrouping,
  onExpandedChange: setExpanded,
  getCoreRowModel: getCoreRowModel(),
  getGroupedRowModel: getGroupedRowModel(), // ← Enable grouping
  getExpandedRowModel: getExpandedRowModel(), // ← Enable expand/collapse
})
```

## Grouping State

```typescript
type GroupingState = string[] // Column IDs to group by

// Examples:
['ItemCategory']                    // Group by category
['ItemCategory', 'ProductName']     // Group by category, then product
[]                                   // No grouping
```

## Group by Column

```typescript
// Programmatically group
table.setGrouping(['ItemCategory'])

// Toggle grouping for column
column.getToggleGroupingHandler()

// Check if column is grouped
column.getIsGrouped() // boolean

// Check group index
column.getGroupedIndex() // number
```

## Grouped Column Display Mode

```typescript
const table = useReactTable({
  data,
  columns,
  groupedColumnMode: 'reorder', // Move grouped columns to start
  // groupedColumnMode: 'remove',  // Hide grouped columns
  // groupedColumnMode: false,     // Keep columns in place
  getCoreRowModel: getCoreRowModel(),
  getGroupedRowModel: getGroupedRowModel(),
})
```

## Built-in Aggregation Functions

```typescript
// Available functions:
'sum'          // Sum of values
'count'        // Count of rows
'min'          // Minimum value
'max'          // Maximum value
'extent'       // [min, max]
'mean'         // Average value
'median'       // Median value
'unique'       // Unique values array
'uniqueCount'  // Count of unique values
```

## Column Aggregation

```typescript
columnHelper.accessor('Quantity', {
  header: 'Quantity',
  aggregationFn: 'sum', // ← Aggregate grouped rows
  cell: ({ getValue, row }) =>
    row.getIsGrouped()
      ? `Total: ${getValue()}`
      : getValue(),
  footer: ({ table }) =>
    table.getFilteredRowModel().rows.reduce(
      (sum, row) => sum + row.getValue('Quantity'),
      0
    ),
})
```

## Custom Aggregation Function

```typescript
const customAverage = (columnId, leafRows, childRows) => {
  const sum = childRows.reduce(
    (total, row) => total + row.getValue(columnId),
    0
  )
  return sum / childRows.length
}

const table = useReactTable({
  data,
  columns,
  aggregationFns: {
    customAverage, // ← Register custom function
  },
  getCoreRowModel: getCoreRowModel(),
  getGroupedRowModel: getGroupedRowModel(),
})

// Use in column
columnHelper.accessor('Quantity', {
  aggregationFn: 'customAverage',
})
```

## Rendering Grouped Rows

```typescript
<tbody>
  {table.getRowModel().rows.map(row => (
    <tr key={row.id}>
      {row.getVisibleCells().map(cell => (
        <td key={cell.id}>
          {cell.getIsGrouped() ? (
            // Grouped cell with expand/collapse
            <>
              <button onClick={row.getToggleExpandedHandler()}>
                {row.getIsExpanded() ? '−' : '+'}{' '}
              </button>
              {flexRender(cell.column.columnDef.cell, cell.getContext())}{' '}
              ({row.subRows.length})
            </>
          ) : cell.getIsAggregated() ? (
            // Aggregated cell
            flexRender(
              cell.column.columnDef.aggregatedCell ??
                cell.column.columnDef.cell,
              cell.getContext()
            )
          ) : cell.getIsPlaceholder() ? null : (
            // Normal cell
            flexRender(cell.column.columnDef.cell, cell.getContext())
          )}
        </td>
      ))}
    </tr>
  ))}
</tbody>
```

## Complete Grouping Example

```typescript
function GroupedTable({ data }: { data: Package[] }) {
  const [grouping, setGrouping] = useState<GroupingState>(['ItemCategory'])
  const [expanded, setExpanded] = useState<ExpandedState>(true) // Start expanded

  const columns = useMemo(() => [
    columnHelper.accessor('ItemCategory', {
      header: 'Category',
      cell: ({ getValue }) => getValue(),
    }),
    columnHelper.accessor('ProductName', {
      header: 'Product',
    }),
    columnHelper.accessor('Quantity', {
      header: 'Quantity',
      aggregationFn: 'sum',
      cell: ({ getValue, row }) =>
        row.getIsGrouped() ? (
          <strong>Total: {getValue()}</strong>
        ) : (
          getValue()
        ),
    }),
    columnHelper.accessor('Label', {
      header: 'Package Tag',
      aggregationFn: 'count',
      cell: ({ getValue, row }) =>
        row.getIsGrouped() ? `${getValue()} packages` : getValue(),
    }),
  ], [])

  const table = useReactTable({
    data,
    columns,
    state: { grouping, expanded },
    onGroupingChange: setGrouping,
    onExpandedChange: setExpanded,
    groupedColumnMode: 'reorder',
    getCoreRowModel: getCoreRowModel(),
    getGroupedRowModel: getGroupedRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
  })

  return (
    <div>
      {/* Group controls */}
      <div className="mb-4">
        <label>
          <input
            type="checkbox"
            checked={grouping.includes('ItemCategory')}
            onChange={e =>
              setGrouping(
                e.target.checked ? ['ItemCategory'] : []
              )
            }
          />
          Group by Category
        </label>
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
              className={row.getIsGrouped() ? 'font-bold bg-gray-100' : ''}
            >
              {row.getVisibleCells().map(cell => (
                <td key={cell.id} className="border px-4 py-2">
                  {cell.getIsGrouped() ? (
                    <>
                      <button
                        onClick={row.getToggleExpandedHandler()}
                        className="mr-2"
                      >
                        {row.getIsExpanded() ? '−' : '+'}{' '}
                      </button>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}{' '}
                      ({row.subRows.length})
                    </>
                  ) : cell.getIsAggregated() ? (
                    flexRender(
                      cell.column.columnDef.cell,
                      cell.getContext()
                    )
                  ) : cell.getIsPlaceholder() ? null : (
                    flexRender(cell.column.columnDef.cell, cell.getContext())
                  )}
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

## API Methods

### Column Methods
```typescript
column.getCanGroup()         // boolean
column.getIsGrouped()        // boolean
column.getGroupedIndex()     // number
column.getToggleGroupingHandler() // For onChange
```

### Cell Methods
```typescript
cell.getIsGrouped()          // boolean
cell.getIsAggregated()       // boolean
cell.getIsPlaceholder()      // boolean
```

### Table Methods
```typescript
table.setGrouping(['columnId'])
table.resetGrouping()
table.getState().grouping
table.getPreGroupedRowModel().rows
```

## Type Definitions

```typescript
type GroupingState = string[]

type AggregationFn<TData> = (
  columnId: string,
  leafRows: Row<TData>[],
  childRows: Row<TData>[]
) => any
```

## Next Steps
- **Custom Aggregations** → Implement business-specific calculations
- **Multi-Level Grouping** → Group by multiple columns
- **Combine with Filtering** → Filter within groups
