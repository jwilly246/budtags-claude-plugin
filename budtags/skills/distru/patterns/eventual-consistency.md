# Pattern — Eventual Consistency

A subset of Distru endpoints exhibit **eventually-consistent read-after-write** behavior. A successful POST returns the resource, but subsequent GETs may not yet include it for ~1 second.

**Phase 0.5 audited 2026-05-21.** Mapping doc: `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md` (Section 10).

## Affected endpoints (Phase 0.5 audit)

| Endpoint | Lag observed | Notes |
|---|---|---|
| `/strains` | ~1s | POST returns 200 with new strain; subsequent `GET /strains?name=...` may not include it for ~1s |
| `/assemblies` | ~1s | Same pattern — created assembly takes ~1s to appear in list. Detail GET by ID returns immediately. |
| `/products` | ~1s | POST returns 200; list scan may briefly omit. Detail GET by ID is consistent. |
| `/test-results` | ~1s | Same pattern as /products |

## NOT eventually consistent (Phase 0.5 audit)

| Endpoint | Confirmed consistent |
|---|---|
| `/orders` | POST → GET by id consistent. List by `updated_datetime` filter includes new order immediately. |
| `/invoices` | Same as orders |
| `/purchases` | Same as orders |
| `/companies` | Consistent |
| `/contacts` | Consistent |
| `/locations` | Consistent |
| `/batches`, `/packages`, `/adjustments` | Consistent (these are side-effects of order/purchase/assembly completion, not direct writes) |

## What "eventually consistent" means here

After `POST /strains` returns HTTP 200 with the new strain's `id`:

- `GET /strains/{id}` (detail) → consistent immediately (returns the new strain).
- `GET /strains` (list) or `GET /strains?name=NewStrain` (filtered list) → MAY NOT include the new strain for ~1s.

The detail endpoint is backed by a strong-consistency primary read; the list endpoint is backed by a search index that lags. This is normal for sharded search indices (likely Elasticsearch / OpenSearch behind the scenes).

## Why this matters for the importer

The naive sync pattern:

1. POST a new strain
2. GET the strain by some property (e.g., `?name=...`)
3. Use the returned id

…fails intermittently on the affected endpoints. Step 2 returns an empty list because the index hasn't caught up. The importer then thinks the create failed and may retry, creating a duplicate.

## Mitigation patterns

### Pattern 1 — Use the POST response

The POST response includes the new resource's `id`. Use it directly instead of querying:

```php
$result = $api->post('/strains', ['name' => 'New Strain', 'type' => 'Hybrid']);
$strainId = $result['id'];      // available immediately, consistent
```

This is the recommended pattern — no querying needed at all.

### Pattern 2 — Detail GET, not list query

When you must verify, use `GET /strains/{id}` instead of `GET /strains?name=...`:

```php
$verify = $api->get("/strains/{$strainId}");      // strong consistency on detail GET
```

### Pattern 3 — Polling with backoff (when forced to use list query)

If you absolutely must query by a non-id property and can't use the POST response:

```php
function findStrainByName(string $name): ?array
{
    $retries = 0;
    $maxRetries = 5;
    $delay = 200_000;   // 200ms initial

    while ($retries < $maxRetries) {
        $result = $api->get('/strains', ['name' => $name]);
        if (!empty($result['data'])) {
            return $result['data'][0];
        }
        usleep($delay);
        $delay *= 2;     // backoff
        $retries++;
    }
    return null;
}
```

Bound the retry budget — eventual consistency lag should be sub-second. If you're still empty after 5 retries (~6.4s total), the resource truly doesn't exist.

## Detection in tests

When writing Phase B integration tests, account for the ~1s lag:

```php
public function test_strain_create_appears_in_list(): void
{
    $strain = $api->post('/strains', ['name' => 'Test Strain', 'type' => 'Hybrid']);

    // Detail GET is immediately consistent — assert against this
    $detailGet = $api->get("/strains/{$strain['id']}");
    $this->assertEquals($strain['id'], $detailGet['id']);

    // Don't assert against list query immediately — it lags
    // If you must, add sleep or polling:
    sleep(2);
    $listResult = $api->get('/strains', ['name' => 'Test Strain']);
    $this->assertNotEmpty($listResult['data']);
}
```

## Why this isn't documented by Distru

Distru's public docs don't mention eventual consistency. The behavior was observed empirically in Phase 0.5 during live API audit. It is **not a bug** — it's a normal property of separating primary writes from search-index reads. But the docs don't warn about it, so importer code must.

## Cross-references

- Pagination interaction (final-page detection): `patterns/pagination.md`
- Write safety: `patterns/write-safety.md`
- Mapping doc Section 10 (API Quirks): canonical reference
