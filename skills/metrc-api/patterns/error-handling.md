# Error Handling

Comprehensive guide to handling Metrc API errors, status codes, and retry strategies.

---

## HTTP Status Codes

| Code | Meaning | Common Causes | Action |
|------|---------|---------------|--------|
| **200** | Success | Request succeeded | Process response data |
| **400** | Bad Request | Invalid parameters, malformed JSON | Fix request format |
| **401** | Unauthorized | Invalid API key, wrong auth | Check authentication |
| **403** | Forbidden | License type mismatch | Check license compatibility |
| **404** | Not Found | Entity doesn't exist, wrong endpoint | Verify IDs/endpoints |
| **413** | Request Entity Too Large | More than 10 objects in request | Chunk into batches of 10 |
| **429** | Too Many Requests | Rate limit exceeded | Use Retry-After header |
| **500** | Server Error | Metrc internal error | Retry with backoff |
| **503** | Service Unavailable | Metrc maintenance/downtime | Retry later |

---

## Error Response Format

Metrc returns errors as plain text or JSON:

```json
{
  "Message": "Package label not found",
  "Field": "Label",
  "Value": "INVALID-TAG"
}
```

Or simple text:
```
Invalid license number
```

---

## Laravel Error Handling

```php
class MetrcApi
{
    public function get(string $endpoint, array $params = []): array
    {
        try {
            $response = Http::withHeaders($this->getHeaders())
                ->get($this->baseUrl . $endpoint, $params);

            // Check for HTTP errors
            if ($response->failed()) {
                $this->handleHttpError($response, $endpoint);
            }

            return $response->json();

        } catch (\Illuminate\Http\Client\ConnectionException $e) {
            // Network/connection errors
            Log::error("Metrc connection failed: {$endpoint}", [
                'error' => $e->getMessage()
            ]);
            throw new \Exception("Failed to connect to Metrc API. Please try again.");

        } catch (\Exception $e) {
            // General errors
            Log::error("Metrc API error: {$endpoint}", [
                'error' => $e->getMessage()
            ]);
            throw $e;
        }
    }

    private function handleHttpError($response, string $endpoint): void
    {
        $status = $response->status();
        $body = $response->body();

        // Try to parse JSON error
        $error = $response->json();
        $message = $error['Message'] ?? $body;

        switch ($status) {
            case 400:
                throw new \InvalidArgumentException("Bad request to {$endpoint}: {$message}");
            case 401:
                throw new \Exception("Metrc authentication failed. Check API key.");
            case 403:
                throw new \Exception("Access forbidden. Check license type compatibility.");
            case 404:
                throw new \Exception("Resource not found: {$message}");
            case 413:
                throw new \Exception("Request too large. Metrc limits requests to 10 objects maximum.");
            case 429:
                $retryAfter = $response->header('Retry-After') ?? 60;
                throw new \Exception("Rate limit exceeded. Retry after {$retryAfter} seconds.");
            case 500:
            case 503:
                throw new \Exception("Metrc server error. Please try again later.");
            default:
                throw new \Exception("Metrc API error ({$status}): {$message}");
        }
    }
}
```

---

## Rate Limiting

Metrc enforces rate limits to ensure fair usage for all users. The exact rate limits depend on your Metrc agreement and service tier.

### Per-Facility vs Per-API-Key

**Rate limits apply differently based on endpoint type:**

- **Per-Facility Basis** (most endpoints):
  - Endpoints that require `licenseNumber` parameter
  - Rate limit is shared across all API keys for that facility
  - Examples: `/packages/v1/active?licenseNumber=123-ABC`

- **Per-API-Key Basis** (few endpoints):
  - Endpoints that do NOT require `licenseNumber`
  - Rate limit is per individual API key
  - Examples: `/facilities/v1/` (list all facilities)

**Implication:** If multiple users in your organization use the same facility license, they share the same rate limit pool.

### Detection and Retry-After Header

When you exceed the rate limit, Metrc returns HTTP 429 with a **Retry-After header** that tells you exactly how many seconds to wait:

```php
if ($response->status() === 429) {
    // IMPORTANT: Use Retry-After header (not guesswork)
    $retryAfter = (int) $response->header('Retry-After');

    if ($retryAfter) {
        // Metrc tells us exactly when to retry
        throw new RateLimitException("Rate limited. Retry after {$retryAfter} seconds.");
    } else {
        // Fallback if header missing (rare)
        throw new RateLimitException("Rate limited. Retry after 60 seconds.");
    }
}
```

**Best Practice:** Always respect the `Retry-After` header value. Don't use hardcoded delays or exponential backoff for 429 errors - Metrc tells you the exact wait time.

### Retry Strategy with Retry-After

```php
private function getWithRetry(string $endpoint, array $params = [], int $maxRetries = 3): array
{
    $attempt = 0;

    while ($attempt < $maxRetries) {
        try {
            $response = Http::withHeaders($this->getHeaders())
                ->get($this->baseUrl . $endpoint, $params);

            if ($response->successful()) {
                return $response->json();
            }

            // Handle rate limiting specifically
            if ($response->status() === 429) {
                $retryAfter = (int) $response->header('Retry-After', 60);

                Log::warning("Rate limited on {$endpoint}. Waiting {$retryAfter} seconds.", [
                    'attempt' => $attempt + 1,
                    'maxRetries' => $maxRetries
                ]);

                if ($attempt < $maxRetries - 1) {
                    sleep($retryAfter);
                    $attempt++;
                    continue;
                }
            }

            // Other errors
            $this->handleHttpError($response, $endpoint);

        } catch (\Exception $e) {
            if ($attempt >= $maxRetries - 1) {
                throw $e;
            }
            $attempt++;
        }
    }

    throw new \Exception("Max retries exceeded for {$endpoint}");
}
```

### Exponential Backoff (For Non-Rate-Limit Errors)

```php
class MetrcApi
{
    private function getWithRetry(string $endpoint, array $params = [], int $maxRetries = 3): array
    {
        $attempt = 0;
        $delay = 1; // Start with 1 second

        while ($attempt < $maxRetries) {
            try {
                return $this->get($endpoint, $params);

            } catch (\Exception $e) {
                $attempt++;

                if ($this->shouldRetry($e) && $attempt < $maxRetries) {
                    Log::warning("Retrying Metrc request (attempt {$attempt}/{$maxRetries})", [
                        'endpoint' => $endpoint,
                        'error' => $e->getMessage()
                    ]);

                    sleep($delay);
                    $delay *= 2; // Exponential backoff: 1s, 2s, 4s
                } else {
                    throw $e;
                }
            }
        }

        throw new \Exception("Max retries exceeded for {$endpoint}");
    }

    private function shouldRetry(\Exception $e): bool
    {
        $message = $e->getMessage();

        // Retry on rate limit or server errors
        return str_contains($message, '429') ||
               str_contains($message, '500') ||
               str_contains($message, '503') ||
               str_contains($message, 'connection') ||
               str_contains($message, 'timeout');
    }
}
```

---

## HTTP 413: Request Entity Too Large

Metrc enforces a **10 object maximum** per request for all POST/PUT/DELETE operations that accept an array of objects.

### Detection

```php
if ($response->status() === 413) {
    throw new \Exception("Request too large. Metrc limits requests to 10 objects maximum. Chunk your data into batches of 10 or fewer.");
}
```

### Solution: Chunking

When you have more than 10 objects to send, you must **chunk** them into batches:

```php
public function createPackages(array $packages, string $license): array
{
    $BATCH_SIZE = 10;
    $createdIds = [];

    // Split into chunks of 10
    $chunks = array_chunk($packages, $BATCH_SIZE);

    foreach ($chunks as $index => $chunk) {
        try {
            $response = Http::withHeaders($this->getHeaders())
                ->post($this->baseUrl . "/packages/v2/create?licenseNumber={$license}", $chunk);

            if ($response->successful()) {
                // Metrc returns array of created IDs
                $ids = $response->json();
                $createdIds = array_merge($createdIds, $ids);

                Log::info("Created batch {$index} of packages", [
                    'count' => count($chunk),
                    'ids' => $ids
                ]);

                // Add delay between batches to avoid rate limiting
                if ($index < count($chunks) - 1) {
                    sleep(1);
                }
            } else {
                throw new \Exception("Failed to create packages batch {$index}: " . $response->body());
            }

        } catch (\Exception $e) {
            Log::error("Package creation batch {$index} failed", [
                'error' => $e->getMessage(),
                'batch' => $chunk
            ]);

            // Decision: Continue with remaining batches or stop?
            // throw $e;  // Stop on first error
            // OR continue with remaining batches
        }
    }

    return $createdIds;
}
```

### Common Causes

- Creating more than 10 packages at once
- Adjusting more than 10 package quantities
- Recording more than 10 sales receipts
- Any bulk operation exceeding 10 objects

**See Also:** [Object Limiting Pattern](./object-limiting.md) for comprehensive chunking strategies.

---

## Validation Errors

```php
public function create_packages(Request $request)
{
    try {
        // Validate before sending to Metrc
        $this->validatePackages($request->packages);

        // Send to Metrc
        $api->post("/packages/v2/create?licenseNumber={$license}", $request->packages);

    } catch (\InvalidArgumentException $e) {
        // Our validation error
        return redirect()->back()->with('error', $e->getMessage());

    } catch (\Exception $e) {
        // Metrc API error
        Log::error("Package creation failed", [
            'packages' => $request->packages,
            'error' => $e->getMessage()
        ]);

        return redirect()->back()->with('error', 'Failed to create packages: ' . $e->getMessage());
    }
}

private function validatePackages(array $packages): void
{
    foreach ($packages as $index => $package) {
        if (empty($package['Tag'])) {
            throw new \InvalidArgumentException("Package {$index}: Tag is required");
        }

        if (empty($package['Item'])) {
            throw new \InvalidArgumentException("Package {$index}: Item is required");
        }

        if (!isset($package['Quantity']) || $package['Quantity'] <= 0) {
            throw new \InvalidArgumentException("Package {$index}: Quantity must be > 0");
        }
    }
}
```

---

## Common Error Scenarios

### 1. "Package label not found"

**Cause**: Tag doesn't exist or already used

**Fix**:
```php
// Check tag availability first
$availableTags = $api->get("/tags/v2/package/available?licenseNumber={$license}");
$tagLabels = array_column($availableTags, 'Label');

if (!in_array($package['Tag'], $tagLabels)) {
    throw new \Exception("Tag {$package['Tag']} not available");
}
```

### 2. "Item not found"

**Cause**: Item doesn't exist in Metrc

**Fix**:
```php
// Verify item exists
$items = $api->get("/items/v2/active?licenseNumber={$license}");
$itemNames = array_column($items, 'Name');

if (!in_array($package['Item'], $itemNames)) {
    throw new \Exception("Item '{$package['Item']}' not found in Metrc");
}
```

### 3. "No valid endpoint found" (401/403)

**Cause**: License type can't access endpoint

**Fix**:
```php
// Check license type before calling plant endpoints
$licenseType = explode('-', $license)[1];

if ($licenseType !== 'C') {
    throw new \Exception("Plant endpoints require cultivation license");
}
```

### 4. "Invalid date format"

**Cause**: Wrong date format

**Fix**:
```php
// Use ISO 8601 format
$date = now()->format('Y-m-d'); // YYYY-MM-DD
```

---

## Logging Best Practices

```php
// Log all API calls (without sensitive data)
Log::info("Metrc API call", [
    'endpoint' => $endpoint,
    'method' => 'GET',
    'license' => substr($license, 0, 8) . '***', // Partial license for privacy
    'params' => array_keys($params) // Keys only, not values
]);

// Log errors with context
Log::error("Metrc API error", [
    'endpoint' => $endpoint,
    'status' => $response->status(),
    'error' => $response->body(),
    'request_data' => json_encode($data),
    'user_id' => auth()->id(),
    'org_id' => auth()->user()->active_org_id
]);
```

---

## Circuit Breaker Pattern

For high-availability systems:

```php
use Illuminate\Support\Facades\Cache;

class MetrcCircuitBreaker
{
    private const FAILURE_THRESHOLD = 5;
    private const TIMEOUT_SECONDS = 60;

    public function execute(callable $callback)
    {
        $key = 'metrc_circuit_breaker';
        $failures = Cache::get($key, 0);

        // Circuit open - too many failures
        if ($failures >= self::FAILURE_THRESHOLD) {
            if (Cache::has($key . '_timeout')) {
                throw new \Exception("Metrc API temporarily unavailable. Try again in " . self::TIMEOUT_SECONDS . " seconds.");
            }

            // Reset after timeout
            Cache::forget($key);
            $failures = 0;
        }

        try {
            $result = $callback();

            // Success - reset failures
            Cache::forget($key);
            return $result;

        } catch (\Exception $e) {
            // Increment failure count
            Cache::put($key, $failures + 1, now()->addMinutes(5));

            // Set timeout if threshold reached
            if ($failures + 1 >= self::FAILURE_THRESHOLD) {
                Cache::put($key . '_timeout', true, now()->addSeconds(self::TIMEOUT_SECONDS));
            }

            throw $e;
        }
    }
}

// Usage
$breaker = new MetrcCircuitBreaker();
$result = $breaker->execute(fn() => $api->get('/packages/v2/active', $params));
```

---

## Summary

✅ **Handle all HTTP status codes** appropriately
✅ **Implement exponential backoff** for retries
✅ **Validate data** before sending to Metrc
✅ **Log errors** with context (not sensitive data)
✅ **Check license compatibility** to prevent 403 errors
✅ **Implement rate limiting** on your end
✅ **Use circuit breaker** for high-availability systems
❌ **Don't retry** 400/404 errors (won't succeed)
❌ **Don't log** API keys or sensitive data
