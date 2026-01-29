# Pattern 12: Column Ordering

## Column Order State

Column ordering controls the sequence in which columns appear beyond their definition order.

```typescript
type ColumnOrderState = string[] // Array of column IDs

// Example:
const columnOrder = ['select', 'Label', 'ProductName', 'Quantity', 'actions']
```

## Enabling Column Ordering

```typescript
const [columnOrder, setColumnOrder] = useState<ColumnOrderState>([])

const table = useReactTable({
  data,
  columns,
  state: { columnOrder },
  onColumnOrderChange: setColumnOrder,
  getCoreRowModel: getCoreRowModel(),
})
```

## Initial Column Order

```typescript
const table = useReactTable({
  data,
  columns,
  initialState: {
    columnOrder: ['select', 'ProductName', 'Label', 'Quantity'],
  },
  getCoreRowModel: getCoreRowModel(),
})
```

## Order Application Sequence

Column order is applied in this sequence:

1. **Column Pinning** - Splits columns into left, center, right sections
2. **Manual Ordering** - `columnOrder` state (only affects unpinned columns)
3. **Grouping** - If enabled with `groupedColumnMode` set to 'reorder' or 'remove'

## Reordering Columns

### Drag and Drop Utility

```typescript
function reorderColumn(
  draggedColumnId: string,
  targetColumnId: string,
  columnOrder: string[]
): string[] {
  const newOrder = [...columnOrder]

  const draggedIndex = newOrder.indexOf(draggedColumnId)
  const targetIndex = newOrder.indexOf(targetColumnId)

  // Remove dragged column
  newOrder.splice(draggedIndex, 1)

  // Insert at new position
  newOrder.splice(targetIndex, 0, draggedColumnId)

  return newOrder
}

// Usage
const handleDrop = (draggedId: string, targetId: string) => {
  setColumnOrder(oldOrder =>
    reorderColumn(draggedId, targetId, oldOrder)
  )
}
```

## Drag and Drop Implementation

### Using @dnd-kit (Recommended)

```typescript
import { DndContext, closestCenter, DragEndEvent } from '@dnd-kit/core'
import {
  SortableContext,
  horizontalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

function DraggableHeader({ header }: { header: Header<any, any> }) {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: header.column.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  return (
    <th ref={setNodeRef} style={style} {...attributes} {...listeners}>
      {flexRender(header.column.columnDef.header, header.getContext())}
    </th>
  )
}

function PackagesTable({ data }: { data: Package[] }) {
  const [columnOrder, setColumnOrder] = useState<ColumnOrderState>([])

  const table = useReactTable({
    data,
    columns,
    state: { columnOrder },
    onColumnOrderChange: setColumnOrder,
    getCoreRowModel: getCoreRowModel(),
  })

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (active && over && active.id !== over.id) {
      setColumnOrder(oldOrder => {
        const oldIndex = oldOrder.indexOf(active.id as string)
        const newIndex = oldOrder.indexOf(over.id as string)
        return arrayMove(oldOrder, oldIndex, newIndex)
      })
    }
  }

  return (
    <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <table>
        <thead>
          {table.getHeaderGroups().map(headerGroup => (
            <tr key={headerGroup.id}>
              <SortableContext
                items={headerGroup.headers.map(h => h.column.id)}
                strategy={horizontalListSortingStrategy}
              >
                {headerGroup.headers.map(header => (
                  <DraggableHeader key={header.id} header={header} />
                ))}
              </SortableContext>
            </tr>
          ))}
        </thead>
        <tbody>{/* ... */}</tbody>
      </table>
    </DndContext>
  )
}
```

### Using Native HTML Drag and Drop

```typescript
function DraggableHeader({ header }: { header: Header<any, any> }) {
  const [isDragging, setIsDragging] = useState(false)

  return (
    <th
      draggable
      onDragStart={e => {
        setIsDragging(true)
        e.dataTransfer.effectAllowed = 'move'
        e.dataTransfer.setData('text/html', header.column.id)
      }}
      onDragEnd={() => setIsDragging(false)}
      onDragOver={e => {
        e.preventDefault()
        e.dataTransfer.dropEffect = 'move'
      }}
      onDrop={e => {
        e.preventDefault()
        const draggedId = e.dataTransfer.getData('text/html')
        const targetId = header.column.id

        if (draggedId !== targetId) {
          table.setColumnOrder(oldOrder =>
            reorderColumn(draggedId, targetId, oldOrder)
          )
        }
      }}
      className={isDragging ? 'opacity-50' : 'cursor-move'}
    >
      {flexRender(header.column.columnDef.header, header.getContext())}
    </th>
  )
}
```

## Programmatic Column Ordering

### Set Specific Order

```typescript
// Set exact order
table.setColumnOrder(['select', 'ProductName', 'Quantity', 'Label'])

// Move column to start
const moveToStart = (columnId: string) => {
  table.setColumnOrder(oldOrder => {
    const filtered = oldOrder.filter(id => id !== columnId)
    return [columnId, ...filtered]
  })
}

// Move column to end
const moveToEnd = (columnId: string) => {
  table.setColumnOrder(oldOrder => {
    const filtered = oldOrder.filter(id => id !== columnId)
    return [...filtered, columnId]
  })
}
```

### Reset Column Order

```typescript
// Reset to default (definition order)
table.resetColumnOrder()

// Reset to initial state
table.resetColumnOrder(true)
```

## Column Ordering with Pinning

When using column pinning, `columnOrder` only affects unpinned (center) columns:

```typescript
const [columnOrder, setColumnOrder] = useState<ColumnOrderState>([])
const [columnPinning, setColumnPinning] = useState<ColumnPinningState>({
  left: ['select'],
  right: ['actions'],
})

const table = useReactTable({
  data,
  columns,
  state: {
    columnOrder,
    columnPinning,
  },
  onColumnOrderChange: setColumnOrder,
  onColumnPinningChange: setColumnPinning,
  getCoreRowModel: getCoreRowModel(),
})

// columnOrder affects: all columns EXCEPT 'select' and 'actions'
```

## Column Order Presets

```typescript
function ColumnOrderPresets({ table }: { table: Table<Package> }) {
  const defaultOrder = () => {
    table.resetColumnOrder(true)
  }

  const alphabeticalOrder = () => {
    const allColumns = table.getAllLeafColumns()
    const sorted = allColumns
      .map(col => col.id)
      .sort((a, b) => a.localeCompare(b))
    table.setColumnOrder(sorted)
  }

  const customOrder = () => {
    table.setColumnOrder([
      'select',
      'Label',
      'ProductName',
      'Quantity',
      'ReceivedDateTime',
      'actions',
    ])
  }

  return (
    <div className="flex gap-2">
      <button onClick={defaultOrder}>Default Order</button>
      <button onClick={alphabeticalOrder}>Alphabetical</button>
      <button onClick={customOrder}>Custom Order</button>
    </div>
  )
}
```

## Save/Load Column Order

```typescript
function PackagesTable({ data }: { data: Package[] }) {
  const [columnOrder, setColumnOrder] = useState<ColumnOrderState>(() => {
    const saved = localStorage.getItem('packageTableColumnOrder')
    return saved ? JSON.parse(saved) : []
  })

  useEffect(() => {
    if (columnOrder.length > 0) {
      localStorage.setItem(
        'packageTableColumnOrder',
        JSON.stringify(columnOrder)
      )
    }
  }, [columnOrder])

  const table = useReactTable({
    data,
    columns,
    state: { columnOrder },
    onColumnOrderChange: setColumnOrder,
    getCoreRowModel: getCoreRowModel(),
  })

  return <table>{/* ... */}</table>
}
```

## Column Ordering API Methods

### Table Methods

```typescript
// Set column order
table.setColumnOrder(['id1', 'id2', 'id3'])

// Reset column order
table.resetColumnOrder()
table.resetColumnOrder(true) // Reset to initial state

// Get state
table.getState().columnOrder
```

## Complete Example with Drag and Drop

```typescript
import { DndContext, closestCenter, DragEndEvent } from '@dnd-kit/core'
import {
  SortableContext,
  horizontalListSortingStrategy,
  useSortable,
  arrayMove,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

function DraggableHeader({ header }: { header: Header<Package, any> }) {
  const { attributes, isDragging, listeners, setNodeRef, transform } =
    useSortable({ id: header.column.id })

  const style = {
    opacity: isDragging ? 0.5 : 1,
    transform: CSS.Translate.toString(transform),
    transition: 'width transform 0.2s ease-in-out',
    cursor: 'move',
  }

  return (
    <th ref={setNodeRef} style={style}>
      <div {...attributes} {...listeners} className="flex items-center gap-2">
        <span className="text-gray-400">⋮⋮</span>
        {flexRender(header.column.columnDef.header, header.getContext())}
      </div>
    </th>
  )
}

function PackagesTable({ data }: { data: Package[] }) {
  const columns = useMemo(() => [
    columnHelper.accessor('Label', { header: 'Package Tag' }),
    columnHelper.accessor('ProductName', { header: 'Product' }),
    columnHelper.accessor('Quantity', { header: 'Quantity' }),
    columnHelper.accessor('ItemCategory', { header: 'Category' }),
  ], [])

  const [columnOrder, setColumnOrder] = useState<ColumnOrderState>(() =>
    columns.map(c => c.id!)
  )

  const table = useReactTable({
    data,
    columns,
    state: { columnOrder },
    onColumnOrderChange: setColumnOrder,
    getCoreRowModel: getCoreRowModel(),
  })

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event

    if (active && over && active.id !== over.id) {
      setColumnOrder(columnOrder => {
        const oldIndex = columnOrder.indexOf(active.id as string)
        const newIndex = columnOrder.indexOf(over.id as string)
        return arrayMove(columnOrder, oldIndex, newIndex)
      })
    }
  }

  return (
    <div>
      <button
        onClick={() => table.resetColumnOrder(true)}
        className="mb-4 text-blue-600"
      >
        Reset Column Order
      </button>

      <DndContext
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <table className="min-w-full">
          <thead>
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                <SortableContext
                  items={headerGroup.headers.map(h => h.column.id)}
                  strategy={horizontalListSortingStrategy}
                >
                  {headerGroup.headers.map(header => (
                    <DraggableHeader key={header.id} header={header} />
                  ))}
                </SortableContext>
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
      </DndContext>
    </div>
  )
}
```

## Recommended DnD Libraries

### @dnd-kit (Recommended)

**Pros:**
- Modern, modular, tree-shakeable
- Excellent React 18+ support
- Good TypeScript support
- Active maintenance
- Accessibility features

**Installation:**
```bash
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
```

### react-beautiful-dnd

**Pros:**
- Polished animations
- Great UX out of the box

**Cons:**
- Large bundle size
- No React 18 StrictMode support
- Not actively maintained

### Native HTML Drag and Drop

**Pros:**
- No dependencies
- Lightweight

**Cons:**
- More code to write
- Touch support requires extra work
- Less polished UX

## Common Mistakes

### ❌ Forgetting to Initialize columnOrder

```typescript
// ❌ Empty array won't work
const [columnOrder, setColumnOrder] = useState<ColumnOrderState>([])

// ✅ Initialize with column IDs
const [columnOrder, setColumnOrder] = useState<ColumnOrderState>(() =>
  columns.map(c => c.id!)
)
```

### ❌ Not Handling Column Pinning

```typescript
// ❌ columnOrder affects pinned columns (unexpected behavior)
const table = useReactTable({
  state: { columnOrder, columnPinning },
  // ...
})

// ✅ Understand that columnOrder only affects unpinned columns
```

## Type Definitions

```typescript
type ColumnOrderState = string[]

type ColumnOrderTableState = {
  columnOrder: ColumnOrderState
}

type ColumnOrderOptions = {
  onColumnOrderChange?: OnChangeFn<ColumnOrderState>
}
```

## Next Steps

- **Column Sizing** → See pattern 13
- **Column Pinning** → See pattern 14
- **Drag and Drop with @dnd-kit** → See examples
- **Persist User Preferences** → Combine with localStorage
