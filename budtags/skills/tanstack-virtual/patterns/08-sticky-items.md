# Pattern 8: Sticky Headers & Items

## Sticky Header with Virtual Table

```typescript
function VirtualTableWithStickyHeader<T>({ data, columns }) {
  const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel() })
  const { rows } = table.getRowModel()
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  })

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto relative">
      {/* Sticky header */}
      <div className="sticky top-0 bg-white z-10 border-b">
        {table.getHeaderGroups().map((headerGroup) => (
          <div key={headerGroup.id} className="flex">
            {headerGroup.headers.map((header) => (
              <div key={header.id} className="flex-1 p-2 font-bold">
                {flexRender(header.column.columnDef.header, header.getContext())}
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Virtual rows */}
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualRow) => {
          const row = rows[virtualRow.index]
          return (
            <div
              key={row.id}
              className="absolute top-0 left-0 w-full flex"
              style={{
                height: `${virtualRow.size}px`,
                transform: `translateY(${virtualRow.start}px)`,
              }}
            >
              {row.getVisibleCells().map((cell) => (
                <div key={cell.id} className="flex-1 p-2">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </div>
              ))}
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

## Sticky Group Headers

```typescript
function VirtualListWithGroups({ groupedItems }) {
  const parentRef = useRef<HTMLDivElement>(null)

  // Flatten groups into single array with headers
  const items = groupedItems.flatMap(group => [
    { type: 'header', label: group.label },
    ...group.items.map(item => ({ type: 'item', data: item })),
  ])

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: (index) => {
      return items[index].type === 'header' ? 40 : 60
    },
  })

  const [stickyHeader, setStickyHeader] = useState<string | null>(null)

  // Track current group header
  useEffect(() => {
    const firstItem = virtualizer.getVirtualItems()[0]
    if (!firstItem) return

    // Find the last header before current scroll position
    for (let i = firstItem.index; i >= 0; i--) {
      if (items[i].type === 'header') {
        setStickyHeader(items[i].label)
        break
      }
    }
  }, [virtualizer.getVirtualItems()])

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto relative">
      {/* Sticky current group header */}
      {stickyHeader && (
        <div className="sticky top-0 bg-blue-100 p-2 font-bold z-10">
          {stickyHeader}
        </div>
      )}

      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualItem) => {
          const item = items[virtualItem.index]

          if (item.type === 'header') {
            return (
              <div
                key={virtualItem.key}
                className="absolute top-0 left-0 w-full bg-gray-100 p-2 font-bold"
                style={{
                  height: `${virtualItem.size}px`,
                  transform: `translateY(${virtualItem.start}px)`,
                }}
              >
                {item.label}
              </div>
            )
          }

          return (
            <div
              key={virtualItem.key}
              className="absolute top-0 left-0 w-full p-2 border-b"
              style={{
                height: `${virtualItem.size}px`,
                transform: `translateY(${virtualItem.start}px)`,
              }}
            >
              {item.data.name}
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
- Read `03-table-integration.md` for table patterns
