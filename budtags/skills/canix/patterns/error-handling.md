# Canix API Error Handling

## HTTP Status Codes

| Code | Name | Description |
|------|------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created (used by photo/file uploads) |
| 204 | No Content | Delete succeeded (no response body) |
| 400 | Bad Request | Invalid request (bad `where` syntax, missing required fields, invalid data) |
| 401 | Not Authenticated | API key missing or invalid |
| 403 | Access Denied | API key doesn't have permission for this resource |
| 404 | Not Found | Resource doesn't exist or wrong ID |
| 422 | Unprocessable | Submission data cannot be fetched (submissions endpoint only) |
| 500 | Server Error | Canix internal error |

## Common Error Scenarios

### Invalid `where` Syntax

The most common error. The `where` parameter uses SQL-like syntax — typos cause 400 errors.

```php
// ❌ WRONG — missing quotes around string value
$api->get('/sales_orders', ['where' => 'status=Active']);

// ✅ CORRECT — string values must be quoted
$api->get('/sales_orders', ['where' => "status='Active'"]);

// ❌ WRONG — using Django-style filter
$api->get('/sales_orders', ['status__in' => 'created,approved']);

// ✅ CORRECT — SQL-like IN clause
$api->get('/sales_orders', ['where' => "status IN ('created', 'approved')"]);
```

### Missing Required Fields (POST/PUT)

Write endpoints return 400 with details about missing fields.

```php
// Sales Order requires: customer_id, name, status, delivery_date, tax rates
// Item requires: name, item_type_id, weight_unit
// Purchase Order requires: facility_id, vendor_id, status, requested_delivery_date, payment_terms
// Strain requires: name
// Vendor requires: name
```

### Invalid Facility ID

If `facility_id` doesn't belong to the company, expect empty results (not an error).

### Authentication Failures

```php
// 401 — Check that X-API-KEY header is set correctly
// The header name is X-API-KEY (not Authorization, not Bearer)

// ❌ WRONG
Http::withToken($key)->get($url);                         // Bearer token
Http::withHeaders(['Authorization' => "App {$key}"])->... // LeafLink format

// ✅ CORRECT
Http::withHeaders(['X-API-KEY' => $key])->get($url);
```

## Retry Strategy

```php
// Recommended retry configuration for BudTags
$response = Http::withHeaders(['X-API-KEY' => $key])
    ->retry(3, 1000, function ($exception, $request) {
        // Retry on server errors and rate limits
        return $exception instanceof ConnectionException
            || ($exception instanceof RequestException
                && $exception->response->status() >= 500);
    })
    ->get($url, $params);
```

### When to Retry

| Scenario | Retry? | Strategy |
|----------|--------|----------|
| 500 Server Error | Yes | Exponential backoff (1s, 2s, 4s) |
| Connection timeout | Yes | Immediate retry, max 3 |
| 400 Bad Request | No | Fix the request (bad syntax) |
| 401 Not Authenticated | No | Fix the API key |
| 403 Access Denied | No | Wrong permissions |
| 404 Not Found | No | Wrong ID or endpoint |
| 429 Rate Limited | Yes | Wait and retry (if Canix implements this) |

## Error Logging in BudTags

```php
// Use LogService, never Log facade
LogService::store(
    'Canix API Error',
    "GET /sales_orders returned {$response->status()}",
    $importJob,
);
```

---

**See:** `patterns/async-submissions.md` for handling errors on async write operations
