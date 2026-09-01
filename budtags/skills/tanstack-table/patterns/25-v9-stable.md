# TanStack Table v9 Stable: Verified Fact Sheet

> **Status (2026-08-12):** v9.0.0 went **stable 2026-08-04** (no RC; straight from beta.80). Patches since: 9.0.1 + 9.1.0 (Aug 7), 9.1.1 (Aug 8), 9.1.2 (Aug 9). **BudTags `main` is still on v8.21.3**, the migration is planned in repo-root `TANSTACK_TABLE_V9_UPGRADE_PLAN.md`. Everything below was verified against the installed `9.1.2` `.d.ts` files and the regenerated migration guide, not from memory.

## Which version am I writing for?

- **On `main` / any branch without the v9 migration:** write **v8** code. Use pattern files 01–24 as-is.
- **On the `tanstack-table-v9` migration branch (or after it merges):** write **v9** code per this file, and prefer the **first-party skills that ship inside the package** (see bottom).

## Version floor

Pin exact, never a range. Floor is **9.1.2**:
- 9.1.1 restored v8's parent-first sorted-`flatRows` order (parity bug in 9.0.0–9.1.0).
- 9.1.2 removed a class of controlled-state render loops (auto-reset firing a semantically identical state value after a `data` reference change, exactly the controlled-wrapper + React Query refetch shape BudTags uses).

## Core architecture change

v8 bundled every feature into `useReactTable`. v9 is tree-shakeable: you register features, row models, and fn registries explicitly, and an API exists only if its feature is registered.

```tsx
import {
  columnFilteringFeature, rowSortingFeature,
  createFilteredRowModel, createSortedRowModel,
  filterFn_includesString, sortFn_alphanumeric,
  tableFeatures, useTable,
} from '@tanstack/react-table'

const features = tableFeatures({
  // 1. features first (prerequisites before dependents)
  columnFilteringFeature,
  rowSortingFeature,
  // 2. then row-model slots, factories take NO arguments
  filteredRowModel: createFilteredRowModel(),
  sortedRowModel: createSortedRowModel(),
  // 3. then fn registries, keyed maps of individually-imported built-ins + customs
  filterFns: { includesString: filterFn_includesString },
  sortFns: { alphanumeric: sortFn_alphanumeric },
})

const table = useTable({ features, columns, data })
```

- `useReactTable` → **`useTable`**; `features` is required.
- The **core row model is automatic**, no `getCoreRowModel()`.
- `stockFeatures` = all-features shortcut (audit aid, not the production target). `useLegacyTable` at `@tanstack/react-table/legacy` = deprecated v8-shaped bridge.
- Feature prerequisites: `columnResizingFeature` requires `columnSizingFeature`; `globalFilteringFeature` requires `columnFilteringFeature`; every slot requires its feature.

**16 stock features:** `cellSelectionFeature` (new), `columnFacetingFeature`, `columnFilteringFeature`, `columnGroupingFeature`, `columnOrderingFeature`, `columnPinningFeature`, `columnResizingFeature`, `columnSizingFeature`, `columnVisibilityFeature`, `globalFilteringFeature`, `rowAggregationFeature`, `rowExpandingFeature`, `rowPaginationFeature`, `rowPinningFeature`, `rowSelectionFeature`, `rowSortingFeature`. (Plus `cellSpanningFeature`, and experimental `workerRowModelsFeature` via the `experimental-worker-plugin` subpath.)

**Row-model slots** (all no-arg factories): `filteredRowModel`, `sortedRowModel`, `paginatedRowModel`, `expandedRowModel`, `groupedRowModel`, `facetedRowModel`, `facetedUniqueValues`, `facetedMinMaxValues`; custom core via `coreRowModel`.

## Complete rename map

| v8 | v9 |
|----|----|
| `useReactTable(options)` | `useTable({ ...options, features })` |
| `sortingFn` / `sortingFns` / `SortingFn` / `SortingFns` | `sortFn` / `sortFns` / `SortFn` / `SortFns` |
| `column.getSortingFn()` / `getAutoSortingFn()` | `column.getSortFn()` / `getAutoSortFn()` |
| `columnPinning.left` / `.right` (state, args, comparisons) | `.start` / `.end` |
| `table.getLeft*()` / `getRight*()` (every pinning getter family) | `getStart*()` / `getEnd*()` |
| `getCenter*()` getters | **UNCHANGED** (only left/right renamed) |
| table option `enablePinning` | `enableColumnPinning` + `enableRowPinning` (column-def `enablePinning` remains) |
| `columnSizingInfo` state / `setColumnSizingInfo` / `onColumnSizingInfoChange` | `columnResizing` / `setColumnResizing` / `onColumnResizingChange` |
| `VisibilityState` type | **`ColumnVisibilityState`** |
| `table.getState()` | REMOVED → `table.state` / `table.store.state` / `table.atoms.<slice>.get()` |
| top-level `onStateChange` | REMOVED → per-slice `on*Change` or `table.store.subscribe()` |
| `row._getAllCellsByColumnId()` | `row.getAllCellsByColumnId()` |
| `table._getPinnedRows()` | `getTopRows()` / `getCenterRows()` / `getBottomRows()` |
| `createColumnHelper<TData>()` | `createColumnHelper<typeof features, TData>()` |
| `ColumnDef<TData, TValue>` (and Table/Row/Cell/Column types) | gain a leading `TFeatures` generic |
| `column.getAggregationFn()` | `column.getAggregationFns()` (plural); custom fns via `constructAggregationFn({ aggregate })` |

`SortingState`, `ColumnFiltersState`, `RowSelectionState`, `PaginationState`, `ExpandedState`, `Updater`, `flexRender` all keep their names.

## Behavior changes (compile silently, break at runtime)

1. **`getIsSomeRowsSelected()` / `getIsSomePageRowsSelected()` mean "at least one"** and stay `true` when ALL rows are selected (v8 returned `false`). Indeterminate checkbox = `getIsSomeRowsSelected() && !getIsAllRowsSelected()`.
2. **`row.getToggleSelectedHandler()` does inclusive shift-range selection by default** when `rowSelectionFeature` is registered. Opt out: `enableRowRangeSelection: false`. Never run both built-in and custom shift-click logic.
3. **Instance methods live on shared prototypes** (that's where the memory win comes from). Destructuring, spreading, `Object.keys`, `JSON.stringify` on rows/cells/columns/headers lose the methods, always call `row.getValue('x')` on the instance. Table-instance methods are exempt.
4. **`RowData` must be a record or array** (`Record<string, any> | Array<any>`; was `unknown`).
5. Pinning is *logical* (`start`/`end`), pair with logical CSS (`inset-inline-start`), not `left`/`right`.

## State model (TanStack Store underneath)

| Need | Surface |
|------|---------|
| Reactive read in a component | `table.state` (respects the `useTable` selector) |
| One-off snapshot | `table.store.state` |
| Narrowest subscription | `useSelector(table.atoms.<slice>)` from `@tanstack/react-store` |
| Render-prop subscription | `<table.Subscribe selector={s => s.sorting}>{sorting => ...}</table.Subscribe>` |
| Controlled slice (v8 pattern, still works) | `state: { sorting }` + `onSortingChange` |
| External ownership | `atoms: { sorting: myAtom }` (atom wins over `state`; `table.reset()` won't reset it) |

**`useTable(options, selector?)`**, the second argument picks the reactive state slice. The DEFAULT subscribes to ALL registered state (v8-like breadth). `useTable(options, () => null)` + `Subscribe`/atoms = fine-grained rendering.

## Composition helpers

- **`createTableHook({ features, ...defaults })`** returns `{ useAppTable, createAppColumnHelper, appFeatures, useTableContext, useCellContext, useHeaderContext }`, the app-level factory pattern, pre-bound to the feature set. This is the BudTags plan's Phase 1 Option B.
- `tableOptions()`, typed reusable partial option objects.
- `columnHelper.columns([...])`, preserves per-column `TValue` inference.
- `<FlexRender cell={cell} />` / `<table.FlexRender>`, preferred component form; `flexRender(def, ctx)` still supported.
- Typing: prefer inference via `typeof features`; meta can be typed per-table with `tableMeta`/`columnMeta`/`filterMeta` slots via `metaHelper<T>()`, or keep global `declare module` augmentation with `TFeatures` added as the first generic. Registry slot keys become the valid string names in column defs (no more `declare module` for custom filterFns).

## Packaging

ESM-only (`"type": "module"`, no CJS), TS target ES2022, no shipped source maps. Subpaths: `.`, `./legacy`, `./flex-render`, `./static-functions`, `./experimental-worker-plugin`. React peer: `>=18`. Devtools ship stable: `@tanstack/react-table-devtools`.

## New capabilities (not in v8)

Cell selection (`cellSelectionFeature`: rectangular ranges, drag, shift-extend; `CellSelectionState`), cell spanning (`cellSpanningFeature`, span-aware selection), worker row models (experimental), `Infinity` page size + `getCanLastPage` (9.1.0), `table.getMaxSubRowDepth()`, `row.getDisplayIndex()`. Announced perf (verify locally before quoting): 86% less retained heap at 1M rows, sort 1.6× / filter 1.5× / core row model 3.9× faster.

## First-party skills ship inside the package (prefer them once v9 is installed)

The v9 packages embed version-pinned agent skills (docs: "Agent Skills / TanStack Intent"):

- `node_modules/@tanstack/table-core/skills/`, per-feature skills + **`migrate-v8-to-v9`** (complete breaking-change inventory + audit checklist, stamped with the installed version).
- `node_modules/@tanstack/react-table/skills/`: `getting-started`, `migrate-v8-to-v9`, `table-state`, `create-table-hook`, `with-tanstack-query`, `with-tanstack-virtual`.

Once v9 is in `package.json`, those files are the API authority for the installed version, read them before this skill's pattern files for any v9 API question, and verify ambiguous symbols against `node_modules/@tanstack/table-core/dist/*.d.ts`.

## BudTags-specific migration facts

- `getCenterVisibleLeafColumns()` survives: `TableExportButton.tsx` needs only the two left/right→start/end renames.
- `DataTable.tsx`'s controlled-state + `Updater` pattern survives; its `VisibilityState` import becomes `ColumnVisibilityState`; any `table.getState()` read must move to `table.state`.
- `TableHelpers.tsx` custom comparators rename `sortingFn`→`sortFn` and register in the `sortFns` slot of `tableFeatures({...})`.
- `createCheckboxColumn`'s header indeterminate logic must add `&& !getIsAllRowsSelected()`.
- The 10 TanStack-caused `"use no memo"` React Compiler opt-outs become removable (v9 exists because v8 broke the Compiler's rules).
