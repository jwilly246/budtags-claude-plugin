# Pattern 7: Window Scrolling

## Use Window as Scroll Container

Instead of `overflow: auto` container, use the browser window:

```typescript
const virtualizer = useVirtualizer({
  count: items.length,
  getScrollElement: () => window, // Use window instead of ref
  estimateSize: () => 100,
  overscan: 10,
})
```

## Complete Example

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'

function WindowVirtualList({ items }: { items: Post[] }) {
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => window,
    estimateSize: () => 200,
    overscan: 5,
  })

  return (
    <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
      {virtualizer.getVirtualItems().map((virtualItem) => {
        const item = items[virtualItem.index]
        return (
          <div
            key={virtualItem.key}
            className="absolute top-0 left-0 w-full p-4 border-b"
            style={{
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <h2>{item.title}</h2>
            <p>{item.body}</p>
          </div>
        )
      })}
    </div>
  )
}
```

## With Header/Footer

Account for fixed headers/footers:

```typescript
function WindowVirtualListWithHeader({ items }: { items: Item[] }) {
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => window,
    estimateSize: () => 100,
    scrollMargin: 80, // Header height
  })

  return (
    <>
      <header className="fixed top-0 left-0 right-0 h-20 bg-white border-b z-50">
        <h1>My App</h1>
      </header>
      <div
        className="pt-20"
        style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => {
          const item = items[virtualItem.index]
          return (
            <div
              key={virtualItem.key}
              className="absolute w-full"
              style={{
                top: 0,
                left: 0,
                height: `${virtualItem.size}px`,
                transform: `translateY(${virtualItem.start}px)`,
              }}
            >
              {item.name}
            </div>
          )
        })}
      </div>
    </>
  )
}
```

## Infinite Scroll with Window

```typescript
function InfiniteScrollList() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useInfiniteQuery({...})

  const allItems = data?.pages.flatMap(page => page.items) ?? []

  const virtualizer = useVirtualizer({
    count: allItems.length,
    getScrollElement: () => window,
    estimateSize: () => 100,
    overscan: 10,
  })

  // Fetch next page when near bottom
  useEffect(() => {
    const [lastItem] = virtualizer.getVirtualItems().slice(-1)

    if (!lastItem) return

    if (
      lastItem.index >= allItems.length - 1 &&
      hasNextPage &&
      !isFetchingNextPage
    ) {
      fetchNextPage()
    }
  }, [
    hasNextPage,
    fetchNextPage,
    allItems.length,
    isFetchingNextPage,
    virtualizer.getVirtualItems(),
  ])

  return (
    <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
      {virtualizer.getVirtualItems().map((virtualItem) => (
        <div
          key={virtualItem.key}
          className="absolute w-full"
          style={{
            top: 0,
            left: 0,
            height: `${virtualItem.size}px`,
            transform: `translateY(${virtualItem.start}px)`,
          }}
        >
          {allItems[virtualItem.index].name}
        </div>
      ))}
    </div>
  )
}
```

## Next Steps
- Read `10-scroll-restoration.md` for scroll position
- Read `09-performance-optimization.md` for performance
