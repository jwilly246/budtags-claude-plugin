# Redis Latency Diagnosis

Identifying and resolving sources of Redis latency.

---

## Latency Sources

### Network Latency

| Location | Typical Latency |
|----------|----------------|
| Same machine | < 0.1ms |
| Same datacenter | 0.1-1ms |
| Cross-region | 10-100ms |
| Internet | 50-200ms |

### Redis Processing Latency

| Cause | Impact | Resolution |
|-------|--------|------------|
| Slow commands | 10-1000ms | Use SCAN, avoid KEYS |
| Big keys | 10-100ms | Split large values |
| Memory pressure | 5-50ms | Add memory, tune eviction |
| Persistence | 5-100ms | Tune AOF/RDB settings |
| Fork (BGSAVE) | 10-1000ms | Reduce dataset size |

---

## Measuring Latency

### Built-in Latency Monitoring

```bash
# Enable monitoring (threshold in ms)
redis-cli CONFIG SET latency-monitor-threshold 5

# Check latest latency events
redis-cli LATENCY LATEST

# Get latency history for specific event
redis-cli LATENCY HISTORY command
redis-cli LATENCY HISTORY fast-command
redis-cli LATENCY HISTORY fork

# Reset latency data
redis-cli LATENCY RESET
```

### Latency Doctor

```bash
redis-cli LATENCY DOCTOR

# Example output:
# I have a few latency reports to share with you:
#
# 1. command: 5 latency spikes (average 20ms, worst 150ms).
#    Worst since restart: 150ms.
#
# 2. fork: 2 latency spikes (average 500ms, worst 800ms).
#    Worst since restart: 800ms.
```

### Intrinsic Latency Test

```bash
# Test system's intrinsic latency (run for 10 seconds)
redis-cli --intrinsic-latency 10

# Output:
# Max latency so far: 1 microseconds.
# Max latency so far: 2 microseconds.
# ...
# 12345678 total runs (avg 0.81 us per run)
```

---

## Common Latency Issues

### 1. Slow Commands

**Detection:**
```bash
# Check slow log
redis-cli SLOWLOG GET 10

# Output shows:
# ID, timestamp, duration (μs), command
```

**Laravel monitoring:**
```php
class SlowCommandMonitor
{
    public function getSlowCommands(int $limit = 10): array
    {
        $slowlog = Redis::slowlog('GET', $limit);

        return array_map(function ($entry) {
            return [
                'id' => $entry[0],
                'timestamp' => date('Y-m-d H:i:s', $entry[1]),
                'duration_ms' => round($entry[2] / 1000, 2),
                'command' => implode(' ', array_slice($entry[3], 0, 5)),
            ];
        }, $slowlog);
    }
}
```

**Common slow commands:**
```php
// ❌ Slow: O(N) commands
Redis::keys('pattern*');           // Use SCAN instead
Redis::smembers('huge:set');       // Use SSCAN instead
Redis::hgetall('huge:hash');       // Use HSCAN instead
Redis::lrange('list', 0, -1);      // Paginate instead

// ✅ Fast alternatives
$cursor = 0;
do {
    [$cursor, $keys] = Redis::scan($cursor, 'MATCH', 'pattern*', 'COUNT', 100);
} while ($cursor != 0);
```

### 2. Big Keys

**Detection:**
```bash
redis-cli --bigkeys
redis-cli --memkeys
```

**Laravel detection:**
```php
class BigKeyFinder
{
    public function find(int $threshold = 10000): array
    {
        $bigKeys = [];
        $cursor = 0;

        do {
            [$cursor, $keys] = Redis::scan($cursor, 'COUNT', 100);

            foreach ($keys as $key) {
                $size = $this->getKeySize($key);
                if ($size >= $threshold) {
                    $bigKeys[$key] = [
                        'type' => Redis::type($key),
                        'size' => $size,
                        'memory' => Redis::memory('USAGE', $key),
                    ];
                }
            }
        } while ($cursor != 0);

        return $bigKeys;
    }

    private function getKeySize(string $key): int
    {
        return match (Redis::type($key)) {
            'string' => Redis::strlen($key),
            'list' => Redis::llen($key),
            'set' => Redis::scard($key),
            'zset' => Redis::zcard($key),
            'hash' => Redis::hlen($key),
            'stream' => Redis::xlen($key),
            default => 0,
        };
    }
}
```

### 3. Fork Latency (BGSAVE/BGREWRITEAOF)

**Detection:**
```php
$info = Redis::info('persistence');

$forkStats = [
    'last_bgsave_time_sec' => $info['rdb_last_bgsave_time_sec'],
    'last_aof_rewrite_time_sec' => $info['aof_last_rewrite_time_sec'],
    'last_cow_size' => $info['rdb_last_cow_size'] ?? 'N/A',
];
```

**Mitigation:**
```
# Reduce fork impact
vm.overcommit_memory = 1

# Disable THP
echo never > /sys/kernel/mm/transparent_hugepage/enabled
```

### 4. Memory Pressure

**Detection:**
```php
$info = Redis::info('memory');

$pressure = [
    'used_memory' => $info['used_memory_human'],
    'maxmemory' => $info['maxmemory'],
    'evicted_keys' => $info['evicted_keys'],
    'fragmentation' => $info['mem_fragmentation_ratio'],
];

if ($info['maxmemory'] > 0) {
    $usage = ($info['used_memory'] / $info['maxmemory']) * 100;
    if ($usage > 80) {
        Log::warning("Redis memory at {$usage}%");
    }
}
```

### 5. Network Issues

**Detection:**
```php
class NetworkLatencyChecker
{
    public function check(int $samples = 100): array
    {
        $latencies = [];

        for ($i = 0; $i < $samples; $i++) {
            $start = hrtime(true);
            Redis::ping();
            $latencies[] = (hrtime(true) - $start) / 1e6;
        }

        $avg = array_sum($latencies) / count($latencies);

        return [
            'avg_ms' => round($avg, 3),
            'max_ms' => round(max($latencies), 3),
            'jitter_ms' => round(max($latencies) - min($latencies), 3),
            'warning' => $avg > 1 ? 'High network latency' : null,
        ];
    }
}
```

---

## Latency Monitoring Dashboard

```php
class LatencyDashboard
{
    public function collect(): array
    {
        return [
            'ping_latency' => $this->measurePing(),
            'slow_commands' => $this->getSlowCommands(),
            'persistence_impact' => $this->getPersistenceStats(),
            'memory_pressure' => $this->getMemoryPressure(),
            'client_stats' => $this->getClientStats(),
        ];
    }

    private function measurePing(): array
    {
        $latencies = [];
        for ($i = 0; $i < 10; $i++) {
            $start = hrtime(true);
            Redis::ping();
            $latencies[] = (hrtime(true) - $start) / 1e6;
        }

        return [
            'avg_ms' => round(array_sum($latencies) / 10, 3),
            'max_ms' => round(max($latencies), 3),
        ];
    }

    private function getSlowCommands(): array
    {
        $slow = Redis::slowlog('GET', 5);
        return array_map(fn($s) => [
            'command' => $s[3][0] ?? 'unknown',
            'duration_ms' => round($s[2] / 1000, 2),
        ], $slow);
    }

    private function getPersistenceStats(): array
    {
        $info = Redis::info('persistence');
        return [
            'rdb_in_progress' => (bool) $info['rdb_bgsave_in_progress'],
            'aof_rewrite_in_progress' => (bool) $info['aof_rewrite_in_progress'],
            'last_fork_ms' => $info['rdb_last_bgsave_time_sec'] * 1000,
        ];
    }

    private function getMemoryPressure(): array
    {
        $info = Redis::info('memory');
        return [
            'used' => $info['used_memory_human'],
            'fragmentation' => $info['mem_fragmentation_ratio'],
            'evicted' => Redis::info('stats')['evicted_keys'],
        ];
    }

    private function getClientStats(): array
    {
        $info = Redis::info('clients');
        return [
            'connected' => $info['connected_clients'],
            'blocked' => $info['blocked_clients'],
        ];
    }
}
```

---

## Slow Log Configuration

```
# redis.conf

# Log commands taking longer than 10ms
slowlog-log-slower-than 10000

# Keep 128 entries
slowlog-max-len 128
```

### Runtime Configuration

```php
// Set threshold (microseconds)
Redis::config('SET', 'slowlog-log-slower-than', 10000);

// Get current settings
$config = Redis::config('GET', 'slowlog-*');
```

---

## Latency Debugging Checklist

### Immediate Checks

```php
class LatencyDebugger
{
    public function diagnose(): array
    {
        $issues = [];

        // 1. Check slow log
        $slowlog = Redis::slowlog('GET', 1);
        if ($slowlog && $slowlog[0][2] > 100000) { // > 100ms
            $issues[] = "Slow command: {$slowlog[0][3][0]} took " .
                       round($slowlog[0][2] / 1000) . "ms";
        }

        // 2. Check persistence
        $persistence = Redis::info('persistence');
        if ($persistence['rdb_bgsave_in_progress']) {
            $issues[] = "BGSAVE in progress";
        }
        if ($persistence['aof_rewrite_in_progress']) {
            $issues[] = "AOF rewrite in progress";
        }

        // 3. Check memory
        $memory = Redis::info('memory');
        if ($memory['mem_fragmentation_ratio'] > 1.5) {
            $issues[] = "High memory fragmentation: {$memory['mem_fragmentation_ratio']}";
        }

        // 4. Check clients
        $clients = Redis::info('clients');
        if ($clients['blocked_clients'] > 0) {
            $issues[] = "Blocked clients: {$clients['blocked_clients']}";
        }

        // 5. Check evictions
        $stats = Redis::info('stats');
        if ($stats['evicted_keys'] > 0) {
            $issues[] = "Keys being evicted: {$stats['evicted_keys']}";
        }

        return $issues ?: ['No obvious latency issues detected'];
    }
}
```

---

## Key Takeaways

1. **Enable latency monitoring** - `latency-monitor-threshold`
2. **Check slow log regularly** - Find problematic commands
3. **Use SCAN not KEYS** - For pattern matching
4. **Split big keys** - Large collections cause delays
5. **Monitor fork operations** - BGSAVE/AOF impact
6. **Watch memory pressure** - Eviction causes latency
7. **Measure network latency** - Separate from Redis latency
8. **Use LATENCY DOCTOR** - Quick diagnostic
