# Pattern 10: Scroll Restoration

## Save/Restore Scroll Position

Preserve scroll position when navigating away and back:

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'
import { useEffect, useRef } from 'react'

function VirtualListWithScrollRestore({ items, listId }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  })

  // Save scroll position to sessionStorage
  useEffect(() => {
    const scrollElement = parentRef.current
    if (!scrollElement) return

    const handleScroll = () => {
      sessionStorage.setItem(
        `scroll-${listId}`,
        scrollElement.scrollTop.toString()
      )
    }

    scrollElement.addEventListener('scroll', handleScroll)
    return () => scrollElement.removeEventListener('scroll', handleScroll)
  }, [listId])

  // Restore scroll position on mount
  useEffect(() => {
    const scrollElement = parentRef.current
    if (!scrollElement) return

    const savedScroll = sessionStorage.getItem(`scroll-${listId}`)
    if (savedScroll) {
      scrollElement.scrollTop = parseInt(savedScroll, 10)
    }
  }, [listId])

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto">
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
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
              {item.name}
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

## Custom Hook for Scroll Restoration

```typescript
function useScrollRestoration(key: string, virtualizer: Virtualizer<any, any>) {
  const scrollElementRef = virtualizer.scrollRect

  useEffect(() => {
    const element = virtualizer.scrollElement
    if (!element) return

    // Restore on mount
    const saved = sessionStorage.getItem(`scroll-${key}`)
    if (saved) {
      element.scrollTop = parseInt(saved, 10)
    }

    // Save on scroll
    const handleScroll = () => {
      sessionStorage.setItem(`scroll-${key}`, element.scrollTop.toString())
    }

    element.addEventListener('scroll', handleScroll, { passive: true })
    return () => element.removeEventListener('scroll', handleScroll)
  }, [key, virtualizer.scrollElement])
}

// Usage
function VirtualList({ items, listKey }) {
  const parentRef = useRef(null)
  const virtualizer = useVirtualizer({...})

  useScrollRestoration(listKey, virtualizer)

  return (...)
}
```

## Scroll to Item on Mount

Restore to specific item instead of pixel position:

```typescript
function VirtualListWithItemRestore({ items, selectedItemId }) {
  const parentRef = useRef(null)

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  })

  // Scroll to selected item on mount
  useEffect(() => {
    if (!selectedItemId) return

    const index = items.findIndex(item => item.id === selectedItemId)
    if (index !== -1) {
      virtualizer.scrollToIndex(index, {
        align: 'center', // 'start' | 'center' | 'end' | 'auto'
      })
    }
  }, []) // Only on mount

  return (...)
}
```

## React Router Integration

```typescript
import { useLocation, useNavigate } from 'react-router-dom'

function VirtualList({ items }) {
  const location = useLocation()
  const navigate = useNavigate()
  const parentRef = useRef(null)

  const virtualizer = useVirtualizer({...})

  // Save scroll position when navigating away
  useEffect(() => {
    return () => {
      const scrollElement = parentRef.current
      if (scrollElement) {
        sessionStorage.setItem(
          `scroll-${location.pathname}`,
          scrollElement.scrollTop.toString()
        )
      }
    }
  }, [location.pathname])

  // Restore scroll position on mount
  useEffect(() => {
    const scrollElement = parentRef.current
    if (!scrollElement) return

    const savedScroll = sessionStorage.getItem(`scroll-${location.pathname}`)
    if (savedScroll) {
      setTimeout(() => {
        scrollElement.scrollTop = parseInt(savedScroll, 10)
      }, 0)
    }
  }, [location.pathname])

  return (...)
}
```

## Inertia.js Integration (BudTags)

```typescript
import { router } from '@inertiajs/react'

function VirtualPackagesTable({ packages }) {
  const parentRef = useRef(null)

  const virtualizer = useVirtualizer({
    count: packages.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  })

  // Save scroll on navigation
  useEffect(() => {
    const removeListener = router.on('before', () => {
      const scrollElement = parentRef.current
      if (scrollElement) {
        sessionStorage.setItem(
          'packages-scroll',
          scrollElement.scrollTop.toString()
        )
      }
    })

    return removeListener
  }, [])

  // Restore scroll on mount
  useEffect(() => {
    const scrollElement = parentRef.current
    if (!scrollElement) return

    const savedScroll = sessionStorage.getItem('packages-scroll')
    if (savedScroll) {
      requestAnimationFrame(() => {
        scrollElement.scrollTop = parseInt(savedScroll, 10)
      })
    }
  }, [])

  return (...)
}
```

## Clear Scroll on Filters

Clear saved scroll when filters change:

```typescript
function VirtualList({ items, filter }) {
  const parentRef = useRef(null)
  const virtualizer = useVirtualizer({...})

  // Clear scroll when filter changes
  useEffect(() => {
    sessionStorage.removeItem('scroll-list')
    parentRef.current?.scrollTo({ top: 0 })
  }, [filter])

  return (...)
}
```

## Next Steps
- Read `11-testing.md` for testing virtualized components
- Read `09-performance-optimization.md` for performance tips
