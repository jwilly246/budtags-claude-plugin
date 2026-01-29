# Pattern 20: TypeScript Best Practices

## Type-Safe Column Definitions

### Using Column Helper (Recommended)

```typescript
import { createColumnHelper } from '@tanstack/react-table'

type Package = {
  Id: number
  Label: string
  ProductName: string
  Quantity: number
  ItemCategory: string
  ReceivedDateTime: string
}

const columnHelper = createColumnHelper<Package>()

// ✅ Full type inference
const columns = [
  columnHelper.accessor('Label', {
    header: 'Package Tag',
    cell: info => info.getValue(), // Type: string
  }),
  columnHelper.accessor('Quantity', {
    header: 'Quantity',
    cell: info => info.getValue(), // Type: number
  }),
  columnHelper.accessor(
    row => `${row.Quantity} units`, // Type: string
    {
      id: 'quantityWithUnit',
      header: 'Quantity',
    }
  ),
]
```

### Without Column Helper

```typescript
import { ColumnDef } from '@tanstack/react-table'

const columns: ColumnDef<Package>[] = [
  {
    accessorKey: 'Label',
    header: 'Package Tag',
    cell: info => info.getValue() as string,
  },
  {
    id: 'quantity',
    accessorFn: row => row.Quantity,
    header: 'Quantity',
  },
]
```

## Typing Table Instance

```typescript
import { Table } from '@tanstack/react-table'

function MyComponent({ table }: { table: Table<Package> }) {
  const rows = table.getRowModel().rows // Row<Package>[]
  const firstRow = rows[0]
  const packageData = firstRow.original // Package
}
```

## Typing State

```typescript
import {
  SortingState,
  ColumnFiltersState,
  VisibilityState,
  PaginationState,
  RowSelectionState,
} from '@tanstack/react-table'

const [sorting, setSorting] = useState<SortingState>([])
const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})
const [rowSelection, setRowSelection] = useState<RowSelectionState>({})
const [pagination, setPagination] = useState<PaginationState>({
  pageIndex: 0,
  pageSize: 10,
})
```

## Typing Column Definitions

```typescript
import { ColumnDef, AccessorFn } from '@tanstack/react-table'

// Accessor column
const accessor: ColumnDef<Package> = {
  accessorKey: 'Label',
  header: 'Package Tag',
}

// Display column
const display: ColumnDef<Package> = {
  id: 'actions',
  cell: ({ row }) => <button onClick={() => handleEdit(row.original)}>Edit</button>,
}

// Group column
const group: ColumnDef<Package> = {
  id: 'info',
  header: 'Package Info',
  columns: [
    { accessorKey: 'Label', header: 'Tag' },
    { accessorKey: 'ProductName', header: 'Product' },
  ],
}
```

## Typing Cell Context

```typescript
import { CellContext } from '@tanstack/react-table'

columnHelper.accessor('Label', {
  cell: (props: CellContext<Package, string>) => {
    const value = props.getValue() // string
    const row = props.row.original // Package
    return <span>{value}</span>
  },
})
```

## Typing Header Context

```typescript
import { HeaderContext } from '@tanstack/react-table'

columnHelper.accessor('Label', {
  header: (props: HeaderContext<Package, string>) => {
    const column = props.column
    return (
      <button onClick={column.getToggleSortingHandler()}>
        Package Tag
      </button>
    )
  },
})
```

## Generic DataTable Component

```typescript
interface DataTableProps<TData> {
  data: TData[]
  columns: ColumnDef<TData, any>[]
  enableSorting?: boolean
  enableFiltering?: boolean
}

function DataTable<TData>({
  data,
  columns,
  enableSorting = true,
  enableFiltering = false,
}: DataTableProps<TData>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: enableSorting ? getSortedRowModel() : undefined,
    getFilteredRowModel: enableFiltering ? getFilteredRowModel() : undefined,
  })

  return <table>{/* ... */}</table>
}

// Usage with full type safety
<DataTable<Package>
  data={packages}
  columns={packageColumns}
  enableSorting
/>
```

## Typing Custom Filter Functions

```typescript
import { FilterFn } from '@tanstack/react-table'

const fuzzyFilter: FilterFn<Package> = (row, columnId, filterValue) => {
  const value = row.getValue(columnId) as string
  return value.toLowerCase().includes(filterValue.toLowerCase())
}

fuzzyFilter.autoRemove = (val: any) => !val
```

## Typing Custom Sorting Functions

```typescript
import { SortingFn } from '@tanstack/react-table'

const dateSortingFn: SortingFn<Package> = (rowA, rowB, columnId) => {
  const dateA = new Date(rowA.getValue(columnId) as string)
  const dateB = new Date(rowB.getValue(columnId) as string)
  return dateA.getTime() - dateB.getTime()
}
```

## Typing Custom Aggregation Functions

```typescript
import { AggregationFn } from '@tanstack/react-table'

const sumAggregation: AggregationFn<Package> = (
  columnId,
  leafRows,
  childRows
) => {
  return childRows.reduce(
    (sum, row) => sum + (row.getValue(columnId) as number),
    0
  )
}
```

## Type Utility Helpers

```typescript
// Extract row type from table
type RowType<T> = T extends Table<infer R> ? R : never

// Extract cell value type
type CellValue<T, K extends keyof T> = T[K]

// Usage
const table = useReactTable<Package>({...})
type MyRow = RowType<typeof table> // Package
```

## Common Type Errors and Fixes

### ❌ Missing Generic Type

```typescript
// ❌ No type safety
const columns = [
  columnHelper.accessor('Label', ...)
]

// ✅ Type-safe
const columnHelper = createColumnHelper<Package>()
const columns = [
  columnHelper.accessor('Label', ...) // Knows 'Label' exists on Package
]
```

### ❌ Incorrect Cell Value Type

```typescript
// ❌ Type error
columnHelper.accessor('Quantity', {
  cell: info => info.getValue().toUpperCase() // Error: number has no toUpperCase
})

// ✅ Correct type handling
columnHelper.accessor('Quantity', {
  cell: info => info.getValue().toString() // number → string
})
```

### ❌ Missing Column ID for Accessor Functions

```typescript
// ❌ Type error - missing id
columnHelper.accessor(
  row => `${row.Quantity} units`,
  {
    header: 'Quantity',
    // Missing id!
  }
)

// ✅ Include id
columnHelper.accessor(
  row => `${row.Quantity} units`,
  {
    id: 'quantityWithUnit',
    header: 'Quantity',
  }
)
```

## Type Definitions Reference

```typescript
import type {
  Table,
  Column,
  Row,
  Cell,
  Header,
  ColumnDef,
  AccessorColumnDef,
  DisplayColumnDef,
  GroupColumnDef,
  IdentifiedColumnDef,
  SortingState,
  ColumnFiltersState,
  VisibilityState,
  ColumnOrderState,
  ColumnPinningState,
  ColumnSizingState,
  ExpandedState,
  GroupingState,
  PaginationState,
  RowSelectionState,
  CellContext,
  HeaderContext,
  FilterFn,
  SortingFn,
  AggregationFn,
} from '@tanstack/react-table'
```

## BudTags Type Patterns

```typescript
// Shared types for Metrc data
import { Package } from '@/Types/types-metrc'

// Column helper for Package tables
const packageColumnHelper = createColumnHelper<Package>()

// Reusable column definitions
const standardPackageColumns = [
  packageColumnHelper.accessor('Label', {
    header: 'Package Tag',
  }),
  packageColumnHelper.accessor('ProductName', {
    header: 'Product',
  }),
  packageColumnHelper.accessor('Quantity', {
    header: 'Quantity',
  }),
]

// Type-safe table props
interface PackageTableProps {
  packages: Package[]
  onSelect?: (packages: Package[]) => void
  enableSelection?: boolean
}
```

## Type Safety Checklist

- ✅ Use `createColumnHelper<YourType>()`
- ✅ Define explicit types for state variables
- ✅ Type component props with generics
- ✅ Use `ColumnDef<YourType>[]` for column arrays
- ✅ Import types from `@tanstack/react-table`
- ✅ Provide `id` for accessor functions
- ✅ Type custom filter/sort/aggregation functions
- ✅ Use type guards for cell value transformations

## Next Steps
- **Generic Components** → Create reusable typed tables
- **Type Utilities** → Build helper types for your domain
- **Strict Mode** → Enable TypeScript strict mode
