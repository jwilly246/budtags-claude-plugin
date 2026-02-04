# Redis Memory Optimization

Strategies for reducing Redis memory footprint while maintaining performance.

---

## Quick Wins

### 1. Use Appropriate Data Structures

```php
// ❌ Bad: Multiple string keys (high overhead)
Redis::set("user:{$id}:name", $name);
Redis::set("user:{$id}:email", $email);
Redis::set("user:{$id}:role", $role);
// Overhead: ~150 bytes per key

// ✅ Good: Single hash (less overhead)
Redis::hmset("user:{$id}", compact('name', 'email', 'role'));
// Overhead: ~50 bytes total
```

### 2. Shorter Key Names

```php
// ❌ Bad: Long verbose keys
$key = "organization:{$orgId}:facility:{$facilityId}:packages:list";

// ✅ Better: Abbreviated keys
$key = "o:{$orgId}:f:{$facilityId}:pkg";
// Saves ~30 bytes per key
```

### 3. Set TTLs

```php
// ❌ Bad: Keys live forever
Cache::forever('api:response', $data);

// ✅ Good: Appropriate TTL
Cache::put('api:response', $data, now()->addHour());
```

### 4. Compress Large Values

```php
// ❌ Bad: Store raw JSON
Redis::set('large:data', json_encode($bigArray));

// ✅ Better: Compress first
Redis::set('large:data', gzcompress(json_encode($bigArray)));

// Reading:
$data = json_decode(gzuncompress(Redis::get('large:data')), true);
```

---

## Encoding Optimization

### Small Aggregate Thresholds

Redis uses memory-efficient encodings for small collections:

```
# redis.conf - Tune these carefully

# Hashes
hash-max-listpack-entries 512    # Max entries for listpack
hash-max-listpack-value 64       # Max value length for listpack

# Lists
list-max-listpack-size -2        # -2 = 8KB per node

# Sets
set-max-intset-entries 512       # Max entries for intset
set-max-listpack-entries 128     # Max entries for listpack
set-max-listpack-value 64        # Max value length

# Sorted Sets
zset-max-listpack-entries 128
zset-max-listpack-value 64
```

### Check Current Encoding

```php
$encoding = Redis::object('ENCODING', 'mykey');
// Returns: "listpack", "hashtable", "intset", etc.
```

### Encoding Comparison

| Type | Compact Encoding | Memory | Threshold Exceeded | Memory |
|------|-----------------|--------|-------------------|--------|
| Hash | listpack | Low | hashtable | 2-3x |
| Set | intset | Very low | hashtable | 5-10x |
| ZSet | listpack | Low | skiplist | 2-3x |
| List | listpack | Low | quicklist | 1.5x |

---

## Hash Bucketing Pattern

Store many small objects in hash buckets:

```php
class HashBucket
{
    private int $bucketSize = 100;

    public function set(string $prefix, int $id, mixed $value): void
    {
        $bucket = (int) floor($id / $this->bucketSize);
        $field = $id % $this->bucketSize;

        Redis::hset("{$prefix}:{$bucket}", $field, json_encode($value));
    }

    public function get(string $prefix, int $id): mixed
    {
        $bucket = (int) floor($id / $this->bucketSize);
        $field = $id % $this->bucketSize;

        $value = Redis::hget("{$prefix}:{$bucket}", $field);
        return $value ? json_decode($value, true) : null;
    }

    public function delete(string $prefix, int $id): void
    {
        $bucket = (int) floor($id / $this->bucketSize);
        $field = $id % $this->bucketSize;

        Redis::hdel("{$prefix}:{$bucket}", $field);
    }
}

// Usage
$bucket = new HashBucket();
$bucket->set('user', 12345, ['name' => 'John', 'email' => 'john@example.com']);
$user = $bucket->get('user', 12345);
```

**Memory savings:** 50-70% compared to individual keys

---

## Expire Keys Aggressively

### Add TTL to Everything Temporary

```php
class CacheWithTtl
{
    public function set(string $key, mixed $value, int $ttl = 3600): void
    {
        Redis::setex($key, $ttl, serialize($value));
    }

    public function remember(string $key, int $ttl, callable $callback): mixed
    {
        $value = Redis::get($key);

        if ($value !== null) {
            return unserialize($value);
        }

        $value = $callback();
        $this->set($key, $value, $ttl);

        return $value;
    }
}
```

### Scan and Expire Old Keys

```php
class KeyCleaner
{
    public function expirePattern(string $pattern, int $ttl): int
    {
        $cursor = 0;
        $count = 0;

        do {
            [$cursor, $keys] = Redis::scan($cursor, 'MATCH', $pattern, 'COUNT', 100);

            foreach ($keys as $key) {
                $currentTtl = Redis::ttl($key);
                if ($currentTtl === -1) { // No expiration
                    Redis::expire($key, $ttl);
                    $count++;
                }
            }
        } while ($cursor != 0);

        return $count;
    }
}
```

---

## Avoid Memory Fragmentation

### Causes

1. Frequent deletions without new allocations
2. Mixed key sizes
3. Memory allocator behavior

### Solutions

```php
// 1. Use UNLINK instead of DEL for large keys
Redis::unlink('large:key'); // Non-blocking delete

// 2. Check fragmentation ratio
$info = Redis::info('memory');
$fragRatio = $info['mem_fragmentation_ratio'];

if ($fragRatio > 1.5) {
    Log::warning("High Redis fragmentation: {$fragRatio}");
}

// 3. Use MEMORY PURGE (jemalloc only)
Redis::command('MEMORY', ['PURGE']);
```

### Memory Defragmentation (Redis 4+)

```
# redis.conf
activedefrag yes
active-defrag-ignore-bytes 100mb
active-defrag-threshold-lower 10
active-defrag-threshold-upper 100
active-defrag-cycle-min 1
active-defrag-cycle-max 25
```

---

## Data Structure Alternatives

### Use Bits for Flags

```php
// ❌ Bad: Hash with boolean fields
Redis::hmset("user:flags:{$id}", [
    'email_verified' => 1,
    'phone_verified' => 0,
    'premium' => 1,
]);
// ~100+ bytes

// ✅ Better: Bitmap
Redis::setbit("user:flags:{$id}", 0, 1); // email_verified
Redis::setbit("user:flags:{$id}", 1, 0); // phone_verified
Redis::setbit("user:flags:{$id}", 2, 1); // premium
// ~1 byte
```

### Use Sorted Sets for Time-Based Data

```php
// ❌ Bad: Many keys with timestamps
Redis::set("event:{$eventId}:time", $timestamp);

// ✅ Better: Single sorted set
Redis::zadd('events', $timestamp, $eventId);
// Automatic ordering, single key
```

### HyperLogLog for Unique Counts

```php
// ❌ Bad: Set of all unique visitors
Redis::sadd('visitors', $visitorId);
// 10M visitors = ~400MB

// ✅ Better: HyperLogLog
Redis::pfadd('visitors:hll', $visitorId);
// Any number of visitors = 12KB
```

---

## Large Key Prevention

### Set Size Limits

```php
class SafeCache
{
    private const MAX_VALUE_SIZE = 1048576; // 1MB

    public function set(string $key, mixed $value): bool
    {
        $serialized = serialize($value);

        if (strlen($serialized) > self::MAX_VALUE_SIZE) {
            Log::warning("Value too large for cache", [
                'key' => $key,
                'size' => strlen($serialized),
            ]);
            return false;
        }

        Redis::set($key, $serialized);
        return true;
    }
}
```

### Find Large Keys

```php
class LargeKeyFinder
{
    public function findLargeKeys(int $minBytes = 10000): array
    {
        $largeKeys = [];
        $cursor = 0;

        do {
            [$cursor, $keys] = Redis::scan($cursor, 'COUNT', 100);

            foreach ($keys as $key) {
                $bytes = Redis::memory('USAGE', $key);
                if ($bytes >= $minBytes) {
                    $largeKeys[$key] = $bytes;
                }
            }
        } while ($cursor != 0);

        arsort($largeKeys);
        return $largeKeys;
    }
}
```

---

## Memory-Efficient Patterns

### Day-Partitioned Keys

```php
// Automatic cleanup via TTL
$key = "stats:" . date('Y-m-d');
Redis::incr($key);
Redis::expire($key, 86400 * 30); // 30 day retention
```

### Lazy Loading with Sliding TTL

```php
class SlidingCache
{
    public function get(string $key, int $ttl = 3600, callable $loader = null): mixed
    {
        $value = Redis::get($key);

        if ($value !== null) {
            // Extend TTL on access
            Redis::expire($key, $ttl);
            return unserialize($value);
        }

        if ($loader) {
            $value = $loader();
            Redis::setex($key, $ttl, serialize($value));
            return $value;
        }

        return null;
    }
}
```

---

## Monitoring Memory

```php
class MemoryMonitor
{
    public function getReport(): array
    {
        $info = Redis::info('memory');
        $stats = Redis::memory('STATS');

        return [
            'used' => $info['used_memory_human'],
            'peak' => $info['used_memory_peak_human'],
            'rss' => $info['used_memory_rss_human'],
            'fragmentation' => $info['mem_fragmentation_ratio'],
            'dataset_bytes' => $stats['dataset.bytes'],
            'overhead_bytes' => $stats['overhead.total'],
            'keys' => Redis::dbsize(),
            'avg_bytes_per_key' => Redis::dbsize() > 0
                ? round($info['used_memory'] / Redis::dbsize(), 2)
                : 0,
        ];
    }
}
```

---

## Key Takeaways

1. **Use hashes** - Less overhead than multiple keys
2. **Short key names** - Save bytes on every key
3. **Set TTLs** - Don't let keys accumulate
4. **Stay under encoding thresholds** - Listpack is much smaller
5. **Compress large values** - gzip for >1KB
6. **Use HyperLogLog** - For unique counts
7. **Monitor fragmentation** - Keep ratio under 1.5
8. **Hash bucketing** - 50-70% savings for many small objects
