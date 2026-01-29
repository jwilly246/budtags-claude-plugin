# Pattern 6: Grid Virtualization (2D)

## 2D Virtualization

Use two virtualizers - one for rows, one for columns:

```typescript
const rowVirtualizer = useVirtualizer({
  count: rows.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 100,
})

const columnVirtualizer = useVirtualizer({
  horizontal: true,
  count: columns.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 150,
})
```

## Complete Grid Example

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'

function VirtualGrid() {
  const parentRef = useRef<HTMLDivElement>(null)

  // 1000 rows × 50 columns = 50,000 cells
  const rows = Array.from({ length: 1000 }, (_, i) => i)
  const columns = Array.from({ length: 50 }, (_, i) => i)

  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  })

  const columnVirtualizer = useVirtualizer({
    horizontal: true,
    count: columns.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100,
    overscan: 3,
  })

  return (
    <div
      ref={parentRef}
      className="overflow-auto border"
      style={{ width: '800px', height: '600px' }}
    >
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: `${columnVirtualizer.getTotalSize()}px`,
          position: 'relative',
        }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.key}
            className="absolute top-0 left-0"
            style={{
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
              width: '100%',
            }}
          >
            {columnVirtualizer.getVirtualItems().map((virtualColumn) => (
              <div
                key={virtualColumn.key}
                className="absolute top-0 border-r border-b"
                style={{
                  width: `${virtualColumn.size}px`,
                  height: '100%',
                  transform: `translateX(${virtualColumn.start}px)`,
                }}
              >
                <div className="p-2">
                  Cell {virtualRow.index},{virtualColumn.index}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
```

## Calendar Grid

```typescript
function VirtualCalendar() {
  const parentRef = useRef<HTMLDivElement>(null)

  const weeks = 52
  const daysPerWeek = 7

  const weekVirtualizer = useVirtualizer({
    count: weeks,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 120,
  })

  const dayVirtualizer = useVirtualizer({
    horizontal: true,
    count: daysPerWeek,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 150,
  })

  return (
    <div ref={parentRef} className="h-screen overflow-auto">
      <div
        style={{
          height: `${weekVirtualizer.getTotalSize()}px`,
          width: `${dayVirtualizer.getTotalSize()}px`,
          position: 'relative',
        }}
      >
        {weekVirtualizer.getVirtualItems().map((virtualWeek) => (
          <div
            key={virtualWeek.key}
            className="absolute"
            style={{
              top: 0,
              left: 0,
              height: `${virtualWeek.size}px`,
              width: '100%',
              transform: `translateY(${virtualWeek.start}px)`,
            }}
          >
            {dayVirtualizer.getVirtualItems().map((virtualDay) => (
              <div
                key={virtualDay.key}
                className="absolute border"
                style={{
                  top: 0,
                  left: 0,
                  width: `${virtualDay.size}px`,
                  height: '100%',
                  transform: `translateX(${virtualDay.start}px)`,
                }}
              >
                <DayCell week={virtualWeek.index} day={virtualDay.index} />
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
```

## Next Steps
- Read `09-performance-optimization.md` for grid performance
- Read `08-sticky-items.md` for sticky headers
