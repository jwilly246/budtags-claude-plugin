---
name: tanstack-table
description: Use when working with TanStack Table for data tables, datagrids, sorting, filtering, pagination, row selection, column customization, or virtualization. Version-aware - BudTags main is on v8; v9 is stable (latest 9.2.6, see patterns/25-v9-stable.md). Load specific pattern files based on the feature needed.
version: 2.1.0
category: project
agent: tanstack-specialist
auto_activate:
  patterns:
    - "**/*.{ts,tsx,js,jsx}"
  keywords:
    - "useReactTable"
    - "TanStack Table"
    - "tanstack-table"
    - "data table"
    - "datagrid"
    - "getCoreRowModel"
    - "getSortedRowModel"
    - "getFilteredRowModel"
    - "getPaginationRowModel"
    - "getExpandedRowModel"
    - "row selection"
    - "column visibility"
    - "column pinning"
    - "column resizing"
    - "column ordering"
    - "sortable table"
    - "filterable table"
    - "paginated table"
    - "DataTable.tsx"
    - "flexRender"
    - "columnDef"
    - "ColumnDef"
    - "useTable"
    - "tableFeatures"
    - "stockFeatures"
    - "createTableHook"
    - "useLegacyTable"
    - "createSortedRowModel"
    - "createFilteredRowModel"
    - "columnFilteringFeature"
    - "rowSortingFeature"
    - "rowSelectionFeature"
    - "table v9"
    - "v9 migration"
    - "table.Subscribe"
    - "createAppColumnHelper"
    - "use no memo"
---

# TanStack Table Expert Skill

## ⚠️ Version State (updated 2026-10-07), read this first

**Two majors are in play. Pick the right one before writing any code:**

- **BudTags `main` runs v8** (`@tanstack/react-table@^8.21.3`). All pattern files 01-24 document v8 and remain the operative guidance for day-to-day work on main.
- **v9 is STABLE** (9.0.0 on 2026-08-04; **latest 9.2.6**, 2026-10-04; no public API change since 9.1.2). It is a ground-up rewrite: `useReactTable`→`useTable`, mandatory `tableFeatures({...})` registration, TanStack Store state, `table.getState()` removed, `sortingFn`→`sortFn`, pinning `left`/`right`→`start`/`end`, row-selection semantics changed, `'auto'` fns resolve only registered names, ESM-only. **Read `patterns/25-v9-stable.md`**, the verified v9 fact sheet, before any v9 work.
- **React Compiler is not a free win in v9:** components that call `useTable` compile, but nested components receiving stable `row`/`cell`/`column`/`header` objects go stale unless they put a `Subscribe` inside. Never delete a TanStack `"use no memo"` without that audit (pattern 25, "React Compiler").
- **The migration is planned, not done:** repo-root `TANSTACK_TABLE_V9_UPGRADE_PLAN.md` (re-verified for 9.2.6 on 2026-10-07). Branch: `tanstack-table-v9`, cut after `chore/dependency-upgrades` merges. Pin exact `9.2.6`.
- **Once v9 is installed**, the package ships version-pinned skills in a **9.2.6 layout**: entry points `node_modules/@tanstack/table-core/skills/{core,table-features,table-state,custom-features,migrate-v8-to-v9}/SKILL.md` and `node_modules/@tanstack/react-table/skills/{getting-started,table-state,migrate-v8-to-v9}/SKILL.md`, with per-feature and per-topic detail under each entry point's `references/` (e.g. `table-features/references/row-selection.md`, `react-table/skills/table-state/references/reactivity.md`, `getting-started/references/create-table-hook.md`). Load with `npx @tanstack/intent@latest load <package>#<skill>`. Prefer those over this skill's pattern files for v9 API detail; this skill stays the authority on BudTags-specific patterns (DataTable wrapper, TableHelpers, export button, virtualization config).

## What This Skill Provides

You are an expert in **TanStack Table** (v8 today on BudTags; v9 stable exists, see Version State above), the headless UI library for building powerful, flexible data tables and datagrids. This skill provides comprehensive documentation, patterns, and BudTags/BobLink-specific examples for implementing table functionality.

## Your Capabilities

When this skill is active, you can:

1. **Guide Table Setup** - Install, configure, and initialize TanStack Table with React
2. **Define Columns** - Create accessor, display, and grouping columns with type safety
3. **Implement Sorting** - Single-column and multi-column sorting with custom sort functions
4. **Add Filtering** - Column filters, global filters, and faceted filtering
5. **Enable Pagination** - Client-side and server-side pagination patterns
6. **Manage Row Selection** - Single, multi, and checkbox-based row selection
7. **Customize Columns** - Column visibility, ordering, resizing, and pinning
8. **Handle Large Datasets** - Virtualization for thousands of rows
9. **Group & Aggregate** - Row grouping with aggregation functions
10. **Expand Rows** - Nested data and expandable rows
11. **Optimize Performance** - Memoization, render optimization, and best practices
12. **Integrate with BudTags** - Adapt existing DataTable.tsx patterns for new features

## Available Resources

### Core Documentation

- `patterns/01-installation-setup.md` (~150 lines) - Installation, dependencies, basic setup
- `patterns/02-core-concepts.md` (~200 lines) - Headless UI philosophy, table instance, state management
- `patterns/03-column-definitions.md` (~250 lines) - Column types, column helpers, accessor patterns
- `patterns/04-table-instance.md` (~180 lines) - Creating tables, options, state, methods
- `patterns/05-row-models.md` (~200 lines) - Core, filtered, sorted, grouped, paginated row models
- `patterns/06-rendering.md` (~220 lines) - Headers, cells, rows, flexRender, custom components

### Feature Documentation

- `patterns/07-sorting.md` (~180 lines) - Sorting setup, multi-sort, custom sort functions
- `patterns/08-filtering.md` (~250 lines) - Column filters, global filter, custom filter functions
- `patterns/09-pagination.md` (~170 lines) - Page state, page controls, manual pagination
- `patterns/10-row-selection.md` (~200 lines) - Selection state, checkboxes, select all patterns
- `patterns/11-column-visibility.md` (~160 lines) - Show/hide columns, visibility toggles
- `patterns/12-column-ordering.md` (~150 lines) - Drag & drop columns, reordering
- `patterns/13-column-sizing.md` (~180 lines) - Resizable columns, min/max widths
- `patterns/14-column-pinning.md` (~150 lines) - Pin left/right, sticky columns
- `patterns/15-row-expansion.md` (~190 lines) - Expandable rows, sub-rows, nested data
- `patterns/16-row-grouping-aggregation.md` - Group by column, group headers, aggregate functions
- `patterns/17-row-pinning.md` - Pin rows to top/bottom
- `patterns/18-virtualization.md` - Virtual scrolling, large datasets
- `patterns/19-faceted-filtering.md` - Faceted search, filter counts

### Advanced Topics

- `patterns/20-typescript.md` - Type safety, generics, type inference
- `patterns/21-performance.md` - Optimization tips, memoization
- `patterns/22-api-reference.md` - Complete API listing (v8)
- `patterns/23-custom-features.md` - Plugin system, custom features
- `patterns/24-budtags-integration.md` - BudTags DataTable wrapper integration

### Version Migration

- `patterns/25-v9-stable.md` - **v9 stable verified fact sheet** (9.2.6, 2026-10-07): architecture, auto-fn registration, complete rename map, behavior changes, state model, React Compiler boundaries, bundled-skill locations (9.2.6 layout), BudTags migration facts

(File names above match disk as of 2026-10-07.)

## Quick Start Guide

*(v8 API below, the version on BudTags `main`. For the v9 equivalent, see `patterns/25-v9-stable.md`.)*

### Installation

```bash
npm install @tanstack/react-table
```

### Basic Table Setup

```typescript
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table'

type Package = {
  Tag: string
  ProductName: string
  Quantity: number
  UnitOfMeasureName: string
}

const columnHelper = createColumnHelper<Package>()

const columns = [
  columnHelper.accessor('Tag', {
    header: 'Package Tag',
    cell: info => info.getValue(),
  }),
  columnHelper.accessor('ProductName', {
    header: 'Product',
  }),
  columnHelper.accessor('Quantity', {
    header: 'Quantity',
    cell: info => {
      const quantity = info.getValue()
      const unit = info.row.original.UnitOfMeasureName
      return `${quantity} ${unit}`
    },
  }),
]

function PackagesTable({ data }: { data: Package[] }) {
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

### With Sorting & Filtering

```typescript
import {
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  useReactTable,
} from '@tanstack/react-table'

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})

// In header rendering:
<th onClick={header.column.getToggleSortingHandler()}>
  {flexRender(header.column.columnDef.header, header.getContext())}
  {{
    asc: ' 🔼',
    desc: ' 🔽',
  }[header.column.getIsSorted() as string] ?? null}
</th>
```

## Progressive Loading Strategy

**Load only what you need:**

1. **Basic Table** → Load patterns 01-06 (setup, columns, rendering)
2. **Add Sorting** → Load pattern 07
3. **Add Filtering** → Load patterns 08, 19 (filtering, faceted)
4. **Add Pagination** → Load pattern 09
5. **Add Selection** → Load pattern 10
6. **Customize Columns** → Load patterns 11-14 (visibility, ordering, sizing, pinning)
7. **Large Datasets** → Load pattern 18 (virtualization)
8. **Advanced Features** → Load patterns 15-17, 23 (expansion, grouping, row pinning, custom features)
9. **Anything v9 / migration** → Load pattern 25 FIRST, then the package's first-party skills if v9 is installed

## Key Patterns from BudTags

### Pattern 1: Reusable DataTable Component

**BudTags Implementation (v8, abridged from `resources/js/Components/DataTable.tsx`):** controlled state for filters/selection/visibility/sorting, manual pagination (no pagination row model), sorting/filtering switchable to server mode, faceting always on.
```typescript
function DataTable<TData>({ data, columns, manualSorting, manualFiltering, enableRowSelection, getRowId, meta, ... }: DataTableProps<TData>) {
  "use no memo"; // TanStack Table incompatible with React Compiler (v8 only)

  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(initialColumnFilters);
  const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>(initialColumnVisibility);
  const [sorting, setSorting] = React.useState<SortingState>(initialSorting);

  const table = useReactTable({
    columns: effectiveColumns, // checkbox column injected when bulk actions need it
    data,
    getRowId,
    meta,
    state: { columnFilters, rowSelection, columnVisibility, sorting },
    onColumnFiltersChange: handleColumnFiltersChange,
    onRowSelectionChange: handleRowSelectionChange,
    onColumnVisibilityChange: handleColumnVisibilityChange,
    onSortingChange: handleSortingChange,
    enableRowSelection,
    manualSorting,
    manualFiltering,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: manualSorting ? undefined : getSortedRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getFacetedMinMaxValues: getFacetedMinMaxValues(),
  });
  // ... header filters (TableFilter), ColumnVisibilityToggle, TableExportButton,
  // customToolbarSlot(table), virtualized rows, mobile cards
}
```
*(v9: this block becomes `useAppTable`/`useTable` with an app-level `tableFeatures` registry; see pattern 25 and the upgrade plan.)*

### Pattern 2: Checkbox Column Helper

**From `TableHelpers.tsx` (`createCheckboxColumn`, v8, abridged):** page-level select-all header; per-row checkbox with a capture-phase Shift-click range handler.
```typescript
export const createCheckboxColumn = <T,>(columnHelper: ColumnHelper<T>, disabledTitle?: string, rowLabel?: (row: T) => string) =>
  columnHelper.display({
    id: 'select',
    size: 36,
    header: ({ table }) => (
      <InputCheckbox
        ariaLabel="Select every row on this page"
        checked={table.getIsAllPageRowsSelected()}
        indeterminate={table.getIsSomePageRowsSelected()}
        onChange={table.getToggleAllPageRowsSelectedHandler()}
      />
    ),
    cell: ({ row, table }) => (
      <div onClickCapture={(e) => { if (e.shiftKey && row.getCanSelect()) { e.stopPropagation(); e.preventDefault(); /* custom range from last selected key */ } }}>
        <InputCheckbox checked={row.getIsSelected()} disabled={!row.getCanSelect()} onChange={row.getToggleSelectedHandler()} />
      </div>
    ),
    enableColumnFilter: false,
    enableSorting: false,
  });
```
*(v9: `getIsSomePageRowsSelected()` means "at least one" and stays `true` at full selection, so indeterminate becomes `getIsSomePageRowsSelected() && !getIsAllPageRowsSelected()`; the Shift handler's `table.getState().rowSelection` becomes `table.atoms.rowSelection.get()`; once `"use no memo"` is gone the header and cell need a `Subscribe` on `rowSelection` (pattern 25, "React Compiler"). The v8 range handler also lacks a guard for an anchor missing from the current rows.)*

### Pattern 3: Filter Button Cells

**From TableHelpers.tsx:**
```typescript
export function createFilterButtonCell<TData, TValue>(
  accessor: (row: TData) => TValue,
  filterKey: string
) {
  return {
    cell: ({ getValue, table }: CellContext<TData, TValue>) => {
      const value = getValue()
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

### Pattern 4: Date Sorting

**From TableHelpers.tsx:**
```typescript
export function createDateSortingFn() {
  return (rowA: Row<any>, rowB: Row<any>, columnId: string) => {
    const dateA = new Date(rowA.getValue(columnId))
    const dateB = new Date(rowB.getValue(columnId))
    return dateA.getTime() - dateB.getTime()
  }
}
```

## Common Use Cases in BudTags/BobLink

### Use Case 1: Metrc Package Tables

**Files:** `features/metrc/components/TablePackages.tsx`

**Features Used:**
- ✅ Column definitions (Tag, Product, Quantity, Location, etc.)
- ✅ Sorting (by date, quantity, product)
- ✅ Filtering (by status, location, product type)
- ✅ Row selection (for bulk label creation)
- ✅ Column visibility (show/hide based on user preference)
- ✅ Virtualization (`virtualize` prop)
- ✅ Faceted header filters (DataTable `TableFilter`)
- ✅ Saved-filter chips (hidden synthetic column with a custom `filterFn`)

### Use Case 2: Order Tables

**Files:** `TableOrdersLeaflink` (see `Pages/Org/OrdersLeaflink.tsx`)

**Features Used:**
- ✅ Column definitions
- ✅ Sorting
- ✅ Pagination
- ⚠️ Missing: Server-side filtering
- ⚠️ Missing: Column pinning (pin status column)

### Use Case 3: Plant Tables

**Files:** `features/metrc/components/TablePlants.tsx`

**Features Used:**
- ✅ Basic table setup
- ✅ Filtering
- ⚠️ Missing: Row grouping (group by growth phase)
- ⚠️ Missing: Aggregation (total count per phase)

## Critical ✅ / ❌ Patterns

### ✅ DO: Use Column Helpers for Type Safety

```typescript
const columnHelper = createColumnHelper<Package>()

const columns = [
  columnHelper.accessor('Tag', {
    header: 'Tag',
    // ✅ Type-safe: Tag is string
  }),
]
```

### ❌ DON'T: Define columns without type safety

```typescript
const columns = [
  {
    accessorKey: 'Tag', // ❌ No type checking
    header: 'Tag',
  },
]
```

### ✅ DO: Memoize Column Definitions

```typescript
const columns = useMemo(() => [
  columnHelper.accessor('Tag', { ... }),
], [])
```

*(v8 tables run under `"use no memo"`, so manual memoization is the only stabilizer. In v9 a compiled component usually doesn't need it, but stable `data`/`columns` references still matter; keep existing memos unless you know why they exist.)*

### ❌ DON'T: Recreate columns on every render

```typescript
// ❌ Creates new column instances every render
const columns = [columnHelper.accessor('Tag', { ... })]
```

### ✅ DO: Use flexRender for Dynamic Components

```typescript
{flexRender(cell.column.columnDef.cell, cell.getContext())}
```

### ❌ DON'T: Render cells directly

```typescript
{cell.column.columnDef.cell} {/* ❌ Won't work with functions */}
```

### ✅ DO: Use Row Models for Features

```typescript
const table = useReactTable({
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(), // ✅ Enable sorting
  getFilteredRowModel: getFilteredRowModel(), // ✅ Enable filtering
})
```

### ❌ DON'T: Try to sort/filter without row models

```typescript
const table = useReactTable({
  getCoreRowModel: getCoreRowModel(),
  // ❌ Missing getSortedRowModel - sorting won't work
})
```

## Common Pitfalls

### Pitfall 1: Data Reference Instability

**Problem:** Table rerenders unnecessarily because `data` array is recreated

**Solution:** Memoize data
```typescript
const data = useMemo(() => packages, [packages])
```

### Pitfall 2: Missing Row Models

**Problem:** Features don't work (sorting, filtering, pagination)

**Solution:** Add required row models
```typescript
getSortedRowModel: getSortedRowModel() // For sorting to work
```

### Pitfall 3: Incorrect Cell Rendering

**Problem:** `cell.column.columnDef.cell` is a function but rendered as string

**Solution:** Use `flexRender`
```typescript
{flexRender(cell.column.columnDef.cell, cell.getContext())}
```

### Pitfall 4: Large Dataset Performance

**Problem:** Table lags with 1000+ rows

**Solution:** Use virtualization
```typescript
import { useVirtualizer } from '@tanstack/react-virtual'
// See pattern 18 for full implementation
```

## Integration with Other TanStack Products

### With TanStack Query

```typescript
const { data: packages } = useQuery({
  queryKey: ['packages', license],
  queryFn: () => fetchPackages(license),
})

const table = useReactTable({
  data: packages ?? [],
  columns,
  getCoreRowModel: getCoreRowModel(),
})
```

### With TanStack Virtual

```typescript
const table = useReactTable({ /* ... */ })

const { rows } = table.getRowModel()

const rowVirtualizer = useVirtualizer({
  count: rows.length,
  getScrollElement: () => tableContainerRef.current,
  estimateSize: () => 50,
})
```

## Your Mission

When helping with TanStack Table:

1. **Assess Requirements** - Determine which features are needed
2. **Load Relevant Patterns** - Reference only the pattern files needed
3. **Provide Type-Safe Code** - Always use TypeScript and column helpers
4. **Follow BudTags Patterns** - Reuse existing patterns from DataTable.tsx, TableHelpers.tsx
5. **Optimize Performance** - Use memoization, consider virtualization for large datasets
6. **Test Thoroughly** - Ensure sorting, filtering, and selection work correctly

**Remember:** TanStack Table is already used extensively in BudTags. Your goal is to help implement new features, optimize existing tables, and solve table-related challenges using the comprehensive documentation in this skill.

Load specific pattern files as needed using progressive disclosure. For basic setup, load patterns 01-06. For specific features, load the corresponding pattern file.
