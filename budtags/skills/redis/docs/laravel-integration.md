# Laravel Redis Integration

How Laravel integrates with Redis through facades, configuration, and common patterns.

---

## Configuration

### Database Configuration (config/database.php)

```php
'redis' => [
    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', Str::slug(env('APP_NAME', 'laravel'), '_').'_database_'),
    ],

    'default' => [
        'url' => env('REDIS_URL'),
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'username' => env('REDIS_USERNAME'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', '6379'),
        'database' => env('REDIS_DB', '0'),
        'prefix' => '',
    ],

    'cache' => [
        // Same connection settings...
        'database' => env('REDIS_CACHE_DB', '1'),
        'prefix' => '',
    ],

    'queue' => [
        // Same connection settings...
        'database' => env('REDIS_QUEUE_DB', '2'),
        'prefix' => '',
    ],
],
```

### Cache Configuration (config/cache.php)

```php
'default' => env('CACHE_STORE', 'redis'),

'stores' => [
    'redis' => [
        'driver' => 'redis',
        'connection' => env('CACHE_REDIS_CONNECTION', 'cache'),
        'lock_connection' => env('CACHE_REDIS_LOCK_CONNECTION', 'default'),
    ],
],
```

---

## Facades Comparison

### Cache Facade

High-level caching abstraction. Use for most caching needs.

```php
use Illuminate\Support\Facades\Cache;

// Automatically uses configured cache store (Redis)
// Handles serialization/deserialization
// Supports tagging (if using Redis)
// Works with any cache driver
```

**Pros:**
- Clean, simple API
- Driver-agnostic (can switch to file, memcached, etc.)
- Automatic serialization
- Built-in remember patterns

**Cons:**
- No access to Redis-specific data structures
- No atomic operations beyond get/put

### Redis Facade

Direct Redis access. Use for Redis-specific features.

```php
use Illuminate\Support\Facades\Redis;

// Direct Redis commands
// Access to all data structures
// Atomic operations
// Lower-level control
```

**Pros:**
- Full Redis feature access
- Atomic operations (incr, decr)
- Sets, sorted sets, hashes, lists
- Pattern matching (keys command)

**Cons:**
- Redis-specific (not portable)
- Manual serialization for complex data
- Must manage DB selection manually

---

## Database Selection

Laravel's Cache facade automatically uses the configured cache connection (DB 1). The Redis facade defaults to the default connection (DB 0).

```php
// Cache facade - automatically uses DB 1 (cache connection)
Cache::put('key', 'value');  // Stored in DB 1

// Redis facade - uses DB 0 by default
Redis::set('key', 'value');  // Stored in DB 0!

// To use Redis facade with cache DB:
Redis::connection('cache')->set('key', 'value');  // DB 1

// Or manually select:
Redis::command('select', [1]);
Redis::set('key', 'value');  // Now in DB 1
```

---

## Key Prefixing

Laravel can prefix all Redis keys. BudTags disables this for clarity.

```php
// With default prefix (config/database.php):
'prefix' => Str::slug(env('APP_NAME'), '_').'_database_'
// Key "foo" becomes "budtags_database_foo"

// BudTags config:
'prefix' => ''
// Key "foo" stays "foo"
```

---

## Serialization

### Cache Facade (Automatic)

```php
// Automatically serializes PHP values
Cache::put('user', ['name' => 'John', 'age' => 30]);
$user = Cache::get('user');  // Returns array

// Works with objects (must be serializable)
Cache::put('carbon', Carbon::now());
$date = Cache::get('carbon');  // Returns Carbon instance
```

### Redis Facade (Manual)

```php
// Must manually serialize complex values
Redis::set('user', json_encode(['name' => 'John']));
$user = json_decode(Redis::get('user'), true);

// Strings/numbers work directly
Redis::set('count', 42);
$count = (int) Redis::get('count');
```

---

## Common Patterns

### Remember Pattern

```php
// Cache facade only
$value = Cache::remember('key', 3600, function () {
    return $this->expensiveOperation();
});

// Forever variant
$value = Cache::rememberForever('key', function () {
    return $this->expensiveOperation();
});
```

### Locking

```php
// Cache facade provides distributed locks
$lock = Cache::lock('resource', 60);

if ($lock->get()) {
    try {
        // Critical section
    } finally {
        $lock->release();
    }
}

// Blocking variant
Cache::lock('resource', 60)->block(10, function () {
    // Critical section
});
```

### Atomic Operations

```php
// Redis facade for atomic counters
$newValue = Redis::incr('counter');
Redis::expire('counter', 3600);

// Cache facade alternative (not atomic)
$current = Cache::get('counter', 0);
Cache::put('counter', $current + 1, 3600);  // Race condition!
```

---

## Error Handling

```php
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Redis;
use Exception;

// Cache facade - graceful degradation
try {
    $value = Cache::get('key');
} catch (Exception $e) {
    // Redis unavailable
    $value = $this->fallbackMethod();
}

// Redis facade - same pattern
try {
    Redis::command('select', [1]);
    $keys = Redis::command('keys', ['*']);
} catch (Exception $e) {
    // Redis unavailable
    $keys = [];
}
```

---

## Horizon Integration

Laravel Horizon uses Redis for queue management. It uses the `queue` connection (DB 2).

```php
// Jobs automatically use Redis queues
dispatch(new ProcessJob($data));

// Horizon manages:
// - Worker processes
// - Job retries
// - Failed job storage
// - Metrics and monitoring
```

---

## Best Practices

### 1. Use Cache Facade for Standard Caching

```php
// ✅ Recommended
Cache::forever('key', $data);
Cache::remember('key', 3600, fn() => $data);

// ❌ Unnecessary complexity
Redis::set('key', serialize($data));
```

### 2. Use Redis Facade for Atomic Operations

```php
// ✅ Atomic and correct
$count = Redis::incr('counter');

// ❌ Race condition
$count = Cache::get('counter', 0) + 1;
Cache::put('counter', $count);
```

### 3. Use Redis Facade for Data Structures

```php
// ✅ Native Redis set
Redis::sadd('unique_items', ...$items);
$all = Redis::smembers('unique_items');

// ❌ Simulating set with array (inefficient)
$items = Cache::get('unique_items', []);
$items = array_unique([...$items, ...$newItems]);
Cache::put('unique_items', $items);
```

### 4. Always Select DB for Direct Redis Operations

```php
// ✅ Explicit DB selection
Redis::command('select', [1]);
$keys = Redis::command('keys', ['*']);

// ❌ May search wrong DB
$keys = Redis::command('keys', ['*']);
```

### 5. Handle Redis Unavailability

```php
// ✅ Graceful fallback
try {
    $data = Cache::get($key);
} catch (Exception $e) {
    LogService::store('Redis', 'Unavailable, using fallback');
    $data = $this->fallbackMethod();
}

// ❌ Crash on Redis failure
$data = Cache::get($key);  // Throws if Redis down
```
