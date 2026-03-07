# Unleashed API Error Handling

HTTP status codes, common errors, and retry strategies.

---

## HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response normally |
| 400 | Bad Request | Validation error - check request body/params |
| 401 | Unauthorized | Verify API ID and HMAC signature |
| 404 | Not Found | Check GUID exists or resource path is correct |
| 405 | Method Not Allowed | Resource doesn't support that HTTP method |
| 500 | Internal Server Error | Retry with exponential backoff |

---

## Common Error Scenarios

### 1. Signature Mismatch (401)
**Cause**: Query string used for HMAC signing doesn't match the actual URL
**Fix**: Ensure the raw query string (without `?`) matches exactly what's in the URL

### 2. Invalid GUID (404)
**Cause**: Resource with that GUID doesn't exist or was deleted
**Fix**: Verify the GUID is correct, check if the resource still exists

### 3. Missing Required Field (400)
**Cause**: POST/PUT body missing a required field
**Fix**: Check the category file for required fields per resource

### 4. Field Validation (400)
**Cause**: Value exceeds max length, wrong type, or invalid format
**Fix**: Check field constraints (max lengths, date formats, enum values)

### 5. Data Loss from Partial PUT (200 but wrong data)
**Cause**: PUT request didn't include all fields - missing ones got blanked
**Fix**: Always GET before PUT. See `patterns/full-object-updates.md`

### 6. Duplicate Code (400)
**Cause**: Trying to create a resource with a code that already exists
**Fix**: Check for existing resource first, or use update instead

---

## Retry Strategy

No documented rate limits, but recommend conservative approach:

```php
public function request_with_retry(string $method, string $url, array $data = [], int $max_retries = 3): mixed
{
    $attempt = 0;

    while ($attempt < $max_retries) {
        $response = $this->make_request($method, $url, $data);

        if ($response->successful()) {
            return $response->json();
        }

        // Don't retry client errors (4xx) - fix the request instead
        if ($response->status() >= 400 && $response->status() < 500) {
            throw new UnleashedException(
                "Unleashed API error {$response->status()}: {$response->body()}"
            );
        }

        // Retry server errors (5xx) with exponential backoff
        $attempt++;
        if ($attempt < $max_retries) {
            sleep(pow(2, $attempt)); // 2s, 4s
        }
    }

    throw new UnleashedException("Unleashed API failed after {$max_retries} retries");
}
```

---

## Timeout Handling

- Reduce `pageSize` for large dataset requests
- Default timeout: 30 seconds recommended
- Large page sizes (500+) may cause slow responses

---

## Logging (BudTags Convention)

```php
LogService::store(
    type: 'unleashed_api_error',
    message: "Unleashed API {$status}: {$endpoint}",
    data: ['response' => $body, 'request' => $payload],
);
```

Never use `Log::info()` or `\Log::` - always use `LogService::store()`.
