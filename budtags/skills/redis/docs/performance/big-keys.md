# Redis Big Keys

Large keys cause performance problems. Learn to identify, prevent, and handle them.

---

## What Are Big Keys?

### Size Thresholds

| Type | Warning | Critical |
|------|---------|----------|
| String | > 1 MB | > 10 MB |
| Hash | > 5,000 fields | > 50,000 fields |
| List | > 10,000 elements | > 100,000 elements |
| Set | > 10,000 members | > 100,000 members |
| Sorted Set | > 10,000 members | > 100,000 members |
| Stream | > 10,000 entries | > 100,000 entries |

### Why Big Keys Are Problems

1. **Slow operations** - O(N) commands block Redis
2. **Network saturation** - Large transfers block other requests
3. **Memory spikes** - Operations may need to copy data
4. **Cluster issues** - Can't migrate large keys efficiently
5. **Deletion blocks** - DEL on big keys freezes Redis

---

## Detection

### redis-cli --bigkeys

```bash
redis-cli --bigkeys

# Output:
# Biggest string found: 'huge:json' has 10485760 bytes
# Biggest hash found: 'user:data' has 50000 fields
# Biggest list found: 'queue:pending' has 100000 items
```

### redis-cli --memkeys

```bash
redis-cli --memkeys

# More accurate memory sampling
```

### Programmatic Detection

```php
class BigKeyScanner
{
    private array $thresholds = [
        'string' => ['size' => 1048576, 'memory' => 10485760],  // 1MB, 10MB
        'hash' => ['size' => 5000, 'memory' => 10485760],
        'list' => ['size' => 10000, 'memory' => 10485760],
        'set' => ['size' => 10000, 'memory' => 10485760],
        'zset' => ['size' => 10000, 'memory' => 10485760],
        'stream' => ['size' => 10000, 'memory' => 10485760],
    ];

    public function scan(): array
    {
        $bigKeys = [];
        $cursor = 0;

        do {
            [$cursor, $keys] = Redis::scan($cursor, 'COUNT', 100);

            foreach ($keys as $key) {
                $info = $this->analyzeKey($key);
                if ($info['is_big']) {
                    $bigKeys[$key] = $info;
                }
            }
        } while ($cursor != 0);

        // Sort by memory descending
        uasort($bigKeys, fn($a, $b) => $b['memory'] <=> $a['memory']);

        return $bigKeys;
    }

    private function analyzeKey(string $key): array
    {
        $type = Redis::type($key);
        $memory = Redis::memory('USAGE', $key) ?? 0;

        $size = match ($type) {
            'string' => Redis::strlen($key),
            'hash' => Redis::hlen($key),
            'list' => Redis::llen($key),
            'set' => Redis::scard($key),
            'zset' => Redis::zcard($key),
            'stream' => Redis::xlen($key),
            default => 0,
        };

        $threshold = $this->thresholds[$type] ?? ['size' => 10000, 'memory' => 10485760];

        return [
            'type' => $type,
            'size' => $size,
            'memory' => $memory,
            'memory_human' => $this->formatBytes($memory),
            'is_big' => $size > $threshold['size'] || $memory > $threshold['memory'],
        ];
    }

    private function formatBytes(int $bytes): string
    {
        $units = ['B', 'KB', 'MB', 'GB'];
        $unit = 0;
        while ($bytes >= 1024 && $unit < count($units) - 1) {
            $bytes /= 1024;
            $unit++;
        }
        return round($bytes, 2) . ' ' . $units[$unit];
    }
}
```

---

## Prevention Strategies

### 1. Set Size Limits

```php
class BoundedCache
{
    private const MAX_VALUE_SIZE = 1048576; // 1MB
    private const MAX_LIST_SIZE = 10000;
    private const MAX_HASH_FIELDS = 5000;

    public function set(string $key, mixed $value): bool
    {
        $serialized = serialize($value);

        if (strlen($serialized) > self::MAX_VALUE_SIZE) {
            Log::warning("Cache value too large", [
                'key' => $key,
                'size' => strlen($serialized),
            ]);
            return false;
        }

        return (bool) Redis::set($key, $serialized);
    }

    public function lpush(string $key, mixed $value): int
    {
        $length = Redis::llen($key);

        if ($length >= self::MAX_LIST_SIZE) {
            // Trim from the other end
            Redis::rpop($key);
        }

        return Redis::lpush($key, serialize($value));
    }
}
```

### 2. Automatic Trimming

```php
class AutoTrimmingList
{
    private string $key;
    private int $maxSize;

    public function __construct(string $key, int $maxSize = 10000)
    {
        $this->key = $key;
        $this->maxSize = $maxSize;
    }

    public function push(mixed $value): void
    {
        Redis::pipeline(function ($pipe) use ($value) {
            $pipe->lpush($this->key, serialize($value));
            $pipe->ltrim($this->key, 0, $this->maxSize - 1);
        });
    }
}
```

### 3. Sharding / Partitioning

```php
class ShardedHash
{
    private string $prefix;
    private int $shardSize;

    public function __construct(string $prefix, int $shardSize = 1000)
    {
        $this->prefix = $prefix;
        $this->shardSize = $shardSize;
    }

    public function hset(string $field, mixed $value): void
    {
        $shard = $this->getShard($field);
        Redis::hset("{$this->prefix}:{$shard}", $field, serialize($value));
    }

    public function hget(string $field): mixed
    {
        $shard = $this->getShard($field);
        $value = Redis::hget("{$this->prefix}:{$shard}", $field);
        return $value ? unserialize($value) : null;
    }

    public function hdel(string $field): void
    {
        $shard = $this->getShard($field);
        Redis::hdel("{$this->prefix}:{$shard}", $field);
    }

    private function getShard(string $field): int
    {
        return crc32($field) % $this->shardSize;
    }
}
```

### 4. Compression for Large Values

```php
class CompressedCache
{
    private const COMPRESSION_THRESHOLD = 1024; // 1KB

    public function set(string $key, mixed $value, int $ttl = 3600): void
    {
        $data = serialize($value);

        if (strlen($data) > self::COMPRESSION_THRESHOLD) {
            $data = gzcompress($data, 6);
            Redis::setex("{$key}:compressed", $ttl, $data);
        } else {
            Redis::setex($key, $ttl, $data);
        }
    }

    public function get(string $key): mixed
    {
        // Try compressed first
        $data = Redis::get("{$key}:compressed");
        if ($data !== null) {
            return unserialize(gzuncompress($data));
        }

        // Fall back to uncompressed
        $data = Redis::get($key);
        return $data ? unserialize($data) : null;
    }
}
```

---

## Safe Deletion

### Use UNLINK Instead of DEL

```php
// ❌ Bad: DEL blocks Redis
Redis::del('huge:key');

// ✅ Good: UNLINK is non-blocking
Redis::unlink('huge:key');
```

### Incremental Deletion for Collections

```php
class SafeDeleter
{
    public function deleteHash(string $key, int $batchSize = 100): void
    {
        while (true) {
            $fields = Redis::hkeys($key);

            if (empty($fields)) {
                Redis::del($key);
                break;
            }

            $batch = array_slice($fields, 0, $batchSize);
            Redis::hdel($key, ...$batch);

            usleep(1000); // Small delay to not block
        }
    }

    public function deleteList(string $key, int $batchSize = 100): void
    {
        while (Redis::llen($key) > 0) {
            Redis::ltrim($key, $batchSize, -1);
            usleep(1000);
        }
        Redis::del($key);
    }

    public function deleteSet(string $key, int $batchSize = 100): void
    {
        while (true) {
            $members = Redis::srandmember($key, $batchSize);

            if (empty($members)) {
                Redis::del($key);
                break;
            }

            Redis::srem($key, ...$members);
            usleep(1000);
        }
    }

    public function deleteSortedSet(string $key, int $batchSize = 100): void
    {
        while (Redis::zcard($key) > 0) {
            Redis::zremrangebyrank($key, 0, $batchSize - 1);
            usleep(1000);
        }
        Redis::del($key);
    }
}
```

---

## Reading Big Keys Safely

### Scan-Based Iteration

```php
class SafeReader
{
    public function iterateHash(string $key, callable $callback): void
    {
        $cursor = 0;

        do {
            [$cursor, $items] = Redis::hscan($key, $cursor, 'COUNT', 100);

            foreach ($items as $field => $value) {
                $callback($field, $value);
            }
        } while ($cursor != 0);
    }

    public function iterateSet(string $key, callable $callback): void
    {
        $cursor = 0;

        do {
            [$cursor, $members] = Redis::sscan($key, $cursor, 'COUNT', 100);

            foreach ($members as $member) {
                $callback($member);
            }
        } while ($cursor != 0);
    }

    public function iterateSortedSet(string $key, callable $callback): void
    {
        $cursor = 0;

        do {
            [$cursor, $items] = Redis::zscan($key, $cursor, 'COUNT', 100);

            foreach ($items as $member => $score) {
                $callback($member, $score);
            }
        } while ($cursor != 0);
    }
}
```

### Paginated List Reading

```php
class PaginatedList
{
    public function getPage(string $key, int $page, int $perPage = 100): array
    {
        $start = ($page - 1) * $perPage;
        $end = $start + $perPage - 1;

        return Redis::lrange($key, $start, $end);
    }

    public function iterate(string $key, callable $callback, int $batchSize = 100): void
    {
        $offset = 0;

        while (true) {
            $items = Redis::lrange($key, $offset, $offset + $batchSize - 1);

            if (empty($items)) {
                break;
            }

            foreach ($items as $item) {
                $callback($item);
            }

            $offset += $batchSize;
        }
    }
}
```

---

## Monitoring

### Scheduled Big Key Check

```php
Schedule::daily(function () {
    $scanner = new BigKeyScanner();
    $bigKeys = $scanner->scan();

    if (!empty($bigKeys)) {
        Log::warning('Big keys detected', [
            'count' => count($bigKeys),
            'keys' => array_slice(array_keys($bigKeys), 0, 10),
        ]);

        // Alert if critical
        $criticalKeys = array_filter($bigKeys, fn($k) => $k['memory'] > 100 * 1024 * 1024);
        if (!empty($criticalKeys)) {
            Log::error('Critical big keys', ['keys' => array_keys($criticalKeys)]);
        }
    }
});
```

---

## BudTags Considerations

### API Response Caching

```php
class ApiResponseCache
{
    private const MAX_RESPONSE_SIZE = 5 * 1024 * 1024; // 5MB

    public function cache(string $key, array $response, int $ttl = 3600): bool
    {
        $data = json_encode($response);

        if (strlen($data) > self::MAX_RESPONSE_SIZE) {
            Log::warning('API response too large to cache', [
                'key' => $key,
                'size' => strlen($data),
            ]);

            // Consider storing metadata only
            return $this->cacheMetadataOnly($key, $response, $ttl);
        }

        Redis::setex($key, $ttl, $data);
        return true;
    }

    private function cacheMetadataOnly(string $key, array $response, int $ttl): bool
    {
        $metadata = [
            'count' => count($response),
            'cached_at' => now()->toIso8601String(),
            'full_data_available' => false,
        ];

        Redis::setex("{$key}:meta", $ttl, json_encode($metadata));
        return false;
    }
}
```

---

## Key Takeaways

1. **Define thresholds** - Set limits for your use case
2. **Scan regularly** - Detect big keys before problems
3. **Use UNLINK** - Non-blocking deletion
4. **Shard large collections** - Distribute across multiple keys
5. **Compress large values** - Reduce memory and network
6. **Iterate with SCAN** - Don't fetch entire collections
7. **Trim automatically** - Cap lists and sets at insert time
8. **Alert on critical keys** - Catch issues early
