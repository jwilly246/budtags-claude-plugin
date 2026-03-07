# Unleashed API Pagination

Page-based pagination with configurable page sizes.

---

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `pageSize` | integer | 200 | 1-1000 | Items per page |
| `pageNumber` | integer | 1 | 1-indexed | Page to retrieve |

Use `pageSize=0` to get item count only (no items returned).

---

## Response Metadata

Every paginated response includes:

```json
{
  "Pagination": {
    "NumberOfItems": 523,
    "PageSize": 200,
    "PageNumber": 1,
    "NumberOfPages": 3
  },
  "Items": [...]
}
```

---

## Endpoints Without Pagination

These return all records in a single response:
- `Currencies`
- `Companies`
- `SellPriceTiers`

---

## Iteration Pattern (PHP)

```php
$page = 1;
$all_items = [];

do {
    $response = $api->get('/SalesOrders', [
        'pageSize' => 200,
        'pageNumber' => $page,
        'modifiedSince' => $since,
    ]);

    $data = $response->json();
    $all_items = array_merge($all_items, $data['Items']);
    $total_pages = $data['Pagination']['NumberOfPages'];
    $page++;
} while ($page <= $total_pages);
```

---

## Single Page Fetch

```php
$response = $api->get('/Products', [
    'pageSize' => 50,
    'pageNumber' => 1,
    'productGroup' => 'Cannabis',
]);

$products = $response->json()['Items'];
$total = $response->json()['Pagination']['NumberOfItems'];
```

---

## Performance Notes

- Large `pageSize` values (500+) can cause slow responses or timeouts
- Reduce `pageSize` if experiencing network performance issues
- Default ordering varies by resource (often `LastModifiedOn` descending)
- Use `modifiedSince` filter with pagination for incremental sync
