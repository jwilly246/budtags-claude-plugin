# TanStack Table v9 Stable: Verified Fact Sheet

> **Status (2026-10-07):** v9.0.0 went **stable 2026-08-04** (no RC; straight from beta.80). Latest is **9.2.6** (2026-10-04). `@tanstack/react-table` / `@tanstack/table-core` went 9.1.2 → 9.2.3 → 9.2.4 → 9.2.5 → 9.2.6 (9.2.0-9.2.2 were never published for these two; the 9.2 minor came from a devtools release). **There is no public API change between 9.1.2 and 9.2.6** (verified by a normalized `.d.ts` diff of the published tarballs). **BudTags `main` is still on v8.21.3**; the migration is planned in repo-root `TANSTACK_TABLE_V9_UPGRADE_PLAN.md`. Everything below was verified against the published 9.2.6 `.d.ts`/`.js`, the 9.2.6-tagged docs, and the bundled 9.2.6 skills.

## Which version am I writing for?

- **On `main` / any branch without the v9 migration:** write **v8** code. Use pattern files 01-24 as-is.
- **On the `tanstack-table-v9` migration branch (or after it merges):** write **v9** code per this file, and load the **bundled skills that ship inside the package** (see "Bundled skills" below) for API detail.

## Version floor

Pin exact, never a range. Floor and target: **9.2.6**.
- 9.1.1: `getSortedRowModel().flatRows` parent-first again (v8 parity).
- 9.1.2: removed a class of controlled-state render loops (auto-reset firing a semantically identical value after a `data` reference change; the controlled-wrapper + React Query refetch shape BudTags uses).
- 9.2.3: `getFilteredRowModel().flatRows` parent-first in both filter modes (v8 parity); `columnFiltersMeta` kept on cloned rows; grouped/worker flatRows preorder.
- 9.2.4: worker row-model fix (experimental plugin only). 9.2.5: TanStack Store patch deps (`@tanstack/react-store` ^0.11.2). 9.2.6: bundled skills restructured (no runtime change).
- Devtools: `@tanstack/react-table-devtools@9.2.5` (no 9.2.6) with peer **`@tanstack/react-devtools >=0.10.0`**, which BudTags does not install today. Dev-only.
- 9.2.7 exists for Vue/Solid only (deprecates `table.Subscribe` there). **React keeps `table.Subscribe`.**

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

- `useReactTable` → **`useTable`**; `features` is required. Define `features` at module scope.
- The **core row model is automatic**, no `getCoreRowModel()` (custom core only via a `coreRowModel` slot).
- `stockFeatures` = all-features shortcut (audit aid, not the production target). `useLegacyTable` at `@tanstack/react-table/legacy` = deprecated, React-only v8-shaped bridge; can exceed the v8 bundle.
- Feature prerequisites: `columnResizingFeature` requires `columnSizingFeature`; `globalFilteringFeature` requires `columnFilteringFeature`; `aggregationFns` requires `rowAggregationFeature`; every slot requires its feature.
- Under `manualSorting`/`manualFiltering` the registered row model is bypassed (`table_getSortedRowModel` returns the pre-sorted model), so registering the slot unconditionally is fine.

**Stock features:** `cellSelectionFeature` (new), `cellSpanningFeature` (new), `columnFacetingFeature`, `columnFilteringFeature`, `columnGroupingFeature`, `columnOrderingFeature`, `columnPinningFeature`, `columnResizingFeature`, `columnSizingFeature`, `columnVisibilityFeature`, `globalFilteringFeature`, `rowAggregationFeature`, `rowExpandingFeature`, `rowPaginationFeature`, `rowPinningFeature`, `rowSelectionFeature`, `rowSortingFeature`. Experimental `workerRowModelsFeature` via `@tanstack/react-table/experimental-worker-plugin`.

**Row-model slots** (all no-arg factories): `filteredRowModel`, `sortedRowModel`, `paginatedRowModel`, `expandedRowModel`, `groupedRowModel`, `facetedRowModel`, `facetedUniqueValues`, `facetedMinMaxValues`; custom core via `coreRowModel`.

## `'auto'` fns resolve ONLY registered names (silent failure mode)

A registry slot's keys are the valid string names, and `'auto'` (the default `filterFn`/`sortFn`) only resolves registered functions:
- Unregistered auto **filter** fn → `column.getFilterFn()` returns `undefined` → the filtered row model **skips that column's filter** (rows stay unfiltered; only a dev-mode `console.warn`).
- Unregistered auto **sort** fn → falls back (`alphanumeric` → `text` → `basic`).

If columns rely on `'auto'` (BudTags: every non-custom column; zero string-named fns in the repo), register everything the resolvers can return:

```ts
filterFns: {
  includesString: filterFn_includesString, inNumberRange: filterFn_inNumberRange,
  equals: filterFn_equals, arrIncludes: filterFn_arrIncludes,
  inDateRange: filterFn_inDateRange, weakEquals: filterFn_weakEquals,
},
sortFns: { alphanumeric: sortFn_alphanumeric, text: sortFn_text, datetime: sortFn_datetime },
```

Functions passed directly on a column (`filterFn: (row, id, value) => ...`, `sortFn: myComparator`) need no registration.

**Auto resolution differs from v8 8.21.3 (compile-silent):**

| | v8 8.21.3 | v9 |
|---|---|---|
| Auto filter sample | first row only | first non-null value across core rows |
| Null first value, string column | `weakEquals` (exact) | `includesString` (substring, case-insensitive) |
| Array value | `equals` (object branch ran first) | `arrIncludes` |
| Date value | `equals` | `inDateRange` |
| Auto sort sample | `flatRows.slice(10)` (skips the first 10 rows; 10 rows or fewer always `basic`) | `flatRows.slice(0, 10)` |

## Complete rename map

| v8 | v9 |
|----|----|
| `useReactTable(options)` | `useTable({ ...options, features })` |
| `sortingFn` / `sortingFns` / `SortingFn` / `SortingFns` | `sortFn` / `sortFns` / `SortFn` / `SortFns` |
| `column.getSortingFn()` / `getAutoSortingFn()` | `column.getSortFn()` / `getAutoSortFn()` |
| `columnPinning.left` / `.right` (state, args, comparisons) | `.start` / `.end` |
| `table.getLeft*()` / `getRight*()`, `row.getLeft/RightVisibleCells()` (every pinning family incl. header groups, footer groups, flat/leaf headers, leaf columns, total size) | `getStart*()` / `getEnd*()` |
| `getCenter*()` getters | **UNCHANGED** (only left/right renamed) |
| table option `enablePinning` | `enableColumnPinning` + `enableRowPinning` (column-def `enablePinning` remains) |
| `columnSizingInfo` state / `setColumnSizingInfo` / `onColumnSizingInfoChange` | `columnResizing` / `setColumnResizing` / `onColumnResizingChange` |
| `VisibilityState` type | **`ColumnVisibilityState`** |
| `table.getState()` | REMOVED → `table.state` / `table.store.state` / `table.atoms.<slice>.get()` |
| top-level `onStateChange` | REMOVED → per-slice `on*Change` or `table.store.subscribe()` |
| `row._getAllCellsByColumnId()` | `row.getAllCellsByColumnId()` |
| `table._getPinnedRows()` | `getTopRows()` / `getCenterRows()` / `getBottomRows()` |
| `table._getFaceted*()` | public `getFaceted*()` on column/table |
| `createColumnHelper<TData>()` | `createColumnHelper<typeof features, TData>()` |
| `ColumnDef<TData, TValue>` (and `Table`/`Row`/`Cell`/`Column`) | gain a leading `TFeatures` generic |
| `column.getAggregationFn()` | `column.getAggregationFns()` (plural); custom fns via `constructAggregationFn({ aggregate, merge? })` |
| `AggregationFn` / `CreatedAggregationFn` types | `AggregationFnDef` |
| global `FilterFns`/`SortFns`/`AggregationFns`/`FilterMeta` augmentation | registry slots (`filterFns`, `sortFns`, `aggregationFns`) + `filterMeta: metaHelper<T>()` |

`SortingState`, `ColumnFiltersState`, `RowSelectionState`, `PaginationState`, `ExpandedState`, `Updater`, `flexRender` keep their names. `CellSelectionState` is new.

## Behavior changes (compile silently, break at runtime)

1. **`getIsSomeRowsSelected()` AND `getIsSomePageRowsSelected()` mean "at least one"** and stay `true` when all are selected (v8 meant "some but not all"). Indeterminate = `getIsSomeRowsSelected() && !getIsAllRowsSelected()`; page checkbox = `getIsSomePageRowsSelected() && !getIsAllPageRowsSelected()`.
2. **`row.getToggleSelectedHandler()` does inclusive Shift-range selection by default.** Gated by `enableRowRangeSelection` (default `true`) and `isRowRangeSelectionEvent` (default `event.shiftKey || event.nativeEvent?.shiftKey`). Anchor = the last row toggled *through the handler*. The clicked checkbox's checked value applies to the whole range (it can deselect). Range follows display order (filter/sort/expansion); with manual pagination only loaded rows participate. `getToggleSelectedHandler({ selectChildren: false })` limits parents. **Direct `row.toggleSelected()` is unchanged.** Opt out: `enableRowRangeSelection: false`.
3. **Instance methods live on shared prototypes.** Destructuring, spreading, bare callbacks (`rows.map(row.getVisibleCells)`), `Object.keys`, `JSON.stringify` on rows/cells/columns/headers lose the methods; always call `row.getValue('x')` on the instance. Table-instance methods are exempt.
4. **`RowData` must be a record or array** (`Record<string, any> | Array<any>`; was `unknown`).
5. Pinning is *logical* (`start`/`end`); pair with logical CSS (`inset-inline-start`, Tailwind 4 `start-*`/`end-*`). `columnResizeDirection` stays `'ltr' | 'rtl'`.
6. **Auto filter/sort resolution changed** (table above) and only resolves registered names.

## State model (TanStack Store underneath)

| Need | Surface |
|------|---------|
| Reactive read in the component that owns `useTable` | `table.state` (shape = the `useTable` selector) |
| One-off snapshot (event handlers) | `table.store.state` / `table.atoms.<slice>.get()` (NOT subscriptions) |
| Narrowest subscription | `useSelector(table.atoms.<slice>)` from `@tanstack/react-store` |
| Render-prop subscription | `<table.Subscribe selector={s => s.sorting}>{sorting => ...}</table.Subscribe>`; standalone `<Subscribe source={...} selector={...}>` in cell/header contexts |
| Controlled slice (v8 pattern, still works) | `state: { sorting }` + `onSortingChange` (supply both) |
| External ownership | `atoms: { sorting: myAtom }` (atom wins over `state`; `table.reset()` won't reset it) |

**`useTable(options, selector?)`**: the DEFAULT selector subscribes to ALL registered state, and the React-facing `table` gets a new reference on every selected change. `useTable(options, () => null)` + `Subscribe`/atoms = fine-grained rendering. Start with the default; narrow only after measuring.

## React Compiler (official guide, 2026-08-16)

- v9 is the first Table version the React Compiler can compile: components that call `useTable` need no directive, and compiled components usually don't need `useMemo`/`useCallback` just to stabilize `data`/`columns` (stable references still matter for row-model rebuilds and auto-resets; keep existing memos unless you know why they exist).
- **The exception that matters:** the core `table` (`row.table`, `cell.table`, render-context `table`) and every `row`/`cell`/`column`/`header` object keep the same reference across state changes. A compiled child whose props are only those objects can be skipped, so `row.getIsSelected()`, `row.getIsExpanded()`, `column.getIsSorted()`, `column.getIsPinned()`, `column.getFilterValue()`, `cell.getValue()` go stale. `cell.getContext()` is memoized on `[cell]`, so `flexRender(def.cell, cell.getContext())` hands a cell component identical props.
- **Fix:** put `Subscribe` **inside** the child that reads the state, and render from the selected value, or pass the selected value as a changing prop. An outer `Subscribe` that ignores its value, or `useSelector` called only to force a render, does NOT fix it.

```tsx
import { Subscribe } from '@tanstack/react-table'

function SelectionCell({ row }: { row: Row<typeof features, Person> }) {
  return (
    <Subscribe source={row.table.atoms.rowSelection} selector={(sel) => sel[row.id]}>
      {(isSelected) => (
        <input type="checkbox" checked={!!isSelected} onChange={row.getToggleSelectedHandler()} />
      )}
    </Subscribe>
  )
}
```

- Multiple slices: `source={table.store}` + a selector returning every slice that can change the output (for `getRowModel()`: filters, sorting, grouping, expansion, pagination as registered).
- **Data-only changes are not in the store** (open issue #6601): a component that holds only a stable `table` and reads `table.getRowModel()` will not re-render when `data` is replaced (React Query refetch). Keep the row loop in the component that owns `useTable`, or pass `data` down.
- Compatibility is contested upstream (open issue #6577: unrelated hooks can change compiler decisions). Remove `"use no memo"` per file, with an interaction test run under the compiler, and keep a revert path.
- TanStack's benchmark: compiler on cuts unrelated-parent re-renders ~86% and broad-owner row selection ~68%; sort/paginate/replace-data barely move. Don't adopt the compiler *for* tables; adopt it for the app and make tables compatible.

## Composition helpers

- **`createTableHook({ features, ...defaults })`** returns `{ useAppTable, createAppColumnHelper, appFeatures, useTableContext, useCellContext, useHeaderContext }` plus `table.AppTable`/`AppCell`/`AppHeader` wrappers. Create it at **module scope**, keep its import graph **acyclic** (a component registry that imports back from the factory module breaks Vite HMR, #6348). Default contexts are module-scoped; nested *different* setups need `createTableHookContexts()`. `table.AppTable` takes plain children without a selector; function children only with `selector`.
- `tableOptions()`: typed reusable partial option objects.
- `columnHelper.columns([...])`: preserves per-column `TValue` inference.
- `<FlexRender cell={cell} />` / `<table.FlexRender>`: preferred component form; `flexRender(def, ctx)` still supported.
- Typing: prefer inference; use `typeof features` only at explicit boundaries. Meta: keep global `declare module '@tanstack/react-table'` augmentation with `TFeatures` as the first generic (9.2.6 declares `ColumnMeta<in out TFeatures extends TableFeatures, in out TData extends RowData, TValue extends CellData = CellData>` and `TableMeta<in out TFeatures ..., in out TData ...>`; match the parameter list), or use per-table `tableMeta`/`columnMeta`/`filterMeta` slots via `metaHelper<T>()`. `@tanstack/react-table` re-exports all of `@tanstack/table-core` and also exports the type names `AppColumnHelper`, `AppReactTable`, `AppCellContext`, ... for `createTableHook`; don't reuse those names for app aliases.

## Packaging

ESM-only (`"type": "module"`, no CJS/UMD), TS target ES2022, no shipped `src`/source maps. Subpaths: `.`, `./legacy`, `./flex-render`, `./static-functions`, `./experimental-worker-plugin`. React peer: `>=18`; depends on `@tanstack/react-store@^0.11.2`. Node engine `>=20`.

## New capabilities (not in v8)

Cell selection (`cellSelectionFeature`: rectangular ranges, drag, Shift-extend, disjoint ranges), cell spanning (`cellSpanningFeature`), worker row models (experimental), `Infinity` page size + `getCanLastPage` (9.1.0), `table.getMaxSubRowDepth()`, `row.getDisplayIndex()`, root totals without grouping (`rowAggregationFeature`). Announced perf (verify locally before quoting): 86% less retained heap at 1M rows, sort 1.6× / filter 1.5× / core row model 3.9× faster.

## Bundled skills (9.2.6 layout; prefer them once v9 is installed)

9.2.6 (#6611) restructured the bundled skills into **8 entry points** with on-demand `references/`. Load with `npx @tanstack/intent@latest load <package>#<skill>` (resolves relative links to the installed package) or read the files directly:

| Package | Entry point | References |
|---|---|---|
| `@tanstack/table-core` | `skills/core/SKILL.md` | `references/typescript.md`, `api-not-found.md`, `rows.md` |
| | `skills/table-features/SKILL.md` | `references/<feature>.md` for every feature (`sorting`, `row-selection`, `column-filtering`, `column-faceting`, `column-visibility`, `column-pinning`, `column-sizing`, `column-resizing`, `pagination`, `expanding`, `grouping`, `aggregation`, `global-filtering`, `row-pinning`, `column-ordering`, `cell-selection`, `cell-spanning`, `client-vs-server`) |
| | `skills/table-state/SKILL.md` | |
| | `skills/custom-features/SKILL.md` | `references/plugin-example.md` |
| | `skills/migrate-v8-to-v9/SKILL.md` (audit checklist) | `references/architecture.md`, `state.md`, `feature-apis.md`, `typescript.md` |
| `@tanstack/react-table` | `skills/getting-started/SKILL.md` | `references/create-table-hook.md`, `with-tanstack-query.md`, `with-tanstack-virtual.md` |
| | `skills/table-state/SKILL.md` | `references/reactivity.md` (React Compiler boundaries) |
| | `skills/migrate-v8-to-v9/SKILL.md` | `references/adapter-migration.md` |

**Retired paths (9.1.x layout, gone in 9.2.6):** `react-table/skills/create-table-hook/`, `react-table/skills/with-tanstack-query/`, `react-table/skills/with-tanstack-virtual/`, every per-feature `table-core/skills/<feature>/SKILL.md`, `table-core/skills/typescript/`, `table-core/skills/api-not-found/`.

Once v9 is in `package.json`, those files (stamped `library_version: '9.2.6'`) are the API authority for the installed version; verify ambiguous symbols against `node_modules/@tanstack/table-core/dist/**/*.d.ts` and `node_modules/@tanstack/react-table/dist/*.d.ts`.

## BudTags-specific migration facts (re-measured 2026-10-07)

- **Floor/pin 9.2.6**; cut the v9 branch only after `chore/dependency-upgrades` (React 19.3, TS 7, Oxlint, Vitest 5) merges.
- `TableExportButton.tsx:144,146` need the two left/right → start/end renames; `getCenterVisibleLeafColumns()` (`:145`) survives; register `columnPinningFeature` or the segment getters don't exist.
- `DataTable.tsx`'s controlled-state + `Updater` pattern survives; `VisibilityState` → `ColumnVisibilityState`. `table.getState()` sites: `TableHelpers.tsx:155,161` (handler → `table.atoms.rowSelection.get()`), `TableInventoryComponents.tsx:343`, `BulkRestoreControls.tsx:45` (→ `table.state.rowSelection`).
- **Register every auto fn** (list above): BudTags has zero string-named fns, so missing registrations silently disable filters.
- `TableHelpers.tsx` custom comparators: column option `sortingFn` → `sortFn` (31 call sites / 7 files); they are passed as functions, no registration needed.
- `createCheckboxColumn` (`TableHelpers.tsx:127`) uses the **Page** predicates: indeterminate → `getIsSomePageRowsSelected() && !getIsAllPageRowsSelected()`. **BudTags decision (2026-10-07): adopt the built-in range.** In v8 its Shift-click path intercepts in the capture phase and lacks an anchor-missing guard (`lastIdx === -1` → `rows[-1]` throws). In v9, delete that intercept and route every row checkbox (this column, `DataTable.tsx:1575` mobile card, `StorefrontLinksTable.tsx:150`) through `row.getToggleSelectedHandler()`: anchor = last clicked row, ranges span pages, range deselect, and an unresolvable anchor falls back to a plain toggle. Keep DataTable's own row-click Shift-range (`row.toggleSelected()`): the built-in handler reads `event.target.checked`, so it cannot serve whole-row clicks.
- `"use no memo"`: 11 TanStack-caused directives (plus 2 unrelated that stay: `useAreaSelection.ts`, `ReservedInlineActions.test.tsx`). **Removing them is NOT automatic:** `TableFilter` (stable `column`) and `createCheckboxColumn` (render-context `row`/`table`) need `Subscribe` boundaries first; `ColumnVisibilityToggle`, `BulkRestoreControls`, `TableExportButton`, and `customToolbarSlot` consumers are safe only while DataTable keeps the default `useTable` selector.
- Types: `DataTableColumnDef<T>` (`Types/types.tsx:2113`, 66 files) becomes `ColumnDef<typeof appTableFeatures, T, any>` in one place; ~85 files import `Row`/`Table`/`Column`/`ColumnHelper` and move to app aliases. Global meta augmentation lives in `app.d.ts:35-60`.
- Saved-filter chip column (`TablePackages.tsx:1171-1187`): v9's filtered row model never consults visibility, so a filter on a hidden column still runs.

## Sources

- Releases/CHANGELOG: https://github.com/TanStack/table/releases , https://github.com/TanStack/table/blob/main/packages/table-core/CHANGELOG.md
- React Compiler guide: https://tanstack.com/table/latest/docs/framework/react/guide/react-compiler
- Migration guide: https://tanstack.com/table/latest/docs/framework/react/guide/migrating
- Row selection (Shift range): https://tanstack.com/table/latest/docs/framework/react/guide/row-selection
- Agent Skills: https://tanstack.com/table/latest/docs/agent-skills ; restructure PR https://github.com/TanStack/table/pull/6611
- Open issues: https://github.com/TanStack/table/issues/6601 , https://github.com/TanStack/table/issues/6577
