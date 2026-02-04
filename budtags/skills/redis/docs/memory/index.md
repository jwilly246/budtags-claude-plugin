# Redis Memory Management

Comprehensive guide to Redis memory optimization, eviction policies, and analysis tools.

---

## Overview

| Topic | File | Description |
|-------|------|-------------|
| Eviction Policies | [eviction-policies.md](./eviction-policies.md) | maxmemory-policy options |
| Memory Optimization | [memory-optimization.md](./memory-optimization.md) | Reducing memory footprint |
| Memory Analysis | [memory-analysis.md](./memory-analysis.md) | MEMORY commands, debugging |
| Object Encoding | [object-encoding.md](./object-encoding.md) | Internal encodings |

---

## Key Metrics

### INFO Memory Output

```php
$info = Redis::info('memory');
```

| Metric | Description |
|--------|-------------|
| `used_memory` | Total bytes allocated |
| `used_memory_human` | Human-readable used memory |
| `used_memory_rss` | OS-reported memory (includes fragmentation) |
| `used_memory_peak` | Maximum used memory |
| `used_memory_peak_human` | Human-readable peak |
| `mem_fragmentation_ratio` | RSS / used_memory |
| `maxmemory` | Configured limit (0 = unlimited) |
| `maxmemory_policy` | Eviction policy name |
| `evicted_keys` | Keys evicted due to maxmemory |

### Healthy Indicators

| Metric | Healthy Range |
|--------|---------------|
| Fragmentation ratio | 1.0 - 1.5 |
| Memory usage | < 80% of maxmemory |
| Evicted keys | 0 (ideally) |

---

## Quick Reference

### Set Memory Limit

```
# redis.conf
maxmemory 2gb

# Runtime
CONFIG SET maxmemory 2gb
```

### Set Eviction Policy

```
# redis.conf
maxmemory-policy allkeys-lru

# Runtime
CONFIG SET maxmemory-policy allkeys-lru
```

### Check Key Memory

```php
$bytes = Redis::memory('USAGE', 'mykey');
```

### Get Memory Stats

```php
$stats = Redis::memory('STATS');
```

### Memory Doctor

```php
$report = Redis::memory('DOCTOR');
```

---

## Memory Budget Guidelines

### Per-Key Overhead

Every key has baseline overhead:

| Component | Bytes |
|-----------|-------|
| Redis object header | 16 |
| Dict entry | 24 |
| Key SDS | 3-9 + key length |
| **Minimum per key** | ~50 |

### Sizing Examples

| Scenario | Keys | Value Size | Memory |
|----------|------|------------|--------|
| Session cache | 100K | 1 KB | ~150 MB |
| API cache | 1M | 2 KB | ~2.5 GB |
| Counters | 1M | 8 bytes | ~60 MB |
| Large objects | 10K | 100 KB | ~1 GB |

---

## BudTags Memory Recommendations

### Current Setup
```
DB 0: Default (sessions)
DB 1: Cache
DB 2: Queues (Horizon)
```

### Recommended Configuration

```
# Set appropriate limit
maxmemory 1gb

# Use LRU for cache database
# (Applied globally, but cache is largest consumer)
maxmemory-policy allkeys-lru

# Monitor evictions
# If evicted_keys > 0, consider increasing maxmemory
```

### Monitoring Script

```php
class RedisMemoryMonitor
{
    public function getStatus(): array
    {
        $info = Redis::info('memory');

        $used = $info['used_memory'];
        $max = $info['maxmemory'] ?: 0;
        $usage = $max > 0 ? ($used / $max) * 100 : 0;

        return [
            'used' => $info['used_memory_human'],
            'peak' => $info['used_memory_peak_human'],
            'max' => $max > 0 ? $this->formatBytes($max) : 'unlimited',
            'usage_percent' => round($usage, 2),
            'fragmentation' => $info['mem_fragmentation_ratio'],
            'evicted_keys' => $info['evicted_keys'],
            'status' => $this->getHealthStatus($usage, $info),
        ];
    }

    private function getHealthStatus(float $usage, array $info): string
    {
        if ($info['evicted_keys'] > 0) {
            return 'warning: keys being evicted';
        }
        if ($usage > 90) {
            return 'critical: high memory usage';
        }
        if ($usage > 80) {
            return 'warning: approaching limit';
        }
        if ($info['mem_fragmentation_ratio'] > 1.5) {
            return 'warning: high fragmentation';
        }
        return 'healthy';
    }
}
```

---

## Common Issues

### High Memory Usage

**Symptoms:** Used memory approaching maxmemory

**Solutions:**
1. Increase maxmemory limit
2. Enable eviction policy
3. Set shorter TTLs
4. Optimize data structures
5. Clean up unused keys

### High Fragmentation

**Symptoms:** `mem_fragmentation_ratio` > 1.5

**Causes:**
- Many deletions without new allocations
- Memory allocator behavior
- Redis process restart

**Solutions:**
1. Restart Redis (reclaims fragmented memory)
2. Use MEMORY PURGE (for jemalloc)
3. Accept some fragmentation (normal < 1.5)

### Keys Being Evicted

**Symptoms:** `evicted_keys` > 0

**Solutions:**
1. Increase maxmemory
2. Review TTL strategy
3. Check for memory leaks (unbounded growth)
4. Use MEMORY USAGE to find large keys

---

## Best Practices

1. **Always set maxmemory** - Prevent OOM killer
2. **Choose appropriate eviction** - allkeys-lru for caches
3. **Monitor regularly** - Track used_memory and evictions
4. **Set TTLs** - On temporary data
5. **Use efficient encodings** - Keep under encoding thresholds
6. **Avoid big keys** - Split large collections
7. **Profile periodically** - MEMORY USAGE on suspicious keys
