# Redis Client-Side Caching

Server-assisted client-side caching for reduced latency and server load.

---

## Overview

Client-side caching stores frequently accessed data in the application memory, with Redis notifying clients when cached data becomes invalid.

### Benefits

- **Reduced latency** - No network round trip for cached data
- **Reduced server load** - Fewer Redis operations
- **Automatic invalidation** - Server notifies on changes

---

## How It Works

```
1. Client requests key → Redis returns value
2. Client caches value locally
3. Another client modifies key
4. Redis notifies first client: "key invalidated"
5. Client removes from local cache
6. Next read fetches fresh data from Redis
```

---

## RESP3 Protocol

Client-side caching requires RESP3 protocol (Redis 6+):

```php
// Connection with RESP3 (phpredis)
$redis = new Redis();
$redis->connect('127.0.0.1', 6379, 0, null, 0, 0, [
    'protocol' => 3,
]);
```

**Note:** Laravel's Redis facade may not fully support RESP3 features yet.

---

## Tracking Modes

### Default (Opt-in)

```bash
# Enable tracking for this connection
CLIENT TRACKING ON

# Disable tracking
CLIENT TRACKING OFF
```

### Broadcast Mode

```bash
# Track all keys matching prefix
CLIENT TRACKING ON BCAST PREFIX user:

# Multiple prefixes
CLIENT TRACKING ON BCAST PREFIX user: PREFIX session:
```

### Redirect Mode

```bash
# Redirect invalidation messages to another connection
CLIENT TRACKING ON REDIRECT <client-id>
```

---

## PHP Implementation

### Basic Client Cache

```php
class ClientSideCache
{
    private array $cache = [];
    private int $maxSize = 1000;
    private array $timestamps = [];

    public function get(string $key): mixed
    {
        // Check local cache first
        if (isset($this->cache[$key])) {
            return $this->cache[$key];
        }

        // Fetch from Redis
        $value = Redis::get($key);

        // Store in local cache
        $this->set($key, $value);

        return $value;
    }

    public function set(string $key, mixed $value): void
    {
        // Evict if at capacity
        if (count($this->cache) >= $this->maxSize) {
            $this->evictOldest();
        }

        $this->cache[$key] = $value;
        $this->timestamps[$key] = time();
    }

    public function invalidate(string $key): void
    {
        unset($this->cache[$key], $this->timestamps[$key]);
    }

    private function evictOldest(): void
    {
        asort($this->timestamps);
        $oldest = array_key_first($this->timestamps);

        if ($oldest) {
            $this->invalidate($oldest);
        }
    }
}
```

### With TTL

```php
class TtlClientCache
{
    private array $cache = [];
    private int $ttl;

    public function __construct(int $ttl = 60)
    {
        $this->ttl = $ttl;
    }

    public function get(string $key): mixed
    {
        if (isset($this->cache[$key])) {
            $entry = $this->cache[$key];

            if ($entry['expires'] > time()) {
                return $entry['value'];
            }

            // Expired
            unset($this->cache[$key]);
        }

        $value = Redis::get($key);

        $this->cache[$key] = [
            'value' => $value,
            'expires' => time() + $this->ttl,
        ];

        return $value;
    }

    public function invalidate(string $key): void
    {
        unset($this->cache[$key]);
    }
}
```

---

## Laravel Integration

### Cache Wrapper

```php
class CachedRedis
{
    private static array $localCache = [];
    private static int $maxSize = 500;

    public static function remember(string $key, int $ttl, callable $callback): mixed
    {
        // Check local cache
        if (isset(self::$localCache[$key])) {
            $entry = self::$localCache[$key];
            if ($entry['expires'] > time()) {
                return $entry['value'];
            }
        }

        // Check Redis
        $value = Cache::get($key);

        if ($value === null) {
            $value = $callback();
            Cache::put($key, $value, $ttl);
        }

        // Store locally
        self::$localCache[$key] = [
            'value' => $value,
            'expires' => time() + min($ttl, 60),  // Local TTL max 60s
        ];

        self::pruneIfNeeded();

        return $value;
    }

    public static function invalidate(string $key): void
    {
        unset(self::$localCache[$key]);
        Cache::forget($key);
    }

    private static function pruneIfNeeded(): void
    {
        if (count(self::$localCache) > self::$maxSize) {
            // Remove expired entries
            $now = time();
            self::$localCache = array_filter(
                self::$localCache,
                fn($entry) => $entry['expires'] > $now
            );
        }
    }
}
```

### Usage

```php
// Automatically uses local + Redis cache
$user = CachedRedis::remember("user:{$id}", 3600, function () use ($id) {
    return User::find($id);
});

// Invalidate on update
CachedRedis::invalidate("user:{$id}");
```

---

## Request-Scoped Cache

### Per-Request Caching

```php
class RequestCache
{
    private static array $cache = [];

    public static function get(string $key, callable $loader): mixed
    {
        if (!isset(self::$cache[$key])) {
            self::$cache[$key] = $loader();
        }

        return self::$cache[$key];
    }

    public static function clear(): void
    {
        self::$cache = [];
    }
}

// Middleware to clear at request end
class ClearRequestCache
{
    public function terminate($request, $response): void
    {
        RequestCache::clear();
    }
}
```

### Usage

```php
// Same key returns cached value within request
$settings = RequestCache::get('settings', fn() => Redis::hgetall('settings'));
$settings = RequestCache::get('settings', fn() => Redis::hgetall('settings'));
// Second call returns cached value, no Redis call
```

---

## Invalidation Strategies

### Time-Based

```php
class TimeBasedCache
{
    public function get(string $key, int $ttl = 60): mixed
    {
        $cached = $this->localCache[$key] ?? null;

        if ($cached && $cached['expires'] > time()) {
            return $cached['value'];
        }

        $value = Redis::get($key);
        $this->localCache[$key] = [
            'value' => $value,
            'expires' => time() + $ttl,
        ];

        return $value;
    }
}
```

### Version-Based

```php
class VersionedCache
{
    public function get(string $key): mixed
    {
        $version = Redis::get("{$key}:version");
        $cacheKey = "{$key}:v{$version}";

        $cached = $this->localCache[$cacheKey] ?? null;

        if ($cached) {
            return $cached;
        }

        $value = Redis::get($key);
        $this->localCache[$cacheKey] = $value;

        return $value;
    }

    public function invalidate(string $key): void
    {
        Redis::incr("{$key}:version");
    }
}
```

---

## Memory Management

### LRU Eviction

```php
class LruCache
{
    private array $cache = [];
    private array $order = [];
    private int $maxSize;

    public function __construct(int $maxSize = 1000)
    {
        $this->maxSize = $maxSize;
    }

    public function get(string $key): mixed
    {
        if (isset($this->cache[$key])) {
            // Move to end (most recently used)
            $this->touch($key);
            return $this->cache[$key];
        }

        return null;
    }

    public function set(string $key, mixed $value): void
    {
        if (count($this->cache) >= $this->maxSize && !isset($this->cache[$key])) {
            // Evict least recently used
            $oldest = array_shift($this->order);
            unset($this->cache[$oldest]);
        }

        $this->cache[$key] = $value;
        $this->touch($key);
    }

    private function touch(string $key): void
    {
        // Remove and re-add to end
        $this->order = array_diff($this->order, [$key]);
        $this->order[] = $key;
    }
}
```

---

## BudTags Usage

### Config Cache

```php
class ConfigCache
{
    private static ?array $settings = null;

    public static function get(int $orgId): array
    {
        if (self::$settings !== null) {
            return self::$settings;
        }

        self::$settings = Cache::remember(
            "org:{$orgId}:settings",
            3600,
            fn() => Setting::forOrg($orgId)->pluck('value', 'key')->toArray()
        );

        return self::$settings;
    }

    public static function invalidate(int $orgId): void
    {
        self::$settings = null;
        Cache::forget("org:{$orgId}:settings");
    }
}
```

---

## Key Takeaways

1. **Two-tier caching** - Local memory + Redis
2. **Short local TTL** - Limit stale data exposure
3. **Size limits** - Prevent memory bloat
4. **LRU eviction** - Remove least used entries
5. **Request scope** - Clear after each request
6. **RESP3 for tracking** - Server-assisted invalidation
7. **Invalidate on writes** - Keep caches consistent
8. **Memory monitoring** - Track local cache size
