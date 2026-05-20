# Canix API Filtering

## Overview

Canix uses a SQL-like `where` query parameter for filtering results. This is fundamentally different from LeafLink's Django-style filter parameters.

## Syntax

The `where` parameter accepts a single string with SQL-like syntax:

```
GET /sales_orders?where=status='Active' AND updated_at >= '2024-01-01'
```

## Supported Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `=` | `status='Active'` | Equality |
| `>` | `id > 100` | Greater than |
| `<` | `id < 500` | Less than |
| `>=` | `updated_at >= '2024-01-01'` | Greater than or equal |
| `<=` | `updated_at <= '2024-12-31'` | Less than or equal |
| `BETWEEN` | `id BETWEEN 1 AND 10000` | Range (inclusive) |
| `IN` | `status IN ('Active', 'Pending')` | List membership |
| `LIKE` | `sku LIKE 'ABC%'` | Pattern matching (% wildcard) |
| `AND` | `status='Active' AND facility_id=123` | Logical AND |
| `OR` | `status='Active' OR status='Pending'` | Logical OR |

## Examples

### Simple Equality
```php
$api->get('/sales_orders', [
    'where' => "status='created'",
]);
```

### Date Range
```php
$api->get('/sales_orders', [
    'where' => "updated_at >= '2024-01-01' AND updated_at <= '2024-12-31'",
]);
```

### BETWEEN Range
```php
$api->get('/packages', [
    'where' => "id BETWEEN 1 AND 10000",
]);
```

### IN List
```php
$api->get('/sales_orders', [
    'where' => "status IN ('created', 'approved', 'filled')",
]);
```

### Pattern Matching
```php
$api->get('/items', [
    'where' => "sku LIKE 'BD-%'",
]);
```

### Compound Filters
```php
$api->get('/items', [
    'where' => "facility_id=123 AND is_active=true AND updated_at >= '2024-06-01'",
]);
```

### Boolean Fields
```php
$api->get('/packages', [
    'where' => "is_active=true AND available_for_sale=true",
]);
```

## URL Encoding

The `where` parameter value must be URL-encoded when sent as a query string:

```php
// Laravel's HTTP client handles encoding automatically
$api->get('/items', [
    'where' => "status='Active' AND updated_at >= '2024-01-01'",
]);

// Raw URL would be:
// /items?where=status%3D%27Active%27%20AND%20updated_at%20%3E%3D%20%272024-01-01%27
```

## Incremental Sync Pattern

For BudTags auto-sync (fetching only records modified since last import):

```php
$modified_since = $last_import->started_at->subDay()->toIso8601String();

$api->get('/sales_orders', [
    'where'    => "updated_at >= '{$modified_since}'",
    'limit'    => 2000,
    'order_by' => 'updated_at asc',
]);
```

## Comparison with LeafLink

| Aspect | LeafLink | Canix |
|--------|----------|-------|
| Filter format | Individual query params | Single `where` string |
| Date filter | `modified__gte=2024-01-01` | `where=updated_at >= '2024-01-01'` |
| Status filter | `status__in=confirmed,shipped` | `where=status IN ('confirmed', 'shipped')` |
| Pattern match | `name__icontains=dream` | `where=name LIKE '%dream%'` |
| Multiple filters | Separate params | Combined with AND/OR |

## Filterable Fields by Entity

Not all fields are filterable. Common filterable fields:

- **Sales Orders**: `status`, `facility_id`, `created_at`, `updated_at`, `delivery_date`
- **Purchase Orders**: `status`, `facility_id`, `created_at`, `updated_at`
- **Items**: `facility_id`, `is_active`, `sku`, `name`, `updated_at`
- **Packages**: `status`, `is_active`, `tag`, `updated_at`
- **Customers**: `is_active`, `updated_at`
- **Plant Batches**: `updated_at`
- **Plants**: `updated_at`

---

**See:** `patterns/date-formats.md` for date format requirements in where clauses
