# Redis Sorted Sets - Deep Dive

Sorted sets combine set uniqueness with score-based ordering. Members are always sorted by score, enabling efficient range queries.

---

## Internal Representation

### Encodings

| Encoding | Condition | Memory |
|----------|-----------|--------|
| `listpack` | ≤ 128 elements AND all values ≤ 64 bytes | Compact |
| `skiplist` | Exceeds limits | Skip list + hash table |

Configuration:
```
zset-max-listpack-entries 128
zset-max-listpack-value 64
```

### Skiplist Structure

When using skiplist encoding, Redis maintains two data structures:
1. **Skip list** - For ordered operations (range queries, rank)
2. **Hash table** - For O(1) member lookups

This dual structure enables both O(log N) ordered operations and O(1) score lookups.

---

## Memory Analysis

### Listpack (Small Sorted Set)
100 members with short values:
```
~50 bytes overhead
~100 × (member + score + encoding) ≈ 2 KB
Total: ~2 KB
```

### Skiplist (Large Sorted Set)
10,000 members:
```
Skip list: ~40 bytes per element
Hash table: ~24 bytes per element
Members: variable
Total: ~640 KB + member storage
```

---

## Use Cases

### 1. Leaderboards

```php
class Leaderboard
{
    private string $key;

    public function __construct(string $name)
    {
        $this->key = "leaderboard:{$name}";
    }

    public function updateScore(string $playerId, float $score): void
    {
        Redis::zadd($this->key, $score, $playerId);
    }

    public function incrementScore(string $playerId, float $amount): float
    {
        return Redis::zincrby($this->key, $amount, $playerId);
    }

    public function getTopPlayers(int $count): array
    {
        return Redis::zrevrange($this->key, 0, $count - 1, 'WITHSCORES');
    }

    public function getPlayerRank(string $playerId): ?int
    {
        $rank = Redis::zrevrank($this->key, $playerId);
        return $rank !== null ? $rank + 1 : null;  // 1-indexed
    }

    public function getPlayerScore(string $playerId): ?float
    {
        return Redis::zscore($this->key, $playerId);
    }

    public function getPlayersAroundRank(string $playerId, int $range = 5): array
    {
        $rank = Redis::zrevrank($this->key, $playerId);
        if ($rank === null) return [];

        $start = max(0, $rank - $range);
        $end = $rank + $range;

        return Redis::zrevrange($this->key, $start, $end, 'WITHSCORES');
    }
}
```

### 2. Rate Limiting (Sliding Window)

```php
class SlidingWindowRateLimiter
{
    public function isAllowed(string $key, int $maxRequests, int $windowSeconds): bool
    {
        $now = microtime(true);
        $windowStart = $now - $windowSeconds;
        $redisKey = "rate:{$key}";

        // Remove old entries
        Redis::zremrangebyscore($redisKey, '-inf', $windowStart);

        // Count current entries
        $count = Redis::zcard($redisKey);

        if ($count >= $maxRequests) {
            return false;
        }

        // Add new entry with unique ID
        Redis::zadd($redisKey, $now, $now . '-' . uniqid());
        Redis::expire($redisKey, $windowSeconds);

        return true;
    }

    public function getRemainingRequests(string $key, int $maxRequests, int $windowSeconds): int
    {
        $windowStart = microtime(true) - $windowSeconds;
        $redisKey = "rate:{$key}";

        Redis::zremrangebyscore($redisKey, '-inf', $windowStart);
        $count = Redis::zcard($redisKey);

        return max(0, $maxRequests - $count);
    }
}
```

### 3. Time-Based Data

```php
class TimeSeriesCache
{
    public function addEvent(string $stream, array $event): void
    {
        $timestamp = microtime(true);
        $data = json_encode($event);

        Redis::zadd($stream, $timestamp, $data);

        // Keep only last 24 hours
        $cutoff = $timestamp - 86400;
        Redis::zremrangebyscore($stream, '-inf', $cutoff);
    }

    public function getEventsSince(string $stream, float $since): array
    {
        $events = Redis::zrangebyscore($stream, $since, '+inf', 'WITHSCORES');

        return array_map(function ($event, $timestamp) {
            return [
                'data' => json_decode($event, true),
                'timestamp' => $timestamp
            ];
        }, array_keys($events), array_values($events));
    }

    public function getRecentEvents(string $stream, int $count): array
    {
        return Redis::zrevrange($stream, 0, $count - 1, 'WITHSCORES');
    }
}
```

### 4. Priority Queue

```php
class PriorityQueue
{
    private string $key;

    public function __construct(string $name)
    {
        $this->key = "pq:{$name}";
    }

    public function enqueue(string $item, float $priority): void
    {
        // Lower score = higher priority
        Redis::zadd($this->key, $priority, $item);
    }

    public function dequeue(): ?string
    {
        $result = Redis::zpopmin($this->key);
        return $result ? $result[0] : null;
    }

    public function dequeueBlocking(int $timeout = 0): ?array
    {
        $result = Redis::bzpopmin($this->key, $timeout);
        return $result ? ['item' => $result[1], 'priority' => $result[2]] : null;
    }

    public function peek(): ?array
    {
        $result = Redis::zrange($this->key, 0, 0, 'WITHSCORES');
        return $result ? ['item' => $result[0][0], 'priority' => $result[0][1]] : null;
    }

    public function size(): int
    {
        return Redis::zcard($this->key);
    }
}
```

### 5. Autocomplete/Prefix Search

```php
class Autocomplete
{
    private string $key;

    public function __construct(string $name)
    {
        $this->key = "autocomplete:{$name}";
    }

    public function addTerm(string $term, float $score = 0): void
    {
        // Store with score 0 for lexicographic ordering
        // Or use actual score for popularity
        Redis::zadd($this->key, $score, strtolower($term));
    }

    public function getSuggestions(string $prefix, int $limit = 10): array
    {
        $prefix = strtolower($prefix);

        // Using lexicographic range
        $start = "[{$prefix}";
        $end = "[{$prefix}\xff";

        return Redis::zrangebylex($this->key, $start, $end, 'LIMIT', 0, $limit);
    }
}
```

---

## Performance Characteristics

### Command Complexities

| Command | Listpack | Skiplist |
|---------|----------|----------|
| ZADD | O(N) | O(log N) |
| ZREM | O(N) | O(log N) |
| ZSCORE | O(N) | O(1) |
| ZRANK | O(N) | O(log N) |
| ZRANGE | O(N) | O(log N + M) |
| ZRANGEBYSCORE | O(N) | O(log N + M) |
| ZINCRBY | O(N) | O(log N) |

M = number of elements returned

### Benchmark Guidelines

| Operation | 10K elements | 100K elements |
|-----------|--------------|---------------|
| ZADD | ~50,000 ops/sec | ~40,000 ops/sec |
| ZSCORE | ~100,000 ops/sec | ~100,000 ops/sec |
| ZRANGE (10 items) | ~80,000 ops/sec | ~70,000 ops/sec |
| ZRANK | ~100,000 ops/sec | ~80,000 ops/sec |

---

## BudTags Potential Usage

### Time-Based Package Cache

```php
class PackageTimeCache
{
    public function cachePackage(string $facility, array $package): void
    {
        $timestamp = strtotime($package['LastModified']);
        $key = "packages:time:{$facility}";

        Redis::zadd($key, $timestamp, json_encode($package));
    }

    public function getPackagesSince(string $facility, int $since): array
    {
        $key = "packages:time:{$facility}";
        $data = Redis::zrangebyscore($key, $since, '+inf');

        return array_map(fn($p) => json_decode($p, true), $data);
    }

    public function getRecentPackages(string $facility, int $count): array
    {
        $key = "packages:time:{$facility}";
        $data = Redis::zrevrange($key, 0, $count - 1);

        return array_map(fn($p) => json_decode($p, true), $data);
    }
}
```

### API Rate Limiting

```php
// Sliding window for Metrc API calls
class MetrcRateLimiter
{
    public function checkLimit(string $facility): bool
    {
        return (new SlidingWindowRateLimiter())->isAllowed(
            "metrc:{$facility}",
            maxRequests: 50,
            windowSeconds: 60
        );
    }
}
```

---

## Anti-Patterns

### 1. Using ZRANGE 0 -1 on Large Sets

```php
// ❌ Bad: Returns entire sorted set
$all = Redis::zrange('huge_zset', 0, -1);

// ✅ Better: Use ZSCAN or pagination
$cursor = 0;
do {
    [$cursor, $batch] = Redis::zscan('huge_zset', $cursor, 'COUNT', 1000);
    processBatch($batch);
} while ($cursor != 0);
```

### 2. Frequent ZRANK on Write-Heavy Sets

```php
// ❌ Bad: ZRANK after every update
Redis::zincrby('leaderboard', 10, $playerId);
$rank = Redis::zrank('leaderboard', $playerId);  // Every time

// ✅ Better: Cache or batch rank lookups
Redis::zincrby('leaderboard', 10, $playerId);
// Only get rank when displaying, not on every update
```

### 3. Not Using LIMIT

```php
// ❌ Bad: Returns all matches
$results = Redis::zrangebyscore('events', $start, $end);

// ✅ Better: Paginate
$results = Redis::zrangebyscore('events', $start, $end, 'LIMIT', $offset, $count);
```

---

## Key Takeaways

1. **Automatic ordering** - Always sorted by score
2. **O(log N) operations** - Efficient for large sets
3. **Dual structure** - Fast ordered + membership operations
4. **Range queries** - By score or lexicographic
5. **Great for time series** - Use timestamp as score
6. **Priority queues** - Use score as priority
7. **ZINCRBY is atomic** - Safe concurrent score updates
8. **Use LIMIT** - For range queries on large sets
