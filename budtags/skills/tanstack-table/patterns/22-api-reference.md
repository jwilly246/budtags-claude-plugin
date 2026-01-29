# Pattern 22: API Quick Reference

## Table Instance Methods

### Row Methods
```typescript
table.getRowModel()                    // Current visible rows
table.getPreFilteredRowModel()         // Before filtering
table.getPreGroupedRowModel()          // Before grouping
table.getPrePaginationRowModel()       // All rows (before pagination)
table.getSelectedRowModel()            // Selected rows
table.getFilteredSelectedRowModel()    // Selected + filtered
table.getGroupedSelectedRowModel()     // Selected + grouped

table.getTopRows()                     // Top pinned rows
table.getCenterRows()                  // Unpinned rows
table.getBottomRows()                  // Bottom pinned rows
```

### Column Methods
```typescript
table.getAllColumns()                  // All columns
table.getAllLeafColumns()              // Leaf columns (no groups)
table.getVisibleLeafColumns()          // Visible leaf columns
table.getLeftLeafColumns()             // Left pinned columns
table.getCenterLeafColumns()           // Unpinned columns
table.getRightLeafColumns()            // Right pinned columns

table.getColumn(id)                    // Get specific column
```

### Header Methods
```typescript
table.getHeaderGroups()                // All header groups
table.getLeftHeaderGroups()            // Left pinned headers
table.getCenterHeaderGroups()          // Unpinned headers
table.getRightHeaderGroups()           // Right pinned headers
table.getFooterGroups()                // Footer groups
table.getFlatHeaders()                 // Flattened headers
table.getLeafHeaders()                 // Leaf headers
```

### State Methods
```typescript
table.getState()                       // Current state
table.setState(newState)               // Update state
table.resetRowSelection()              // Reset selection
table.resetColumnFilters()             // Reset filters
table.resetSorting()                   // Reset sorting
table.resetPagination()                // Reset pagination
table.resetColumnVisibility()          // Reset visibility
table.resetColumnOrder()               // Reset order
table.resetColumnSizing()              // Reset sizing
table.resetColumnPinning()             // Reset pinning
table.resetRowPinning()                // Reset row pinning
table.resetGrouping()                  // Reset grouping
table.resetExpanded()                  // Reset expansion
```

### Pagination Methods
```typescript
table.firstPage()                      // Go to first page
table.previousPage()                   // Go to previous page
table.nextPage()                       // Go to next page
table.lastPage()                       // Go to last page
table.setPageIndex(index)              // Go to specific page
table.setPageSize(size)                // Change page size
table.getCanPreviousPage()             // boolean
table.getCanNextPage()                 // boolean
table.getPageCount()                   // Total pages
table.getRowCount()                    // Total rows
```

### Size Methods
```typescript
table.getTotalSize()                   // Total width
table.getLeftTotalSize()               // Left pinned width
table.getCenterTotalSize()             // Unpinned width
table.getRightTotalSize()              // Right pinned width
```

### Selection Methods
```typescript
table.toggleAllRowsSelected(value?)    // Select/deselect all
table.toggleAllPageRowsSelected(value?) // Select/deselect page
table.getIsAllRowsSelected()           // boolean
table.getIsSomeRowsSelected()          // boolean
table.getIsAllPageRowsSelected()       // boolean
table.getIsSomePageRowsSelected()      // boolean
table.getToggleAllRowsSelectedHandler() // Handler
table.getToggleAllPageRowsSelectedHandler() // Handler
```

## Row Instance Methods

### Basic
```typescript
row.id                                 // Row ID
row.index                              // Row index
row.depth                              // Nesting depth
row.original                           // Original data
row.getValue(columnId)                 // Get cell value
row.renderValue(columnId)              // Get rendered value
```

### Cells
```typescript
row.getAllCells()                      // All cells
row.getVisibleCells()                  // Visible cells
row.getLeftVisibleCells()              // Left pinned cells
row.getCenterVisibleCells()            // Unpinned cells
row.getRightVisibleCells()             // Right pinned cells
```

### Selection
```typescript
row.getIsSelected()                    // boolean
row.getIsSomeSelected()                // boolean (for parent rows)
row.getCanSelect()                     // boolean
row.toggleSelected(value?)             // Toggle selection
row.getToggleSelectedHandler()         // Handler
```

### Expansion
```typescript
row.getCanExpand()                     // boolean
row.getIsExpanded()                    // boolean
row.toggleExpanded(value?)             // Toggle expansion
row.getToggleExpandedHandler()         // Handler
row.getParentRow()                     // Parent row
row.subRows                            // Child rows
```

### Pinning
```typescript
row.getCanPin()                        // boolean
row.getIsPinned()                      // 'top' | 'bottom' | false
row.pin(position)                      // Pin row
```

## Column Instance Methods

### Basic
```typescript
column.id                              // Column ID
column.getIndex()                      // Column index
column.getSize()                       // Column width
column.columnDef                       // Column definition
```

### Visibility
```typescript
column.getCanHide()                    // boolean
column.getIsVisible()                  // boolean
column.toggleVisibility(value?)        // Toggle visibility
column.getToggleVisibilityHandler()    // Handler
```

### Sorting
```typescript
column.getCanSort()                    // boolean
column.getIsSorted()                   // false | 'asc' | 'desc'
column.getSortIndex()                  // number
column.toggleSorting(desc?)            // Toggle sort
column.getToggleSortingHandler()       // Handler
column.clearSorting()                  // Clear sort
column.getAutoSortDir()                // 'asc' | 'desc'
column.getAutoSortingFn()              // Function
column.getSortingFn()                  // Function
```

### Filtering
```typescript
column.getCanFilter()                  // boolean
column.getIsFiltered()                 // boolean
column.getFilterIndex()                // number
column.getFilterValue()                // Current filter
column.setFilterValue(value)           // Set filter
column.getFacetedRowModel()            // Faceted rows
column.getFacetedUniqueValues()        // Map<value, count>
column.getFacetedMinMaxValues()        // [min, max]
```

### Grouping
```typescript
column.getCanGroup()                   // boolean
column.getIsGrouped()                  // boolean
column.getGroupedIndex()               // number
column.getToggleGroupingHandler()      // Handler
```

### Pinning
```typescript
column.getCanPin()                     // boolean
column.getIsPinned()                   // 'left' | 'right' | false
column.pin(position)                   // Pin column
column.getStart(position?)             // CSS left value
column.getAfter(position?)             // CSS right value
column.getIsLastColumn(position)       // boolean
column.getIsFirstColumn(position)      // boolean
```

### Resizing
```typescript
column.getCanResize()                  // boolean
column.getIsResizing()                 // boolean
column.resetSize()                     // Reset to initial
```

## Cell Instance Methods

```typescript
cell.id                                // Cell ID
cell.getValue()                        // Cell value
cell.renderValue()                     // Rendered value
cell.row                               // Parent row
cell.column                            // Parent column
cell.getContext()                      // Cell context

// Grouping
cell.getIsGrouped()                    // boolean
cell.getIsAggregated()                 // boolean
cell.getIsPlaceholder()                // boolean
```

## Header Instance Methods

```typescript
header.id                              // Header ID
header.index                           // Header index
header.depth                           // Header depth
header.column                          // Parent column
header.colSpan                         // Column span
header.rowSpan                         // Row span
header.isPlaceholder                   // boolean
header.getSize()                       // Header width
header.getStart(position?)             // CSS left value
header.getContext()                    // Header context
header.getResizeHandler()              // Resize handler
```

## State Types

```typescript
type SortingState = ColumnSort[]
type ColumnSort = { id: string; desc: boolean }

type ColumnFiltersState = ColumnFilter[]
type ColumnFilter = { id: string; value: unknown }

type VisibilityState = Record<string, boolean>

type ColumnOrderState = string[]

type ColumnPinningState = { left?: string[]; right?: string[] }

type RowPinningState = { top?: string[]; bottom?: string[] }

type ColumnSizingState = Record<string, number>

type ExpandedState = Record<string, boolean> | true

type GroupingState = string[]

type PaginationState = { pageIndex: number; pageSize: number }

type RowSelectionState = Record<string, boolean>
```

## Common Patterns

### Get Selected Row Data
```typescript
const selectedPackages = table
  .getSelectedRowModel()
  .rows.map(row => row.original)
```

### Get Filtered Row Count
```typescript
const count = table.getRowModel().rows.length
const total = table.getPreFilteredRowModel().rows.length
```

### Check if Any Filters Active
```typescript
const hasFilters = table.getState().columnFilters.length > 0
```

### Get Current Sort
```typescript
const sorting = table.getState().sorting
// [{ id: 'ProductName', desc: false }]
```

### Reset All State
```typescript
table.resetSorting()
table.resetColumnFilters()
table.resetPagination()
table.resetRowSelection()
table.resetColumnVisibility()
```

## Next Steps
- **Full API Docs** → tanstack.com/table/latest/docs/api
- **TypeScript Types** → Import from '@tanstack/react-table'
- **Examples** → tanstack.com/table/latest/docs/examples
