# Pattern — Filtering

Distru uses **per-endpoint query-string filters**. There is no Canix-style `where` SQL string, no LeafLink-style Django `__gte`/`__lte`, no general-purpose filter expression. Each endpoint exposes its own named filter parameters.

## General Shape

```
GET /public/v1/orders?status=FULFILLED&updated_at_from=2026-01-01T00:00:00Z
```

## Common Filter Names

These appear on **most** business endpoints, but always verify against the specific category file:

| Filter | Type | Meaning |
|--------|------|---------|
| `updated_at_from` | ISO 8601 timestamp | Records updated on or after this time |
| `updated_at_to` | ISO 8601 timestamp | Records updated on or before this time |
| `created_at_from` | ISO 8601 timestamp | Records created on or after this time |
| `created_at_to` | ISO 8601 timestamp | Records created on or before this time |

## Endpoint-Specific Filters

| Endpoint | Filters |
|----------|---------|
| `/orders` | `status`, `company_id`, `updated_at_from/to` |
| `/purchases` | `status`, `company_id`, `updated_at_from/to` |
| `/companies` | `relationship_type`, `category`, `name` |
| `/products` | `brand_id`, `category`, `subcategory` |
| `/batches` | `location_id`, `include_costs`, `updated_at_from/to` |
| `/assemblies` | `completion_datetime_from/to`, `creation_source`, `license_number` |

> Filter names not in your endpoint's documented list are usually **ignored silently**. They do not return 400. Always verify a filter works by spot-checking response counts.

## Incremental Sync

The recommended Budtags incremental-sync pattern uses `updated_at_from`:

```php
$lastSync = $importJob->last_synced_at?->toIso8601String() ?? '1970-01-01T00:00:00Z';

$response = $api->get('/orders', [
    'updated_at_from' => $lastSync,
    'page[number]'    => 1,
    'page[size]'      => 100,
]);
```

**Save the high-water mark only after a fully successful import** — never advance the cursor mid-pagination.

## No Logical Operators

You cannot AND/OR/combine filters in a single field. The only combination semantics are the implicit AND across distinct query parameters. For complex selections, pull broadly and filter Budtags-side.

## Sorting

Documented sort behavior is limited. Most endpoints return **newest-updated or oldest-created** depending on the resource — do not assume an order without verifying. For Assemblies, results are documented as **oldest-to-newest** creation order.

## Pitfalls

- Expecting a `where` parameter — that's Canix.
- Expecting `__gte`/`__lte`/`__in` suffixes — that's LeafLink.
- Combining filter names that the endpoint does not list — silently ignored.
- Trusting an undocumented sort order — verify.

## Cross-references

- Date format: `patterns/date-formats.md`
- Pagination: `patterns/pagination.md`
