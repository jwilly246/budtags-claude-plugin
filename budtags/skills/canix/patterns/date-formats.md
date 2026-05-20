# Canix API Date Formats

## Timestamp Format

Canix uses ISO 8601 timestamps with millisecond precision and UTC timezone:

```
2018-11-06T08:00:00.000Z
2021-05-24T19:58:00.000Z
```

## Date-Only Format

Some fields use date-only format (no time component):

```
2021-06-07
2024-02-03
```

## Common Date Fields by Entity

### Timestamps (ISO 8601 with time)
- `created_at` — When record was created in Canix (most entities)
- `updated_at` — When record was last modified (most entities)
- `submitted_date` — When audited action was submitted
- `approval_date` — When audited action was approved

### Dates (date-only)
- `delivery_date` — Sales/purchase order delivery date
- `payment_date` — When payment was made/due
- `packaged_date` — When package was created
- `expiration_date` — Package or BOM expiration
- `received_date` — When package was received
- `harvest_date` — When harvest occurred
- `planted_date` — When plant/batch was planted
- `vegetative_date` — When plant entered veg phase
- `flowering_date` — When plant entered flowering
- `harvested_date` — When plant was harvested
- `destroyed_date` — When plant was destroyed
- `start_date` — Manufacturing run or standard cost start
- `end_date` — Manufacturing run or standard cost end
- `active_date` — BOM active date
- `license_expiration_date` — Customer/vendor license expiry
- `production_batch_date` — Package production batch date
- `test_date` — Lab test date

## Laravel Carbon Formatting

```php
// Parse Canix timestamp
$date = Carbon::parse('2021-05-24T19:58:00.000Z');

// Format for Canix API (write operations)
$canix_timestamp = $date->toIso8601String();    // 2021-05-24T19:58:00+00:00
$canix_date = $date->format('Y-m-d');           // 2021-05-24

// For where filters
$where = "updated_at >= '{$date->format('Y-m-d')}'";
```

## Date Filtering in WHERE Clause

```php
// Filter by date range
$api->get('/sales_orders', [
    'where' => "updated_at >= '2024-01-01' AND updated_at <= '2024-12-31'",
]);

// Incremental sync (modified since last import)
$since = $last_import->started_at->subDay()->format('Y-m-d\TH:i:s.000\Z');
$api->get('/sales_orders', [
    'where' => "updated_at >= '{$since}'",
]);
```

## Key Notes

- All timestamps are in **UTC** (Z suffix)
- Date-only fields have no timezone — treated as local to the facility
- The `where` filter accepts both timestamp and date-only formats
- `order_by=updated_at asc` is recommended for incremental imports

---

**See:** `patterns/filtering.md` for complete WHERE clause syntax
