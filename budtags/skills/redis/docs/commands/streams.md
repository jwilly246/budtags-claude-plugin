# Redis Stream Commands

Streams are append-only log data structures, ideal for event sourcing, messaging, and activity feeds. They support consumer groups for distributed processing.

---

## Adding Entries

### XADD

Appends an entry to a stream.

```
XADD key [NOMKSTREAM] [MAXLEN|MINID [=|~] threshold [LIMIT count]] *|ID field value [field value ...]
```

| Option | Description |
|--------|-------------|
| `*` | Auto-generate ID (timestamp-sequence) |
| `ID` | Specify exact ID (must be greater than last) |
| `NOMKSTREAM` | Don't create stream if doesn't exist |
| `MAXLEN ~ N` | Approximate trimming to N entries |
| `MAXLEN = N` | Exact trimming to N entries |
| `MINID ~ ID` | Remove entries older than ID |
| `LIMIT count` | Max entries to trim per call |

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string - the entry ID |
| **Complexity** | O(1) for adding, O(N) for trimming |
| **Creates** | Key if it doesn't exist |

```php
// Auto-generated ID
$id = Redis::xadd('events', '*', 'action', 'login', 'user_id', '123');
// Returns: "1234567890123-0"

// With max length (approximate)
$id = Redis::xadd('events', 'MAXLEN', '~', 1000, '*', 'action', 'login');

// Specific ID
$id = Redis::xadd('events', '1234567890123-0', 'action', 'login');
```

---

### XLEN

Returns the number of entries.

```
XLEN key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - entry count |
| **Complexity** | O(1) |

---

### XDEL

Removes entries by ID.

```
XDEL key ID [ID ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of entries deleted |
| **Complexity** | O(1) per entry |

---

### XTRIM

Trims the stream to a specified length or ID.

```
XTRIM key MAXLEN|MINID [=|~] threshold [LIMIT count]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of entries deleted |
| **Complexity** | O(N) |

```php
// Keep approximately 1000 most recent
Redis::xtrim('events', 'MAXLEN', '~', 1000);

// Remove entries older than specific ID
Redis::xtrim('events', 'MINID', '~', $oldId);
```

---

## Reading Entries

### XRANGE

Returns entries in ID range.

```
XRANGE key start end [COUNT count]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of [ID, [field, value, ...]] |
| **Complexity** | O(N) where N is entries returned |

Use `-` for minimum ID, `+` for maximum ID.

```php
// Get all entries
$entries = Redis::xrange('events', '-', '+');

// Get last 10 entries
$entries = Redis::xrange('events', '-', '+', 'COUNT', 10);

// Get entries after specific ID
$entries = Redis::xrange('events', $lastId, '+', 'COUNT', 100);
```

---

### XREVRANGE

Returns entries in reverse order.

```
XREVRANGE key end start [COUNT count]
```

```php
// Get 10 most recent entries
$recent = Redis::xrevrange('events', '+', '-', 'COUNT', 10);
```

---

### XREAD

Reads from one or more streams.

```
XREAD [COUNT count] [BLOCK milliseconds] STREAMS key [key ...] ID [ID ...]
```

| Option | Description |
|--------|-------------|
| `COUNT` | Maximum entries to return per stream |
| `BLOCK` | Wait for new entries (0 = indefinitely) |
| ID | Start reading after this ID |
| `$` | Only new entries (with BLOCK) |
| `0` | All entries from beginning |

| Aspect | Details |
|--------|---------|
| **Returns** | Array of [stream, [[ID, fields], ...]] |
| **Complexity** | O(N) |

```php
// Read new entries (non-blocking)
$entries = Redis::xread('STREAMS', 'events', $lastId);

// Block for up to 5 seconds for new entries
$entries = Redis::xread('BLOCK', 5000, 'STREAMS', 'events', '$');

// Read from multiple streams
$entries = Redis::xread('STREAMS', 'events', 'logs', $eventId, $logId);
```

---

## Consumer Groups

### XGROUP CREATE

Creates a consumer group.

```
XGROUP CREATE key group ID|$ [MKSTREAM] [ENTRIESREAD entries-read]
```

| Option | Description |
|--------|-------------|
| `$` | Start from new entries only |
| `0` | Process all existing entries |
| `MKSTREAM` | Create stream if doesn't exist |

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(1) |

```php
// Create group starting from new entries
Redis::xgroup('CREATE', 'events', 'my-group', '$', 'MKSTREAM');

// Create group to process all entries
Redis::xgroup('CREATE', 'events', 'my-group', '0');
```

---

### XGROUP DESTROY

Destroys a consumer group.

```
XGROUP DESTROY key group
```

---

### XGROUP CREATECONSUMER

Creates a consumer in a group.

```
XGROUP CREATECONSUMER key group consumer
```

---

### XGROUP DELCONSUMER

Deletes a consumer from a group.

```
XGROUP DELCONSUMER key group consumer
```

---

### XGROUP SETID

Sets the last delivered ID for a group.

```
XGROUP SETID key group ID|$ [ENTRIESREAD entries-read]
```

---

### XREADGROUP

Reads entries as a consumer in a group.

```
XREADGROUP GROUP group consumer [COUNT count] [BLOCK ms] [NOACK] STREAMS key [key ...] ID [ID ...]
```

| ID | Meaning |
|----|---------|
| `>` | New entries never delivered to this consumer |
| `0` | Pending entries for this consumer |
| specific ID | Entries after this ID in pending list |

| Aspect | Details |
|--------|---------|
| **Returns** | Array of [stream, [[ID, fields], ...]] |
| **Complexity** | O(M) where M is entries returned |

```php
// Read new entries
$entries = Redis::xreadgroup(
    'GROUP', 'my-group', 'consumer-1',
    'COUNT', 10,
    'BLOCK', 5000,
    'STREAMS', 'events', '>'
);

// Read pending entries (for recovery)
$pending = Redis::xreadgroup(
    'GROUP', 'my-group', 'consumer-1',
    'STREAMS', 'events', '0'
);
```

---

### XACK

Acknowledges entry processing.

```
XACK key group ID [ID ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number acknowledged |
| **Complexity** | O(1) per ID |

```php
// Acknowledge processed entries
Redis::xack('events', 'my-group', $id1, $id2, $id3);
```

---

### XPENDING

Returns pending entries information.

```
XPENDING key group [[IDLE min-idle-time] start end count [consumer]]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Summary or detailed pending info |
| **Complexity** | O(N) |

```php
// Get pending summary
$summary = Redis::xpending('events', 'my-group');
// Returns: [count, first-id, last-id, [[consumer, count], ...]]

// Get pending details
$pending = Redis::xpending('events', 'my-group', '-', '+', 100);

// Get old pending entries (idle > 60 seconds)
$stale = Redis::xpending('events', 'my-group', 'IDLE', 60000, '-', '+', 100);
```

---

### XCLAIM

Claims pending entries for a different consumer.

```
XCLAIM key group consumer min-idle-time ID [ID ...] [IDLE ms] [TIME ms-unix-time] [RETRYCOUNT count] [FORCE] [JUSTID]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of claimed entries (or IDs with JUSTID) |
| **Complexity** | O(N) |

```php
// Claim entries idle for more than 60 seconds
$claimed = Redis::xclaim('events', 'my-group', 'consumer-2', 60000, $id1, $id2);
```

---

### XAUTOCLAIM

Automatically claims old pending entries (Redis 6.2+).

```
XAUTOCLAIM key group consumer min-idle-time start [COUNT count] [JUSTID]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array [next-start-id, [entries], [deleted-ids]] |
| **Complexity** | O(1) |

```php
// Auto-claim entries idle > 60 seconds
[$nextId, $entries, $deleted] = Redis::xautoclaim(
    'events', 'my-group', 'consumer-2', 60000, '0-0', 'COUNT', 100
);
```

---

## Information Commands

### XINFO STREAM

Returns stream information.

```
XINFO STREAM key [FULL [COUNT count]]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Stream metadata |
| **Complexity** | O(1) or O(N) with FULL |

---

### XINFO GROUPS

Returns consumer groups info.

```
XINFO GROUPS key
```

---

### XINFO CONSUMERS

Returns consumers info for a group.

```
XINFO CONSUMERS key group
```

---

## Use Cases

### Event Sourcing

```php
class EventStore
{
    public function append(string $stream, array $event): string
    {
        return Redis::xadd(
            "events:{$stream}",
            'MAXLEN', '~', 10000,  // Keep ~10000 events
            '*',
            'type', $event['type'],
            'data', json_encode($event['data']),
            'timestamp', now()->toIso8601String()
        );
    }

    public function replay(string $stream, string $fromId = '0'): array
    {
        return Redis::xrange("events:{$stream}", $fromId, '+');
    }
}
```

### Message Queue with Consumer Groups

```php
class MessageQueue
{
    private string $stream = 'tasks';
    private string $group = 'workers';

    public function setup(): void
    {
        Redis::xgroup('CREATE', $this->stream, $this->group, '0', 'MKSTREAM');
    }

    public function publish(array $task): string
    {
        return Redis::xadd($this->stream, '*', 'payload', json_encode($task));
    }

    public function consume(string $consumer, int $timeout = 5000): ?array
    {
        $result = Redis::xreadgroup(
            'GROUP', $this->group, $consumer,
            'COUNT', 1,
            'BLOCK', $timeout,
            'STREAMS', $this->stream, '>'
        );

        return $result ? $result[0][1][0] : null;
    }

    public function acknowledge(string $id): void
    {
        Redis::xack($this->stream, $this->group, $id);
    }

    public function recoverStale(string $consumer, int $idleMs = 60000): array
    {
        return Redis::xautoclaim(
            $this->stream, $this->group, $consumer,
            $idleMs, '0-0', 'COUNT', 100
        )[1];
    }
}
```

### Activity Feed

```php
// Add activity
Redis::xadd("feed:{$userId}", 'MAXLEN', '~', 1000, '*',
    'action', 'post',
    'item_id', $postId,
    'timestamp', time()
);

// Get recent activity
$activity = Redis::xrevrange("feed:{$userId}", '+', '-', 'COUNT', 20);

// Poll for new activity (real-time)
$new = Redis::xread('BLOCK', 30000, 'STREAMS', "feed:{$userId}", $lastId);
```

---

## Performance Characteristics

| Command | Complexity | Notes |
|---------|------------|-------|
| XADD | O(1) | Plus O(N) for trimming |
| XLEN | O(1) | Fast count |
| XRANGE/XREVRANGE | O(N) | N = entries returned |
| XREAD | O(N) | Efficient blocking |
| XREADGROUP | O(M) | M = entries returned |
| XACK | O(1) per entry | Very fast |
| XPENDING | O(N) | N = pending entries |

**Best Practices:**
- Use `~` (approximate) with MAXLEN for better performance
- Set appropriate COUNT limits in reads
- Acknowledge entries promptly to keep pending list small
- Use XAUTOCLAIM for recovering stale entries
- Consider stream trimming to manage memory
- Use consumer groups for distributed processing
