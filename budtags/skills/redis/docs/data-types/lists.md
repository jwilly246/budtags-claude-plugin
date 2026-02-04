# Redis Lists - Deep Dive

Lists are ordered collections of strings, implemented as doubly-linked lists. They support push/pop operations from both ends in O(1) time.

---

## Internal Representation

### Encodings

| Encoding | Condition | Memory |
|----------|-----------|--------|
| `listpack` | ≤ 512 elements AND all values ≤ 64 bytes | Compact |
| `quicklist` | Exceeds limits | Linked list of listpacks |

Configuration:
```
list-max-listpack-size -2    # -2 = 8KB per node (default)
list-compress-depth 0        # Compress middle nodes
```

### Quicklist Structure

Redis 7 uses quicklist (linked list of listpacks):
- Head and tail for O(1) push/pop
- Listpack nodes for memory efficiency
- Optional compression for middle nodes

---

## Memory Analysis

### Small List (Listpack)
100 short elements:
```
~50 bytes overhead
~100 × (element + encoding) ≈ 1-2 KB
Total: ~2 KB
```

### Large List (Quicklist)
10,000 elements:
```
Quicklist overhead: ~40 bytes per node
Listpack per node: ~8 KB
Total: ~80-100 KB (depending on element sizes)
```

---

## Use Cases

### 1. Message Queue (Simple)

```php
class SimpleQueue
{
    private string $key;

    public function __construct(string $name)
    {
        $this->key = "queue:{$name}";
    }

    public function push(mixed $data): int
    {
        return Redis::rpush($this->key, json_encode($data));
    }

    public function pop(): ?array
    {
        $data = Redis::lpop($this->key);
        return $data ? json_decode($data, true) : null;
    }

    public function blockingPop(int $timeout = 0): ?array
    {
        $result = Redis::blpop($this->key, $timeout);
        return $result ? json_decode($result[1], true) : null;
    }

    public function length(): int
    {
        return Redis::llen($this->key);
    }

    public function peek(int $count = 10): array
    {
        $items = Redis::lrange($this->key, 0, $count - 1);
        return array_map(fn($item) => json_decode($item, true), $items);
    }
}
```

### 2. Activity Feed / Timeline

```php
class ActivityFeed
{
    private const MAX_ITEMS = 1000;

    public function addActivity(int $userId, array $activity): void
    {
        $key = "feed:user:{$userId}";
        $data = json_encode([
            ...$activity,
            'timestamp' => time(),
        ]);

        Redis::pipeline(function ($pipe) use ($key, $data) {
            $pipe->lpush($key, $data);
            $pipe->ltrim($key, 0, self::MAX_ITEMS - 1);
        });
    }

    public function getRecent(int $userId, int $count = 20): array
    {
        $key = "feed:user:{$userId}";
        $items = Redis::lrange($key, 0, $count - 1);

        return array_map(fn($item) => json_decode($item, true), $items);
    }

    public function paginate(int $userId, int $page, int $perPage = 20): array
    {
        $key = "feed:user:{$userId}";
        $start = ($page - 1) * $perPage;
        $end = $start + $perPage - 1;

        $items = Redis::lrange($key, $start, $end);
        return array_map(fn($item) => json_decode($item, true), $items);
    }
}
```

### 3. Recent Items Cache

```php
class RecentItemsCache
{
    public function addRecentlyViewed(int $userId, int $itemId): void
    {
        $key = "recent:viewed:{$userId}";

        Redis::pipeline(function ($pipe) use ($key, $itemId) {
            // Remove if exists (avoid duplicates)
            $pipe->lrem($key, 0, $itemId);
            // Add to front
            $pipe->lpush($key, $itemId);
            // Keep only last 50
            $pipe->ltrim($key, 0, 49);
        });
    }

    public function getRecentlyViewed(int $userId, int $count = 10): array
    {
        return Redis::lrange("recent:viewed:{$userId}", 0, $count - 1);
    }
}
```

### 4. Circular Buffer / Log

```php
class CircularLog
{
    private string $key;
    private int $maxSize;

    public function __construct(string $name, int $maxSize = 1000)
    {
        $this->key = "log:{$name}";
        $this->maxSize = $maxSize;
    }

    public function append(string $message): void
    {
        $entry = json_encode([
            'message' => $message,
            'timestamp' => microtime(true),
        ]);

        Redis::pipeline(function ($pipe) use ($entry) {
            $pipe->rpush($this->key, $entry);
            $pipe->ltrim($this->key, -$this->maxSize, -1);
        });
    }

    public function getTail(int $count = 100): array
    {
        $items = Redis::lrange($this->key, -$count, -1);
        return array_map(fn($item) => json_decode($item, true), $items);
    }

    public function getAll(): array
    {
        $items = Redis::lrange($this->key, 0, -1);
        return array_map(fn($item) => json_decode($item, true), $items);
    }
}
```

### 5. Job Priority with Multiple Lists

```php
class PriorityJobQueue
{
    private array $queues = ['high', 'medium', 'low'];

    public function enqueue(string $priority, array $job): void
    {
        $key = "jobs:{$priority}";
        Redis::rpush($key, json_encode($job));
    }

    public function dequeue(int $timeout = 5): ?array
    {
        // BLPOP checks queues in order - high priority first
        $keys = array_map(fn($p) => "jobs:{$p}", $this->queues);
        $result = Redis::blpop($keys, $timeout);

        if ($result) {
            return [
                'queue' => str_replace('jobs:', '', $result[0]),
                'job' => json_decode($result[1], true),
            ];
        }

        return null;
    }

    public function getStats(): array
    {
        return Redis::pipeline(function ($pipe) {
            foreach ($this->queues as $priority) {
                $pipe->llen("jobs:{$priority}");
            }
        });
    }
}
```

---

## Performance Characteristics

### Command Complexities

| Command | Complexity | Notes |
|---------|------------|-------|
| LPUSH/RPUSH | O(1) per element | Fast |
| LPOP/RPOP | O(1) | Fast |
| LLEN | O(1) | Fast |
| LINDEX | O(N) | N = index position |
| LRANGE | O(S+N) | S = start offset, N = elements |
| LSET | O(N) | N = index position |
| LREM | O(N) | Scans entire list |
| LINSERT | O(N) | Scans to find pivot |

### Benchmark Guidelines

| Operation | Ops/sec |
|-----------|---------|
| LPUSH/RPUSH | 100,000+ |
| LPOP/RPOP | 100,000+ |
| LRANGE (100 items) | 50,000+ |
| LINDEX (small list) | 80,000+ |

---

## BudTags Usage Opportunities

### Sync Progress Tracking

```php
class SyncProgressTracker
{
    public function logProgress(string $syncId, array $entry): void
    {
        $key = "sync:log:{$syncId}";

        Redis::pipeline(function ($pipe) use ($key, $entry) {
            $pipe->rpush($key, json_encode([
                ...$entry,
                'at' => now()->toIso8601String(),
            ]));
            $pipe->expire($key, 86400); // Keep for 24 hours
        });
    }

    public function getLog(string $syncId): array
    {
        $items = Redis::lrange("sync:log:{$syncId}", 0, -1);
        return array_map(fn($item) => json_decode($item, true), $items);
    }
}
```

### API Request Log

```php
class ApiRequestLog
{
    public function log(string $facility, array $request): void
    {
        $key = "api:log:{$facility}:" . date('Y-m-d');

        Redis::pipeline(function ($pipe) use ($key, $request) {
            $pipe->rpush($key, json_encode($request));
            $pipe->ltrim($key, -10000, -1); // Keep last 10K
            $pipe->expire($key, 86400 * 7); // 7 days
        });
    }
}
```

---

## Anti-Patterns

### 1. Using LINDEX for Random Access

```php
// ❌ Bad: O(N) for each access
for ($i = 0; $i < 100; $i++) {
    $item = Redis::lindex('mylist', $i);
}

// ✅ Better: Get range in one call
$items = Redis::lrange('mylist', 0, 99);
```

### 2. Using Lists as Deduped Collections

```php
// ❌ Bad: Lists allow duplicates
Redis::rpush('items', 'A');
Redis::rpush('items', 'A'); // Duplicate added

// ✅ Better: Use Sets for unique items
Redis::sadd('items', 'A');
Redis::sadd('items', 'A'); // Ignored
```

### 3. Not Capping List Size

```php
// ❌ Bad: Unbounded growth
Redis::lpush('logs', $entry);

// ✅ Good: Always cap
Redis::pipeline(function ($pipe) use ($entry) {
    $pipe->lpush('logs', $entry);
    $pipe->ltrim('logs', 0, 9999);
});
```

### 4. LRANGE 0 -1 on Large Lists

```php
// ❌ Bad: Fetches entire list
$all = Redis::lrange('huge_list', 0, -1);

// ✅ Better: Paginate
$page = Redis::lrange('huge_list', $offset, $offset + $limit - 1);
```

---

## Key Takeaways

1. **O(1) at ends** - LPUSH/RPUSH/LPOP/RPOP are fast
2. **O(N) in middle** - LINDEX, LINSERT, LSET scan from ends
3. **Natural for queues** - FIFO or LIFO patterns
4. **Duplicates allowed** - Unlike sets
5. **Always cap** - Use LTRIM to prevent unbounded growth
6. **Use LRANGE** - Batch access instead of LINDEX loop
7. **BLPOP for workers** - Blocking pop for job consumers
8. **Compression available** - list-compress-depth for large lists
