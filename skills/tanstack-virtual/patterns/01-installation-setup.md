# Pattern 1: Installation & Setup

## Installation

```bash
npm install @tanstack/react-virtual
```

## Basic Imports

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'
```

## What You Get

- `useVirtualizer` - Main hook for creating virtualizer instance
- Virtual items only render what's visible
- Automatic performance optimization

## Minimal Example

```typescript
function BasicList() {
  const parentRef = useRef<HTMLDivElement>(null)
  const items = Array.from({ length: 10000 }, (_, i) => `Item ${i}`)

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
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
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

## Next Steps
- Read `02-basic-list.md` for detailed API
- Read `03-table-integration.md` for TanStack Table integration
