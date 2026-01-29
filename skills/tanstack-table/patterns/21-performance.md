# Pattern 21: Performance Optimization

## Memoization Essentials

### Memoize Data

```typescript
// ❌ BAD - Recreates array every render
const table = useReactTable({
  data: packages.filter(p => p.Quantity > 0),
  columns,
  getCoreRowModel: getCoreRowModel(),
})

// ✅ GOOD - Memoized
const filteredPackages = useMemo(
  () => packages.filter(p => p.Quantity > 0),
  [packages]
)

const table = useReactTable({
  data: filteredPackages,
  columns,
  getCoreRowModel: getCoreRowModel(),
})
```

### Memoize Columns

```typescript
// ❌ BAD - Recreates columns every render
const columns = [
  columnHelper.accessor('Label', { header: 'Tag' }),
  columnHelper.accessor('ProductName', { header: 'Product' }),
]

// ✅ GOOD - Memoized
const columns = useMemo(
  () => [
    columnHelper.accessor('Label', { header: 'Tag' }),
    columnHelper.accessor('ProductName', { header: 'Product' }),
  ],
  []
)
```

### Memoize Table Instance Options

```typescript
const tableOptions = useMemo(
  () => ({
    data,
    columns,
    state: { sorting, columnFilters, pagination },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  }),
  [data, columns, sorting, columnFilters, pagination]
)

const table = useReactTable(tableOptions)
```

## React.memo for Components

### Memoize Row Components

```typescript
const TableRow = memo(({ row }: { row: Row<Package> }) => (
  <tr>
    {row.getVisibleCells().map(cell => (
      <td key={cell.id}>
        {flexRender(cell.column.columnDef.cell, cell.getContext())}
      </td>
    ))}
  </tr>
))

// Usage
<tbody>
  {table.getRowModel().rows.map(row => (
    <TableRow key={row.id} row={row} />
  ))}
</tbody>
```

### Memoize Cell Components

```typescript
const TableCell = memo(({ cell }: { cell: Cell<Package, any> }) => (
  <td className="px-4 py-2">
    {flexRender(cell.column.columnDef.cell, cell.getContext())}
  </td>
))
```

## Pagination Over Full Rendering

```typescript
// ✅ GOOD - Only renders 25 rows
const table = useReactTable({
  data,
  columns,
  initialState: { pagination: { pageSize: 25 } },
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
})

// ❌ BAD - Renders all 10,000 rows
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
})
```

## Virtualization for Large Datasets

```typescript
// For datasets > 1,000 rows, use virtualization
import { useVirtualizer } from '@tanstack/react-virtual'

const rowVirtualizer = useVirtualizer({
  count: table.getRowModel().rows.length,
  getScrollElement: () => containerRef.current,
  estimateSize: () => 50,
  overscan: 5,
})

// Only renders ~20 visible rows instead of all rows
```

## Debounce Filter Inputs

```typescript
import { useDebounce } from '@/hooks/useDebounce'

function SearchFilter({ column }: { column: Column<any> }) {
  const [value, setValue] = useState('')
  const debouncedValue = useDebounce(value, 300)

  useEffect(() => {
    column.setFilterValue(debouncedValue)
  }, [debouncedValue, column])

  return (
    <input
      value={value}
      onChange={e => setValue(e.target.value)}
      placeholder="Search..."
    />
  )
}
```

## Conditional Row Models

Only add row models for features you're using:

```typescript
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),

  // ✅ Only add if sorting is enabled
  getSortedRowModel: enableSorting ? getSortedRowModel() : undefined,

  // ✅ Only add if filtering is enabled
  getFilteredRowModel: enableFiltering ? getFilteredRowModel() : undefined,

  // ✅ Only add if pagination is enabled
  getPaginationRowModel: enablePagination
    ? getPaginationRowModel()
    : undefined,
})
```

## Avoid Re-renders During Resize

```typescript
const columnSizeVars = useMemo(() => {
  const headers = table.getFlatHeaders()
  return Object.fromEntries(
    headers.map(h => [`--col-${h.column.id}-size`, `${h.getSize()}px`])
  )
}, [table.getState().columnSizing])

// Memoize table body during resize
const tableBody = useMemo(
  () => (
    <tbody>
      {table.getRowModel().rows.map(row => (
        <TableRow key={row.id} row={row} />
      ))}
    </tbody>
  ),
  [
    table.getRowModel().rows,
    !table.getState().columnSizingInfo.isResizingColumn,
  ]
)
```

## Server-Side Operations

For large datasets, push operations to the server:

```typescript
const [sorting, setSorting] = useState<SortingState>([])
const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 25 })

const { data: serverData } = useQuery({
  queryKey: ['packages', sorting, columnFilters, pagination],
  queryFn: () => fetchPackages({ sorting, columnFilters, pagination }),
})

const table = useReactTable({
  data: serverData?.data ?? [],
  columns,
  pageCount: serverData?.pageCount,
  state: { sorting, columnFilters, pagination },
  onSortingChange: setSorting,
  onColumnFiltersChange: setColumnFilters,
  onPaginationChange: setPagination,
  manualSorting: true,
  manualFiltering: true,
  manualPagination: true,
  getCoreRowModel: getCoreRowModel(),
})
```

## Optimize Cell Rendering

### Avoid Inline Functions

```typescript
// ❌ BAD - Creates new function every render
cell: info => <button onClick={() => handleClick(info.row)}>Edit</button>

// ✅ GOOD - Stable function reference
const handleRowClick = useCallback((row: Row<Package>) => {
  // handle click
}, [])

cell: info => <button onClick={() => handleRowClick(info.row)}>Edit</button>
```

### Use CSS for Styling

```typescript
// ❌ BAD - Inline styles recalculated every render
<td style={{ padding: '8px', color: 'blue' }}>

// ✅ GOOD - CSS classes
<td className="px-2 py-1 text-blue-600">
```

## Bundle Size Optimization

### Tree-Shaking

```typescript
// ✅ GOOD - Only imports what you need
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
} from '@tanstack/react-table'

// ❌ BAD - Imports everything
import * as TableLibrary from '@tanstack/react-table'
```

## Performance Monitoring

### Measure Render Time

```typescript
function PerformanceMonitor({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const start = performance.now()
    return () => {
      const end = performance.now()
      console.log(`Render time: ${end - start}ms`)
    }
  })
  return <>{children}</>
}
```

### React DevTools Profiler

Use React DevTools Profiler to identify slow components:
1. Record a profiling session
2. Identify components that re-render unnecessarily
3. Add memoization where needed

## Performance Checklist

- ✅ Memoize data with `useMemo`
- ✅ Memoize columns with `useMemo`
- ✅ Use `React.memo` for row/cell components
- ✅ Enable pagination for > 100 rows
- ✅ Use virtualization for > 1,000 rows
- ✅ Debounce filter inputs
- ✅ Only add row models you need
- ✅ Use server-side operations for large datasets
- ✅ Avoid inline functions in cells
- ✅ Use CSS classes instead of inline styles
- ✅ Tree-shake imports

## Performance Comparison

| Dataset Size | Recommended Approach | Renders |
|--------------|---------------------|---------|
| < 100 rows | No optimization needed | All rows |
| 100-1,000 | Pagination | 10-50 rows |
| 1,000-10,000 | Pagination + Memoization | 10-50 rows |
| 10,000+ | Virtualization | ~20 rows |
| 100,000+ | Server-side + Virtualization | ~20 rows |

## Case Study: Dependency Cascade in Inline Editing

This section documents a complex performance bug discovered in BudTags (Jan 2026) involving inline editing, React Query mutations, and columns stability. Understanding this pattern prevents hours of debugging.

### The Symptoms

1. **Typing caused focus loss** - Every keystroke in an inline edit input caused the input to lose focus
2. **Tab navigation broke selection** - Pressing Tab would briefly select the next field, then immediately deselect
3. **Image thumbnails flickered** - All images in the table re-rendered on every interaction

### The Root Cause: Dependency Cascade

```
React Query mutation (new object every render)
    ↓
useCallback dependency changes
    ↓
saveQuantity callback recreated
    ↓
renderEditableCell callback recreated
    ↓
columns useMemo dependency changes
    ↓
columns array recreated
    ↓
TanStack Table sees "new" columns
    ↓
ALL cells remount (not just re-render)
    ↓
Input element destroyed and recreated
    ↓
Focus lost, images flicker
```

### Debugging Strategy

Add strategic console.log statements to trace the cascade:

```typescript
// In hook, OUTSIDE useCallback (logs on every render)
console.log('[DEBUG] renderEditableCell useCallback evaluated');

// In useMemo callback (logs only when recreating)
const columns = useMemo(() => {
  console.log('[DEBUG] columns useMemo RECREATING');
  return [...];
}, [deps]);

// In cell component
const InlineEditInput = memo(function InlineEditInput(props) {
  console.log('[DEBUG] InlineEditInput render:', props.itemId);

  const [value, setValue] = useState(() => {
    // This only logs on MOUNT, not re-render
    console.log('[DEBUG] InlineEditInput initial state:', props.itemId);
    return props.initialValue;
  });
});
```

**Key insight:** If you see `columns useMemo RECREATING` when you didn't expect it, something in the dependency array is unstable.

### The Fix: Refs for Unstable Dependencies

React Query's `useMutation` returns a new object every render. If this is in a useCallback dependency array, the callback is recreated every render.

```typescript
// ❌ BAD - mutation is new every render
const updateMutation = useMutation({...});

const saveQuantity = useCallback((id, value) => {
  updateMutation.mutate({ id, value });
}, [updateMutation]); // ← Unstable!

const renderEditableCell = useCallback(() => {
  // uses saveQuantity
}, [saveQuantity]); // ← Also unstable now!
```

```typescript
// ✅ GOOD - Store mutation in ref
const updateMutation = useMutation({...});
const updateMutationRef = useRef(updateMutation);
updateMutationRef.current = updateMutation;

const saveQuantity = useCallback((id, value) => {
  updateMutationRef.current.mutate({ id, value });
}, []); // ← Stable! No dependencies.

const renderEditableCell = useCallback(() => {
  // uses saveQuantity
}, [saveQuantity]); // ← Also stable now!
```

### Pattern: Ref for Latest Value

Use this pattern for ANY value that:
1. Changes on every render (mutations, callbacks from props)
2. Is needed inside a callback that must be stable

```typescript
// Generic pattern
const [state, setState] = useState(initialValue);
const stateRef = useRef(state);
stateRef.current = state; // Update ref every render

// Props from parent that change
const callbackRef = useRef(props.onUpdate);
callbackRef.current = props.onUpdate;

// In stable callback, use .current
const stableCallback = useCallback(() => {
  // Access latest values via refs
  stateRef.current;
  callbackRef.current?.(value);
}, []); // Empty deps = fully stable
```

### Common Unstable Dependencies

| Dependency | Why Unstable | Solution |
|------------|--------------|----------|
| `useMutation()` result | New object every render | Store in ref |
| `useQuery()` result | New object every render | Store in ref |
| Inline callbacks | `() => {}` creates new function | Store in ref or useCallback |
| Array/object literals | `[]` or `{}` creates new reference | useMemo or define outside |
| Props callbacks | Parent may not memoize | Store in ref |

### Inline Edit Input: Isolated Local State

For inputs that need to maintain focus during typing, isolate the typing state:

```typescript
// ❌ BAD - Parent state causes re-render cascade
function TableCell({ value, onChange }) {
  return (
    <input
      value={value}
      onChange={e => onChange(e.target.value)} // Parent re-renders!
    />
  );
}

// ✅ GOOD - Local state, sync on blur/save
const InlineEditInput = memo(function InlineEditInput({
  initialValue,
  onSave
}) {
  // Local state for typing - isolated from parent
  const [inputValue, setInputValue] = useState(initialValue);

  const handleBlur = () => {
    if (inputValue !== initialValue) {
      onSave(inputValue); // Only update parent on commit
    }
  };

  return (
    <input
      value={inputValue}
      onChange={e => setInputValue(e.target.value)}
      onBlur={handleBlur}
    />
  );
});
```

### React Compiler Compatibility

TanStack Table cells are incompatible with React Compiler's automatic memoization. Add the directive:

```typescript
const InlineEditInput = memo(function InlineEditInput(props) {
  "use no forget"; // Disable React Compiler for this component

  // ... component code
});
```

### Tab Navigation with Mutations

When implementing Tab-to-next-field with background saves:

```typescript
const handleKeyDown = (e) => {
  if (e.key === 'Tab') {
    e.preventDefault();

    // 1. Mark that we're navigating (prevents blur interference)
    isNavigatingRef.current = true;

    // 2. Move focus FIRST
    startEditing(nextItemId);

    // 3. Fire save in background (if value changed)
    if (valueChanged) {
      onLocalUpdate(itemId, newValue); // Optimistic update
      mutationRef.current.mutate({ itemId, newValue });
    }

    // 4. Reset navigation flag after render
    queueMicrotask(() => { isNavigatingRef.current = false; });
  }
};

const handleBlur = () => {
  // Skip during Tab navigation
  if (isNavigatingRef.current) return;

  // Normal blur handling...
};
```

### Performance Debugging Checklist

When experiencing unexpected re-renders in TanStack Table:

1. **Add logging** to useMemo/useCallback to see what's recreating
2. **Check mutation dependencies** - are you depending on `useMutation()` result?
3. **Check props dependencies** - are parent callbacks stable?
4. **Check for inline literals** - `[]`, `{}`, `() => {}` in deps
5. **Verify `"use no forget"`** - is React Compiler interfering?
6. **Check data stability** - is the data array reference changing?

### Files Reference (BudTags)

- Hook: `resources/js/Hooks/useInlineQuantityEdit.tsx`
- Table: `resources/js/Components/Marketplace/Products/MarketplaceProductsTable.tsx`
- DataTable: `resources/js/Components/DataTable.tsx`

## Next Steps
- **Profiling** → Use React DevTools to find bottlenecks
- **Code Splitting** → Lazy load table components
- **Web Workers** → Offload heavy computations
