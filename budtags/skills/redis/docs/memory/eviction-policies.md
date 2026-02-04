# Redis Eviction Policies

When Redis memory usage reaches `maxmemory`, the eviction policy determines which keys to remove.

---

## Configuration

```
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru

# Runtime
CONFIG SET maxmemory 2gb
CONFIG SET maxmemory-policy allkeys-lru
```

---

## Available Policies

### noeviction (Default)

```
maxmemory-policy noeviction
```

| Behavior | Returns error on writes when memory full |
|----------|------------------------------------------|
| Reads | Always allowed |
| Writes | Error when at maxmemory |
| Use case | When data loss is unacceptable |

**Error returned:** `OOM command not allowed when used memory > 'maxmemory'`

---

### allkeys-lru

```
maxmemory-policy allkeys-lru
```

| Behavior | Evicts least recently used keys from ALL keys |
|----------|----------------------------------------------|
| Scope | All keys |
| Algorithm | Approximate LRU |
| Use case | **General-purpose caching (recommended)** |

**Best for:** When you can't predict which keys will be accessed.

---

### allkeys-lfu

```
maxmemory-policy allkeys-lfu
```

| Behavior | Evicts least frequently used keys from ALL keys |
|----------|------------------------------------------------|
| Scope | All keys |
| Algorithm | Approximate LFU |
| Use case | When frequency matters more than recency |

**Best for:** Data with varying popularity (some keys always hot).

---

### allkeys-random

```
maxmemory-policy allkeys-random
```

| Behavior | Evicts random keys |
|----------|-------------------|
| Scope | All keys |
| Use case | Uniform access pattern |

**Best for:** When all keys are accessed with similar frequency.

---

### volatile-lru

```
maxmemory-policy volatile-lru
```

| Behavior | Evicts LRU keys with TTL set |
|----------|------------------------------|
| Scope | Only keys with `expire` |
| Use case | Mix of persistent and cache data |

**Note:** If no keys have TTL, behaves like noeviction.

---

### volatile-lfu

```
maxmemory-policy volatile-lfu
```

| Behavior | Evicts LFU keys with TTL set |
|----------|------------------------------|
| Scope | Only keys with `expire` |
| Use case | TTL keys with varying popularity |

---

### volatile-random

```
maxmemory-policy volatile-random
```

| Behavior | Evicts random keys with TTL set |
|----------|--------------------------------|
| Scope | Only keys with `expire` |
| Use case | When TTL selection is arbitrary |

---

### volatile-ttl

```
maxmemory-policy volatile-ttl
```

| Behavior | Evicts keys with shortest TTL |
|----------|------------------------------|
| Scope | Only keys with `expire` |
| Use case | When TTL reflects importance |

**Best for:** When you've assigned TTLs based on data importance.

---

## Policy Selection Guide

| Scenario | Recommended Policy |
|----------|-------------------|
| **Pure cache** | `allkeys-lru` |
| **Cache with hot spots** | `allkeys-lfu` |
| **Mix of cache and persistent** | `volatile-lru` |
| **TTL = importance** | `volatile-ttl` |
| **Uniform access** | `allkeys-random` |
| **No data loss acceptable** | `noeviction` |

### BudTags Recommendation

```
maxmemory-policy allkeys-lru
```

**Rationale:**
- Primary use is caching (API responses)
- Can regenerate any evicted data
- Simple and effective for most cases

---

## LRU Algorithm Details

Redis uses **approximated LRU** to save memory:

1. Samples random keys (configurable count)
2. Evicts oldest among samples
3. Repeats until memory freed

### Tuning LRU Sampling

```
# More samples = more accurate, higher CPU
maxmemory-samples 5    # Default
maxmemory-samples 10   # More accurate
```

**Trade-off:** Higher samples = better eviction choices, more CPU.

---

## LFU Algorithm Details

LFU tracks access frequency with a logarithmic counter:

1. Counter increments based on access
2. Counter decays over time
3. Lowest frequency gets evicted

### Tuning LFU

```
# Counter saturation (higher = more accesses to saturate)
lfu-log-factor 10

# Decay time in minutes (0 = never decay)
lfu-decay-time 1
```

**lfu-log-factor:**
- Higher values require more accesses to reach max counter
- Default 10: ~1M requests to saturate

**lfu-decay-time:**
- Minutes before counter decays
- Default 1: Counter halves every minute

---

## Monitoring Evictions

### Check Evicted Keys

```php
$info = Redis::info('stats');
$evicted = $info['evicted_keys'];

if ($evicted > 0) {
    // Keys have been evicted - consider increasing maxmemory
    Log::warning("Redis evicted {$evicted} keys");
}
```

### Check Current Policy

```php
$config = Redis::config('GET', 'maxmemory-policy');
// ['maxmemory-policy' => 'allkeys-lru']
```

### Monitor Memory Pressure

```php
$info = Redis::info('memory');
$used = $info['used_memory'];
$max = $info['maxmemory'];

if ($max > 0) {
    $percent = ($used / $max) * 100;
    if ($percent > 80) {
        // Warning: approaching memory limit
    }
}
```

---

## Common Mistakes

### 1. Using noeviction for Cache

```php
// ❌ Bad: Errors when memory full
maxmemory-policy noeviction

// ✅ Good: Automatically manages memory
maxmemory-policy allkeys-lru
```

### 2. volatile-* Without TTLs

```php
// ❌ Bad: No keys have TTL, nothing to evict
maxmemory-policy volatile-lru
Cache::forever('key', $value);  // No TTL

// ✅ Good: Set TTLs on cache keys
Cache::put('key', $value, 3600);
```

### 3. Not Monitoring Evictions

```php
// ✅ Good: Regular monitoring
Schedule::call(function () {
    $evicted = Redis::info('stats')['evicted_keys'];
    if ($evicted > $lastChecked) {
        // Alert or log
    }
})->everyFiveMinutes();
```

---

## Key Takeaways

1. **allkeys-lru** is best for most caching scenarios
2. **volatile-*** only affects keys with TTL
3. **noeviction** causes errors when full
4. **Monitor evicted_keys** to detect memory pressure
5. **Tune maxmemory-samples** for LRU accuracy vs CPU
6. **LFU** is better when some data is always hot
