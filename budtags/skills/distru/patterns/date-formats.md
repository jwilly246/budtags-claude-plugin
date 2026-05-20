# Pattern — Date Formats

Distru uses **ISO 8601** for all timestamps. Date-only fields use the `YYYY-MM-DD` form. Timezone handling is **not explicitly documented** — assume UTC and always send a Z suffix on timestamps to be safe.

## Timestamps (full)

```
2026-05-16T14:42:00Z
2026-05-16T14:42:00.000Z
2026-05-16T14:42:00+00:00
```

All three are valid ISO 8601. Prefer the `Z` form for clarity.

## Date-only fields

```
2026-05-16
```

Used for fields like `expiration_date`. Distru treats these as calendar dates with no timezone.

## Sending Filters

```php
$filterFrom = now()->subDays(7)->utc()->toIso8601String(); // 2026-05-09T14:42:00+00:00
$api->get('/orders', ['updated_at_from' => $filterFrom]);
```

If you have a Carbon instance:

```php
$carbon->utc()->format('Y-m-d\TH:i:s\Z'); // 2026-05-16T14:42:00Z
```

## Parsing Responses

```php
$createdAt = Carbon::parse($order['created_at']); // Carbon auto-detects ISO 8601
$expDate   = Carbon::parse($batch['expiration_date'])->startOfDay();
```

## Timezone Footguns

- Distru's UI may display times in the **user's local timezone**, but the API returns UTC. A "noon Pacific" event surfaces as `19:00:00Z` (or `20:00:00Z` during DST).
- When importing into Budtags, normalize to UTC and store. Render in the user's tz at the view layer.
- When writing, **always send UTC**. Sending a local-time string without an offset is undefined behavior.

## Cross-references

- Filter usage: `patterns/filtering.md`
- Eventual consistency on Strains/Assemblies: `patterns/eventual-consistency.md`
