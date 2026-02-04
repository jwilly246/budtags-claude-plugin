# Redis Hashes - Deep Dive

Hashes are maps of field-value pairs, optimized for storing objects and grouping related data.

---

## Internal Representation

### Encodings

| Encoding | Condition | Memory |
|----------|-----------|--------|
| `listpack` | ≤ 512 fields AND all values ≤ 64 bytes | Very compact |
| `hashtable` | Exceeds limits | Full hash table |

Configuration (redis.conf):
```
hash-max-listpack-entries 512
hash-max-listpack-value 64
```

### Why Listpack?

Listpack stores entries sequentially in memory:
- No pointers between elements
- Better cache locality
- ~10x more memory efficient than hashtable

When any condition exceeds the limit, Redis converts to hashtable (one-way).

---

## Memory Analysis

### Listpack (Small Hash)

For a hash with 5 fields, 10-byte values each:
```
Overhead: ~60 bytes (key + object)
Data: ~5 × (field + value + encoding) ≈ 100 bytes
Total: ~160 bytes
```

### Hashtable (Large Hash)

Same 5 fields after exceeding limits:
```
Overhead: ~60 bytes
Hash table: ~200 bytes
Dict entries: ~5 × 24 bytes = 120 bytes
Total: ~380 bytes
```

**Listpack is 2x+ more efficient!**

---

## Memory Comparison: Hash vs Multiple Strings

Storing user with 5 fields:

### Approach 1: Separate Strings
```php
Redis::set("user:1:name", "John");
Redis::set("user:1:email", "john@example.com");
Redis::set("user:1:role", "admin");
Redis::set("user:1:created", "2024-01-15");
Redis::set("user:1:status", "active");
// 5 keys × ~60 bytes overhead = 300 bytes overhead
// Total: ~400 bytes
```

### Approach 2: Single Hash
```php
Redis::hmset("user:1", [
    'name' => 'John',
    'email' => 'john@example.com',
    'role' => 'admin',
    'created' => '2024-01-15',
    'status' => 'active'
]);
// 1 key × ~60 bytes overhead = 60 bytes overhead
// Total: ~150 bytes (with listpack)
```

**Hash is 2.5x more memory efficient!**

---

## Use Cases

### 1. Object Storage

```php
class UserCache
{
    public function set(User $user): void
    {
        Redis::hmset("user:{$user->id}", [
            'name' => $user->name,
            'email' => $user->email,
            'role' => $user->role,
            'avatar' => $user->avatar_url,
            'last_login' => $user->last_login?->toIso8601String(),
        ]);
        Redis::expire("user:{$user->id}", 3600);
    }

    public function get(int $id): ?array
    {
        $data = Redis::hgetall("user:{$id}");
        return empty($data) ? null : $data;
    }

    public function getField(int $id, string $field): ?string
    {
        return Redis::hget("user:{$id}", $field);
    }

    public function updateField(int $id, string $field, string $value): void
    {
        Redis::hset("user:{$id}", $field, $value);
    }
}
```

### 2. Counter Groups

```php
class MetricsTracker
{
    public function track(string $page, string $metric): void
    {
        Redis::hincrby("metrics:{$page}", $metric, 1);
    }

    public function trackMultiple(string $page, array $metrics): void
    {
        foreach ($metrics as $metric => $increment) {
            Redis::hincrby("metrics:{$page}", $metric, $increment);
        }
    }

    public function getAll(string $page): array
    {
        return Redis::hgetall("metrics:{$page}");
    }
}

// Usage
$tracker = new MetricsTracker();
$tracker->track('home', 'views');
$tracker->track('home', 'clicks');
$tracker->trackMultiple('home', ['api_calls' => 5, 'errors' => 1]);
```

### 3. Configuration Storage

```php
class ConfigCache
{
    private string $key = 'config:app';

    public function set(array $config): void
    {
        Redis::hmset($this->key, $config);
    }

    public function get(string $key): ?string
    {
        return Redis::hget($this->key, $key);
    }

    public function getMultiple(array $keys): array
    {
        return array_combine($keys, Redis::hmget($this->key, ...$keys));
    }

    public function getAll(): array
    {
        return Redis::hgetall($this->key);
    }
}
```

### 4. Shopping Cart

```php
class ShoppingCart
{
    public function addItem(int $userId, string $productId, int $quantity): void
    {
        Redis::hincrby("cart:{$userId}", $productId, $quantity);
    }

    public function setQuantity(int $userId, string $productId, int $quantity): void
    {
        if ($quantity <= 0) {
            Redis::hdel("cart:{$userId}", $productId);
        } else {
            Redis::hset("cart:{$userId}", $productId, $quantity);
        }
    }

    public function getCart(int $userId): array
    {
        return Redis::hgetall("cart:{$userId}");
    }

    public function getItemCount(int $userId): int
    {
        return Redis::hlen("cart:{$userId}");
    }

    public function clear(int $userId): void
    {
        Redis::del("cart:{$userId}");
    }
}
```

---

## Performance Characteristics

### Command Complexities

| Command | Listpack | Hashtable |
|---------|----------|-----------|
| HGET | O(N) | O(1) |
| HSET | O(N) | O(1) |
| HDEL | O(N) | O(1) |
| HGETALL | O(N) | O(N) |
| HLEN | O(1) | O(1) |
| HINCRBY | O(N) | O(1) |

**Note:** For listpack, N is number of fields. Small N makes listpack faster due to cache locality.

### Benchmark Guidelines

| Operation | Listpack (100 fields) | Hashtable |
|-----------|----------------------|-----------|
| HGET | ~80,000 ops/sec | ~120,000 ops/sec |
| HSET | ~70,000 ops/sec | ~100,000 ops/sec |
| HGETALL | ~50,000 ops/sec | ~50,000 ops/sec |

---

## Memory Optimization: Hash Bucketing

For millions of small objects, use hash bucketing:

```php
class HashBucket
{
    private int $bucketSize = 100;

    private function getBucket(string $id): array
    {
        $bucket = intdiv((int) $id, $this->bucketSize);
        $field = $id % $this->bucketSize;
        return ["bucket:{$bucket}", (string) $field];
    }

    public function set(string $id, string $value): void
    {
        [$key, $field] = $this->getBucket($id);
        Redis::hset($key, $field, $value);
    }

    public function get(string $id): ?string
    {
        [$key, $field] = $this->getBucket($id);
        return Redis::hget($key, $field);
    }
}
```

**Memory savings:** Up to 10x for millions of small values!

---

## Field Expiration (Redis 7.4+)

Individual field expiration is now possible:

```php
// Set field with expiration
Redis::hset("user:1", "session_token", $token);
Redis::hexpire("user:1", 3600, "session_token");

// Check TTL
$ttl = Redis::httl("user:1", "session_token");

// Remove expiration
Redis::hpersist("user:1", "session_token");
```

---

## BudTags Potential Usage

### Package Metadata Cache

```php
// Instead of full JSON serialization
class PackageCache
{
    public function set(array $package): void
    {
        $key = "pkg:{$package['Label']}";
        Redis::hmset($key, [
            'label' => $package['Label'],
            'quantity' => $package['Quantity'],
            'unit' => $package['UnitOfMeasureName'],
            'strain' => $package['Item']['StrainName'] ?? '',
            'room' => $package['LocationName'] ?? '',
            'last_modified' => $package['LastModified'],
        ]);
    }

    public function getQuantity(string $label): ?string
    {
        return Redis::hget("pkg:{$label}", 'quantity');
    }

    public function updateLocation(string $label, string $room): void
    {
        Redis::hset("pkg:{$label}", 'room', $room);
    }
}
```

### Daily Statistics

```php
class DailyStats
{
    public function trackApiCall(string $facility, string $endpoint): void
    {
        $key = "stats:{$facility}:" . date('Y-m-d');
        Redis::hincrby($key, "api:{$endpoint}", 1);
        Redis::expire($key, 86400 * 7);  // Keep 7 days
    }

    public function trackCacheHit(string $facility): void
    {
        $key = "stats:{$facility}:" . date('Y-m-d');
        Redis::hincrby($key, 'cache_hits', 1);
    }

    public function trackCacheMiss(string $facility): void
    {
        $key = "stats:{$facility}:" . date('Y-m-d');
        Redis::hincrby($key, 'cache_misses', 1);
    }

    public function getDailyStats(string $facility, string $date): array
    {
        return Redis::hgetall("stats:{$facility}:{$date}");
    }
}
```

---

## Anti-Patterns

### 1. Too Many Fields

```php
// ❌ Bad: 10,000 fields in one hash
foreach ($allUsers as $user) {
    Redis::hset('all_users', $user->id, json_encode($user));
}

// ✅ Better: Separate hashes or bucketing
foreach ($allUsers as $user) {
    Redis::hmset("user:{$user->id}", $user->toArray());
}
```

### 2. Large Field Values

```php
// ❌ Bad: Large JSON in field (breaks listpack)
Redis::hset('data', 'payload', json_encode($largeArray));

// ✅ Better: Separate key for large data
Redis::set('data:payload', json_encode($largeArray));
Redis::hset('data', 'payload_key', 'data:payload');
```

### 3. Not Using HMGET

```php
// ❌ Bad: Multiple round trips
$name = Redis::hget('user:1', 'name');
$email = Redis::hget('user:1', 'email');
$role = Redis::hget('user:1', 'role');

// ✅ Good: Single round trip
[$name, $email, $role] = Redis::hmget('user:1', 'name', 'email', 'role');
```

---

## Key Takeaways

1. **Hashes save memory** - 2-10x more efficient than separate keys
2. **Keep values small** - Stay under 64 bytes for listpack encoding
3. **Use HMGET/HMSET** - Reduce network round trips
4. **HINCRBY is atomic** - Safe for concurrent counters
5. **Consider bucketing** - For millions of small objects
6. **Field expiration (7.4+)** - Per-field TTL now available
7. **Check encoding** - `OBJECT ENCODING key` to verify
