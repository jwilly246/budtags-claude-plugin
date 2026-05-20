# Pattern — Error Handling

Distru does **not document its error response format** in the public docs. Treat error bodies as opaque and route by HTTP status code.

## HTTP Status Codes (observed and inferred)

| Code | Meaning | Retry? | Notes |
|------|---------|--------|-------|
| 200 | Success | — | |
| 201 | Created (writes) | — | Response includes the new resource id |
| 400 | Bad Request | No (fix request) | Malformed body or invalid field |
| 401 | Unauthorized | No (refresh credentials) | Wrong header, expired/revoked token |
| 403 | Forbidden | No | Token team permissions exclude this resource |
| 404 | Not Found | No | Unknown id or removed resource |
| 409 | Conflict | Maybe | Concurrent modification (verify per endpoint) |
| 422 | Unprocessable | No (fix payload) | Validation failure |
| 429 | Too Many Requests | **Yes (back off)** | Rate limit (undocumented but assumed) |
| 5xx | Server Error | **Yes (retry)** | Transient — exponential backoff |

## Retry Strategy

Mirror the `CanixApi` retry policy:

- **3 retries** on 5xx and `Illuminate\Http\Client\ConnectionException`.
- **Exponential backoff** starting at 1s, capped at 30s.
- **429**: respect `Retry-After` if present; otherwise back off.
- **Never retry** 4xx other than 408/429.

```php
$response = Http::retry(3, 1000, function (\Throwable $e, $request) {
    if ($e instanceof ConnectionException) return true;
    if ($e->response?->status() >= 500) return true;
    if ($e->response?->status() === 429) return true;
    return false;
})->withHeaders(...)->get(...);
```

## Error Body — Treat as Opaque

The public docs do not commit to a schema. Examples of shapes observed across similar APIs (any may apply):

```jsonc
// Possibility A
{ "error": "Unauthorized" }

// Possibility B
{ "errors": [ { "code": "...", "message": "..." } ] }

// Possibility C
"Plain text body"
```

When logging, **capture both the status code and the raw body** — never assume a parseable structure. Surface `status code + first 200 chars of body` in error events.

## Write-Specific Errors

Because writes are UPSERT with no idempotency keys, a 5xx after a write is **ambiguous** — the write may have committed before the failure. Recovery:

1. Catch the error.
2. Re-fetch by the natural key (SKU, order number) and inspect.
3. If present, reconcile — store the discovered id.
4. If absent, retry the write.

See `patterns/write-safety.md` for the full UPSERT discussion.

## Logging Conventions

For Budtags, use the BaseMarketplaceApi's structured logger:

```php
Log::warning('distru.api.error', [
    'method' => $method,
    'path' => $path,
    'status' => $response->status(),
    'body' => Str::limit($response->body(), 500),
    'org_id' => $org->id,
]);
```

## Cross-references

- Write retry semantics: `patterns/write-safety.md`
- Authentication errors: `patterns/authentication.md`
