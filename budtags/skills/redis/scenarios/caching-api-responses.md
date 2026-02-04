# Scenario: Caching API Responses

The most common caching scenario in BudTags is caching Metrc API responses using the `fetch_from_cache_or_api` pattern.

---

## Overview

The `fetch_from_cache_or_api` method in `MetrcApi.php` provides a complete solution for:

1. Checking cache before API calls
2. Fetching from API if cache miss
3. Caching the result (with configurable TTL)
4. Optionally caching individual items from array responses
5. Cleaning stale data from previous days

---

## Pattern Breakdown

### Method Signature

```php
protected function fetch_from_cache_or_api(
    string $key,                    // Primary cache key
    callable $call,                 // API fetch function
    ?callable $each = null,         // Optional: cache each item individually
    bool $force_fetch = false,      // Bypass cache
    ?int $seconds_to_cache = self::DEFAULT_CACHE_TIME,  // null = forever
    ?Carbon $delete_backward_from = null,  // Clean stale data
): array
```

---

## Common Implementations

### Simple Caching (List Endpoint)

```php
public function locations(string $facility, bool $force_fetch = false): array {
    return $this->fetch_from_cache_or_api(
        "metrc:locations:{$facility}",
        fn() => $this->get('/locations/v2/active', ['licenseNumber' => $facility])->json('Data'),
        null,           // No individual item caching
        $force_fetch,   // Allow force refresh
    );
}
```

### With Individual Item Caching

```php
public function strains(string $facility): array {
    return $this->fetch_from_cache_or_api(
        "metrc:strains:{$facility}",                    // List cache key
        fn() => $this->get('/strains/v2/active?licenseNumber='.$facility)->json('Data'),
        fn($strain) => "metrc:strain:{$strain['Id']}",  // Individual strain cache key
        false,
        120,  // 2 minute TTL
    );
}
```

### Day-Partitioned with Force-Fetch Today

```php
public function one_day_of_packages(string $facility, Carbon $start_day, bool $force_fetch = false): array {
    $timestamp = $start_day->isoFormat('M/D/Y');  // "1/15/2025"
    $cache_key = "metrc:day-of-packages:{$facility}:{$timestamp}";

    $end_day = $start_day->copy()->addHours(24);

    return $this->fetch_from_cache_or_api(
        $cache_key,
        fn() => $this->get('/packages/v2/active', [
            'licenseNumber' => $facility,
            'lastModifiedStart' => $start_day->format('c'),
            'lastModifiedEnd' => $end_day->format('c'),
        ])->json('Data'),
        fn($pkg) => "metrc:package:{$pkg['Label']}",  // Cache individual packages
        $force_fetch || $start_day->isToday(),       // ALWAYS force-fetch today
        self::DEFAULT_CACHE_TIME,                    // Forever (invalidated explicitly)
        $start_day,                                  // Clean stale data from past days
    );
}
```

---

## Implementation Checklist

When implementing API response caching:

### 1. Choose Cache Key Pattern

```php
// Single scope
"metrc:{entity}:{scope}"
// Example: "metrc:locations:AU-P-000001"

// Day-partitioned
"metrc:day-of-{entity}:{scope}:{date}"
// Example: "metrc:day-of-packages:AU-P-000001:1/15/2025"
```

### 2. Determine TTL Strategy

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Active entities | `null` (forever) | Invalidated on user action |
| Fast-changing | `120` (2 min) | External changes |
| Reference data | `null` (forever) | Rarely changes |
| Historical | `60*60*24*30` (30 days) | No longer changes |

### 3. Consider Individual Item Caching

```php
// Do cache individually when:
// - Items are fetched by ID elsewhere
// - Items have unique identifiers
fn($pkg) => "metrc:package:{$pkg['Label']}"

// Don't cache individually when:
// - Items are always fetched as list
// - No unique ID access pattern
null
```

### 4. Implement Force Fetch for Today

```php
// Always force-fetch "today" data
$force_fetch || $start_day->isToday()
```

### 5. Add Stale Data Cleanup (Optional)

```php
// Pass the start date to clean duplicates from past days
// Used when items move between day buckets (packages modified today
// should be removed from yesterday's cache)
$start_day
```

---

## Creating a New Cached Endpoint

### Example: Caching Package Adjustments

```php
public function package_adjustments(string $facility, bool $force_fetch = false): array {
    return $this->fetch_from_cache_or_api(
        "metrc:package-adjustments:{$facility}",
        function () use ($facility) {
            $pageNum = 1;
            $adjustments = [];

            // Fetch all pages
            while (true) {
                $res = $this->get('/packages/v2/adjustments', [
                    'licenseNumber' => $facility,
                    'pageNumber' => $pageNum,
                    'pageSize' => 20,
                    'lastModifiedStart' => $this->get_facility_credentialed_date($facility),
                    'lastModifiedEnd' => now()->format('Y-m-d'),
                ]);

                $adjustments = [...$adjustments, ...$res->json('Data')];

                if ($res->json('Page') >= $res->json('TotalPages')) {
                    break;
                }
                usleep(200000);  // Rate limit: 200ms between requests
                $pageNum++;
            }

            return $adjustments;
        },
        null,           // No individual caching (adjustments fetched in bulk)
        $force_fetch,
        null,           // Forever - adjustments are immutable
    );
}
```

---

## Handling Cache Misses

```php
// The pattern handles cache misses automatically:
// 1. Check cache
// 2. If miss, execute callable
// 3. Cache result
// 4. Return data

// For manual cache checking (rare):
$cache_key = "metrc:package:{$label}";
$was_cached = Cache::has($cache_key);

$package = $this->fetch_from_cache_or_api(
    $cache_key,
    fn() => $this->get("/packages/v2/{$label}")->json(),
);

if (!$was_cached) {
    LogService::store('CacheMiss', "Package {$label} fetched from API");
}
```

---

## Error Handling

```php
// Errors in API call bubble up - don't cache errors
public function risky_endpoint(string $facility): array {
    try {
        return $this->fetch_from_cache_or_api(
            "metrc:risky:{$facility}",
            fn() => $this->get('/risky/endpoint')->json('Data'),
        );
    } catch (MetrcException $e) {
        LogService::store('MetrcError', "Failed to fetch risky data: {$e->getMessage()}");
        return [];  // Return empty, don't cache the error
    }
}
```

---

## Invalidation After Write Operations

```php
// After creating a package
public function create_package(string $facility, array $data): Response {
    $response = $this->post("/packages/v2/create?licenseNumber={$facility}", $data);

    // Invalidate relevant caches
    $this->invalidate_package_caches($facility);

    return $response;
}
```
