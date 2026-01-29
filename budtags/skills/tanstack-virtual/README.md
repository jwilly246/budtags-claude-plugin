# TanStack Virtual Skill

Virtualization for large lists and tables - only render what's visible.

## Installation

```bash
npm install @tanstack/react-virtual
```

## Basic Usage

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'

function VirtualList({ items }) {
  const parentRef = useRef(null)

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 35,
  })

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              transform: `translateY(${virtualItem.start}px)`,
              height: `${virtualItem.size}px`,
            }}
          >
            {items[virtualItem.index]}
          </div>
        ))}
      </div>
    </div>
  )
}
```

## Resources

- **Docs:** https://tanstack.com/virtual/latest
- **GitHub:** https://github.com/TanStack/virtual
