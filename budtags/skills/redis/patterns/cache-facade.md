# Cache Facade Patterns

The Laravel `Cache` facade provides a high-level API for caching in BudTags. It automatically uses the configured cache driver (Redis in production).

---

## Core Operations

### Get / Put

```php
use Illuminate\Support\Facades\Cache;

// Basic get (returns null if not found)
$package = Cache::get("metrc:package:{$label}");

// Get with default value
$data = Cache::get($key, []);

// Basic put with TTL (seconds)
Cache::put("metrc:strains:{$facility}", $strains, 120);  // 2 minutes

// Check existence
if (Cache::has($key)) {
    $cached = Cache::get($key);
}
```

### Forever (No Expiration)

```php
// Cache permanently (most Metrc entity data)
Cache::forever("metrc:package:{$label}", $package);

// Used for: packages, plants, harvests, locations
// Rationale: Data changes tracked via lastModified, cache invalidated explicitly
```

### Remember / RememberForever

```php
// Remember: get from cache OR execute closure and cache result
$packages = Cache::remember(
    "metrc:day-of-packages:{$facility}:{$date}",
    self::DEFAULT_CACHE_TIME,  // null = forever
    fn() => $this->fetchFromApi()
);

// RememberForever: same but no TTL
$locations = Cache::rememberForever(
    "metrc:locations:{$facility}",
    fn() => $this->get('/locations/v2/active', ['licenseNumber' => $facility])->json('Data')
);
```

### Forget (Invalidation)

```php
// Single key deletion
Cache::forget("metrc:package:{$label}");

// Common invalidation pattern (MetrcApi.php:612-621)
public function invalidate_package_caches(string $facility, array $labels = []): void {
    $today = now()->isoFormat('M/D/Y');
    Cache::forget("metrc:day-of-packages:{$facility}:{$today}");
    Cache::forget("metrc:day-of-inactive-packages:{$facility}:{$today}");
    Cache::forget("metrc:package-available-tags:{$facility}");

    foreach ($labels as $label) {
        Cache::forget("metrc:package:{$label}");
    }
}
```

### Flush (Clear All)

```php
// Clear entire cache (DevController.php:89-93)
public function clear_cache(): RedirectResponse {
    Cache::flush();
    return redirect()->back()->with('message', 'Flushed the entire app cache');
}

// WARNING: Flushes ALL cached data, use sparingly
```

---

## BudTags-Specific Patterns

### The fetch_from_cache_or_api Pattern (MetrcApi.php:266-330)

This is the primary caching pattern used throughout BudTags:

```php
protected function fetch_from_cache_or_api(
    string $key,
    callable $call,
    ?callable $each = null,           // Optional: cache individual items
    bool $force_fetch = false,        // Bypass cache
    ?int $seconds_to_cache = self::DEFAULT_CACHE_TIME,  // null = forever
    ?Carbon $delete_backward_from = null,  // Clean stale data
): array {
    $check_cache_then_fetch = function () use ($call, $each, $seconds_to_cache) {
        $data = collect($call());

        // Cache individual items if $each callback provided
        if ($each) {
            foreach ($data as $item) {
                $item_key = $each($item);
                if ($seconds_to_cache === null) {
                    Cache::forever($item_key, $item);
                } else {
                    Cache::set($item_key, $item, $seconds_to_cache);
                }
            }
        }

        return $data->toArray();
    };

    if ($force_fetch || ($seconds_to_cache !== null && $seconds_to_cache <= 0)) {
        $results = $check_cache_then_fetch();
        if ($seconds_to_cache === null) {
            Cache::forever($key, $results);
        } else {
            Cache::put($key, $results, $seconds_to_cache);
        }
    } else {
        if ($seconds_to_cache === null) {
            $results = Cache::rememberForever($key, $check_cache_then_fetch);
        } else {
            $results = Cache::remember($key, $seconds_to_cache, $check_cache_then_fetch);
        }
    }

    return $results ?? [];
}
```

### Usage Examples

```php
// Simple caching with TTL
public function strains(string $facility): array {
    return $this->fetch_from_cache_or_api(
        "metrc:strains:{$facility}",
        fn() => $this->get('/strains/v2/active?licenseNumber='.$facility)->json('Data'),
        fn($strain) => "metrc:strain:{$strain['Id']}",  // Also cache individual strains
        false,
        120,  // 2 minute TTL
    );
}

// Day-partitioned caching with force-fetch for today
public function one_day_of_packages(string $facility, Carbon $start_day, bool $force_fetch = false): array {
    $timestamp = $start_day->isoFormat('M/D/Y');
    $cache_key = "metrc:day-of-packages:{$facility}:{$timestamp}";

    return $this->fetch_from_cache_or_api(
        $cache_key,
        fn() => $this->get('/packages/v2/active', [
            'licenseNumber' => $facility,
            'lastModifiedStart' => $start_day->format('c'),
            'lastModifiedEnd' => $start_day->copy()->addHours(24)->format('c'),
        ])->json('Data'),
        fn($pkg) => "metrc:package:{$pkg['Label']}",
        $force_fetch || $start_day->isToday(),  // Always force-fetch today
        self::DEFAULT_CACHE_TIME,  // null = forever
        $start_day,  // Clean duplicates from past days
    );
}
```

---

## Common Anti-Patterns

```php
// ❌ WRONG: Magic numbers for TTL
Cache::put($key, $data, 3600);

// ✅ CORRECT: Use constants
Cache::put($key, $data, self::DEFAULT_CACHE_TIME);

// ❌ WRONG: Not force-fetching today's data
$packages = $this->fetch_from_cache_or_api($key, $call, null, false);

// ✅ CORRECT: Force-fetch if today
$packages = $this->fetch_from_cache_or_api(
    $key, $call, null,
    $force_fetch || $start_day->isToday()
);

// ❌ WRONG: Missing scope in key
Cache::forever("packages", $packages);

// ✅ CORRECT: Include scope
Cache::forever("metrc:packages:{$facility}", $packages);
```

---

## Reference: MetrcApi Cache Constants

```php
// From app/Services/Api/MetrcApi.php
const DEFAULT_CACHE_TIME = null;        // Permanent cache
const INACTIVE_CACHE_TIME = 60*60*24*30; // 30 days
const PLANT_CACHE_DAYS = 365;           // History iteration range
const PLANT_CACHE_TIME = null;          // Permanent for active plants
```
