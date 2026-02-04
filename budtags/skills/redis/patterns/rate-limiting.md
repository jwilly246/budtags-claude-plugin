# Rate Limiting

Rate limiting protects external APIs from being overwhelmed and prevents hitting rate limits. BudTags implements rate limiting patterns primarily in `MetrcApi.php`.

---

## Metrc API Rate Limits

Metrc enforces a **5 requests per second** rate limit. Exceeding this returns `429 Too Many Requests`.

### Retry Pattern (MetrcApi.php:174-221)

```php
protected function execute_with_retry(callable $request, string $context): Response {
    $maxRetries = 3;
    $response = null;

    for ($attempt = 0; $attempt < $maxRetries; $attempt++) {
        try {
            $response = $request();
        } catch (ConnectionException $e) {
            // Connection reset, timeout, DNS failure
            if ($attempt < $maxRetries - 1) {
                $backoff = (int) pow(2, $attempt) * 2;  // 2s, 4s, 8s
                LogService::store('MetrcConnection', "Connection error on {$context}. Retrying in {$backoff}s");
                sleep($backoff);
                continue;
            }
            throw $e;
        }

        // Handle 429 rate limit with Retry-After header
        if ($response->status() === 429) {
            $retryAfter = (int) $response->header('Retry-After', 60);

            if ($attempt < $maxRetries - 1) {
                LogService::store('MetrcRateLimit', "Rate limited on {$context}. Waiting {$retryAfter}s");
                sleep($retryAfter);
                continue;
            }
        }

        // Handle 5xx server errors with exponential backoff
        if ($response->status() >= 500 && $attempt < $maxRetries - 1) {
            $backoff = (int) pow(2, $attempt) * 2;
            LogService::store('MetrcServerError', "Server error {$response->status()} on {$context}. Retrying in {$backoff}s");
            sleep($backoff);
            continue;
        }

        break;
    }

    $this->check_for_errors($response);
    return $response;
}
```

---

## Request Spacing Pattern

For paginated endpoints, add delays between requests:

```php
// From MetrcApi.php - paginated fetching
public function all_active_packages(string $facility, bool $force_fetch = false): array {
    return $this->fetch_from_cache_or_api(
        "metrc:all-active-packages:{$facility}",
        function () use ($facility) {
            $packages = [];
            $pageNum = 1;

            while (true) {
                $res = $this->get('/packages/v2/active', [
                    'licenseNumber' => $facility,
                    'pageNumber' => $pageNum,
                    'pageSize' => 20,
                    // ... date params
                ]);

                $packages = [...$packages, ...$res->json('Data')];

                if ($res->json('Page') >= $res->json('TotalPages')) {
                    break;
                }

                usleep(200000);  // 200ms delay = 5 req/sec max
                $pageNum++;
            }

            return $packages;
        },
        fn($pkg) => "metrc:package:{$pkg['Label']}",
        $force_fetch,
        43200,
    );
}
```

### Delay Calculation

```
5 requests/second = 200ms between requests
usleep(200000) = 200,000 microseconds = 200ms
```

---

## Sliding Window Rate Limiter

For implementing custom rate limits:

```php
use Illuminate\Support\Facades\RateLimiter;

// Define a rate limiter
$executed = RateLimiter::attempt(
    "metrc-api:{$facility}",  // Key
    5,                         // Max attempts
    function () use ($request) {
        return $this->executeRequest($request);
    },
    60                         // Decay seconds (window size)
);

if (!$executed) {
    throw new RateLimitException("Too many requests to Metrc API");
}
```

---

## Redis-Based Custom Rate Limiter

For more control, implement directly with Redis:

```php
class RateLimiter {
    private string $prefix = 'ratelimit:';
    private int $maxRequests;
    private int $windowSeconds;

    public function __construct(int $maxRequests = 5, int $windowSeconds = 1) {
        $this->maxRequests = $maxRequests;
        $this->windowSeconds = $windowSeconds;
    }

    public function attempt(string $key, callable $callback): mixed {
        $cacheKey = $this->prefix . $key;
        $currentTime = time();
        $windowStart = $currentTime - $this->windowSeconds;

        // Use Redis sorted set for sliding window
        Redis::zremrangebyscore($cacheKey, '-inf', $windowStart);

        $requestCount = Redis::zcard($cacheKey);

        if ($requestCount >= $this->maxRequests) {
            // Get oldest request time to calculate wait
            $oldest = Redis::zrange($cacheKey, 0, 0, ['WITHSCORES' => true]);
            $waitTime = $this->windowSeconds - ($currentTime - (int) array_values($oldest)[0]);

            throw new RateLimitException("Rate limit exceeded. Retry in {$waitTime}s");
        }

        // Record this request
        Redis::zadd($cacheKey, $currentTime, uniqid());
        Redis::expire($cacheKey, $this->windowSeconds + 1);

        return $callback();
    }
}

// Usage
$limiter = new RateLimiter(5, 1);  // 5 requests per second
$result = $limiter->attempt("metrc:{$facility}", fn() => $this->callApi());
```

---

## Exponential Backoff Pattern

```php
function exponential_backoff(int $attempt, int $baseSeconds = 2): int {
    return (int) pow(2, $attempt) * $baseSeconds;
}

// Attempt 0: 2s
// Attempt 1: 4s
// Attempt 2: 8s
// Attempt 3: 16s

for ($attempt = 0; $attempt < $maxRetries; $attempt++) {
    try {
        return $this->makeRequest();
    } catch (RateLimitException $e) {
        if ($attempt < $maxRetries - 1) {
            $backoff = exponential_backoff($attempt);
            LogService::store('RateLimit', "Backing off {$backoff}s");
            sleep($backoff);
        } else {
            throw $e;
        }
    }
}
```

---

## Request Batching

Reduce API calls by batching:

```php
// Instead of fetching each package individually
foreach ($labels as $label) {
    $packages[] = $this->metrcApi->package($label);  // N API calls!
}

// Batch fetch and cache individually
public function prefetch_packages(array $labels, string $facility): array {
    // Single paginated call
    $allPackages = $this->all_active_packages($facility);

    // Filter and cache individually
    $requested = collect($allPackages)
        ->filter(fn($pkg) => in_array($pkg['Label'], $labels));

    foreach ($requested as $pkg) {
        Cache::forever("metrc:package:{$pkg['Label']}", $pkg);
    }

    return $requested->toArray();
}
```

---

## Anti-Patterns

```php
// ❌ WRONG: No delay in pagination loop
while (true) {
    $res = $this->get('/packages/v2/active', [...]);
    // Process...
    if ($res->json('Page') >= $res->json('TotalPages')) break;
    // No delay! Will hit rate limit!
}

// ✅ CORRECT: Add delay
while (true) {
    $res = $this->get('/packages/v2/active', [...]);
    // Process...
    if ($res->json('Page') >= $res->json('TotalPages')) break;
    usleep(200000);  // 200ms delay
}

// ❌ WRONG: Ignoring Retry-After header
if ($response->status() === 429) {
    sleep(5);  // Arbitrary delay
}

// ✅ CORRECT: Respect Retry-After
if ($response->status() === 429) {
    $retryAfter = (int) $response->header('Retry-After', 60);
    sleep($retryAfter);
}

// ❌ WRONG: Linear backoff
sleep($attempt * 2);  // 2s, 4s, 6s, 8s

// ✅ CORRECT: Exponential backoff
sleep((int) pow(2, $attempt) * 2);  // 2s, 4s, 8s, 16s
```

---

## Rate Limit Constants

```php
// Metrc API limits
const METRC_REQUESTS_PER_SECOND = 5;
const METRC_REQUEST_DELAY_US = 200000;  // 200ms in microseconds

// Retry configuration
const MAX_RETRIES = 3;
const BASE_BACKOFF_SECONDS = 2;
const DEFAULT_RETRY_AFTER = 60;
```
