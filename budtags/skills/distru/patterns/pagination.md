# Pattern — Pagination

Distru uses **page-number based pagination** with one critical twist: the `next_page` field in the response envelope is a **FULL URL STRING** (not an integer page number, not a cursor token). Treat it as opaque and follow it verbatim.

**Phase 0.5 audited 2026-05-21.** Mapping doc: `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md` (Section 10, API Quirks).

## Response envelope

```jsonc
{
  "data": [ /* records */ ],
  "next_page": "https://app.distru.com/public/v1/orders?page%5Bnumber%5D=2&...",   // FULL URL STRING
}
// OR on final page:
{
  "data": [ /* records */ ],
  "next_page": null
}
// OR on final page (alternate, depending on endpoint):
{
  "data": [ /* records */ ]
  // next_page key OMITTED entirely
}
```

**Final-page detection:** check `empty($body['next_page'])` (Laravel/PHP idiom) — this handles both `null` and missing-key. Do NOT check `isset($body['next_page'])` alone (returns true for null value).

## `next_page` is a URL — not a page number

The mistake to avoid: don't parse the URL and reconstruct it. Distru includes the original query parameters (filters, page[size], custom params) baked into the URL. The simplest correct loop:

```php
$url = '/public/v1/orders?updated_datetime=2026-01-01T00:00:00Z,';
while ($url) {
    $response = $api->get($url);
    foreach ($response['data'] as $record) {
        process($record);
    }
    $url = $response['next_page'] ?? null;          // follow blindly
}
```

If you reconstruct the URL with your own `page[number]` increment, you'll silently drop filter params and re-fetch the unfiltered first page repeatedly until OOM.

## Page-size parameter is mostly NON-FUNCTIONAL

`page[size]` is **silently ignored** on most endpoints. Distru applies a per-endpoint hardcoded cap regardless of what you request:

| Endpoint | Effective page size |
|---|---|
| `/strains` | 50,000 (highest cap in API) |
| `/products`, `/batches`, `/packages`, `/adjustments`, `/inventory`, `/test-results`, `/companies`, `/payment-methods`, `/assemblies` | 5,000 |
| `/contacts`, `/locations`, `/users` | 1,000 |
| `/orders`, `/purchases`, `/invoices`, `/menus` | 500 |

The cap is **not the value you sent** — it's the server-side default per endpoint. Don't expect `page[size]=10` to actually return 10 records on most endpoints (it will return up to the cap). Treat `page[size]` as a hint; expect responses up to the endpoint's hardcoded cap.

Exceptions where `page[size]` does work: setting it to a *smaller* value than the cap reduces returned record count proportionally on some endpoints (notably `/strains` and a few others). Setting it *higher* than the cap has no effect.

## Pagination params

- `page[number]` — 1-indexed (first page is `page[number]=1`)
- `page[size]` — usually ignored, see above

## Recommended client pattern

```php
class DistruPaginator
{
    public function __construct(private DistruClient $client) {}

    public function each(string $initialPath, array $query = []): Generator
    {
        $url = $initialPath;
        if (!empty($query)) {
            $url .= '?' . http_build_query($query);
        }

        while ($url) {
            $response = $this->client->get($url);
            foreach ($response['data'] as $record) {
                yield $record;
            }
            $url = $response['next_page'] ?? null;
        }
    }
}

// Usage
foreach ($paginator->each('/orders', ['updated_datetime' => '2026-01-01,']) as $order) {
    // process each order
}
```

The Generator pattern avoids materializing the full dataset in memory — important for high-volume endpoints like `/companies` (5k+) or `/strains` (potentially 50k+).

## Performance tips

- **Always include an `updated_datetime` filter for incremental syncs.** Unfiltered calls on `/orders` time out at HTTP 500 (~20s) on high-volume orgs.
- **`/assemblies` is the slowest endpoint** — 20-30s per page. Use background queues; set HTTP client timeouts to 60s+.
- **Don't parallelize pagination** — Distru doesn't document rate limits, but issuing 10 concurrent page requests is a fast way to get throttled or 429'd. Sequential is safer.
- **Eventual consistency** on Strains/Assemblies/Products/TestResults: a write may take ~1s to appear in subsequent GETs. Re-poll if a newly-created record isn't returned.

## Cross-references

- Filter parameter conventions: `patterns/filtering.md`
- Eventual consistency details: `patterns/eventual-consistency.md`
- Error handling and timeouts: `patterns/error-handling.md`
