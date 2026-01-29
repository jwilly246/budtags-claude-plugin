# Pattern 17: Row Pinning

## Enabling Row Pinning

Row pinning splits rows into three sections: top-pinned, center (unpinned), and bottom-pinned.

```typescript
const [rowPinning, setRowPinning] = useState<RowPinningState>({
  top: [],
  bottom: [],
})

const table = useReactTable({
  data,
  columns,
  state: { rowPinning },
  onRowPinningChange: setRowPinning,
  getCoreRowModel: getCoreRowModel(),
})
```

## Row Pinning State

```typescript
type RowPinningState = {
  top?: string[]    // Row IDs pinned to top
  bottom?: string[] // Row IDs pinned to bottom
}

// Example:
const rowPinning = {
  top: ['0', '1'],      // First two rows at top
  bottom: ['99'],       // Last row at bottom
}
```

## Pin/Unpin Rows

```typescript
// Pin row to top
row.pin('top')

// Pin row to bottom
row.pin('bottom')

// Unpin row
row.pin(false)

// Get pin status
row.getIsPinned()  // 'top' | 'bottom' | false

// Check if can pin
row.getCanPin()    // boolean
```

## Rendering Pinned Rows

```typescript
<table>
  <thead>{/* ... */}</thead>

  {/* Top pinned rows */}
  {table.getTopRows().length > 0 && (
    <tbody className="bg-blue-50 border-b-2">
      {table.getTopRows().map(row => (
        <tr key={row.id}>
          {row.getVisibleCells().map(cell => (
            <td key={cell.id} className="px-4 py-2">
              {flexRender(cell.column.columnDef.cell, cell.getContext())}
              <button
                onClick={() => row.pin(false)}
                className="ml-2 text-blue-600"
              >
                Unpin
              </button>
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  )}

  {/* Center (unpinned) rows */}
  <tbody>
    {table.getCenterRows().map(row => (
      <tr key={row.id}>
        {row.getVisibleCells().map(cell => (
          <td key={cell.id} className="px-4 py-2">
            {flexRender(cell.column.columnDef.cell, cell.getContext())}
          </td>
        ))}
      </tr>
    ))}
  </tbody>

  {/* Bottom pinned rows */}
  {table.getBottomRows().length > 0 && (
    <tbody className="bg-blue-50 border-t-2">
      {table.getBottomRows().map(row => (
        <tr key={row.id}>
          {row.getVisibleCells().map(cell => (
            <td key={cell.id} className="px-4 py-2">
              {flexRender(cell.column.columnDef.cell, cell.getContext())}
              <button
                onClick={() => row.pin(false)}
                className="ml-2 text-blue-600"
              >
                Unpin
              </button>
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  )}
</table>
```

## Complete Example

```typescript
function PinnableTable({ data }: { data: Package[] }) {
  const [rowPinning, setRowPinning] = useState<RowPinningState>({
    top: [],
    bottom: [],
  })

  const columns = useMemo(() => [
    columnHelper.display({
      id: 'pin',
      cell: ({ row }) => (
        <div className="flex gap-1">
          <button
            onClick={() => row.pin('top')}
            disabled={row.getIsPinned() === 'top'}
            className="text-xs px-2 py-1 border rounded disabled:opacity-50"
          >
            ⬆
          </button>
          <button
            onClick={() => row.pin(false)}
            disabled={!row.getIsPinned()}
            className="text-xs px-2 py-1 border rounded disabled:opacity-50"
          >
            ○
          </button>
          <button
            onClick={() => row.pin('bottom')}
            disabled={row.getIsPinned() === 'bottom'}
            className="text-xs px-2 py-1 border rounded disabled:opacity-50"
          >
            ⬇
          </button>
        </div>
      ),
    }),
    columnHelper.accessor('Label', { header: 'Package Tag' }),
    columnHelper.accessor('ProductName', { header: 'Product' }),
    columnHelper.accessor('Quantity', { header: 'Quantity' }),
  ], [])

  const table = useReactTable({
    data,
    columns,
    state: { rowPinning },
    onRowPinningChange: setRowPinning,
    getRowId: row => row.Id.toString(),
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div>
      <div className="mb-4 text-sm text-gray-600">
        Pinned: {table.getTopRows().length} top, {table.getBottomRows().length} bottom
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

        {/* Top pinned */}
        {table.getTopRows().length > 0 && (
          <tbody className="bg-blue-50">
            {table.getTopRows().map(row => (
              <tr key={row.id}>
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id} className="border px-4 py-2">
                    {flexRender(
                      cell.column.columnDef.cell,
                      cell.getContext()
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        )}

        {/* Unpinned */}
        <tbody>
          {table.getCenterRows().map(row => (
            <tr key={row.id} className="hover:bg-gray-50">
              {row.getVisibleCells().map(cell => (
                <td key={cell.id} className="border px-4 py-2">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>

        {/* Bottom pinned */}
        {table.getBottomRows().length > 0 && (
          <tbody className="bg-blue-50">
            {table.getBottomRows().map(row => (
              <tr key={row.id}>
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id} className="border px-4 py-2">
                    {flexRender(
                      cell.column.columnDef.cell,
                      cell.getContext()
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        )}
      </table>
    </div>
  )
}
```

## Order of Operations

Row pinning takes precedence before sorting:
1. **Row Pinning** - Split into top/center/bottom
2. **Sorting** - Applied within each section

## API Methods

### Row Methods
```typescript
row.getCanPin()      // boolean
row.getIsPinned()    // 'top' | 'bottom' | false
row.pin(position)    // 'top' | 'bottom' | false
```

### Table Methods
```typescript
table.getTopRows()               // Top pinned rows
table.getCenterRows()            // Unpinned rows
table.getBottomRows()            // Bottom pinned rows

table.setRowPinning({ top: [...], bottom: [...] })
table.resetRowPinning()
table.getState().rowPinning
```

## Type Definitions

```typescript
type RowPinningState = {
  top?: string[]
  bottom?: string[]
}

type RowPinningPosition = 'top' | 'bottom' | false
```

## Common Use Cases

- **Pin totals row** to bottom
- **Pin header row** for sub-tables
- **Pin important rows** for quick access
- **Pin selected rows** for comparison

## Next Steps
- **Combine with Sorting** → Sorting within pinned sections
- **Sticky Positioning** → Make pinned rows sticky during scroll
