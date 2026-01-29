# Pattern 03: Column Definitions

## Column Types

TanStack Table supports three types of columns:

1. **Accessor Columns** - Have data model (can sort, filter, group)
2. **Display Columns** - No data model (buttons, checkboxes, actions)
3. **Group Columns** - Organize other columns visually

## Column Helper (Recommended)

Use `createColumnHelper` for type-safe column definitions:

```typescript
import { createColumnHelper } from '@tanstack/react-table'

type Package = {
  Tag: string
  ProductName: string
  Quantity: number
}

const columnHelper = createColumnHelper<Package>()
```

### Benefits of Column Helper

- ✅ Full TypeScript type inference
- ✅ Autocomplete for accessor keys
- ✅ Type-safe cell/header functions
- ✅ Prevents typos in column IDs

## Accessor Columns

Accessor columns extract data from your row objects.

### By Object Key

```typescript
columnHelper.accessor('Tag', {
  header: 'Package Tag',
  cell: info => info.getValue(), // Type: string
})
```

### By Array Index

For tuple data:

```typescript
type Order = [Date, number, string] // [date, amount, status]

columnHelper.accessor(1, {
  header: 'Amount',
  cell: info => `$${info.getValue()}`, // Type: number
})
```

### By Accessor Function

Compute derived values:

```typescript
columnHelper.accessor(
  row => `${row.Quantity} ${row.UnitOfMeasureName}`,
  {
    id: 'quantityWithUnit',
    header: 'Quantity',
  }
)
```

**Important:** When using accessor function, you must provide an `id`!

## Display Columns

Display columns have no data model - used for buttons, checkboxes, etc.

### Basic Display Column

```typescript
columnHelper.display({
  id: 'actions',
  header: 'Actions',
  cell: props => (
    <button onClick={() => handleEdit(props.row.original)}>
      Edit
    </button>
  ),
})
```

### Checkbox Selection Column

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
      onChange={row.getToggleSelectedHandler()}
    />
  ),
})
```

## Group Columns

Group columns organize other columns visually:

```typescript
columnHelper.group({
  id: 'name',
  header: 'Full Name',
  columns: [
    columnHelper.accessor('firstName', {
      header: 'First',
    }),
    columnHelper.accessor('lastName', {
      header: 'Last',
    }),
  ],
})
```

## Column Definition Properties

### Common Properties

```typescript
columnHelper.accessor('Tag', {
  // Identification
  id: 'tag',               // Optional if using accessorKey

  // Display
  header: 'Package Tag',   // String or function
  footer: 'Total',         // String or function
  cell: info => info.getValue(), // Cell renderer

  // Features
  enableSorting: true,     // Enable sorting
  enableFiltering: true,   // Enable filtering
  enableGrouping: false,   // Enable grouping
  enableHiding: true,      // Can be hidden

  // Sizing
  size: 150,               // Default width
  minSize: 50,             // Minimum width
  maxSize: 500,            // Maximum width

  // Sorting
  sortingFn: 'alphanumeric', // Sort function

  // Filtering
  filterFn: 'includesString', // Filter function

  // Aggregation
  aggregationFn: 'sum',    // Aggregation function
})
```

## Cell Rendering

### Simple Value

```typescript
cell: info => info.getValue()
```

### Custom Formatting

```typescript
cell: info => {
  const value = info.getValue()
  return `$${value.toFixed(2)}`
}
```

### With Row Data

```typescript
cell: info => {
  const quantity = info.getValue()
  const unit = info.row.original.UnitOfMeasureName
  return `${quantity} ${unit}`
}
```

### With Component

```typescript
cell: info => <Badge>{info.getValue()}</Badge>
```

## Header Rendering

### String Header

```typescript
header: 'Product Name'
```

### Function Header

```typescript
header: () => <span className="font-bold">Product</span>
```

### With Context

```typescript
header: ({ column }) => (
  <button onClick={column.getToggleSortingHandler()}>
    Product Name
    {{
      asc: ' 🔼',
      desc: ' 🔽',
    }[column.getIsSorted() as string] ?? null}
  </button>
)
```

## Footer Rendering

```typescript
footer: props => {
  const total = props.table.getFilteredRowModel().rows
    .reduce((sum, row) => sum + row.getValue('quantity'), 0)
  return `Total: ${total}`
}
```

## BudTags Patterns

### Pattern 1: Checkbox Column (from TableHelpers.tsx)

```typescript
export function createCheckboxColumn<TData>(): ColumnDef<TData> {
  return {
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
        disabled={!row.getCanSelect()}
        onChange={row.getToggleSelectedHandler()}
      />
    ),
  }
}
```

### Pattern 2: Filter Button Cell (from TableHelpers.tsx)

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
```

### Pattern 3: Date Column with Sorting (from TableHelpers.tsx)

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

## Column Definition Examples

### Metrc Package Columns

```typescript
const columns = [
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

  columnHelper.accessor('Label', {
    header: 'Package Tag',
    cell: info => (
      <button
        onClick={() => viewPackage(info.row.original)}
        className="text-blue-600 hover:underline"
      >
        {info.getValue()}
      </button>
    ),
  }),

  columnHelper.accessor('ProductName', {
    header: 'Product',
    enableSorting: true,
    enableFiltering: true,
  }),

  columnHelper.accessor(
    row => `${row.Quantity} ${row.UnitOfMeasureName}`,
    {
      id: 'quantity',
      header: 'Quantity',
      enableSorting: false,
    }
  ),

  columnHelper.accessor('FinishedDate', {
    header: 'Finished',
    cell: info => {
      const date = info.getValue()
      return date ? new Date(date).toLocaleDateString() : 'Active'
    },
    sortingFn: 'datetime',
  }),
]
```

## Advanced: Memoization

Always memoize column definitions to prevent recreation on every render:

```typescript
const columns = useMemo(
  () => [
    columnHelper.accessor('Tag', { header: 'Tag' }),
    columnHelper.accessor('ProductName', { header: 'Product' }),
  ],
  []
)
```

## Common Mistakes

### ❌ Missing ID with Accessor Function

```typescript
// ❌ Error: Missing required 'id' property
columnHelper.accessor(row => row.firstName + row.lastName, {
  header: 'Full Name',
})

// ✅ Correct
columnHelper.accessor(row => row.firstName + row.lastName, {
  id: 'fullName',
  header: 'Full Name',
})
```

### ❌ Not Memoizing Columns

```typescript
// ❌ Recreates columns every render
function MyTable() {
  const columns = [columnHelper.accessor('name')]
  // ...
}

// ✅ Memoized
function MyTable() {
  const columns = useMemo(() => [
    columnHelper.accessor('name')
  ], [])
  // ...
}
```

### ❌ Using Accessor Function for Sorting

```typescript
// ❌ Can't sort - returns string, not primitive
columnHelper.accessor(
  row => `${row.Quantity} ${row.Unit}`,
  { enableSorting: true } // Won't work properly
)

// ✅ Use separate accessor for data
columnHelper.accessor('Quantity', {
  header: 'Quantity',
  cell: info => `${info.getValue()} ${info.row.original.Unit}`,
  enableSorting: true, // ✅ Works - sorts by Quantity number
})
```

## Type Definitions

```typescript
type ColumnDef<TData, TValue = any> =
  | DisplayColumnDef<TData, TValue>
  | GroupColumnDef<TData, TValue>
  | AccessorColumnDef<TData, TValue>

type AccessorColumnDef<TData, TValue> = {
  id?: string
  accessorKey?: keyof TData
  accessorFn?: (row: TData) => TValue
  header?: string | ((props: HeaderContext<TData, TValue>) => any)
  cell?: (props: CellContext<TData, TValue>) => any
  footer?: (props: HeaderContext<TData, TValue>) => any
  enableSorting?: boolean
  enableFiltering?: boolean
  enableGrouping?: boolean
  // ... many more
}
```

## Next Steps

- **Table Instance** → See pattern 04
- **Custom Cell Rendering** → See pattern 06
- **Sorting Setup** → See pattern 07
- **Filtering Setup** → See pattern 08
