---
name: tanstack-virtual
description: TanStack Virtual patterns for virtualized lists, tables, and grids with high-performance rendering of large datasets
version: 1.0.0
category: project
agent: tanstack-specialist
auto_activate:
  patterns:
    - "**/*.{ts,tsx,js,jsx}"
  keywords:
    - "useVirtualizer"
    - "virtualizer"
    - "virtual scroll"
    - "virtualization"
    - "tanstack virtual"
    - "react-virtual"
---

# TanStack Virtual Skill

High-performance virtualization for rendering large lists, tables, and grids. Only render what's visible.

## All Pattern Files (12 Total)

### Foundation (2 patterns)
- `01-installation-setup.md` - Installation, basic setup
- `02-basic-list.md` - useVirtualizer hook, simple list

### Lists & Tables (3 patterns)
- `03-table-integration.md` - TanStack Table + Virtual integration
- `04-dynamic-heights.md` - Variable row heights
- `05-horizontal-virtualization.md` - Horizontal scrolling

### Advanced (3 patterns)
- `06-grid-virtualization.md` - 2D virtualization
- `07-window-scrolling.md` - Window as scrollElement
- `08-sticky-items.md` - Sticky headers/footers

### Production (3 patterns)
- `09-performance-optimization.md` - Overscan, throttling
- `10-scroll-restoration.md` - Restore scroll position
- `11-testing.md` - Testing virtualized components

### BudTags (1 pattern)
- `12-budtags-integration.md` - DataTable.tsx examples

## Quick Start

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'

const virtualizer = useVirtualizer({
  count: items.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 35,
})
```
