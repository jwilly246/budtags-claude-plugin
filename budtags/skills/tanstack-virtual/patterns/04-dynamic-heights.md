# Pattern 4: Dynamic Row Heights

## Problem

Fixed `estimateSize` doesn't work when rows have variable heights (text wrapping, images, etc.).

## Solution: measureElement

Tell virtualizer to measure actual element heights:

```typescript
const virtualizer = useVirtualizer({
  count: items.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 100, // Initial estimate
  measureElement: (element) => element.getBoundingClientRect().height,
  overscan: 5,
})
```

## Complete Example

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'

interface Post {
  id: number
  title: string
  body: string
}

function VirtualPostList({ posts }: { posts: Post[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: posts.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 150, // Rough estimate
    measureElement: (element) => {
      // Measure actual height after render
      return element.getBoundingClientRect().height
    },
  })

  return (
    <div ref={parentRef} className="h-screen overflow-auto">
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => {
          const post = posts[virtualItem.index]
          return (
            <div
              key={virtualItem.key}
              data-index={virtualItem.index}
              ref={virtualizer.measureElement}
              className="absolute top-0 left-0 w-full p-4 border-b"
              style={{
                transform: `translateY(${virtualItem.start}px)`,
              }}
            >
              <h3 className="font-bold text-lg">{post.title}</h3>
              <p className="mt-2">{post.body}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

## Key Points

1. **Add `data-index` attribute** - Required for measureElement to work
2. **Add `ref={virtualizer.measureElement}`** - Allows measurement
3. **Remove `height` from style** - Let content determine height
4. **Keep `estimateSize`** - Used for initial layout before measurement

## With Images

```typescript
function VirtualImageList({ items }: { items: ImageItem[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 200,
    measureElement: (element) => element.getBoundingClientRect().height,
  })

  return (
    <div ref={parentRef} className="h-screen overflow-auto">
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualItem) => {
          const item = items[virtualItem.index]
          return (
            <div
              key={virtualItem.key}
              data-index={virtualItem.index}
              ref={virtualizer.measureElement}
              className="absolute top-0 left-0 w-full p-4"
              style={{ transform: `translateY(${virtualItem.start}px)` }}
            >
              <img
                src={item.imageUrl}
                alt={item.title}
                className="w-full"
                onLoad={() => {
                  // Re-measure after image loads
                  virtualizer.measure()
                }}
              />
              <p>{item.title}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

## Next Steps
- Read `09-performance-optimization.md` for performance tips
- Read `10-scroll-restoration.md` for scroll position
