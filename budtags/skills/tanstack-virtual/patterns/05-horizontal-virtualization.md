# Pattern 5: Horizontal Virtualization

## Horizontal List

Change `horizontal: true` and adjust styles:

```typescript
const virtualizer = useVirtualizer({
  horizontal: true, // Enable horizontal mode
  count: items.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 200, // Width instead of height
})
```

## Complete Example

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'

function HorizontalList({ items }: { items: Product[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    horizontal: true,
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 250,
    overscan: 3,
  })

  return (
    <div
      ref={parentRef}
      className="overflow-x-auto overflow-y-hidden"
      style={{ width: '100%', height: '400px' }}
    >
      <div
        style={{
          width: `${virtualizer.getTotalSize()}px`,
          height: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => {
          const item = items[virtualItem.index]
          return (
            <div
              key={virtualItem.key}
              className="absolute top-0 left-0 h-full"
              style={{
                width: `${virtualItem.size}px`,
                transform: `translateX(${virtualItem.start}px)`,
              }}
            >
              <div className="p-4 h-full border-r">
                <img src={item.image} className="w-full h-48 object-cover" />
                <h3>{item.name}</h3>
                <p>${item.price}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

## Horizontal Scroll Cards

```typescript
function ProductCarousel({ products }: { products: Product[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    horizontal: true,
    count: products.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 300,
  })

  return (
    <div>
      <div
        ref={parentRef}
        className="flex overflow-x-auto snap-x"
        style={{ width: '100%' }}
      >
        <div
          style={{
            width: `${virtualizer.getTotalSize()}px`,
            display: 'flex',
          }}
        >
          {virtualizer.getVirtualItems().map((virtualItem) => {
            const product = products[virtualItem.index]
            return (
              <div
                key={virtualItem.key}
                className="snap-start"
                style={{
                  width: `${virtualItem.size}px`,
                  transform: `translateX(${virtualItem.start}px)`,
                }}
              >
                <ProductCard product={product} />
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
```

## Next Steps
- Read `06-grid-virtualization.md` for 2D virtualization
- Read `09-performance-optimization.md` for performance
