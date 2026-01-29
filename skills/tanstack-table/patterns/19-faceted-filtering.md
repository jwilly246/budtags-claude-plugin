# Pattern 19: Faceted Filtering

## What is Faceted Filtering?

Faceted filtering provides metadata about unique values in filtered columns, enabling dynamic filter UIs like checkboxes, range sliders, and counts.

## Enabling Faceted Filtering

```typescript
import {
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFacetedMinMaxValues,
} from '@tanstack/react-table'

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getFacetedRowModel: getFacetedRowModel(),           // ← Enable facets
  getFacetedUniqueValues: getFacetedUniqueValues(),   // ← Unique values + counts
  getFacetedMinMaxValues: getFacetedMinMaxValues(),   // ← Min/max for ranges
})
```

## Get Unique Values with Counts

```typescript
// Get unique values for a column with their counts
const uniqueValues = column.getFacetedUniqueValues()

// Example result:
// Map {
//   'Flower' => 45,
//   'Edible' => 23,
//   'Concentrate' => 12
// }

// Convert to array
const options = Array.from(uniqueValues.keys())
// ['Flower', 'Edible', 'Concentrate']

const optionsWithCounts = Array.from(uniqueValues.entries())
// [['Flower', 45], ['Edible', 23], ['Concentrate', 12]]
```

## Checkbox Filter with Counts

```typescript
function CheckboxFilter({ column }: { column: Column<any> }) {
  const uniqueValues = column.getFacetedUniqueValues()
  const sortedValues = Array.from(uniqueValues.keys()).sort()

  return (
    <div className="space-y-2">
      {sortedValues.map(value => {
        const count = uniqueValues.get(value) ?? 0
        const isChecked = (column.getFilterValue() as string[])?.includes(
          value
        )

        return (
          <label key={value} className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={isChecked}
              onChange={e => {
                const currentFilter = (column.getFilterValue() as string[]) ?? []
                if (e.target.checked) {
                  column.setFilterValue([...currentFilter, value])
                } else {
                  column.setFilterValue(
                    currentFilter.filter(v => v !== value)
                  )
                }
              }}
            />
            <span>
              {value} ({count})
            </span>
          </label>
        )
      })}
    </div>
  )
}

// Use with arrIncludes filter
columnHelper.accessor('ItemCategory', {
  header: 'Category',
  filterFn: 'arrIncludes',
})
```

## Range Slider Filter

```typescript
function RangeFilter({ column }: { column: Column<any> }) {
  const [min, max] = column.getFacetedMinMaxValues() ?? [0, 100]
  const [range, setRange] = useState<[number, number]>([min, max])

  useEffect(() => {
    setRange([min, max])
  }, [min, max])

  return (
    <div>
      <div className="flex justify-between text-sm mb-2">
        <span>{range[0]}</span>
        <span>{range[1]}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={range[0]}
        onChange={e => {
          const value = Number(e.target.value)
          setRange([value, range[1]])
          column.setFilterValue([value, range[1]])
        }}
        className="w-full"
      />
      <input
        type="range"
        min={min}
        max={max}
        value={range[1]}
        onChange={e => {
          const value = Number(e.target.value)
          setRange([range[0], value])
          column.setFilterValue([range[0], value])
        }}
        className="w-full"
      />
    </div>
  )
}

// Use with inNumberRange filter
columnHelper.accessor('Quantity', {
  header: 'Quantity',
  filterFn: 'inNumberRange',
})
```

## Complete Faceted Filtering Example

```typescript
function FacetedTable({ data }: { data: Package[] }) {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])

  const columns = useMemo(() => [
    columnHelper.accessor('Label', { header: 'Package Tag' }),
    columnHelper.accessor('ProductName', {
      header: 'Product',
      filterFn: 'includesString',
    }),
    columnHelper.accessor('ItemCategory', {
      header: 'Category',
      filterFn: 'arrIncludes',
    }),
    columnHelper.accessor('Quantity', {
      header: 'Quantity',
      filterFn: 'inNumberRange',
    }),
  ], [])

  const table = useReactTable({
    data,
    columns,
    state: { columnFilters },
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getFacetedMinMaxValues: getFacetedMinMaxValues(),
  })

  const categoryColumn = table.getColumn('ItemCategory')
  const quantityColumn = table.getColumn('Quantity')

  return (
    <div className="flex gap-4">
      {/* Filters sidebar */}
      <div className="w-64 border-r pr-4">
        <h3 className="font-bold mb-4">Filters</h3>

        {/* Category checkboxes */}
        {categoryColumn && (
          <div className="mb-6">
            <div className="font-semibold mb-2">Category</div>
            <CheckboxFilter column={categoryColumn} />
          </div>
        )}

        {/* Quantity range */}
        {quantityColumn && (
          <div className="mb-6">
            <div className="font-semibold mb-2">Quantity</div>
            <RangeFilter column={quantityColumn} />
          </div>
        )}

        {/* Clear filters */}
        <button
          onClick={() => table.resetColumnFilters()}
          className="text-blue-600 text-sm"
        >
          Clear All Filters
        </button>
      </div>

      {/* Table */}
      <div className="flex-1">
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
        </table>

        <div className="mt-4 text-sm text-gray-600">
          Showing {table.getRowModel().rows.length} of{' '}
          {table.getPreFilteredRowModel().rows.length} results
        </div>
      </div>
    </div>
  )
}
```

## Faceted Global Filtering

```typescript
const [globalFilter, setGlobalFilter] = useState('')

const table = useReactTable({
  data,
  columns,
  state: { globalFilter },
  onGlobalFilterChange: setGlobalFilter,
  globalFilterFn: 'includesString',
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getFacetedRowModel: getFacetedRowModel(),       // Global facets
  getFacetedUniqueValues: getFacetedUniqueValues(),
})

// Get faceted values for global filter
const globalFacets = table.getColumn('_global')?.getFacetedUniqueValues()
```

## API Methods

### Column Methods
```typescript
column.getFacetedRowModel()      // Faceted rows
column.getFacetedUniqueValues()  // Map<value, count>
column.getFacetedMinMaxValues()  // [min, max] | undefined
```

### Table Methods
```typescript
table.getFacetedRowModel()
table.getFacetedUniqueValues()
table.getFacetedMinMaxValues()
```

## Performance Considerations

Faceted filtering computes unique values for ALL rows (not just visible page), which can be expensive for large datasets.

**Optimize by:**
1. Only enable for specific columns
2. Use server-side faceting for large datasets
3. Memoize facet calculations

## Type Definitions

```typescript
type FacetedRowModel<TData> = () => RowModel<TData>
type FacetedUniqueValues = () => Map<any, number>
type FacetedMinMaxValues = () => [number, number] | undefined
```

## Next Steps
- **Dynamic Filter UI** → Build filter panels from facets
- **Server-Side Faceting** → Handle facets on backend
- **Multi-Select Filters** → Combine with checkbox filters
