# Redis Streams - Deep Dive

Streams are append-only log data structures, designed for event sourcing, message queues, and real-time data processing. Introduced in Redis 5.0.

---

## Internal Representation

Streams use radix trees with listpack-encoded entries:
- **Radix tree** - Maps entry IDs to data
- **Listpack nodes** - Store multiple entries efficiently
- **Consumer groups** - Track delivery and acknowledgment

Configuration:
```
stream-node-max-bytes 4096     # Max bytes per listpack node
stream-node-max-entries 100    # Max entries per node
```

---

## Entry IDs

### Auto-generated IDs

```php
// Default: timestamp-sequence
$id = Redis::xadd('mystream', '*', 'field', 'value');
// Returns: "1609459200000-0"

// Subsequent entries in same millisecond
// Returns: "1609459200000-1", "1609459200000-2", etc.
```

### Custom IDs

```php
// Explicit ID (must be greater than last)
Redis::xadd('mystream', '1609459200001-0', 'field', 'value');

// Partial ID (auto-complete sequence)
Redis::xadd('mystream', '1609459200002-*', 'field', 'value');
```

---

## Use Cases

### 1. Event Log / Audit Trail

```php
class EventStream
{
    private string $key;

    public function __construct(string $name)
    {
        $this->key = "events:{$name}";
    }

    public function append(string $type, array $data): string
    {
        return Redis::xadd($this->key, '*', [
            'type' => $type,
            'data' => json_encode($data),
            'timestamp' => now()->toIso8601String(),
        ]);
    }

    public function readAll(): array
    {
        return Redis::xrange($this->key, '-', '+');
    }

    public function readSince(string $lastId): array
    {
        // Exclusive range (entries after lastId)
        return Redis::xrange($this->key, "({$lastId}", '+');
    }

    public function readLast(int $count): array
    {
        return Redis::xrevrange($this->key, '+', '-', 'COUNT', $count);
    }

    public function trim(int $maxLen): int
    {
        return Redis::xtrim($this->key, 'MAXLEN', '~', $maxLen);
    }
}
```

### 2. Consumer Group Processing

```php
class StreamProcessor
{
    private string $stream;
    private string $group;
    private string $consumer;

    public function __construct(string $stream, string $group, string $consumer)
    {
        $this->stream = $stream;
        $this->group = $group;
        $this->consumer = $consumer;

        $this->ensureGroup();
    }

    private function ensureGroup(): void
    {
        try {
            Redis::xgroup('CREATE', $this->stream, $this->group, '0', 'MKSTREAM');
        } catch (\Exception $e) {
            // Group already exists - OK
            if (!str_contains($e->getMessage(), 'BUSYGROUP')) {
                throw $e;
            }
        }
    }

    public function process(callable $handler, int $timeout = 5000): void
    {
        while (true) {
            // Read pending entries first
            $pending = $this->readPending();
            foreach ($pending as $entry) {
                $this->processEntry($entry, $handler);
            }

            // Then read new entries
            $entries = Redis::xreadgroup(
                'GROUP', $this->group, $this->consumer,
                'COUNT', 10,
                'BLOCK', $timeout,
                'STREAMS', $this->stream, '>'
            );

            if ($entries) {
                foreach ($entries[$this->stream] ?? [] as $id => $data) {
                    $this->processEntry(['id' => $id, 'data' => $data], $handler);
                }
            }
        }
    }

    private function readPending(): array
    {
        // Check for entries that were delivered but not acknowledged
        $pending = Redis::xpending($this->stream, $this->group, '-', '+', 10, $this->consumer);

        if (empty($pending)) {
            return [];
        }

        $ids = array_column($pending, 0);
        return Redis::xrange($this->stream, $ids[0], end($ids));
    }

    private function processEntry(array $entry, callable $handler): void
    {
        try {
            $handler($entry['id'], $entry['data']);
            Redis::xack($this->stream, $this->group, $entry['id']);
        } catch (\Exception $e) {
            // Entry will be redelivered on next run
            throw $e;
        }
    }

    public function getInfo(): array
    {
        return [
            'stream' => Redis::xinfo('STREAM', $this->stream),
            'groups' => Redis::xinfo('GROUPS', $this->stream),
            'consumers' => Redis::xinfo('CONSUMERS', $this->stream, $this->group),
        ];
    }
}
```

### 3. Real-time Notifications

```php
class NotificationStream
{
    public function publish(int $userId, array $notification): string
    {
        $stream = "notifications:{$userId}";

        $id = Redis::xadd($stream, 'MAXLEN', '~', 1000, '*', [
            'type' => $notification['type'],
            'data' => json_encode($notification['data']),
        ]);

        // Optionally publish to channel for real-time delivery
        Redis::publish("notifications:{$userId}", json_encode([
            'id' => $id,
            ...$notification,
        ]));

        return $id;
    }

    public function getUnread(int $userId, ?string $lastSeenId = null): array
    {
        $stream = "notifications:{$userId}";
        $start = $lastSeenId ? "({$lastSeenId}" : '-';

        return Redis::xrange($stream, $start, '+');
    }

    public function markRead(int $userId, string $lastReadId): void
    {
        Cache::put("notifications:last_read:{$userId}", $lastReadId, now()->addYear());
    }
}
```

### 4. Time-Series Data

```php
class MetricsStream
{
    public function record(string $metric, float $value, array $tags = []): string
    {
        $stream = "metrics:{$metric}";

        return Redis::xadd($stream, 'MAXLEN', '~', 10000, '*', [
            'value' => $value,
            'tags' => json_encode($tags),
        ]);
    }

    public function getRange(string $metric, int $startTime, int $endTime): array
    {
        $stream = "metrics:{$metric}";

        // Convert timestamps to stream IDs
        $startId = ($startTime * 1000) . '-0';
        $endId = ($endTime * 1000) . '-9999999999999';

        return Redis::xrange($stream, $startId, $endId);
    }

    public function getRecent(string $metric, int $count = 100): array
    {
        return Redis::xrevrange("metrics:{$metric}", '+', '-', 'COUNT', $count);
    }

    public function aggregate(string $metric, int $startTime, int $endTime): array
    {
        $entries = $this->getRange($metric, $startTime, $endTime);

        $values = array_map(fn($e) => (float) $e['value'], $entries);

        return [
            'count' => count($values),
            'min' => min($values),
            'max' => max($values),
            'avg' => array_sum($values) / count($values),
            'sum' => array_sum($values),
        ];
    }
}
```

---

## Consumer Groups

### Creating Groups

```php
// Start from beginning
Redis::xgroup('CREATE', 'mystream', 'mygroup', '0', 'MKSTREAM');

// Start from end (new entries only)
Redis::xgroup('CREATE', 'mystream', 'mygroup', '$', 'MKSTREAM');

// Start from specific ID
Redis::xgroup('CREATE', 'mystream', 'mygroup', '1609459200000-0');
```

### Reading with Groups

```php
// Read new entries (>)
$entries = Redis::xreadgroup(
    'GROUP', 'mygroup', 'consumer1',
    'COUNT', 10,
    'BLOCK', 5000,  // 5 second timeout
    'STREAMS', 'mystream', '>'
);

// Read pending entries (0)
$pending = Redis::xreadgroup(
    'GROUP', 'mygroup', 'consumer1',
    'COUNT', 10,
    'STREAMS', 'mystream', '0'
);
```

### Acknowledging Entries

```php
// Single acknowledgment
Redis::xack('mystream', 'mygroup', '1609459200000-0');

// Multiple acknowledgments
Redis::xack('mystream', 'mygroup', '1609459200000-0', '1609459200000-1');
```

### Claiming Stale Entries

```php
// Claim entries idle for more than 60 seconds
$claimed = Redis::xclaim(
    'mystream', 'mygroup', 'consumer2',
    60000,  // min-idle-time in ms
    '1609459200000-0', '1609459200000-1'
);

// Auto-claim (Redis 6.2+)
[$nextId, $entries] = Redis::xautoclaim(
    'mystream', 'mygroup', 'consumer2',
    60000,  // min-idle-time
    '0-0',  // start
    'COUNT', 10
);
```

---

## Performance Characteristics

### Command Complexities

| Command | Complexity |
|---------|------------|
| XADD | O(1) |
| XLEN | O(1) |
| XRANGE/XREVRANGE | O(N) where N = entries returned |
| XREAD | O(N) per stream |
| XREADGROUP | O(M) + O(N) |
| XACK | O(1) per ID |
| XTRIM | O(N) where N = entries trimmed |
| XINFO | O(N) for consumers listing |

### Memory Estimation

Per entry overhead: ~80-100 bytes + field/value data

10,000 entries with ~200 bytes each:
```
Overhead: ~1 MB
Data: ~2 MB
Total: ~3 MB
```

---

## BudTags Usage Opportunities

### Metrc Sync Event Log

```php
class MetrcSyncStream
{
    public function logApiCall(string $facility, string $endpoint, array $response): string
    {
        $stream = "metrc:sync:{$facility}";

        return Redis::xadd($stream, 'MAXLEN', '~', 5000, '*', [
            'endpoint' => $endpoint,
            'status' => $response['status'] ?? 'unknown',
            'count' => $response['count'] ?? 0,
            'duration_ms' => $response['duration_ms'] ?? 0,
        ]);
    }

    public function getRecentActivity(string $facility, int $count = 100): array
    {
        return Redis::xrevrange("metrc:sync:{$facility}", '+', '-', 'COUNT', $count);
    }
}
```

### Webhook Processing Queue

```php
class WebhookStream
{
    public function queue(string $type, array $payload): string
    {
        return Redis::xadd('webhooks', '*', [
            'type' => $type,
            'payload' => json_encode($payload),
            'received_at' => now()->toIso8601String(),
        ]);
    }
}
```

---

## Trimming Strategies

### MAXLEN (Hard Limit)

```php
// Exact limit (may be slower)
Redis::xtrim('mystream', 'MAXLEN', 1000);

// Approximate (faster, ~1000 entries)
Redis::xtrim('mystream', 'MAXLEN', '~', 1000);
```

### MINID (Time-based)

```php
// Remove entries older than timestamp
$cutoffId = (strtotime('-7 days') * 1000) . '-0';
Redis::xtrim('mystream', 'MINID', '~', $cutoffId);
```

### Inline Trimming

```php
// Trim while adding
Redis::xadd('mystream', 'MAXLEN', '~', 1000, '*', 'field', 'value');
```

---

## Key Takeaways

1. **Append-only** - Entries cannot be modified, only trimmed
2. **Ordered by ID** - Time-based ordering built-in
3. **Consumer groups** - Distributed processing with acknowledgments
4. **Persistence** - Survives restarts (unlike Pub/Sub)
5. **Blocking reads** - XREAD BLOCK for real-time processing
6. **Auto-claim** - Handle dead consumers automatically
7. **Approximate trimming** - Use `~` for better performance
8. **ID format** - `<timestamp>-<sequence>` enables time queries
