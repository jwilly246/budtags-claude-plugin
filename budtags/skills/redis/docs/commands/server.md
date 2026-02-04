# Redis Server Commands

Server commands manage Redis configuration, monitoring, persistence, and administration.

---

## Information & Monitoring

### INFO

Returns server information and statistics.

```
INFO [section]
```

| Section | Contents |
|---------|----------|
| `server` | Version, OS, process info |
| `clients` | Connected clients, blocked clients |
| `memory` | Memory usage, fragmentation |
| `persistence` | RDB/AOF status |
| `stats` | Commands processed, connections |
| `replication` | Master/replica info |
| `cpu` | CPU consumption |
| `modules` | Loaded modules |
| `errorstats` | Error statistics |
| `cluster` | Cluster status |
| `keyspace` | Database key counts |

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string with stats |
| **Complexity** | O(1) |

```php
// Get all info
$info = Redis::info();

// Get specific section
$memory = Redis::info('memory');

// Key metrics
$usedMemory = $info['used_memory_human'];
$connectedClients = $info['connected_clients'];
$hitRate = $info['keyspace_hits'] / ($info['keyspace_hits'] + $info['keyspace_misses']);
```

---

### DBSIZE

Returns number of keys in current database.

```
DBSIZE
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - key count |
| **Complexity** | O(1) |

```php
Redis::command('select', [1]);
$keyCount = Redis::command('dbsize');
```

---

### TIME

Returns server time.

```
TIME
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array [unix_timestamp, microseconds] |
| **Complexity** | O(1) |

---

### LASTSAVE

Returns timestamp of last successful save.

```
LASTSAVE
```

---

## Configuration

### CONFIG GET

Gets configuration parameter values.

```
CONFIG GET parameter
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of name-value pairs |
| **Complexity** | O(N) |

```php
// Get specific parameter
$maxmemory = Redis::config('GET', 'maxmemory');

// Get multiple with pattern
$allTimeout = Redis::config('GET', '*timeout*');

// Get all
$all = Redis::config('GET', '*');
```

---

### CONFIG SET

Sets configuration parameters at runtime.

```
CONFIG SET parameter value [parameter value ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(N) |

```php
Redis::config('SET', 'maxmemory', '2gb');
Redis::config('SET', 'maxmemory-policy', 'allkeys-lru');
```

---

### CONFIG REWRITE

Persists runtime config changes to redis.conf.

```
CONFIG REWRITE
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(N) |

---

### CONFIG RESETSTAT

Resets INFO statistics.

```
CONFIG RESETSTAT
```

Resets: keyspace_hits, keyspace_misses, total_commands_processed, etc.

---

## Memory Management

### MEMORY STATS

Returns memory usage details.

```
MEMORY STATS
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of memory statistics |
| **Complexity** | O(1) |

```php
$memStats = Redis::memory('STATS');
```

---

### MEMORY DOCTOR

Analyzes memory and suggests optimizations.

```
MEMORY DOCTOR
```

| Aspect | Details |
|--------|---------|
| **Returns** | Analysis report |
| **Complexity** | O(1) |

---

### MEMORY USAGE

Estimates memory used by a key.

```
MEMORY USAGE key [SAMPLES count]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - bytes |
| **Complexity** | O(N) for collections |

```php
$bytes = Redis::memory('USAGE', 'mykey');
```

---

### MEMORY MALLOC-STATS

Returns allocator statistics.

```
MEMORY MALLOC-STATS
```

---

### MEMORY PURGE

Requests memory release to OS.

```
MEMORY PURGE
```

---

## Persistence

### SAVE

Synchronously saves database to disk.

```
SAVE
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(N) |
| **Blocking** | Yes - blocks all clients |

**Warning:** Blocks Redis. Use BGSAVE instead.

---

### BGSAVE

Asynchronously saves database to disk.

```
BGSAVE [SCHEDULE]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Background saving started |
| **Complexity** | O(1) to start |
| **SCHEDULE** | Waits for other saves to complete |

```php
Redis::bgsave();
```

---

### BGREWRITEAOF

Asynchronously rewrites AOF file.

```
BGREWRITEAOF
```

| Aspect | Details |
|--------|---------|
| **Returns** | Background append only file rewriting started |
| **Complexity** | O(1) to start |

---

## Performance Analysis

### SLOWLOG

Manages the slow query log.

```
SLOWLOG GET [count]
SLOWLOG LEN
SLOWLOG RESET
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of slow queries |
| **Complexity** | O(N) |

```php
// Get last 10 slow queries
$slow = Redis::slowlog('GET', 10);
// Each entry: [id, timestamp, duration_microseconds, [command, args...]]

// Get count
$count = Redis::slowlog('LEN');

// Clear log
Redis::slowlog('RESET');
```

---

### LATENCY

Monitors latency events.

```
LATENCY LATEST
LATENCY HISTORY event-name
LATENCY RESET [event-name ...]
LATENCY DOCTOR
LATENCY GRAPH event-name
LATENCY HISTOGRAM [command-name ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Latency data |
| **Complexity** | Varies |

```php
// Get latest latency events
$latest = Redis::latency('LATEST');

// Get analysis
$analysis = Redis::latency('DOCTOR');
```

---

### MONITOR

Real-time command stream (debugging).

```
MONITOR
```

**Warning:** Impacts performance significantly. Use only for debugging.

---

## Client Management

### CLIENT LIST

Lists connected clients.

```
CLIENT LIST [TYPE normal|master|replica|pubsub] [ID client-id ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Client information |
| **Complexity** | O(N) |

```php
$clients = Redis::client('LIST');
```

---

### CLIENT INFO

Returns current connection info.

```
CLIENT INFO
```

---

### CLIENT KILL

Terminates client connections.

```
CLIENT KILL [IP:port | ID client-id | TYPE type | USER username | ADDR addr:port | SKIPME yes|no]
```

---

### CLIENT PAUSE

Suspends client commands.

```
CLIENT PAUSE timeout [WRITE|ALL]
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Use** | Controlled failover, maintenance |

---

### CLIENT UNPAUSE

Resumes paused clients.

```
CLIENT UNPAUSE
```

---

### CLIENT SETNAME / GETNAME

Sets/gets connection name.

```
CLIENT SETNAME connection-name
CLIENT GETNAME
```

Useful for identifying connections in CLIENT LIST.

---

### CLIENT ID

Returns current connection ID.

```
CLIENT ID
```

---

### CLIENT TRACKING

Enables client-side caching.

```
CLIENT TRACKING ON|OFF [REDIRECT client-id] [PREFIX prefix ...] [BCAST] [OPTIN] [OPTOUT] [NOLOOP]
```

| Aspect | Details |
|--------|---------|
| **Since** | Redis 6.0 |
| **Use** | Client-side caching invalidation |

---

## Command Information

### COMMAND

Lists all commands.

```
COMMAND
COMMAND COUNT
COMMAND INFO command-name [command-name ...]
COMMAND DOCS [command-name ...]
COMMAND LIST [FILTERBY MODULE|ACLCAT|PATTERN ...]
COMMAND GETKEYS command [arg ...]
COMMAND GETKEYSANDFLAGS command [arg ...]
```

---

## Debugging

### DEBUG

Various debugging commands.

```
DEBUG OBJECT key
DEBUG SEGFAULT
DEBUG SLEEP seconds
DEBUG QUICKLIST-PACKED-THRESHOLD threshold
```

**Warning:** For debugging only. Can crash Redis.

---

### OBJECT

Inspects key internals.

```
OBJECT ENCODING key
OBJECT FREQ key
OBJECT IDLETIME key
OBJECT REFCOUNT key
OBJECT HELP
```

```php
// Check internal encoding
$encoding = Redis::object('ENCODING', 'mykey');
// "embstr", "int", "listpack", "hashtable", etc.
```

---

## Server Lifecycle

### SHUTDOWN

Shuts down Redis.

```
SHUTDOWN [NOSAVE|SAVE] [NOW] [FORCE] [ABORT]
```

| Option | Description |
|--------|-------------|
| `SAVE` | Save before shutdown |
| `NOSAVE` | Don't save |
| `NOW` | Skip waiting for clients |
| `FORCE` | Ignore errors during save |
| `ABORT` | Cancel in-progress shutdown |

---

### PING

Tests connectivity.

```
PING [message]
```

| Aspect | Details |
|--------|---------|
| **Returns** | PONG or echoed message |
| **Complexity** | O(1) |

```php
$pong = Redis::ping();  // "PONG"
$echo = Redis::ping('hello');  // "hello"
```

---

### ECHO

Echoes message.

```
ECHO message
```

---

## BudTags Monitoring

### Health Check

```php
class RedisHealthCheck
{
    public function check(): array
    {
        $info = Redis::info();

        return [
            'status' => 'healthy',
            'version' => $info['redis_version'],
            'uptime_days' => floor($info['uptime_in_seconds'] / 86400),
            'connected_clients' => $info['connected_clients'],
            'used_memory' => $info['used_memory_human'],
            'peak_memory' => $info['used_memory_peak_human'],
            'hit_rate' => $this->calculateHitRate($info),
            'keys' => [
                'db0' => $info['db0'] ?? 'empty',
                'db1' => $info['db1'] ?? 'empty',
                'db2' => $info['db2'] ?? 'empty',
            ],
        ];
    }

    private function calculateHitRate(array $info): string
    {
        $hits = $info['keyspace_hits'];
        $misses = $info['keyspace_misses'];
        $total = $hits + $misses;

        return $total > 0
            ? round(($hits / $total) * 100, 2) . '%'
            : 'N/A';
    }
}
```

### Memory Monitoring

```php
class RedisMemoryMonitor
{
    public function analyze(): array
    {
        $info = Redis::info('memory');
        $stats = Redis::memory('STATS');

        $used = $info['used_memory'];
        $max = $info['maxmemory'] ?: PHP_INT_MAX;
        $usage = $max > 0 ? ($used / $max) * 100 : 0;

        return [
            'used' => $info['used_memory_human'],
            'peak' => $info['used_memory_peak_human'],
            'max' => $info['maxmemory_human'] ?: 'unlimited',
            'usage_percent' => round($usage, 2),
            'fragmentation_ratio' => $info['mem_fragmentation_ratio'],
            'evicted_keys' => $info['evicted_keys'],
            'warning' => $usage > 80 ? 'High memory usage' : null,
        ];
    }
}
```

---

## Performance Notes

| Command | Impact | Production Safe |
|---------|--------|-----------------|
| INFO | Low | Yes |
| CONFIG GET | Low | Yes |
| CONFIG SET | Low | Yes (careful with settings) |
| SAVE | High | **No** (use BGSAVE) |
| BGSAVE | Medium | Yes |
| MONITOR | High | **No** |
| DEBUG | Variable | **No** |
| SLOWLOG | Low | Yes |
