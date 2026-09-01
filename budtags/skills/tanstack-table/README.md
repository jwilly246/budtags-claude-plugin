# TanStack Table Skill

## What's Included

This skill provides comprehensive documentation for **TanStack Table**, sourced from the official documentation at https://tanstack.com/table/latest

**Version state (2026-08-12):** pattern files 01–24 document **v8**, the version installed on BudTags `main` (`^8.21.3`). **v9 went stable 2026-08-04** (latest 9.1.2); `patterns/25-v9-stable.md` is the verified v9 fact sheet, and the repo-root `TANSTACK_TABLE_V9_UPGRADE_PLAN.md` in BudTags tracks the migration. v9 packages ship their own version-pinned agent skills at `node_modules/@tanstack/{react-table,table-core}/skills/`, prefer those for v9 API detail once v9 is installed.

**Coverage:**
- Complete API reference for all table features
- React-specific implementation patterns
- BudTags/BobLink integration examples
- Progressive disclosure documentation (load only what you need)
- 24 pattern files covering every aspect of table functionality

## Installation

TanStack Table is already installed in BudTags:

```bash
npm install @tanstack/react-table
```

**Current version in BudTags:** Check `package.json`

**Peer Dependencies:**
- React 18+
- TypeScript 4.7+ (recommended)

## File Structure

```
tanstack-table/
├── SKILL.md                           # Main skill entry point
├── README.md                          # This file
└── patterns/                          # Progressive disclosure docs
    ├── 01-installation-setup.md       # Installation & basic setup
    ├── 02-core-concepts.md            # Headless UI, table instance
    ├── 03-column-definitions.md       # Column types & helpers
    ├── 04-table-instance.md           # Table creation & options
    ├── 05-row-models.md               # Row processing pipeline
    ├── 06-rendering.md                # Headers, cells, flexRender
    ├── 07-sorting.md                  # Sorting features
    ├── 08-filtering.md                # Column & global filters
    ├── 09-pagination.md               # Pagination setup
    ├── 10-row-selection.md            # Selection state
    ├── 11-column-visibility.md        # Show/hide columns
    ├── 12-column-ordering.md          # Reorder columns
    ├── 13-column-sizing.md            # Resizable columns
    ├── 14-column-pinning.md           # Sticky columns
    ├── 15-row-expansion.md            # Expandable rows
    ├── 16-row-grouping-aggregation.md # Group rows + aggregate functions
    ├── 17-row-pinning.md              # Pin rows
    ├── 18-virtualization.md           # Virtual scrolling
    ├── 19-faceted-filtering.md        # Faceted search
    ├── 20-typescript.md               # Type safety
    ├── 21-performance.md              # Optimization
    ├── 22-api-reference.md            # Complete API (v8)
    ├── 23-custom-features.md          # Plugin system
    ├── 24-budtags-integration.md      # BudTags DataTable integration
    └── 25-v9-stable.md                # v9 stable verified fact sheet (2026-08-12)
```

## Quick Start

### Basic Table

```typescript
import { useReactTable, getCoreRowModel, createColumnHelper } from '@tanstack/react-table'

type Data = { id: number; name: string }

const columnHelper = createColumnHelper<Data>()
const columns = [
  columnHelper.accessor('id', { header: 'ID' }),
  columnHelper.accessor('name', { header: 'Name' }),
]

function MyTable({ data }: { data: Data[] }) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  // Render table...
}
```

### With Common Features

```typescript
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  state: {
    sorting,
    columnFilters,
    pagination,
  },
  onSortingChange: setSorting,
  onColumnFiltersChange: setColumnFilters,
  onPaginationChange: setPagination,
})
```

## Usage in BudTags

**Current Implementation Files:**
- `resources/js/Components/DataTable.tsx` - Generic data table component
- `resources/js/Components/TableHelpers.tsx` - Reusable column helpers
- `resources/js/Components/TablePackages.tsx` - Metrc packages table
- `resources/js/Components/TableOrdersLeaflink.tsx` - LeafLink orders table
- Multiple page-specific table components

**Common Patterns:**
- Checkbox columns for row selection
- Filter buttons for quick filtering
- Date sorting helpers
- Column visibility toggles

## When to Use This Skill

Activate this skill when you need to:

- Create a new data table
- Add sorting, filtering, or pagination
- Implement row selection
- Customize column behavior (visibility, sizing, pinning)
- Optimize table performance for large datasets
- Troubleshoot table issues
- Add advanced features (grouping, expansion, virtualization)

## Progressive Loading

The skill uses progressive disclosure - load only the pattern files you need:

**For Basic Tables:** Load patterns 01-06
**For Sorting:** Add pattern 07
**For Filtering:** Add patterns 08, 19
**For Selection:** Add pattern 10
**For Large Data:** Add pattern 18
**For v9 / migration:** Load pattern 25 first
**For Everything:** Load all 25 patterns (not recommended - high token usage)

## Key Features Covered

### Core Features
- ✅ Headless UI architecture
- ✅ Column definitions (accessor, display, grouping)
- ✅ Table instance creation
- ✅ Row models (core, filtered, sorted, grouped, paginated)
- ✅ Rendering (headers, cells, rows, flexRender)

### Table Features
- ✅ Sorting (single, multi, custom sort functions)
- ✅ Filtering (column, global, faceted)
- ✅ Pagination (client-side, server-side)
- ✅ Row selection (single, multi, checkbox)
- ✅ Column visibility (show/hide)
- ✅ Column ordering (drag & drop)
- ✅ Column sizing (resizable)
- ✅ Column pinning (sticky left/right)
- ✅ Row expansion (nested data)
- ✅ Row grouping (group by column)
- ✅ Aggregation (sum, count, min, max, etc.)
- ✅ Row pinning (sticky top/bottom)
- ✅ Virtualization (large datasets)
- ✅ Custom features (plugin system)

### Developer Experience
- ✅ TypeScript support (full type safety)
- ✅ Performance optimization patterns
- ✅ Framework-agnostic core
- ✅ React adapter for state management
- ✅ Comprehensive API reference

## Official Documentation

This skill is based on the official TanStack Table documentation:

**Website:** https://tanstack.com/table/latest
**GitHub:** https://github.com/TanStack/table
**Version:** patterns 01-24 = v8; pattern 25 = v9 stable (9.1.2, verified 2026-08-12)

All content is sourced from official docs and adapted for progressive disclosure to optimize Claude Code token usage.

## Related Skills

- `tanstack-query` - Data fetching for table data
- `tanstack-form` - Form handling for table filters
- `verify-alignment` - BudTags coding standards

## Sharing This Skill

To share this skill with another Claude Code workspace:

1. Copy the entire `tanstack-table/` directory
2. Place it in `.claude/skills/` in the target workspace
3. The skill will auto-activate when table-related tasks are detected

## Contributing

This skill is maintained alongside the BudTags codebase. When TanStack Table is updated:

1. Review changelog at https://github.com/TanStack/table/releases
2. Update pattern files with new features
3. Update version number in README
4. Test with BudTags table implementations

## Support

For issues or questions:

- Check SKILL.md for quick patterns
- Load specific pattern files for detailed guidance
- Refer to official docs for latest updates
- Check BudTags components for real-world examples
