# Pattern 13: Column Sizing

## ⚠️ CRITICAL: TanStack Table is HEADLESS - Size is NOT CSS!

**This is the #1 source of confusion with TanStack Table column sizing.**

TanStack Table's `size` property is **just a number stored in state**. It does NOT automatically apply CSS to your table. The browser has NO IDEA what your `size` values are unless YOU apply them via styles.

### The Problem You Will Face

You set `size: 64` on a column. You apply `style={{ width: header.getSize() }}` to your cells. But the column is STILL 120px wide. **WHY?**

**Because HTML tables have their own layout algorithm that IGNORES your width hints.**

### Why `width` and `maxWidth` Don't Work (with table-layout: auto)

With `table-layout: auto` (the browser default):
- The browser calculates column widths based on **content**
- Your `width` and `maxWidth` styles are treated as **hints**, not constraints
- The browser **distributes excess table width proportionally** across ALL columns
- Even columns with explicit widths get expanded

```typescript
// ❌ THIS WILL NOT WORK AS EXPECTED
<table className="w-full"> {/* table-layout: auto by default */}
  <th style={{ width: 64, maxWidth: 64 }}>Image</th>  {/* Browser ignores this! */}
  <th>Name</th>
  <th style={{ width: 100 }}>Actions</th>
</table>
// Result: Image column is ~120px, not 64px
```

### The Solution: table-layout: fixed + Explicit Sizes on ALL Columns

**You MUST do BOTH of these things:**

1. **Set `table-layout: fixed`** on the `<table>` element
2. **Give EVERY column an explicit `size`** - including your "flex" column

```typescript
// ✅ THIS WORKS
<table style={{ tableLayout: 'fixed' }} className="w-full">
  <th style={{ width: 64 }}>Image</th>      {/* Gets exactly 64px */}
  <th style={{ width: 500 }}>Name</th>       {/* Gets exactly 500px (largest = "flex") */}
  <th style={{ width: 100 }}>Status</th>     {/* Gets exactly 100px */}
  <th style={{ width: 44 }}>Actions</th>     {/* Gets exactly 44px */}
</table>
// Total: 708px - fits in container, Name column is largest
```

### The "Flex Column" Pattern

If you want one column to absorb remaining space like a flex container, you might think to NOT give it a size. **This does NOT work reliably.**

```typescript
// ❌ UNRELIABLE - undefined size with table-fixed
columnHelper.accessor('name', {
  header: 'Name',
  // No size - hoping it absorbs remaining space
})
// Result: Unpredictable behavior, may get default 150px or weird distribution
```

**Instead, give your "flex" column a LARGE explicit size:**

```typescript
// ✅ CORRECT - Large size acts as "flex"
columnHelper.accessor('name', {
  header: 'Name',
  size: 500,  // Largest column = gets most space
})
```

### Complete Working Example (BudTags Pattern)

```typescript
// In your table component
const columns = useMemo(() => [
  columnHelper.accessor('image', {
    id: 'image',
    header: '',
    size: 64,  // Small fixed column
  }),
  columnHelper.accessor('name', {
    id: 'name',
    header: 'Product',
    size: 500,  // LARGEST = "flex" column, absorbs most space
  }),
  columnHelper.accessor('status', {
    id: 'status',
    header: 'Status',
    size: 110,  // Medium fixed column
  }),
  columnHelper.display({
    id: 'actions',
    header: '',
    size: 44,  // Small fixed column for kebab menu
  }),
], [])

// In DataTable, apply tableLayout: fixed conditionally
<DataTable
  columns={columns}
  data={data}
  tableStyle={{ tableLayout: 'fixed' }}  // CRITICAL!
/>

// Inside DataTable's render:
<table
  className="w-full"
  style={tableStyle}  // { tableLayout: 'fixed' }
>
  <thead>
    {headers.map(header => (
      <th
        key={header.id}
        style={{
          width: header.column.columnDef.size,  // Apply size as width
          maxWidth: header.column.columnDef.size
        }}
      >
        {/* ... */}
      </th>
    ))}
  </thead>
  <tbody>
    {rows.map(row => (
      <tr>
        {row.getVisibleCells().map(cell => (
          <td
            style={{
              width: cell.column.columnDef.size,
              maxWidth: cell.column.columnDef.size
            }}
          >
            {/* ... */}
          </td>
        ))}
      </tr>
    ))}
  </tbody>
</table>
```

### Quick Reference: Column Sizing That Actually Works

| What You Want | What To Do |
|--------------|------------|
| Fixed 64px column | `size: 64` + `tableLayout: 'fixed'` |
| Column that absorbs remaining space | `size: 500` (or larger than other columns) |
| All columns respect their sizes | `tableLayout: 'fixed'` on `<table>` |
| Columns in a full-width table | Sum of all sizes < container width |

### Calculating Total Width

**Your column sizes should sum to LESS than or equal to the container width to avoid horizontal scroll.**

```typescript
// Example: Container is ~1200px
const columns = [
  { id: 'image', size: 64 },      // 64px
  { id: 'name', size: 500 },      // 500px (flex)
  { id: 'status', size: 110 },    // 110px
  { id: 'qty', size: 130 },       // 130px
  { id: 'actions', size: 44 },    // 44px
]
// Total: 848px ✓ (fits in 1200px container)
```

---

## Default Column Sizes

TanStack Table provides default sizes for all columns:

```typescript
// Built-in defaults:
size: 150        // Default width (px)
minSize: 20      // Minimum width (px)
maxSize: Number.MAX_SAFE_INTEGER  // Maximum width
```

## Setting Column Sizes

### Per-Column Sizing

```typescript
const columns = [
  columnHelper.accessor('Label', {
    header: 'Package Tag',
    size: 200,      // Fixed width
    minSize: 100,   // Minimum width
    maxSize: 400,   // Maximum width
  }),
  columnHelper.accessor('ProductName', {
    header: 'Product',
    size: 300,
  }),
]
```

### Default for All Columns

```typescript
const table = useReactTable({
  data,
  columns,
  defaultColumn: {
    size: 200,      // Default for all columns
    minSize: 50,    // Minimum for all columns
    maxSize: 500,   // Maximum for all columns
  },
  getCoreRowModel: getCoreRowModel(),
})
```

## Column Resizing

### Enable Resizing

Column resizing is enabled by default. Manage the state:

```typescript
const [columnSizing, setColumnSizing] = useState<ColumnSizingState>({})

const table = useReactTable({
  data,
  columns,
  state: { columnSizing },
  onColumnSizingChange: setColumnSizing,
  columnResizeMode: 'onChange', // or 'onEnd'
  getCoreRowModel: getCoreRowModel(),
})
```

### Column Sizing State

```typescript
type ColumnSizingState = Record<string, number>

// Example:
const columnSizing = {
  'Label': 250,
  'ProductName': 300,
  'Quantity': 100,
}
```

### Resize Modes

```typescript
// Update size immediately during drag
columnResizeMode: 'onChange'  // ← Real-time updates

// Update size only after drag completes
columnResizeMode: 'onEnd'     // ← Default, better performance
```

## Resizable Headers

### Basic Resize Handle

```typescript
<th key={header.id} style={{ width: header.getSize() }}>
  {flexRender(header.column.columnDef.header, header.getContext())}
  {header.column.getCanResize() && (
    <div
      onMouseDown={header.getResizeHandler()}
      onTouchStart={header.getResizeHandler()}
      className="resizer"
    />
  )}
</th>
```

### Styled Resize Handle

```typescript
<th
  key={header.id}
  style={{
    width: header.getSize(),
    position: 'relative',
  }}
>
  {flexRender(header.column.columnDef.header, header.getContext())}
  {header.column.getCanResize() && (
    <div
      onMouseDown={header.getResizeHandler()}
      onTouchStart={header.getResizeHandler()}
      className={`
        absolute right-0 top-0 h-full w-1
        bg-gray-300 cursor-col-resize
        hover:bg-blue-500
        ${header.column.getIsResizing() ? 'bg-blue-500' : ''}
      `}
    />
  )}
</th>
```

## Applying Column Sizes

### Inline Styles

```typescript
<th style={{ width: header.getSize() }}>
  {flexRender(header.column.columnDef.header, header.getContext())}
</th>

<td style={{ width: cell.column.getSize() }}>
  {flexRender(cell.column.columnDef.cell, cell.getContext())}
</td>
```

### CSS Variables (Recommended)

```typescript
<th
  style={{
    ['--col-width' as any]: `${header.getSize()}px`,
  }}
  className="w-[var(--col-width)]"
>
  {flexRender(header.column.columnDef.header, header.getContext())}
</th>
```

### CSS Grid Layout

```typescript
const columnSizeVars = useMemo(() => {
  const headers = table.getFlatHeaders()
  const sizes: { [key: string]: number } = {}

  headers.forEach(header => {
    sizes[`--header-${header.id}-size`] = header.getSize()
    sizes[`--col-${header.column.id}-size`] = header.column.getSize()
  })

  return sizes
}, [table.getState().columnSizing])

return (
  <table
    style={{
      ...columnSizeVars,
      width: table.getTotalSize(),
    }}
  >
    {/* ... */}
  </table>
)
```

## Disable Resizing

### Disable for Specific Column

```typescript
columnHelper.accessor('Label', {
  header: 'Package Tag',
  enableResizing: false, // ← Can't resize this column
})
```

### Disable for All Columns

```typescript
const table = useReactTable({
  data,
  columns,
  enableColumnResizing: false, // ← Disable all resizing
  getCoreRowModel: getCoreRowModel(),
})
```

## Resize Direction

For right-to-left layouts:

```typescript
const table = useReactTable({
  data,
  columns,
  columnResizeDirection: 'rtl', // ← Right-to-left
  getCoreRowModel: getCoreRowModel(),
})
```

## Complete Resizable Example

```typescript
function ResizableTable({ data }: { data: Package[] }) {
  const [columnSizing, setColumnSizing] = useState<ColumnSizingState>({})

  const columns = useMemo(() => [
    columnHelper.accessor('Label', {
      header: 'Package Tag',
      size: 200,
      minSize: 100,
      maxSize: 400,
    }),
    columnHelper.accessor('ProductName', {
      header: 'Product',
      size: 300,
      minSize: 150,
      maxSize: 600,
    }),
    columnHelper.accessor('Quantity', {
      header: 'Quantity',
      size: 100,
      minSize: 60,
      maxSize: 200,
    }),
    columnHelper.display({
      id: 'actions',
      header: 'Actions',
      size: 100,
      enableResizing: false, // Fixed width
      cell: () => <button>Edit</button>,
    }),
  ], [])

  const table = useReactTable({
    data,
    columns,
    state: { columnSizing },
    onColumnSizingChange: setColumnSizing,
    columnResizeMode: 'onChange',
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div>
      <button
        onClick={() => table.resetColumnSizing()}
        className="mb-4 text-blue-600"
      >
        Reset Column Sizes
      </button>

      <div className="overflow-x-auto">
        <table
          style={{
            width: table.getCenterTotalSize(),
          }}
          className="border-collapse"
        >
          <thead>
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th
                    key={header.id}
                    style={{
                      width: header.getSize(),
                      position: 'relative',
                    }}
                    className="border px-4 py-2 bg-gray-50"
                  >
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
                    {header.column.getCanResize() && (
                      <div
                        onMouseDown={header.getResizeHandler()}
                        onTouchStart={header.getResizeHandler()}
                        className={`
                          absolute right-0 top-0 h-full w-1
                          cursor-col-resize select-none touch-none
                          ${
                            header.column.getIsResizing()
                              ? 'bg-blue-500 opacity-100'
                              : 'bg-gray-300 opacity-0 hover:opacity-100'
                          }
                        `}
                      />
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
                  <td
                    key={cell.id}
                    style={{ width: cell.column.getSize() }}
                    className="border px-4 py-2"
                  >
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
    </div>
  )
}
```

## Resize Indicator

Show a visual indicator while resizing:

```typescript
function ResizeIndicator({ table }: { table: Table<any> }) {
  const columnSizingInfo = table.getState().columnSizingInfo

  return columnSizingInfo.isResizingColumn ? (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: `${columnSizingInfo.deltaOffset}px`,
        height: '100%',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        pointerEvents: 'none',
      }}
    />
  ) : null
}
```

## Column Sizing API Methods

### Header Methods

```typescript
header.getSize()             // Get current size
header.getResizeHandler()    // Get resize event handler
header.column.getCanResize() // Check if resizable
header.column.getIsResizing() // Check if currently resizing
```

### Column Methods

```typescript
column.getSize()             // Get current size
column.getCanResize()        // Check if resizable
column.getIsResizing()       // Check if currently resizing
column.resetSize()           // Reset to initial size
```

### Table Methods

```typescript
table.getTotalSize()         // Total width of all columns
table.getLeftTotalSize()     // Total width of left pinned columns
table.getCenterTotalSize()   // Total width of unpinned columns
table.getRightTotalSize()    // Total width of right pinned columns

table.resetColumnSizing()    // Reset all column sizes
table.setColumnSizing({ ... }) // Set specific sizes

table.getState().columnSizing // Get current sizing state
table.getState().columnSizingInfo // Get resize info (deltaOffset, etc.)
```

## Save/Load Column Sizes

```typescript
function PackagesTable({ data }: { data: Package[] }) {
  const [columnSizing, setColumnSizing] = useState<ColumnSizingState>(() => {
    const saved = localStorage.getItem('packageTableColumnSizing')
    return saved ? JSON.parse(saved) : {}
  })

  useEffect(() => {
    localStorage.setItem(
      'packageTableColumnSizing',
      JSON.stringify(columnSizing)
    )
  }, [columnSizing])

  const table = useReactTable({
    data,
    columns,
    state: { columnSizing },
    onColumnSizingChange: setColumnSizing,
    getCoreRowModel: getCoreRowModel(),
  })

  return <table>{/* ... */}</table>
}
```

## Performance Optimization

For large tables, memoize calculations during resize:

```typescript
const columnSizeVars = useMemo(() => {
  const headers = table.getFlatHeaders()
  return Object.fromEntries(
    headers.map(header => [
      `--col-${header.column.id}-size`,
      `${header.getSize()}px`,
    ])
  )
}, [table.getState().columnSizing])

// Memoize table body during resize
const tableBody = useMemo(
  () => (
    <tbody>
      {table.getRowModel().rows.map(row => (/* ... */))}
    </tbody>
  ),
  [table.getRowModel().rows, table.getState().columnSizingInfo.isResizingColumn]
)
```

## Common Mistakes

### ❌ BIGGEST MISTAKE: Forgetting table-layout: fixed

```typescript
// ❌ BROKEN - table-layout: auto ignores your widths!
<table className="w-full table-auto">
  <th style={{ width: 64 }}>...</th>  // Browser: "That's cute, here's 120px"
</table>

// ✅ WORKS - table-layout: fixed respects widths
<table className="w-full" style={{ tableLayout: 'fixed' }}>
  <th style={{ width: 64 }}>...</th>  // Browser: "OK, 64px it is"
</table>
```

### ❌ Expecting Undefined Size to Create a "Flex" Column

```typescript
// ❌ BROKEN - undefined size = unpredictable behavior
columnHelper.accessor('name', {
  header: 'Name',
  // No size defined - you think it will "flex"
  // Reality: Gets default 150px or weird distribution
})

// ✅ WORKS - explicit large size = reliable "flex" behavior
columnHelper.accessor('name', {
  header: 'Name',
  size: 500,  // Large value makes this the dominant column
})
```

### ❌ Column Sizes Sum Exceeds Container Width

```typescript
// ❌ BROKEN - causes horizontal scroll
const columns = [
  { size: 200 },
  { size: 9999 },  // WAY too big!
  { size: 300 },
]
// Total: 10499px > screen width = horizontal scroll

// ✅ WORKS - sizes fit within container
const columns = [
  { size: 64 },
  { size: 500 },  // Large but reasonable
  { size: 100 },
]
// Total: 664px < typical container width
```

### ❌ Using Tailwind Classes Instead of Inline Styles

```typescript
// ❌ UNRELIABLE - Tailwind classes may not apply correctly to table cells
<th className="w-16">...</th>  // May be overridden by table layout

// ✅ RELIABLE - Inline styles take precedence
<th style={{ width: 64, maxWidth: 64 }}>...</th>
```

### ❌ Not Applying Sizes to Headers AND Cells

```typescript
// ❌ Only on headers
<th style={{ width: header.getSize() }}>...</th>
<td>...</td>

// ✅ Apply to both
<th style={{ width: header.getSize() }}>...</th>
<td style={{ width: cell.column.getSize() }}>...</td>
```

### ❌ Missing Touch Events

```typescript
// ❌ Mouse only
<div onMouseDown={header.getResizeHandler()} />

// ✅ Mouse and touch
<div
  onMouseDown={header.getResizeHandler()}
  onTouchStart={header.getResizeHandler()}
/>
```

## Type Definitions

```typescript
type ColumnSizingState = Record<string, number>

type ColumnSizingInfoState = {
  startOffset: number | null
  startSize: number | null
  deltaOffset: number | null
  deltaPercentage: number | null
  isResizingColumn: string | false
  columnSizingStart: [string, number][]
}

type ColumnSizingOptions = {
  enableColumnResizing?: boolean
  columnResizeMode?: 'onChange' | 'onEnd'
  columnResizeDirection?: 'ltr' | 'rtl'
  onColumnSizingChange?: OnChangeFn<ColumnSizingState>
}
```

## Troubleshooting: "My Column Widths Aren't Working!"

### Symptom: Columns are wider than their `size` value

**Diagnosis checklist:**

1. **Is `tableLayout: 'fixed'` set on the `<table>`?**
   ```typescript
   // Check your table element
   <table style={{ tableLayout: 'fixed' }}>  // Must have this!
   ```

2. **Do ALL columns have explicit `size` values?**
   ```typescript
   // Check every column definition
   { id: 'image', size: 64 },      // ✓
   { id: 'name', size: 500 },      // ✓ Even the "flex" column needs a size!
   { id: 'actions', size: 44 },    // ✓
   ```

3. **Is the `size` being applied as a `style` attribute?**
   ```typescript
   // Check your <th> and <td> elements
   <th style={{ width: header.column.columnDef.size }}>  // Must apply size as width!
   ```

4. **Are you using `columnDef.size` (what you set) vs `getSize()` (computed)?**
   ```typescript
   // columnDef.size = what YOU defined (undefined if not set)
   // getSize() = computed value (includes defaults, may be 150)

   // For conditional styling, check columnDef.size
   style={header.column.columnDef.size !== undefined
     ? { width: header.column.columnDef.size }
     : undefined}
   ```

### Symptom: Horizontal scroll appears unexpectedly

**Your column sizes sum to more than the container width.**

```typescript
// Calculate total:
const total = columns.reduce((sum, col) => sum + (col.size || 150), 0)
console.log('Total column width:', total)  // Should be < container width
```

**Fix:** Reduce your "flex" column size or other column sizes.

### Symptom: One column is way too small/large

**Check that column's `size` value:**

```typescript
// Debug: Add data attributes to see what's happening
<td data-size={cell.column.columnDef.size} data-computed={cell.column.getSize()}>
```

### Symptom: Changes don't appear after editing code

**Hot reload may not be working. Try:**
1. Hard refresh (Ctrl+Shift+R)
2. Check if Vite dev server is running
3. Check browser console for errors

## Next Steps

- **Column Pinning** → See pattern 14
- **Responsive Tables** → Combine with visibility
- **Save Preferences** → Persist sizing to localStorage
