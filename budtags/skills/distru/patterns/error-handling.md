# Pattern — Error Handling

Distru returns standard HTTP status codes but has some specific quirks worth documenting — notably **silent failure** on unknown filter params (no 400) and **HTTP 422** for quota/storage exhaustion on `/file-attachments`.

**Phase 0.5 audited 2026-05-21.** Mapping doc: `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md`.

## HTTP status codes observed

| Code | Meaning | Notes |
|---|---|---|
| 200 | OK | Includes successful reads and successful UPSERT writes |
| 400 | Bad Request | Wrong status enum casing, invalid filter value type, validation failure |
| 401 | Unauthorized | Missing `Authorization: Bearer <jwt>` header |
| 403 | Forbidden | API key lacks RBAC permission for the endpoint |
| 404 | Not Found | Resource ID doesn't exist OR slug is wrong (e.g. `/stock_adjustments` → 404) |
| 422 | Unprocessable Entity | **`/file-attachments` quota exceeded** (storage limit) |
| 429 | Too Many Requests | Rate limit (rate limit details not documented) |
| 500 | Internal Server Error | Server timeout — most commonly seen on `/orders` unfiltered (~20s) |

## Important quirk — Silent failure on unknown filters

Distru does NOT return 400 for unrecognized query parameters. It returns 200 with unfiltered results.

```bash
GET /public/v1/orders?relationship_type=Customer
# Returns 200 with ALL orders — the typo'd filter is silently ignored
```

This means you cannot rely on Distru's HTTP response to validate your filter parameters. Defensive coding:

- Log the filter params sent vs the result-count expected.
- Track filter param names in code; don't accept arbitrary strings.
- Match observed Phase 0.5 filter catalogs (see `patterns/filtering.md`).

## HTTP 422 on `/file-attachments` quota

Distru tracks per-tenant storage quotas for file attachments. When a customer is near or over their quota:

```
POST /public/v1/file-attachments
{ ... file upload ... }
→ 422 Unprocessable Entity
{ "error": "Storage quota exceeded" }
```

This is unique to `/file-attachments`. Other POST endpoints return 200/400.

Handling: catch 422 specifically on file uploads and surface to the user as "storage quota exceeded" rather than a generic "request invalid" error.

## HTTP 400 patterns

Most 400 errors include a JSON body with field-level validation messages:

```jsonc
{
  "errors": {
    "status": ["is not included in the list"],
    "items.0.product_id": ["can't be blank"]
  }
}
```

Common causes:
- **Status enum casing wrong** — sending `"PENDING"` to /purchases filter (which requires Title Case `"Pending"`)
- **Status enum typo** — `"CANCELLED"` (double L) instead of `"CANCELED"` (single L)
- **Non-sparse update missing required fields** — items[] omitted but the order had items
- **Blaze-retailer order without `blaze_payment_type`**
- **Sending `full_name` on /contacts** (server-derived, write-rejected)
- **Editing a purchase past `Pending`** (server-side immutability)

## HTTP 500 — server timeouts

The most common 500 cause is endpoint timeout, not actual server crash:

- `/orders` unfiltered → 500 after ~20s (high-volume orgs)
- `/assemblies` page > 5,000 → 500 after ~60s on large orgs
- `/inventory` with `grouping[]=PACKAGE` on 10k+ packages → 500 if no other narrowing

**Strategy:** always pass a narrowing filter on high-volume endpoints. Set HTTP client timeout to ~60s minimum for `/assemblies`.

## HTTP 429 — rate limiting

Distru does not document its rate limit. Observed in Phase 0.5: sequential single-threaded requests never hit it; parallel 10x requests caused intermittent 429s. The 429 response includes no `Retry-After` header.

**Strategy:** sequential pagination, exponential backoff on 429 (retry after 5s → 15s → 30s, then fail).

## Retry strategy

Distru does NOT support idempotency keys on POST. Retries on writes are risky:

| Scenario | Safe to retry? |
|---|---|
| GET returning 500 / 429 | Yes — idempotent |
| POST returning 500 with no response body | **No** — write may have succeeded silently. Capture response `id` if present; reconcile by querying. |
| POST returning 429 | Yes if same payload (likely never reached server), but verify if it has `id` field |
| POST returning 400 | No — validation failure, fix the payload |
| POST returning 200 | Confirmed success — capture `id` |

For UPSERT writes (the only write pattern Distru exposes), the safest pattern is:

1. Send POST with optional `id`.
2. If 500/timeout, query the entity by your local idempotency key (e.g. order_number) to verify whether the create succeeded.
3. Only retry once you've confirmed the resource doesn't exist.

## Error handling pattern (PHP)

```php
try {
    $response = $api->post('/orders', $payload);
} catch (RequestException $e) {
    $status = $e->response->status();
    if ($status === 422 && str_contains($e->getMessage(), 'quota')) {
        throw new DistruQuotaException(...);
    }
    if ($status === 400) {
        $errors = $e->response->json('errors', []);
        throw new DistruValidationException($errors);
    }
    if ($status === 403) {
        throw new DistruPermissionException('Missing RBAC: see system.md');
    }
    if ($status === 500 || $status === 429) {
        // Idempotency-safe retry logic here
        return $this->retryWithBackoff(...);
    }
    throw $e;
}
```

## Cross-references

- Write safety semantics: `patterns/write-safety.md`
- RBAC permissions reference: `categories/system.md`
- Per-endpoint validation specifics: each `categories/*.md`
- Filter param silent-ignore: `patterns/filtering.md`
