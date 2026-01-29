# Pattern 2: Basic Virtual List

## useVirtualizer Hook

```typescript
const virtualizer = useVirtualizer({
  count: items.length,              // Total number of items
  getScrollElement: () => parentRef.current,  // Scroll container
  estimateSize: () => 35,           // Estimated item height
  overscan: 5,                      // Items to render outside viewport
})
```

## Key Properties

```typescript
virtualizer.getTotalSize()         // Total height of all items
virtualizer.getVirtualItems()      // Array of visible items
virtualizer.scrollToIndex(index)   // Scroll to specific item
virtualizer.scrollToOffset(px)     // Scroll to pixel offset
```

## Virtual Item Properties

```typescript
virtualItem.key       // Unique key for React
virtualItem.index     // Original array index
virtualItem.start     // Y position (pixels from top)
virtualItem.size      // Height in pixels
virtualItem.end       // Y position + height
```

## Complete Example

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'

interface Item {
  id: number
  name: string
}

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 10,
  })

  return (
    <div>
      <div ref={parentRef} className="h-96 overflow-auto border">
        <div
          style={{
            height: `${virtualizer.getTotalSize()}px`,
            width: '100%',
            position: 'relative',
          }}
        >
          {virtualizer.getVirtualItems().map((virtualItem) => {
            const item = items[virtualItem.index]
            return (
              <div
                key={virtualItem.key}
                className="absolute top-0 left-0 w-full"
                style={{
                  height: `${virtualItem.size}px`,
                  transform: `translateY(${virtualItem.start}px)`,
                }}
              >
                <div className="p-4 border-b">
                  {item.name}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
```

## Scroll to Item

```typescript
function ScrollToButton() {
  const virtualizer = useVirtualizer({...})

  return (
    <button onClick={() => virtualizer.scrollToIndex(500)}>
      Scroll to item 500
    </button>
  )
}
```

## Next Steps
- Read `04-dynamic-heights.md` for variable row heights
- Read `03-table-integration.md` for table usage
