# Pattern 17: Paginated Queries

## Page-Based Pagination

Use regular `useQuery` with page numbers:

```typescript
function Packages() {
  const [page, setPage] = useState(1)

  const { data, isLoading, isPlaceholderData } = useQuery({
    queryKey: ['packages', page],
    queryFn: () => fetchPackages({ page }),
    placeholderData: (previousData) => previousData, // Keep previous data while loading
  })

  return (
    <div>
      {data?.items.map(pkg => <PackageCard key={pkg.id} pkg={pkg} />)}

      <div className="flex gap-2 mt-4">
        <button
          onClick={() => setPage(old => Math.max(old - 1, 1))}
          disabled={page === 1}
        >
          Previous
        </button>

        <span>Page {page} of {data?.totalPages}</span>

        <button
          onClick={() => setPage(old => old + 1)}
          disabled={isPlaceholderData || page === data?.totalPages}
        >
          Next
        </button>
      </div>
    </div>
  )
}
```

## keepPreviousData (Deprecated in v5)

In v5, use `placeholderData`:

```typescript
// ❌ v4 syntax (deprecated)
useQuery({
  queryKey: ['packages', page],
  queryFn: () => fetchPackages(page),
  keepPreviousData: true,
})

// ✅ v5 syntax
useQuery({
  queryKey: ['packages', page],
  queryFn: () => fetchPackages(page),
  placeholderData: (previousData) => previousData,
})
```

## isPlaceholderData Flag

Know when showing previous data vs new data:

```typescript
const { data, isPlaceholderData } = useQuery({
  queryKey: ['packages', page],
  queryFn: () => fetchPackages(page),
  placeholderData: (previousData) => previousData,
})

// While fetching new page:
isPlaceholderData === true  // Showing old data
data // Previous page's data

// After new data loads:
isPlaceholderData === false
data // New page's data
```

## Disable Navigation During Fetch

Prevent clicking next/previous while loading:

```typescript
<button
  onClick={() => setPage(old => old + 1)}
  disabled={isPlaceholderData || !data?.hasMore}
>
  Next
</button>
```

## BudTags Examples

### Metrc Packages with Pagination

```typescript
function PaginatedPackages() {
  const { user } = usePage<PageProps>().props
  const license = usePage<PageProps>().props.session.license
  const [page, setPage] = useState(1)
  const [perPage, setPerPage] = useState(25)

  const {
    data,
    isLoading,
    isPlaceholderData,
  } = useQuery({
    queryKey: ['metrc', 'packages', license, { page, perPage }],
    queryFn: async () => {
      const api = new MetrcApi()
      api.set_user(user)
      return api.packages_paginated(license, page, perPage)
    },
    placeholderData: (previousData) => previousData,
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) return <Spinner />

  return (
    <div>
      <DataTable data={data.items} />

      <div className="mt-4 flex items-center justify-between">
        <div>
          Showing {(page - 1) * perPage + 1} to{' '}
          {Math.min(page * perPage, data.total)} of {data.total}
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setPage(old => Math.max(old - 1, 1))}
            disabled={page === 1 || isPlaceholderData}
            className="px-4 py-2 border rounded disabled:opacity-50"
          >
            Previous
          </button>

          <span className="px-4 py-2">
            Page {page} of {data.totalPages}
          </span>

          <button
            onClick={() => setPage(old => old + 1)}
            disabled={page >= data.totalPages || isPlaceholderData}
            className="px-4 py-2 border rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>

        <select
          value={perPage}
          onChange={(e) => {
            setPerPage(Number(e.target.value))
            setPage(1) // Reset to first page
          }}
          className="border rounded px-2 py-1"
        >
          <option value={10}>10 per page</option>
          <option value={25}>25 per page</option>
          <option value={50}>50 per page</option>
          <option value={100}>100 per page</option>
        </select>
      </div>
    </div>
  )
}
```

### Page Numbers

```typescript
function PageNumbers({ currentPage, totalPages, onPageChange }: Props) {
  const pages = []

  // Show first page
  pages.push(1)

  // Show pages around current
  for (let i = currentPage - 2; i <= currentPage + 2; i++) {
    if (i > 1 && i < totalPages) {
      pages.push(i)
    }
  }

  // Show last page
  if (totalPages > 1) {
    pages.push(totalPages)
  }

  return (
    <div className="flex gap-2">
      {pages.map((page, i) => {
        // Add ellipsis if gap
        if (i > 0 && pages[i - 1] < page - 1) {
          return (
            <React.Fragment key={page}>
              <span>...</span>
              <button
                onClick={() => onPageChange(page)}
                className={currentPage === page ? 'font-bold' : ''}
              >
                {page}
              </button>
            </React.Fragment>
          )
        }

        return (
          <button
            key={page}
            onClick={() => onPageChange(page)}
            className={currentPage === page ? 'font-bold' : ''}
          >
            {page}
          </button>
        )
      })}
    </div>
  )
}
```

### URL-Based Pagination

```typescript
function PaginatedPackages() {
  const [searchParams, setSearchParams] = useSearchParams()
  const page = Number(searchParams.get('page') || '1')

  const { data, isPlaceholderData } = useQuery({
    queryKey: ['packages', page],
    queryFn: () => fetchPackages(page),
    placeholderData: (previousData) => previousData,
  })

  const setPage = (newPage: number) => {
    setSearchParams({ page: String(newPage) })
  }

  return (
    <div>
      <DataTable data={data.items} />

      <button onClick={() => setPage(page - 1)} disabled={page === 1}>
        Previous
      </button>
      <button onClick={() => setPage(page + 1)} disabled={isPlaceholderData}>
        Next
      </button>
    </div>
  )
}
```

### Prefetch Next Page

```typescript
function PaginatedPackages() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)

  const { data } = useQuery({
    queryKey: ['packages', page],
    queryFn: () => fetchPackages(page),
    placeholderData: (previousData) => previousData,
  })

  // Prefetch next page
  useEffect(() => {
    if (data?.hasMore) {
      queryClient.prefetchQuery({
        queryKey: ['packages', page + 1],
        queryFn: () => fetchPackages(page + 1),
      })
    }
  }, [page, data, queryClient])

  return <DataTable data={data.items} />
}
```

## Cursor-Based Pagination

For APIs that use cursors instead of page numbers:

```typescript
function CursorPagination() {
  const [cursor, setCursor] = useState<string | null>(null)

  const { data } = useQuery({
    queryKey: ['packages', cursor],
    queryFn: () => fetchPackages({ cursor }),
    placeholderData: (previousData) => previousData,
  })

  return (
    <div>
      <DataTable data={data.items} />

      <button onClick={() => setCursor(data.prevCursor)}>
        Previous
      </button>
      <button onClick={() => setCursor(data.nextCursor)}>
        Next
      </button>
    </div>
  )
}
```

## Infinite Queries vs Paginated Queries

### Use Paginated Queries When:
- ✅ Fixed page sizes (1, 2, 3...)
- ✅ Jump to specific page needed
- ✅ Total pages known
- ✅ Table/grid UI
- ✅ Server returns page metadata

### Use Infinite Queries When:
- ✅ Infinite scroll
- ✅ "Load more" buttons
- ✅ Unknown total pages
- ✅ Feed/timeline UI
- ✅ Progressive loading

## Next Steps
- **Infinite Queries** → Read `16-infinite-queries.md`
- **Prefetching** → Read `18-prefetching.md`
- **Placeholder Data** → Read `19-initial-placeholder-data.md`
