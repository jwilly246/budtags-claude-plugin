# Redis Memory Analysis

Tools and techniques for understanding and debugging Redis memory usage.

---

## MEMORY Commands

### MEMORY USAGE

Get memory used by a single key:

```php
// Basic usage
$bytes = Redis::memory('USAGE', 'mykey');

// With samples (for large collections)
$bytes = Redis::memory('USAGE', 'large:hash', 'SAMPLES', 5);
```

**Output:** Integer (bytes) or null if key doesn't exist

### MEMORY STATS

Comprehensive memory statistics:

```php
$stats = Redis::memory('STATS');

// Key metrics:
[
    'peak.allocated' => 12345678,          // Peak memory
    'total.allocated' => 10000000,         // Current allocated
    'startup.allocated' => 1000000,        // Base memory
    'replication.backlog' => 0,            // Replication buffer
    'clients.slaves' => 0,                 // Replica connections
    'clients.normal' => 15000,             // Client connections
    'aof.buffer' => 0,                     // AOF pending buffer
    'dataset.bytes' => 8000000,            // Actual data
    'dataset.percentage' => 80.0,          // Data % of total
    'overhead.total' => 2000000,           // Non-data overhead
    'overhead.hashtable.main' => 500000,   // Main dict overhead
    'overhead.hashtable.expires' => 100000,// Expires dict overhead
    'fragmentation' => 1.2,                // Fragmentation ratio
    'fragmentation.bytes' => 500000,       // Fragmented bytes
]
```

### MEMORY DOCTOR

Get memory health report:

```php
$report = Redis::memory('DOCTOR');

// Returns diagnostic text, e.g.:
// "Sam, I have no memory problems with you."
// OR
// "High fragmentation detected. Consider restarting..."
```

### MEMORY MALLOC-SIZE

Check allocation size for a pointer:

```php
$size = Redis::memory('MALLOC-SIZE', 12345);
```

### MEMORY PURGE

Force memory allocator to release memory (jemalloc only):

```php
Redis::memory('PURGE');
```

---

## INFO Memory Section

```php
$info = Redis::info('memory');
```

| Metric | Description |
|--------|-------------|
| `used_memory` | Total bytes allocated by Redis |
| `used_memory_human` | Human-readable used memory |
| `used_memory_rss` | OS-reported resident set size |
| `used_memory_peak` | Peak memory usage |
| `used_memory_peak_human` | Human-readable peak |
| `used_memory_overhead` | Non-data memory |
| `used_memory_dataset` | Data memory |
| `used_memory_startup` | Initial memory at startup |
| `mem_fragmentation_ratio` | RSS / used_memory |
| `mem_fragmentation_bytes` | Fragmented bytes |
| `mem_allocator` | Memory allocator (jemalloc, libc, etc.) |
| `maxmemory` | Configured limit |
| `maxmemory_policy` | Eviction policy |
| `mem_clients_normal` | Memory for client buffers |
| `mem_clients_slaves` | Memory for replica buffers |

---

## Analyzing Memory Distribution

### By Key Pattern

```php
class MemoryAnalyzer
{
    public function analyzeByPattern(): array
    {
        $patterns = [];
        $cursor = 0;

        do {
            [$cursor, $keys] = Redis::scan($cursor, 'COUNT', 1000);

            foreach ($keys as $key) {
                $pattern = $this->extractPattern($key);
                $bytes = Redis::memory('USAGE', $key) ?? 0;

                if (!isset($patterns[$pattern])) {
                    $patterns[$pattern] = ['count' => 0, 'bytes' => 0];
                }

                $patterns[$pattern]['count']++;
                $patterns[$pattern]['bytes'] += $bytes;
            }
        } while ($cursor != 0);

        // Sort by bytes descending
        uasort($patterns, fn($a, $b) => $b['bytes'] <=> $a['bytes']);

        return $patterns;
    }

    private function extractPattern(string $key): string
    {
        // Replace numeric IDs with placeholder
        return preg_replace('/:\d+/', ':*', $key);
    }
}

// Usage
$analyzer = new MemoryAnalyzer();
$distribution = $analyzer->analyzeByPattern();

// Output:
// [
//     'cache:api:*' => ['count' => 5000, 'bytes' => 50000000],
//     'session:*' => ['count' => 1000, 'bytes' => 10000000],
//     'user:*:data' => ['count' => 500, 'bytes' => 5000000],
// ]
```

### By Data Type

```php
class TypeAnalyzer
{
    public function analyzeByType(): array
    {
        $types = [
            'string' => ['count' => 0, 'bytes' => 0],
            'hash' => ['count' => 0, 'bytes' => 0],
            'list' => ['count' => 0, 'bytes' => 0],
            'set' => ['count' => 0, 'bytes' => 0],
            'zset' => ['count' => 0, 'bytes' => 0],
            'stream' => ['count' => 0, 'bytes' => 0],
        ];

        $cursor = 0;

        do {
            [$cursor, $keys] = Redis::scan($cursor, 'COUNT', 1000);

            foreach ($keys as $key) {
                $type = Redis::type($key);
                $bytes = Redis::memory('USAGE', $key) ?? 0;

                if (isset($types[$type])) {
                    $types[$type]['count']++;
                    $types[$type]['bytes'] += $bytes;
                }
            }
        } while ($cursor != 0);

        return $types;
    }
}
```

---

## Finding Large Keys

### Scan-Based Approach

```php
class LargeKeyScanner
{
    public function findTopKeys(int $limit = 20, int $minBytes = 1000): array
    {
        $largeKeys = new \SplPriorityQueue();
        $largeKeys->setExtractFlags(\SplPriorityQueue::EXTR_BOTH);

        $cursor = 0;

        do {
            [$cursor, $keys] = Redis::scan($cursor, 'COUNT', 100);

            foreach ($keys as $key) {
                $bytes = Redis::memory('USAGE', $key);

                if ($bytes >= $minBytes) {
                    $largeKeys->insert([
                        'key' => $key,
                        'bytes' => $bytes,
                        'type' => Redis::type($key),
                    ], $bytes);
                }
            }
        } while ($cursor != 0);

        $result = [];
        $count = 0;

        while (!$largeKeys->isEmpty() && $count < $limit) {
            $item = $largeKeys->extract();
            $result[] = $item['data'];
            $count++;
        }

        return $result;
    }
}
```

### redis-cli --bigkeys

```bash
redis-cli --bigkeys

# Output:
# Biggest string found: 'large:json' has 1234567 bytes
# Biggest hash found: 'user:data' has 5000 fields
# Biggest list found: 'queue:pending' has 10000 items
```

### redis-cli --memkeys

```bash
redis-cli --memkeys

# Samples memory usage of keys
# More accurate than --bigkeys for actual memory
```

---

## Memory Debugging

### Check Specific Key

```php
class KeyDebugger
{
    public function debug(string $key): array
    {
        if (!Redis::exists($key)) {
            return ['error' => 'Key does not exist'];
        }

        $type = Redis::type($key);
        $encoding = Redis::object('ENCODING', $key);
        $bytes = Redis::memory('USAGE', $key);
        $ttl = Redis::ttl($key);

        $info = [
            'key' => $key,
            'type' => $type,
            'encoding' => $encoding,
            'bytes' => $bytes,
            'bytes_human' => $this->formatBytes($bytes),
            'ttl' => $ttl === -1 ? 'no expiry' : "{$ttl}s",
        ];

        // Add type-specific info
        switch ($type) {
            case 'string':
                $info['length'] = Redis::strlen($key);
                break;
            case 'hash':
                $info['fields'] = Redis::hlen($key);
                break;
            case 'list':
                $info['length'] = Redis::llen($key);
                break;
            case 'set':
                $info['cardinality'] = Redis::scard($key);
                break;
            case 'zset':
                $info['cardinality'] = Redis::zcard($key);
                break;
        }

        return $info;
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

### Encoding Analysis

```php
class EncodingAnalyzer
{
    public function getEncodingStats(): array
    {
        $encodings = [];
        $cursor = 0;

        do {
            [$cursor, $keys] = Redis::scan($cursor, 'COUNT', 1000);

            foreach ($keys as $key) {
                $type = Redis::type($key);
                $encoding = Redis::object('ENCODING', $key);
                $encodingKey = "{$type}:{$encoding}";

                if (!isset($encodings[$encodingKey])) {
                    $encodings[$encodingKey] = ['count' => 0, 'bytes' => 0];
                }

                $encodings[$encodingKey]['count']++;
                $encodings[$encodingKey]['bytes'] += Redis::memory('USAGE', $key) ?? 0;
            }
        } while ($cursor != 0);

        return $encodings;
    }
}

// Example output:
// [
//     'hash:listpack' => ['count' => 5000, 'bytes' => 1000000],    // Good
//     'hash:hashtable' => ['count' => 100, 'bytes' => 5000000],   // Consider optimization
//     'string:embstr' => ['count' => 10000, 'bytes' => 500000],   // Good
//     'string:raw' => ['count' => 500, 'bytes' => 2000000],       // Large strings
// ]
```

---

## Memory Leak Detection

### Track Growth Over Time

```php
class MemoryTracker
{
    private string $trackingKey = 'memory:tracking';

    public function recordSnapshot(): void
    {
        $info = Redis::info('memory');

        $snapshot = [
            'timestamp' => time(),
            'used_memory' => $info['used_memory'],
            'keys' => Redis::dbsize(),
        ];

        Redis::lpush($this->trackingKey, json_encode($snapshot));
        Redis::ltrim($this->trackingKey, 0, 1440); // Keep 24 hours (1/min)
    }

    public function detectAnomalies(): array
    {
        $snapshots = Redis::lrange($this->trackingKey, 0, 60); // Last hour
        $anomalies = [];

        if (count($snapshots) < 2) {
            return [];
        }

        $latest = json_decode($snapshots[0], true);
        $oldest = json_decode(end($snapshots), true);

        // Check for unusual growth
        $memoryGrowth = $latest['used_memory'] - $oldest['used_memory'];
        $keyGrowth = $latest['keys'] - $oldest['keys'];

        if ($memoryGrowth > 100 * 1024 * 1024) { // > 100MB growth
            $anomalies[] = [
                'type' => 'rapid_memory_growth',
                'growth_mb' => round($memoryGrowth / 1048576, 2),
            ];
        }

        if ($keyGrowth > 10000) { // > 10K new keys
            $anomalies[] = [
                'type' => 'rapid_key_growth',
                'growth' => $keyGrowth,
            ];
        }

        return $anomalies;
    }
}
```

---

## Comprehensive Memory Report

```php
class MemoryReport
{
    public function generate(): array
    {
        $info = Redis::info('memory');
        $stats = Redis::memory('STATS');
        $dbsize = Redis::dbsize();

        return [
            'summary' => [
                'used' => $info['used_memory_human'],
                'peak' => $info['used_memory_peak_human'],
                'rss' => $info['used_memory_rss_human'],
                'keys' => $dbsize,
                'avg_per_key' => $dbsize > 0
                    ? round($info['used_memory'] / $dbsize, 2) . ' bytes'
                    : 'N/A',
            ],
            'limits' => [
                'maxmemory' => $info['maxmemory']
                    ? $this->formatBytes($info['maxmemory'])
                    : 'unlimited',
                'usage_percent' => $info['maxmemory'] > 0
                    ? round(($info['used_memory'] / $info['maxmemory']) * 100, 2)
                    : 0,
                'policy' => $info['maxmemory_policy'],
            ],
            'fragmentation' => [
                'ratio' => $info['mem_fragmentation_ratio'],
                'bytes' => $this->formatBytes($info['mem_fragmentation_bytes']),
                'status' => $this->assessFragmentation($info['mem_fragmentation_ratio']),
            ],
            'breakdown' => [
                'dataset' => $this->formatBytes($stats['dataset.bytes']),
                'overhead' => $this->formatBytes($stats['overhead.total']),
                'clients' => $this->formatBytes($info['mem_clients_normal']),
            ],
            'allocator' => $info['mem_allocator'],
            'doctor' => Redis::memory('DOCTOR'),
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

    private function assessFragmentation(float $ratio): string
    {
        if ($ratio < 1.0) return 'low (possible underreporting)';
        if ($ratio < 1.5) return 'healthy';
        if ($ratio < 2.0) return 'moderate - consider monitoring';
        return 'high - consider restart or defrag';
    }
}
```

---

## Key Takeaways

1. **MEMORY USAGE** - Check individual key memory
2. **MEMORY STATS** - Comprehensive breakdown
3. **MEMORY DOCTOR** - Quick health check
4. **redis-cli --bigkeys** - Find largest keys by count
5. **redis-cli --memkeys** - Find largest keys by memory
6. **Scan patterns** - Identify memory by key namespace
7. **Check encodings** - hashtable uses more than listpack
8. **Track over time** - Detect leaks and anomalies
