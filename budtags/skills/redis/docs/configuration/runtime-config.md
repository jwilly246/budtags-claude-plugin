# Redis Runtime Configuration

Modify Redis settings without restart using CONFIG commands.

---

## CONFIG GET

### Get Single Setting

```php
$value = Redis::config('GET', 'maxmemory');
// Returns: ['maxmemory' => '2147483648']
```

### Get Multiple Settings (Pattern)

```php
// Get all memory settings
$memorySettings = Redis::config('GET', 'maxmemory*');

// Get all settings
$allSettings = Redis::config('GET', '*');
```

---

## CONFIG SET

### Set Single Value

```php
// Memory limit
Redis::config('SET', 'maxmemory', '2gb');

// Eviction policy
Redis::config('SET', 'maxmemory-policy', 'allkeys-lru');

// Slow log threshold (microseconds)
Redis::config('SET', 'slowlog-log-slower-than', '10000');
```

### Common Runtime Changes

```php
// Memory management
Redis::config('SET', 'maxmemory', '4gb');
Redis::config('SET', 'maxmemory-policy', 'volatile-lru');
Redis::config('SET', 'maxmemory-samples', '10');

// Persistence
Redis::config('SET', 'appendfsync', 'everysec');
Redis::config('SET', 'auto-aof-rewrite-percentage', '100');

// Performance
Redis::config('SET', 'activedefrag', 'yes');
Redis::config('SET', 'lazyfree-lazy-eviction', 'yes');

// Slow log
Redis::config('SET', 'slowlog-log-slower-than', '5000');
Redis::config('SET', 'slowlog-max-len', '256');

// Client limits
Redis::config('SET', 'timeout', '300');
Redis::config('SET', 'maxclients', '5000');
```

---

## CONFIG REWRITE

Save current configuration to redis.conf:

```php
// Persist runtime changes to config file
Redis::config('REWRITE');
```

**Note:** Requires writable config file path.

---

## CONFIG RESETSTAT

Reset INFO statistics:

```php
Redis::config('RESETSTAT');
```

Resets:
- Keyspace hits/misses
- Commands processed
- Connections received
- Expired keys count

---

## Commonly Modified Settings

### Memory

| Setting | Example | Effect |
|---------|---------|--------|
| maxmemory | 2gb | Memory limit |
| maxmemory-policy | allkeys-lru | Eviction behavior |
| maxmemory-samples | 10 | LRU accuracy |

### Persistence

| Setting | Example | Effect |
|---------|---------|--------|
| appendfsync | everysec | AOF sync frequency |
| auto-aof-rewrite-percentage | 100 | Rewrite threshold |
| save | "900 1" | RDB trigger |

### Performance

| Setting | Example | Effect |
|---------|---------|--------|
| activedefrag | yes | Memory defragmentation |
| lazyfree-lazy-eviction | yes | Async eviction |
| hz | 10 | Server frequency |

### Clients

| Setting | Example | Effect |
|---------|---------|--------|
| timeout | 300 | Client timeout |
| maxclients | 10000 | Max connections |

### Monitoring

| Setting | Example | Effect |
|---------|---------|--------|
| slowlog-log-slower-than | 10000 | Slow log threshold (μs) |
| slowlog-max-len | 128 | Slow log entries |
| latency-monitor-threshold | 100 | Latency monitoring |

---

## Settings That Cannot Be Changed at Runtime

Some settings require restart:

| Setting | Reason |
|---------|--------|
| bind | Network binding |
| port | Network binding |
| unixsocket | Socket creation |
| daemonize | Process mode |
| pidfile | File handle |
| cluster-enabled | Cluster mode |
| replicaof (initial) | Replication setup |
| loadmodule | Module loading |
| tls-* | TLS configuration |

---

## Laravel Configuration Helper

```php
class RedisConfigManager
{
    public function get(string $pattern = '*'): array
    {
        return Redis::config('GET', $pattern);
    }

    public function set(string $key, string $value): bool
    {
        return Redis::config('SET', $key, $value) === 'OK';
    }

    public function persist(): bool
    {
        try {
            Redis::config('REWRITE');
            return true;
        } catch (\Exception $e) {
            Log::error('Failed to persist Redis config', ['error' => $e->getMessage()]);
            return false;
        }
    }

    public function setMemory(string $limit, string $policy = 'allkeys-lru'): void
    {
        $this->set('maxmemory', $limit);
        $this->set('maxmemory-policy', $policy);
    }

    public function enableSlowLog(int $thresholdMs = 10, int $maxEntries = 128): void
    {
        $this->set('slowlog-log-slower-than', (string) ($thresholdMs * 1000));
        $this->set('slowlog-max-len', (string) $maxEntries);
    }

    public function optimizeForPerformance(): void
    {
        $this->set('activedefrag', 'yes');
        $this->set('lazyfree-lazy-eviction', 'yes');
        $this->set('lazyfree-lazy-expire', 'yes');
        $this->set('lazyfree-lazy-server-del', 'yes');
    }

    public function getStatus(): array
    {
        $config = $this->get('*');

        return [
            'memory' => [
                'maxmemory' => $config['maxmemory'],
                'policy' => $config['maxmemory-policy'],
            ],
            'persistence' => [
                'rdb_enabled' => !empty($config['save']),
                'aof_enabled' => $config['appendonly'] === 'yes',
            ],
            'performance' => [
                'activedefrag' => $config['activedefrag'],
                'lazyfree' => $config['lazyfree-lazy-eviction'],
            ],
        ];
    }
}
```

---

## Monitoring Configuration Changes

### Log Configuration Changes

```php
class ConfigChangeLogger
{
    public function setAndLog(string $key, string $newValue, string $reason): bool
    {
        $current = Redis::config('GET', $key);
        $oldValue = $current[$key] ?? 'not set';

        $success = Redis::config('SET', $key, $newValue) === 'OK';

        Log::info('Redis configuration changed', [
            'key' => $key,
            'old_value' => $oldValue,
            'new_value' => $newValue,
            'reason' => $reason,
            'success' => $success,
        ]);

        return $success;
    }
}
```

### Track Current vs Default

```php
class ConfigAuditor
{
    private array $defaults = [
        'maxmemory' => '0',
        'maxmemory-policy' => 'noeviction',
        'appendonly' => 'no',
        'activedefrag' => 'no',
    ];

    public function getCustomized(): array
    {
        $current = Redis::config('GET', '*');
        $customized = [];

        foreach ($this->defaults as $key => $default) {
            if (isset($current[$key]) && $current[$key] !== $default) {
                $customized[$key] = [
                    'default' => $default,
                    'current' => $current[$key],
                ];
            }
        }

        return $customized;
    }
}
```

---

## Scheduled Configuration

### Adjust Settings by Time

```php
// Peak hours: more aggressive eviction
Schedule::call(function () {
    Redis::config('SET', 'maxmemory-samples', '15');
})->dailyAt('08:00');

// Off-peak: reduce CPU
Schedule::call(function () {
    Redis::config('SET', 'maxmemory-samples', '5');
})->dailyAt('22:00');
```

### Temporary Changes

```php
class TemporaryConfig
{
    public function withConfig(array $settings, callable $callback): mixed
    {
        $original = [];

        // Store and apply new settings
        foreach ($settings as $key => $value) {
            $current = Redis::config('GET', $key);
            $original[$key] = $current[$key] ?? null;
            Redis::config('SET', $key, $value);
        }

        try {
            return $callback();
        } finally {
            // Restore original settings
            foreach ($original as $key => $value) {
                if ($value !== null) {
                    Redis::config('SET', $key, $value);
                }
            }
        }
    }
}

// Usage
$config = new TemporaryConfig();
$config->withConfig(
    ['maxmemory-samples' => '20'],
    function () {
        // Run with higher accuracy
        performCriticalOperation();
    }
);
```

---

## Key Takeaways

1. **CONFIG GET** - Read current settings
2. **CONFIG SET** - Change settings without restart
3. **CONFIG REWRITE** - Persist changes to file
4. **Pattern matching** - Use `*` for multiple settings
5. **Some require restart** - Network, cluster, TLS settings
6. **Log changes** - Track who changed what
7. **Test first** - Verify in staging
8. **Persist important changes** - Use REWRITE for durability
