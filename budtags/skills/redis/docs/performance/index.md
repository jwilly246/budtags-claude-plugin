# Redis Performance Optimization

Guide to maximizing Redis performance through pipelining, connection management, and best practices.

---

## Overview

| Topic | File | Description |
|-------|------|-------------|
| Pipelining | [pipelining.md](./pipelining.md) | Batching commands |
| Connection Pooling | [connection-pooling.md](./connection-pooling.md) | Managing connections |
| Benchmarking | [benchmarking.md](./benchmarking.md) | Measuring performance |
| Latency | [latency.md](./latency.md) | Diagnosing delays |
| Big Keys | [big-keys.md](./big-keys.md) | Avoiding large key issues |

---

## Quick Wins

### 1. Use Pipelining

```php
// ❌ Bad: 100 round trips
foreach ($keys as $key) {
    $values[] = Redis::get($key);
}

// ✅ Good: 1 round trip
$values = Redis::pipeline(function ($pipe) use ($keys) {
    foreach ($keys as $key) {
        $pipe->get($key);
    }
});
```

**Impact:** 10-100x faster for multiple commands.

### 2. Use MGET/MSET

```php
// ❌ Bad: Multiple commands
$a = Redis::get('key1');
$b = Redis::get('key2');

// ✅ Good: Single command
[$a, $b] = Redis::mget(['key1', 'key2']);
```

### 3. Avoid KEYS Command

```php
// ❌ Bad: Blocks Redis, O(N)
$keys = Redis::keys('pattern*');

// ✅ Good: Non-blocking iteration
$cursor = 0;
do {
    [$cursor, $keys] = Redis::scan($cursor, 'MATCH', 'pattern*', 'COUNT', 100);
    // Process $keys
} while ($cursor != 0);
```

### 4. Use Appropriate Data Structures

```php
// ❌ Bad: Many string keys
Redis::set("user:{$id}:name", $name);
Redis::set("user:{$id}:email", $email);

// ✅ Good: Single hash (less overhead)
Redis::hmset("user:{$id}", compact('name', 'email'));
```

---

## Performance Metrics

### Key Indicators

```php
$info = Redis::info();

$metrics = [
    'ops_per_sec' => $info['instantaneous_ops_per_sec'],
    'connected_clients' => $info['connected_clients'],
    'blocked_clients' => $info['blocked_clients'],
    'used_memory' => $info['used_memory_human'],
    'hit_rate' => $this->calculateHitRate($info),
    'latency_us' => $info['instantaneous_input_kbps'], // Approximate
];
```

### Hit Rate Calculation

```php
function calculateHitRate(array $info): float
{
    $hits = $info['keyspace_hits'];
    $misses = $info['keyspace_misses'];
    $total = $hits + $misses;

    return $total > 0 ? ($hits / $total) * 100 : 0;
}
```

**Healthy hit rate:** > 90% for cache use cases.

---

## Command Complexity Reference

### O(1) - Constant Time (Fast)

- GET, SET, INCR, DECR
- HGET, HSET
- SADD, SISMEMBER
- LPUSH, RPUSH, LPOP, RPOP

### O(log N) - Logarithmic (Fast)

- ZADD, ZREM, ZRANK
- ZSCORE

### O(N) - Linear (Careful)

- KEYS, SMEMBERS, HGETALL
- LRANGE (full list)
- DEL (large collections)

### O(N*M) - Expensive (Avoid)

- SINTER, SUNION with large sets

---

## Slow Command Detection

### Enable Slow Log

```
slowlog-log-slower-than 10000   # 10ms
slowlog-max-len 128             # Keep 128 entries
```

### Query Slow Log

```php
// Get last 10 slow commands
$slow = Redis::slowlog('GET', 10);

foreach ($slow as $entry) {
    $id = $entry[0];
    $timestamp = $entry[1];
    $duration_us = $entry[2];
    $command = $entry[3];

    Log::warning("Slow Redis command", [
        'duration_ms' => $duration_us / 1000,
        'command' => implode(' ', $command),
    ]);
}
```

---

## Connection Best Practices

### Laravel Configuration

```php
// config/database.php
'redis' => [
    'client' => env('REDIS_CLIENT', 'phpredis'),  // phpredis is faster

    'default' => [
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'port' => env('REDIS_PORT', 6379),
        'database' => env('REDIS_DB', 0),
        'read_timeout' => 60,
        'persistent' => true,  // Reuse connections
    ],
],
```

### Connection Limits

```
# redis.conf
maxclients 10000
```

Monitor with:
```php
$clients = Redis::info('clients')['connected_clients'];
```

---

## BudTags Performance Checklist

### API Caching

- [ ] Use `Cache::remember()` for automatic cache-or-fetch
- [ ] Set appropriate TTLs
- [ ] Use day-partitioned keys for time-based data
- [ ] Consider compression for large JSON responses

### Bulk Operations

- [ ] Use pipelining for multiple operations
- [ ] Chunk large datasets
- [ ] Use SCAN instead of KEYS
- [ ] Set progress counters with Redis::incr()

### Background Jobs

- [ ] Use atomic counters for progress
- [ ] Set TTL on temporary tracking keys
- [ ] Clean up after job completion

---

## Anti-Patterns to Avoid

### 1. Hot Keys

```php
// ❌ Bad: Single key hammered by all requests
Redis::incr('global_counter');

// ✅ Better: Distribute load
$shard = $userId % 10;
Redis::incr("counter:shard:{$shard}");
// Sum shards when needed
```

### 2. Unbounded Growth

```php
// ❌ Bad: List grows forever
Redis::lpush('logs', $entry);

// ✅ Good: Capped list
Redis::lpush('logs', $entry);
Redis::ltrim('logs', 0, 9999);  // Keep last 10000
```

### 3. Large Values

```php
// ❌ Bad: 10MB value
Redis::set('huge', $tenMegabytes);

// ✅ Better: Split or compress
Redis::set('huge', gzcompress($data));
// Or split into chunks
```

### 4. Blocking in Web Requests

```php
// ❌ Bad: Blocks web request
[$key, $value] = Redis::blpop('queue', 30);

// ✅ Good: Use in queue workers only, or use non-blocking
$value = Redis::lpop('queue');
```

---

## Benchmarking Baseline

### Expected Performance (Single Node)

| Operation | Ops/sec |
|-----------|---------|
| GET/SET (small) | 100,000+ |
| INCR | 100,000+ |
| LPUSH/LPOP | 100,000+ |
| HSET/HGET | 80,000+ |
| ZADD | 50,000+ |

### Testing Your Setup

```bash
redis-benchmark -h localhost -p 6379 -c 50 -n 100000
```

---

## Key Takeaways

1. **Pipeline multiple commands** - Reduces round trips
2. **Use multi-key commands** - MGET, MSET, HMGET
3. **Avoid KEYS** - Use SCAN
4. **Monitor slow log** - Find problematic commands
5. **Check hit rate** - Should be > 90% for caches
6. **Limit key sizes** - Split large values
7. **Use phpredis** - Faster than predis
8. **Enable persistent connections** - Reduces overhead
