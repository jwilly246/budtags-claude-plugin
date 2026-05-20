# Canix API Pagination

## Overview

Canix uses simple offset-based pagination. There is no cursor-based or token-based pagination.

## Parameters

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `limit` | integer | 2000 | 2000 | Max records per page |
| `offset` | integer | 0 | — | Starting position (0-indexed) |
| `order_by` | string | — | — | SQL format: `"id desc"`, `"updated_at asc"` |

## Response Format

**CRITICAL DIFFERENCE FROM LEAFLINK**: Canix returns **raw arrays**, not pagination wrapper objects.

```json
// Canix response (raw array)
[
  { "id": 1, "name": "Order #001", ... },
  { "id": 2, "name": "Order #002", ... }
]

// LeafLink response (wrapper object) — NOT how Canix works
// { "count": 100, "next": "...", "previous": "...", "results": [...] }
```

## Detecting Last Page

Since there's no `count` or `next` field, detect the last page by checking:

```php
$is_last_page = count($response) < $limit;
```

If the response has fewer records than the limit, you've reached the end.

## Iterating All Pages

```php
$all_records = [];
$offset = 0;
$limit = 2000;

do {
    $page = $api->get('/sales_orders', [
        'limit'    => $limit,
        'offset'   => $offset,
        'order_by' => 'id asc',
    ]);

    $all_records = array_merge($all_records, $page);
    $offset += $limit;
} while (count($page) === $limit);
```

## Combining with Filters

Pagination parameters work alongside `where` and `order_by`:

```php
$api->get('/items', [
    'limit'    => 2000,
    'offset'   => 0,
    'where'    => "is_active=true AND facility_id=123",
    'order_by' => 'updated_at desc',
]);
```

## Key Differences from LeafLink

| Aspect | LeafLink | Canix |
|--------|----------|-------|
| Default page size | 50 | 2000 |
| Max page size | 100 | 2000 |
| Response format | `{count, next, previous, results}` | Raw array |
| Cursor pagination | Supported | Not supported |
| Last page detection | `next === null` | `count(response) < limit` |

## Best Practices

- Always pass `order_by` for deterministic pagination (e.g., `order_by=id asc`)
- Use `limit=2000` for bulk imports (max throughput per request)
- Use smaller limits for user-facing features to reduce response time
- Track offset manually — no `next` URL is provided
- For incremental sync, combine with `where=updated_at >= '{date}'` to limit results

---

**See:** `patterns/filtering.md` for the SQL-like `where` parameter syntax
