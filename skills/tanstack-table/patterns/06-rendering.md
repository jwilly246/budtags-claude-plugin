# Pattern 06: Rendering

## flexRender Utility

Use `flexRender` to render dynamic content (strings, functions, or components):

```typescript
import { flexRender } from '@tanstack/react-table'

// ✅ Handles all types correctly
{flexRender(cell.column.columnDef.cell, cell.getContext())}

// ❌ Won't work if cell is a function
{cell.column.columnDef.cell}
```

## Basic Table Rendering

### Complete Example

```typescript
function DataTable({ data, columns }: DataTableProps) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
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
  )
}
```

## Rendering Headers

### Simple Headers

```typescript
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
```

### Headers with Sorting

```typescript
<th
  key={header.id}
  onClick={header.column.getToggleSortingHandler()}
  className="cursor-pointer"
>
  {flexRender(header.column.columnDef.header, header.getContext())}
  {{
    asc: ' 🔼',
    desc: ' 🔽',
  }[header.column.getIsSorted() as string] ?? null}
</th>
```

### Grouped Headers

For column groups, iterate through header groups:

```typescript
<thead>
  {table.getHeaderGroups().map(headerGroup => (
    <tr key={headerGroup.id}>
      {headerGroup.headers.map(header => (
        <th
          key={header.id}
          colSpan={header.colSpan}
          rowSpan={header.rowSpan}
        >
          {header.isPlaceholder ? null : (
            flexRender(
              header.column.columnDef.header,
              header.getContext()
            )
          )}
        </th>
      ))}
    </tr>
  ))}
</thead>
```

## Rendering Cells

### Basic Cells

```typescript
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
```

### Cells with Conditional Styling

```typescript
<td
  key={cell.id}
  className={
    cell.column.id === 'Quantity' && cell.getValue() < 10
      ? 'text-red-600'
      : ''
  }
>
  {flexRender(cell.column.columnDef.cell, cell.getContext())}
</td>
```

## Rendering Footers

```typescript
<tfoot>
  {table.getFooterGroups().map(footerGroup => (
    <tr key={footerGroup.id}>
      {footerGroup.headers.map(header => (
        <th key={header.id}>
          {header.isPlaceholder ? null : (
            flexRender(
              header.column.columnDef.footer,
              header.getContext()
            )
          )}
        </th>
      ))}
    </tr>
  ))}
</tfoot>
```

## Empty State

Handle empty data gracefully:

```typescript
<tbody>
  {table.getRowModel().rows.length > 0 ? (
    table.getRowModel().rows.map(row => (
      <tr key={row.id}>
        {row.getVisibleCells().map(cell => (
          <td key={cell.id}>
            {flexRender(cell.column.columnDef.cell, cell.getContext())}
          </td>
        ))}
      </tr>
    ))
  ) : (
    <tr>
      <td colSpan={columns.length} className="text-center py-8 text-gray-500">
        No data available
      </td>
    </tr>
  )}
</tbody>
```

## Loading State

Show loading indicator:

```typescript
function DataTable({ data, columns, isLoading }: DataTableProps) {
  const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel() })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
      </div>
    )
  }

  return <table>{/* Normal rendering */}</table>
}
```

## With Tailwind CSS

```typescript
<table className="min-w-full divide-y divide-gray-200">
  <thead className="bg-gray-50">
    {table.getHeaderGroups().map(headerGroup => (
      <tr key={headerGroup.id}>
        {headerGroup.headers.map(header => (
          <th
            key={header.id}
            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            {flexRender(header.column.columnDef.header, header.getContext())}
          </th>
        ))}
      </tr>
    ))}
  </thead>
  <tbody className="bg-white divide-y divide-gray-200">
    {table.getRowModel().rows.map(row => (
      <tr key={row.id} className="hover:bg-gray-50">
        {row.getVisibleCells().map(cell => (
          <td
            key={cell.id}
            className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
          >
            {flexRender(cell.column.columnDef.cell, cell.getContext())}
          </td>
        ))}
      </tr>
    ))}
  </tbody>
</table>
```

## BudTags Pattern: BoxMain Container

**File:** `resources/js/Components/DataTable.tsx`

```typescript
export function DataTable<TData>({ data, columns }: DataTableProps<TData>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <BoxMain>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th
                    key={header.id}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase"
                  >
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {table.getRowModel().rows.map(row => (
              <tr key={row.id} className="hover:bg-gray-50">
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id} className="px-6 py-4 whitespace-nowrap">
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
      </div>
    </BoxMain>
  )
}
```

## Advanced: Custom Row Components

Extract row rendering to separate component:

```typescript
function TableRow({ row }: { row: Row<Package> }) {
  return (
    <tr className="hover:bg-gray-50">
      {row.getVisibleCells().map(cell => (
        <td key={cell.id} className="px-6 py-4">
          {flexRender(cell.column.columnDef.cell, cell.getContext())}
        </td>
      ))}
    </tr>
  )
}

function DataTable({ data, columns }: DataTableProps) {
  const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel() })

  return (
    <table>
      <thead>{/* ... */}</thead>
      <tbody>
        {table.getRowModel().rows.map(row => (
          <TableRow key={row.id} row={row} />
        ))}
      </tbody>
    </table>
  )
}
```

## Context Available in Renderers

### Header Context

```typescript
header: (context) => {
  context.column      // Column instance
  context.header      // Header instance
  context.table       // Table instance
  return <div>{context.column.id}</div>
}
```

### Cell Context

```typescript
cell: (context) => {
  context.getValue()   // Get cell value
  context.row          // Row instance
  context.column       // Column instance
  context.cell         // Cell instance
  context.table        // Table instance
  return <div>{context.getValue()}</div>
}
```

### Footer Context

```typescript
footer: (context) => {
  context.column      // Column instance
  context.header      // Header instance
  context.table       // Table instance
  return <div>Footer</div>
}
```

## Common Mistakes

### ❌ Not Using flexRender

```typescript
// ❌ Won't work if header is a function
<th>{header.column.columnDef.header}</th>

// ✅ Works with functions and components
<th>{flexRender(header.column.columnDef.header, header.getContext())}</th>
```

### ❌ Missing Key Props

```typescript
// ❌ React will warn about missing keys
{table.getRowModel().rows.map(row => (
  <tr>...</tr>
))}

// ✅ Always include key
{table.getRowModel().rows.map(row => (
  <tr key={row.id}>...</tr>
))}
```

### ❌ Using getAllCells Instead of getVisibleCells

```typescript
// ❌ Renders hidden columns
{row.getAllCells().map(cell => ...)}

// ✅ Only renders visible columns
{row.getVisibleCells().map(cell => ...)}
```

## Type Definitions

```typescript
type HeaderContext<TData, TValue> = {
  table: Table<TData>
  header: Header<TData, TValue>
  column: Column<TData, TValue>
}

type CellContext<TData, TValue> = {
  table: Table<TData>
  column: Column<TData, TValue>
  row: Row<TData>
  cell: Cell<TData, TValue>
  getValue: () => TValue
  renderValue: () => TValue
}
```

## Next Steps

- **Add Sorting** → See pattern 07
- **Add Filtering** → See pattern 08
- **Add Pagination** → See pattern 09
- **Style Headers/Cells** → See patterns 07-14
