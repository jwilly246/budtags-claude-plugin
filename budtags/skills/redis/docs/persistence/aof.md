# Redis AOF Persistence

AOF (Append Only File) logs every write operation, providing better durability than RDB.

---

## How AOF Works

1. Every write command is appended to AOF log
2. On restart, Redis replays commands to rebuild dataset
3. Periodic rewrites compact the log
4. Configurable fsync policies control durability

### Redis 7 Multi-Part AOF

Redis 7+ uses a new AOF structure:
```
appendonlydir/
├── appendonly.aof.1.base.rdb     # Base RDB snapshot
├── appendonly.aof.1.incr.aof     # Incremental AOF
└── appendonly.aof.manifest       # Tracks AOF files
```

---

## Configuration

### Enable AOF

```
# redis.conf
appendonly yes

# AOF directory (Redis 7+)
appenddirname "appendonlydir"

# AOF filename prefix
appendfilename "appendonly.aof"
```

### Fsync Policies

```
# Options: always, everysec, no

# Every write (safest, slowest)
appendfsync always

# Every second (recommended balance)
appendfsync everysec

# Let OS decide (fastest, least safe)
appendfsync no
```

### Policy Comparison

| Policy | Data Loss Risk | Performance Impact |
|--------|---------------|-------------------|
| `always` | ~0 | High (30-50% slower) |
| `everysec` | ~1 second | Low |
| `no` | OS dependent | None |

---

## AOF Rewrite

### Why Rewrite?

AOF logs every command, so it grows continuously:
```
SET counter 1
INCR counter
INCR counter
INCR counter
# Rewrite compacts to: SET counter 4
```

### Configuration

```
# Trigger rewrite when AOF is 100% larger than last rewrite
auto-aof-rewrite-percentage 100

# Minimum size before first rewrite
auto-aof-rewrite-min-size 64mb

# Use RDB preamble in AOF (faster loading)
aof-use-rdb-preamble yes
```

### Manual Rewrite

```php
// Trigger background rewrite
Redis::bgrewriteaof();

// Check status
$info = Redis::info('persistence');
$rewriting = $info['aof_rewrite_in_progress'];
```

---

## Fsync Details

### `appendfsync always`

```
Client → Redis → AOF Buffer → Disk (immediate)
```
- **Durability:** Maximum
- **Performance:** Lowest (~10,000 ops/sec)
- **Use case:** Financial transactions, critical data

### `appendfsync everysec`

```
Client → Redis → AOF Buffer → [1 sec] → Disk
```
- **Durability:** ~1 second data loss
- **Performance:** Good (~100,000 ops/sec)
- **Use case:** Most production workloads

### `appendfsync no`

```
Client → Redis → AOF Buffer → [OS decides] → Disk
```
- **Durability:** Up to 30 seconds data loss (Linux default)
- **Performance:** Maximum
- **Use case:** When durability isn't critical

---

## Commands

### Check AOF Status

```php
$info = Redis::info('persistence');

$aofStatus = [
    'enabled' => (bool) $info['aof_enabled'],
    'current_size' => $info['aof_current_size'],
    'base_size' => $info['aof_base_size'],
    'pending_rewrite' => (bool) $info['aof_pending_rewrite'],
    'rewrite_in_progress' => (bool) $info['aof_rewrite_in_progress'],
    'last_rewrite_time_sec' => $info['aof_last_rewrite_time_sec'],
    'buffer_length' => $info['aof_buffer_length'],
    'pending_bio_fsync' => $info['aof_pending_bio_fsync'],
];
```

### Manage AOF

```php
// Enable AOF at runtime
Redis::config('SET', 'appendonly', 'yes');

// Trigger rewrite
Redis::bgrewriteaof();
```

---

## AOF Advantages

| Advantage | Description |
|-----------|-------------|
| **Durability** | Configurable, up to every write |
| **Readable format** | Human-readable commands (pre-rewrite) |
| **Append-only** | No corruption from partial writes |
| **Auto-rewrite** | Compacts automatically |
| **Crash recovery** | Replay logs exactly |

---

## AOF Disadvantages

| Disadvantage | Description |
|--------------|-------------|
| **File size** | Larger than RDB (before rewrite) |
| **Slower restart** | Must replay commands |
| **Performance** | fsync overhead (with `always`) |
| **Disk I/O** | Continuous writes |

---

## Recovery

### Normal Recovery

```bash
# AOF is automatically loaded on restart
systemctl restart redis
```

### Corrupted AOF Recovery

```bash
# Check for corruption
redis-check-aof /var/lib/redis/appendonlydir/appendonly.aof.1.incr.aof

# Fix corruption (truncates at error point)
redis-check-aof --fix /var/lib/redis/appendonlydir/appendonly.aof.1.incr.aof

# Restart Redis
systemctl restart redis
```

### Recovery Order (when both enabled)

1. Redis checks for AOF first (if enabled)
2. Falls back to RDB if AOF doesn't exist
3. With `aof-use-rdb-preamble yes`: loads RDB portion, then replays AOF

---

## Monitoring

### AOF Health Check

```php
class AofMonitor
{
    public function check(): array
    {
        $info = Redis::info('persistence');

        $status = [
            'enabled' => (bool) $info['aof_enabled'],
            'current_size_mb' => round($info['aof_current_size'] / 1048576, 2),
            'last_rewrite_sec' => $info['aof_last_rewrite_time_sec'],
        ];

        // Check if rewrite is needed
        if ($info['aof_base_size'] > 0) {
            $growthRatio = $info['aof_current_size'] / $info['aof_base_size'];
            $status['growth_ratio'] = round($growthRatio, 2);
            $status['needs_rewrite'] = $growthRatio > 2;
        }

        // Check for lagging fsync
        if ($info['aof_pending_bio_fsync'] > 0) {
            $status['warning'] = 'Pending fsync operations';
        }

        return $status;
    }
}
```

### AOF Growth Alert

```php
Schedule::call(function () {
    $info = Redis::info('persistence');

    $sizeMb = $info['aof_current_size'] / 1048576;

    if ($sizeMb > 1024) {  // > 1 GB
        Log::warning("AOF file large: {$sizeMb}MB");
    }

    if ($info['aof_delayed_fsync'] > 0) {
        Log::warning("AOF fsync delays: {$info['aof_delayed_fsync']}");
    }
})->everyFiveMinutes();
```

---

## Performance Tuning

### Reduce Rewrite Impact

```
# Don't fsync during rewrite (faster, slightly less safe)
no-appendfsync-on-rewrite yes

# Rewrite less frequently
auto-aof-rewrite-percentage 200
auto-aof-rewrite-min-size 128mb
```

### RDB Preamble (Recommended)

```
# Uses RDB format for base, AOF for changes
# Faster loading, smaller files
aof-use-rdb-preamble yes
```

---

## BudTags Configuration

### For Session/Queue Data

```
# Good durability for sessions and queues
appendonly yes
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-use-rdb-preamble yes
```

### For Cache Only

```
# AOF not needed for regenerable cache
appendonly no
```

---

## AOF Format

### Pre-Rewrite (RESP Protocol)

```
*3
$3
SET
$5
mykey
$7
myvalue
```

### With RDB Preamble

```
[RDB binary data]
*3
$3
SET
$5
newkey
$8
newvalue
```

---

## Key Takeaways

1. **Append-only** - Commands logged sequentially
2. **fsync policies** - Trade durability for performance
3. **everysec recommended** - Best balance for most uses
4. **Auto-rewrite** - Compacts periodically
5. **RDB preamble** - Faster loading (Redis 4+)
6. **Larger files** - But more durable than RDB
7. **Slower restart** - Command replay takes time
8. **Combine with RDB** - Best of both worlds
