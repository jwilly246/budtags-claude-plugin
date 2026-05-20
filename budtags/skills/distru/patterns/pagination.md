# Pattern — Pagination

Distru uses **page-number pagination** with an explicit `next_page` indicator in the response envelope.

## Request Parameters

| Param | Default | Notes |
|-------|---------|-------|
| `page[number]` | 1 | 1-based page index |
| `page[size]` | varies | Records per page; ignored on Assemblies (fixed 500) |

> Note the **bracket-key syntax** — `page[number]` and `page[size]` are URL parameter names with literal brackets. Most HTTP clients will URL-encode these for you; verify by inspecting the outgoing request if you see unexpected 400s.

## Response Envelope

```jsonc
{
  "data": [ /* records */ ],
  "next_page": 3        // or null on the last page
}
```

## Terminal Detection

```php
$page = 1;
do {
    $response = $api->get('/orders', [
        'page[number]' => $page,
        'page[size]'   => 100,
    ]);

    foreach ($response['data'] as $record) {
        // process record
    }

    $page++;
} while ($response['next_page'] !== null);
```

**Stop when `next_page === null`** — and treat a missing `next_page` field the same as `null`.

> **Do NOT use `count($response['data']) < $pageSize`.** The Assemblies endpoint always returns up to 500 per page regardless of what you asked for, so a "short page" signal is unreliable across endpoints.

## Endpoint Quirks

| Endpoint | Quirk |
|----------|-------|
| `/assemblies` | Fixed 500 per page. `page[size]` is ignored. |
| (most others) | Configurable `page[size]`, typically 50-500 supported |

## Avoid Re-paginating

If the dataset is being modified concurrently (orders are being created during your import), records can shift across pages. Strategies:

- Filter by an `updated_at` window so the result set is stable.
- Or pull a snapshot ordered by `id` ascending and accept that newer-than-snapshot records arrive on the next import.

## Pitfalls

- Treating absent `next_page` as "I don't know, keep going" — treat it as `null` (terminal).
- Hardcoding `page[size]=500` — only valid for Assemblies; other endpoints may cap lower.
- Skipping pages on retry after a transient error — restart pagination from the failed page, not from `page[number] + 1`.

## Cross-references

- Filtering for stable pagination: `patterns/filtering.md`
- Assemblies quirk: `categories/manufacturing.md`
