# Redis Facade Patterns

The Laravel `Redis` facade provides low-level access to Redis commands. Use it for atomic operations, data structures (sets, lists, hashes), and operations not supported by the Cache facade.

---

## When to Use Redis vs Cache

| Operation | Facade | Reason |
|-----------|--------|--------|
| Get/Put single values | `Cache::` | Cleaner API |
| Remember patterns | `Cache::` | Built-in support |
| Atomic increment/decrement | `Redis::` | Atomic operations |
| Sets (sadd/smembers) | `Redis::` | Data structures |
| Pattern-based key search | `Redis::` | Not in Cache facade |
| Database selection | `Redis::` | Low-level operation |

---

## Core Operations

### Atomic Counters (Redis::incr / Redis::expire)

From `app/Jobs/GeneratePackageLabel.php:52-58`:

```php
use Illuminate\Support\Facades\Redis;

// Atomic increment for progress tracking
$key = "label_group_success:{$this->group->id}";
$successCount = (int) Redis::incr($key);
Redis::expire($key, 3600);  // Clean up after 1 hour

// Usage: Track batch job progress without database overhead
// - Faster than COUNT(*) queries
// - Atomic (safe for concurrent workers)
// - Auto-cleanup with expire
```

### Sets (Redis::sadd / Redis::smembers / Redis::del)

```php
// Add to set (used for tracking package labels)
$labels = ['ABC123', 'DEF456', 'GHI789'];
Redis::sadd("metrc:package-labels:{$facility}", ...$labels);

// Get all members
$allLabels = Redis::smembers("metrc:package-labels:{$facility}");

// Delete entire set
Redis::del("metrc:package-labels:{$facility}");

// Use case: Temporary tracking of items for bulk operations
```

### Direct Commands (Redis::command)

From `app/Http/Controllers/DevController.php:46-55`:

```php
// Select database (IMPORTANT: cache is DB 1)
Redis::command('select', [1]);

// Pattern-based key search
$keys = Redis::command('keys', ['*day-of-packages*']);

// Get database size (key count)
$keyCount = Redis::command('dbsize');

// Extract unique licenses from keys
$licenses = collect(Redis::command('keys', ['*day-of-packages*']))
    ->map(fn($key) => preg_replace("/^.+day-of-packages:([a-zA-Z0-9\-]+):.+$/", '$1', $key))
    ->unique()
    ->values();
```

### Pattern-Based Deletion

From `app/Http/Controllers/DevController.php:94-110`:

```php
public function forget_cache(): RedirectResponse {
    request()->validate(['key' => 'string|required']);

    $pattern = "*" . request()->key . "*";

    Redis::command('select', [1]);  // Switch to cache DB
    $keys = Redis::command('keys', [$pattern]);

    foreach ($keys as $key) {
        Redis::command('del', [$key]);
    }

    $count = count($keys);
    return redirect()->back()->with('message', "Deleted {$count} items from the cache.");
}
```

---

## Database Configuration

From `config/database.php`:

```php
'redis' => [
    'default' => [
        'database' => env('REDIS_DB', '0'),  // Default: sessions, etc.
        'prefix' => '',
    ],
    'cache' => [
        'database' => env('REDIS_CACHE_DB', '1'),  // Cache data
        'prefix' => '',
    ],
    'queue' => [
        'database' => env('REDIS_QUEUE_DB', '2'),  // Horizon queues
        'prefix' => '',
    ],
],
```

**CRITICAL**: When using `Redis::command` for cache operations, always select DB 1 first:

```php
// ✅ CORRECT
Redis::command('select', [1]);
$keys = Redis::command('keys', ['metrc:*']);

// ❌ WRONG - Will search wrong database
$keys = Redis::command('keys', ['metrc:*']);  // Searches DB 0
```

---

## Common Patterns

### Progress Tracking in Jobs

```php
class ProcessBatchJob implements ShouldQueue {
    public function handle(): void {
        foreach ($this->items as $index => $item) {
            // Process item...

            // Track progress atomically
            $key = "batch_progress:{$this->batchId}";
            $completed = (int) Redis::incr($key);
            Redis::expire($key, 7200);  // 2 hour cleanup

            // Broadcast progress if needed
            if ($completed % 10 === 0) {
                broadcast(new BatchProgress($this->batchId, $completed, count($this->items)));
            }
        }
    }
}
```

### Temporary Set Operations

```php
// Track items being processed (prevent duplicates)
$lockKey = "processing:packages:{$facility}";

// Before processing
if (!Redis::sismember($lockKey, $packageLabel)) {
    Redis::sadd($lockKey, $packageLabel);
    Redis::expire($lockKey, 300);  // 5 minute lock

    // Process package...

    Redis::srem($lockKey, $packageLabel);  // Remove after processing
}
```

### Cache Statistics

```php
public function get_cache_stats(): array {
    Redis::command('select', [1]);

    return [
        'total_keys' => Redis::command('dbsize'),
        'package_keys' => count(Redis::command('keys', ['metrc:package:*'])),
        'day_caches' => count(Redis::command('keys', ['*day-of-*'])),
        'memory_usage' => Redis::command('info', ['memory'])['used_memory_human'] ?? 'unknown',
    ];
}
```

---

## Anti-Patterns

```php
// ❌ WRONG: Using Redis for simple get/put
Redis::set($key, json_encode($data));
$data = json_decode(Redis::get($key), true);

// ✅ CORRECT: Use Cache facade for simple operations
Cache::put($key, $data, 3600);
$data = Cache::get($key);

// ❌ WRONG: Forgetting to select cache DB
$keys = Redis::command('keys', ['*packages*']);

// ✅ CORRECT: Always select DB 1 for cache operations
Redis::command('select', [1]);
$keys = Redis::command('keys', ['*packages*']);

// ❌ WRONG: Not setting expire on counters
Redis::incr("counter:{$id}");

// ✅ CORRECT: Always set cleanup expiration
Redis::incr("counter:{$id}");
Redis::expire("counter:{$id}", 3600);
```

---

## Error Handling

```php
try {
    Redis::command('select', [1]);
    $keys = Redis::command('keys', ['*pattern*']);
} catch (Exception $e) {
    // Redis unavailable - graceful degradation
    LogService::store('Redis', "Redis unavailable: {$e->getMessage()}");
    $keys = [];  // Return empty, don't crash
}
```
