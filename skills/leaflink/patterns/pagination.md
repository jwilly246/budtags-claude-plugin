# LeafLink Pagination

Offset-based pagination patterns for LeafLink Marketplace V2 API.

---

## Pagination Method

LeafLink uses **offset-based pagination** for all list endpoints.

### Parameters

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `limit` | integer | 50 | 100 | Number of results per page |
| `offset` | integer | 0 | - | Starting position (0-indexed) |

---

## Request Example

```php
$response = $api->get('/orders-received/', [
    'limit' => 100,    // Get 100 results
    'offset' => 0      // Start at beginning
]);
```

---

## Response Structure

```json
{
    "count": 250,                           // Total number of results
    "next": "https://app.leaflink.com/api/v2/orders-received/?limit=100&offset=100",  // Next page URL
    "previous": null,                       // Previous page URL (null for first page)
    "results": [...]                        // Array of results (up to 'limit' items)
}
```

**Response Fields:**
- `count` - Total number of matching results across all pages
- `next` - Full URL to next page (null if no more pages)
- `previous` - Full URL to previous page (null on first page)
- `results` - Array of items for current page

---

## Calculating Pages

```php
// Calculate total pages
$totalPages = ceil($response->json('count') / $limit);

// Calculate current page (1-indexed for display)
$currentPage = ($offset / $limit) + 1;

// Calculate next offset
$nextOffset = $offset + $limit;

// Check if more pages exist
$hasMore = $response->json('next') !== null;
```

---

## Implementation in BudTags

The `LeafLinkApi` service provides a helper method for Laravel pagination:

```php
// LeafLinkApi::paginate_get()
protected function paginate_get(
    string $url,
    int $page,
    string $path,
    array $values = [],
): LengthAwarePaginator {
    $amt = 50;  // Results per page

    if ($page < 1) {
        $page = 1;
    }

    $offset = ($page - 1) * $amt;

    $response = $this->get($url, [
        'limit' => $amt,
        'offset' => $offset,
        ...$values,
    ]);

    return new LengthAwarePaginator(
        $response->json('results'),
        $response->json('count'),
        50,
        $page,
        ['path' => $path]
    );
}
```

**Usage:**
```php
// Controller method
public function index(Request $request) {
    $orders = $this->api->paginate_get(
        url: '/orders-received/',
        page: $request->get('page', 1),
        path: '/leaflink/orders',
        values: [
            'status' => 'confirmed',
            'created_date__gte' => '2025-01-01'
        ]
    );

    return Inertia::render('Leaflink/Orders', [
        'orders' => $orders
    ]);
}
```

---

## Iterating Through All Pages

### Manual Iteration

```php
// Fetch all results across multiple pages
$allResults = [];
$offset = 0;
$limit = 100;

do {
    $response = $api->get('/orders-received/', [
        'limit' => $limit,
        'offset' => $offset
    ]);

    $data = $response->json();
    $allResults = array_merge($allResults, $data['results']);

    $offset += $limit;
} while ($data['next'] !== null);

// $allResults now contains all orders
```

### Using 'next' URL

```php
// Alternative: Follow 'next' URLs
$allResults = [];
$url = '/orders-received/';

do {
    $response = $api->get($url);
    $data = $response->json();

    $allResults = array_merge($allResults, $data['results']);

    // Extract path from next URL
    $url = $data['next'] ? parse_url($data['next'], PHP_URL_PATH) . '?' . parse_url($data['next'], PHP_URL_QUERY) : null;
} while ($url !== null);
```

---

## Combining Pagination with Filters

```php
// Paginate with filters
$response = $api->get('/orders-received/', [
    'limit' => 100,
    'offset' => 0,
    'status' => 'confirmed',
    'created_date__gte' => '2025-01-01',
    'created_date__lte' => '2025-01-31'
]);

// Response includes filtered count
// count: 45  (total matching filtered results)
// results: [... up to 100 items ...]
```

---

## Performance Considerations

### Optimal Page Sizes

| Use Case | Recommended Limit | Reason |
|----------|------------------|---------|
| **UI Display** | 50 | Good balance for user experience |
| **Bulk Processing** | 100 | Maximum allowed, minimize API calls |
| **Real-time Updates** | 25-50 | Faster response times |
| **Mobile Apps** | 25 | Smaller payloads |

### Caching Strategy

```php
// Cache first page for frequently accessed lists
$cacheKey = "leaflink_orders_page1_{$orgId}";

$firstPage = Cache::remember($cacheKey, 300, function () use ($api) {
    return $api->get('/orders-received/', [
        'limit' => 50,
        'offset' => 0,
        'status' => 'confirmed'
    ])->json();
});
```

---

## Common Pitfalls

❌ **Don't:**
- Fetch all results at once without pagination (may timeout or hit memory limits)
- Use negative offset values
- Exceed limit of 100 per page
- Forget to handle the case when `results` is empty

✅ **Do:**
- Use maximum limit (100) for bulk operations
- Check `next` field to determine if more pages exist
- Cache frequently accessed first pages
- Handle empty `results` array gracefully
- Show total count to users: `count` field

---

## Quick Reference

```php
// Basic pagination
$page1 = $api->get('/orders-received/', ['limit' => 50, 'offset' => 0]);
$page2 = $api->get('/orders-received/', ['limit' => 50, 'offset' => 50]);
$page3 = $api->get('/orders-received/', ['limit' => 50, 'offset' => 100]);

// Check for more pages
$hasMore = $response->json('next') !== null;

// Get total result count
$total = $response->json('count');
```
