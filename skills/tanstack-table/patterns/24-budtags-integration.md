# Pattern 24: BudTags Integration Examples

## BudTags DataTable Component

**File:** `resources/js/Components/DataTable.tsx`

```typescript
import { flexRender, Table } from '@tanstack/react-table'
import BoxMain from './BoxMain'

interface DataTableProps<TData> {
  table: Table<TData>
  isLoading?: boolean
}

export function DataTable<TData>({ table, isLoading = false }: DataTableProps<TData>) {
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
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
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
            {isLoading ? (
              <tr>
                <td colSpan={table.getAllColumns().length} className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto" />
                </td>
              </tr>
            ) : table.getRowModel().rows.length > 0 ? (
              table.getRowModel().rows.map(row => (
                <tr key={row.id} className="hover:bg-gray-50">
                  {row.getVisibleCells().map(cell => (
                    <td key={cell.id} className="px-6 py-4 whitespace-nowrap">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={table.getAllColumns().length} className="text-center py-8 text-gray-500">
                  No data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </BoxMain>
  )
}
```

## TableHelpers Utilities

**File:** `resources/js/Components/TableHelpers.tsx`

```typescript
import { ColumnDef, Row } from '@tanstack/react-table'
import { Package } from '@/Types/types-metrc'

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

export function createFilterButtonCell<TData, TValue>(filterKey: string) {
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

export function createDateSortingFn<TData>() {
  return (rowA: Row<TData>, rowB: Row<TData>, columnId: string) => {
    const dateA = new Date(rowA.getValue(columnId) as string)
    const dateB = new Date(rowB.getValue(columnId) as string)
    return dateA.getTime() - dateB.getTime()
  }
}

export function filterByActiveState<T extends { FinishedDate?: string; ArchivedDate?: string }>(
  items: T[],
  showActive: boolean
): T[] {
  return items.filter(item => {
    const isFinished = !!item.FinishedDate || !!item.ArchivedDate
    return showActive ? !isFinished : isFinished
  })
}

export function getDaysUntilExpiration(expirationDate: string): number {
  const today = new Date()
  const expiration = new Date(expirationDate)
  const diffTime = expiration.getTime() - today.getTime()
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

export function getDaysFromHarvest(harvestDate: string): number {
  const today = new Date()
  const harvest = new Date(harvestDate)
  const diffTime = today.getTime() - harvest.getTime()
  return Math.floor(diffTime / (1000 * 60 * 60 * 24))
}
```

## Packages Table Example

**File:** `resources/js/Pages/Metrc/Packages/Index.tsx`

```typescript
import { useMemo, useState } from 'react'
import { router } from '@inertiajs/react'
import { createColumnHelper, useReactTable, getCoreRowModel, getSortedRowModel, getFilteredRowModel, getPaginationRowModel } from '@tanstack/react-table'
import { Package } from '@/Types/types-metrc'
import { DataTable } from '@/Components/DataTable'
import { createCheckboxColumn, createFilterButtonCell, filterByActiveState } from '@/Components/TableHelpers'
import { useUrlToggle } from '@/hooks/useUrlToggle'

const columnHelper = createColumnHelper<Package>()

export default function Packages({ packages }: { packages: Package[] }) {
  const [showActive, setShowActive] = useUrlToggle('active', true)
  const [rowSelection, setRowSelection] = useState({})
  const [globalFilter, setGlobalFilter] = useState('')

  const filteredData = useMemo(
    () => filterByActiveState(packages, showActive),
    [packages, showActive]
  )

  const columns = useMemo(() => [
    createCheckboxColumn<Package>(),
    columnHelper.accessor('Label', {
      header: 'Package Tag',
      ...createFilterButtonCell('Label'),
    }),
    columnHelper.accessor('ProductName', {
      header: 'Product',
      ...createFilterButtonCell('ProductName'),
    }),
    columnHelper.accessor(row => `${row.Quantity} ${row.UnitOfMeasureName}`, {
      id: 'quantity',
      header: 'Quantity',
    }),
    columnHelper.accessor('ItemCategory', {
      header: 'Category',
      filterFn: 'arrIncludes',
    }),
    columnHelper.accessor('ReceivedDateTime', {
      header: 'Received',
      cell: info => new Date(info.getValue()).toLocaleDateString(),
      sortingFn: createDateSortingFn(),
    }),
    columnHelper.display({
      id: 'actions',
      cell: ({ row }) => (
        <button
          onClick={() => router.visit(`/packages/${row.original.Id}`)}
          className="text-blue-600 hover:underline"
        >
          View
        </button>
      ),
    }),
  ], [])

  const table = useReactTable({
    data: filteredData,
    columns,
    state: { rowSelection, globalFilter },
    onRowSelectionChange: setRowSelection,
    onGlobalFilterChange: setGlobalFilter,
    enableRowSelection: true,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: { pageSize: 25 },
      sorting: [{ id: 'ReceivedDateTime', desc: true }],
    },
  })

  const selectedPackages = table.getSelectedRowModel().rows.map(r => r.original)

  return (
    <div>
      <div className="mb-4 flex gap-4">
        {/* Toggle active/finished */}
        <button
          onClick={() => setShowActive(!showActive)}
          className={`px-4 py-2 rounded ${
            showActive ? 'bg-green-500 text-white' : 'bg-gray-200'
          }`}
        >
          {showActive ? 'Active' : 'Finished'}
        </button>

        {/* Global search */}
        <input
          value={globalFilter ?? ''}
          onChange={e => setGlobalFilter(e.target.value)}
          placeholder="Search all columns..."
          className="border rounded px-4 py-2 flex-1"
        />

        {/* Selected count */}
        {selectedPackages.length > 0 && (
          <span className="flex items-center">
            {selectedPackages.length} selected
          </span>
        )}
      </div>

      <DataTable table={table} />

      {/* Pagination */}
      <div className="mt-4 flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Showing {table.getState().pagination.pageIndex * 25 + 1} to{' '}
          {Math.min(
            (table.getState().pagination.pageIndex + 1) * 25,
            table.getRowCount()
          )}{' '}
          of {table.getRowCount()} results
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="px-4 py-2 border rounded disabled:opacity-50"
          >
            Previous
          </button>
          <button
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="px-4 py-2 border rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  )
}
```

## useUrlToggle Hook

**File:** `resources/js/hooks/useUrlToggle.ts`

```typescript
import { useState, useEffect } from 'react'
import { router } from '@inertiajs/react'

export function useUrlToggle(key: string, defaultValue: boolean = false) {
  const [value, setValue] = useState(() => {
    const params = new URLSearchParams(window.location.search)
    return params.get(key) === 'true' ? true : params.get(key) === 'false' ? false : defaultValue
  })

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    params.set(key, String(value))
    router.visit(`${window.location.pathname}?${params.toString()}`, {
      preserveScroll: true,
      preserveState: true,
      replace: true,
    })
  }, [key, value])

  return [value, setValue] as const
}
```

## Integration with Inertia.js

### Fetching Data

```typescript
// Laravel Controller
public function index(Request $request)
{
    $packages = Package::where('organization_id', $request->user()->active_org->id)
        ->with(['product', 'location'])
        ->get();

    return Inertia::render('Metrc/Packages/Index', [
        'packages' => $packages,
    ]);
}
```

### Type Definitions

**File:** `resources/js/Types/types-metrc.tsx`

```typescript
export type Package = {
  Id: number
  Label: string
  ProductName: string
  ProductId: number
  Quantity: number
  UnitOfMeasureName: string
  ItemCategory: string
  ReceivedDateTime: string
  FinishedDate?: string
  ArchivedDate?: string
  LocationId?: number
  LocationName?: string
}

export type Plant = {
  Id: number
  Label: string
  PlantBatchName: string
  StrainName: string
  PlantedDate: string
  VegetativeDate?: string
  FloweringDate?: string
  HarvestedDate?: string
  DestroyedDate?: string
  LocationName?: string
}

export type Harvest = {
  Id: number
  Name: string
  HarvestType: string
  DryingLocationName: string
  HarvestStartDate: string
  FinishedDate?: string
  ArchivedDate?: string
  TotalWasteWeight: number
  TotalWetWeight: number
  TotalRestoredWeight: number
  UnitOfWeightName: string
}
```

## Common BudTags Patterns

### Active/Finished Toggle

```typescript
const [showActive, setShowActive] = useUrlToggle('active', true)
const filteredData = useMemo(
  () => filterByActiveState(data, showActive),
  [data, showActive]
)
```

### Clickable Filter Cells

```typescript
columnHelper.accessor('ProductName', {
  header: 'Product',
  ...createFilterButtonCell('ProductName'),
})
```

### Organization Scoping

All tables automatically filtered by organization in Laravel:

```php
$packages = Package::where('organization_id', auth()->user()->active_org->id)->get();
```

### Date Formatting

```typescript
columnHelper.accessor('ReceivedDateTime', {
  header: 'Received',
  cell: info => new Date(info.getValue()).toLocaleDateString(),
  sortingFn: createDateSortingFn(),
})
```

## Next Steps
- **Create New Tables** → Follow BudTags patterns
- **Reuse Components** → Use DataTable, TableHelpers
- **Type Safety** → Import from types-metrc.tsx
- **Organization Scoping** → Always filter by active_org
