# Pattern 9: Performance Optimization

## Overscan

Render extra items outside viewport to reduce blank areas during fast scrolling:

```typescript
const virtualizer = useVirtualizer({
  count: items.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 50,
  overscan: 10, // Render 10 items above/below viewport
})
```

**Default:** 1
**Recommended:** 5-10 for smooth scrolling
**High values:** More items rendered, but smoother UX

## Memoize estimateSize

Don't create new function on every render:

```typescript
// ❌ BAD - New function each render
const virtualizer = useVirtualizer({
  estimateSize: () => 50,
})

// ✅ GOOD - Stable function reference
const estimateSize = useCallback(() => 50, [])

const virtualizer = useVirtualizer({
  estimateSize,
})

// ✅ BETTER - For dynamic heights based on data
const estimateSize = useCallback((index: number) => {
  const item = items[index]
  return item.isExpanded ? 200 : 50
}, [items])
```

## Memoize Virtual Items Rendering

```typescript
function VirtualList({ items }) {
  const parentRef = useRef(null)

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  })

  const virtualItems = virtualizer.getVirtualItems()

  // ✅ Memoize rendering of virtual items
  const renderedItems = useMemo(() => {
    return virtualItems.map((virtualItem) => {
      const item = items[virtualItem.index]
      return (
        <VirtualRow
          key={virtualItem.key}
          virtualItem={virtualItem}
          item={item}
        />
      )
    })
  }, [virtualItems, items])

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto">
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {renderedItems}
      </div>
    </div>
  )
}

// Extract row component
const VirtualRow = memo(({ virtualItem, item }) => (
  <div
    className="absolute top-0 left-0 w-full"
    style={{
      height: `${virtualItem.size}px`,
      transform: `translateY(${virtualItem.start}px)`,
    }}
  >
    {item.name}
  </div>
))
```

## debounce scrollToIndex

Prevent excessive scroll operations:

```typescript
const debouncedScrollTo = useMemo(
  () => debounce((index: number) => virtualizer.scrollToIndex(index), 150),
  [virtualizer]
)

// Use debounced version
debouncedScrollTo(selectedIndex)
```

## Lane Configuration

Split rendering into multiple passes for better performance:

```typescript
const virtualizer = useVirtualizer({
  count: items.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 50,
  lanes: 3, // Render in 3 columns
})
```

## Reduce Paint Operations

Use `will-change` CSS for smoother animations:

```typescript
<div
  style={{
    height: `${virtualItem.size}px`,
    transform: `translateY(${virtualItem.start}px)`,
    willChange: 'transform', // Hint to browser for GPU acceleration
  }}
>
  {content}
</div>
```

## BudTags DataTable Optimization

Current optimizations in `DataTable.tsx`:

```typescript
export function DataTable<T>({ table }: { table: Table<T> }) {
  const { rows } = table.getRowModel()
  const parentRef = useRef<HTMLDivElement>(null)

  // ✅ Overscan for smooth scrolling
  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 10, // Good balance for tables
  })

  // ✅ Extract virtual items once
  const virtualRows = virtualizer.getVirtualItems()

  return (
    <div ref={parentRef} className="overflow-auto" style={{ height: '600px' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualRows.map((virtualRow) => {
          const row = rows[virtualRow.index]
          return <TableRow key={row.id} row={row} virtualRow={virtualRow} />
        })}
      </div>
    </div>
  )
}

// ✅ Memoized row component
const TableRow = memo(({ row, virtualRow }) => (
  <div
    className="absolute top-0 left-0 w-full"
    style={{
      height: `${virtualRow.size}px`,
      transform: `translateY(${virtualRow.start}px)`,
    }}
  >
    {row.getVisibleCells().map((cell) => (
      <div key={cell.id}>
        {flexRender(cell.column.columnDef.cell, cell.getContext())}
      </div>
    ))}
  </div>
))
```

## Checklist

- [ ] Set appropriate `overscan` value (5-10)
- [ ] Memoize `estimateSize` function
- [ ] Memoize virtual items rendering with `useMemo`
- [ ] Extract row components and use `memo()`
- [ ] Use `will-change: transform` for smooth scrolling
- [ ] Debounce programmatic scrolling
- [ ] Avoid expensive computations in render
- [ ] Use `React.memo()` for row components

## Next Steps
- Read `10-scroll-restoration.md` for scroll position management
- Read `11-testing.md` for testing patterns
