# Redis 7.x Commands Reference

This directory contains comprehensive documentation for all Redis commands organized by category.

---

## Command Categories

| Category | File | Description | Commands |
|----------|------|-------------|----------|
| **Strings** | [strings.md](./strings.md) | String value operations | GET, SET, INCR, APPEND, etc. |
| **Lists** | [lists.md](./lists.md) | Ordered collections | LPUSH, RPUSH, LRANGE, BLPOP, etc. |
| **Sets** | [sets.md](./sets.md) | Unordered unique collections | SADD, SMEMBERS, SINTER, etc. |
| **Sorted Sets** | [sorted-sets.md](./sorted-sets.md) | Score-ordered collections | ZADD, ZRANGE, ZRANGEBYSCORE, etc. |
| **Hashes** | [hashes.md](./hashes.md) | Field-value maps | HSET, HGET, HINCRBY, etc. |
| **Streams** | [streams.md](./streams.md) | Append-only log structures | XADD, XREAD, XGROUP, etc. |
| **Geospatial** | [geospatial.md](./geospatial.md) | Location-based operations | GEOADD, GEOSEARCH, GEODIST, etc. |
| **HyperLogLog** | [hyperloglog.md](./hyperloglog.md) | Cardinality estimation | PFADD, PFCOUNT, PFMERGE |
| **Bitmaps** | [bitmaps.md](./bitmaps.md) | Bit-level operations | SETBIT, GETBIT, BITCOUNT, etc. |
| **Keys** | [keys.md](./keys.md) | Key management | KEYS, SCAN, EXISTS, EXPIRE, etc. |
| **Transactions** | [transactions.md](./transactions.md) | Atomic execution | MULTI, EXEC, WATCH, DISCARD |
| **Scripting** | [scripting.md](./scripting.md) | Lua scripts & Functions | EVAL, EVALSHA, FUNCTION, etc. |
| **Pub/Sub** | [pubsub.md](./pubsub.md) | Message broadcasting | PUBLISH, SUBSCRIBE, PSUBSCRIBE, etc. |
| **Server** | [server.md](./server.md) | Administration | INFO, CONFIG, MEMORY, etc. |
| **Cluster** | [cluster.md](./cluster.md) | Cluster management | CLUSTER NODES, CLUSTER INFO, etc. |
| **ACL** | [acl.md](./acl.md) | Access control | ACL SETUSER, ACL LIST, etc. |

---

## Quick Reference by Use Case

### Caching (Most Common in BudTags)

```php
// Laravel Cache facade (uses strings internally)
Cache::put($key, $value, $ttl);     // SET with EX
Cache::get($key);                    // GET
Cache::forever($key, $value);        // SET (no expiry)
Cache::remember($key, $ttl, $fn);    // GET or SET
Cache::forget($key);                 // DEL
```

### Counters & Atomic Operations

```php
// Via Redis facade for atomic operations
Redis::incr($key);                   // INCR
Redis::incrby($key, $amount);        // INCRBY
Redis::decr($key);                   // DECR
```

### Set Operations (Tracking Unique Items)

```php
Redis::sadd($key, ...$members);      // SADD
Redis::smembers($key);               // SMEMBERS
Redis::sismember($key, $member);     // SISMEMBER
Redis::srem($key, $member);          // SREM
```

### Key Management

```php
Redis::command('select', [1]);       // SELECT (switch DB)
Redis::command('keys', ['pattern*']); // KEYS (careful in production!)
Redis::del($key);                    // DEL
Redis::expire($key, $seconds);       // EXPIRE
```

---

## Time Complexity Reference

### O(1) - Constant Time
Most single-key operations: GET, SET, INCR, HGET, HSET, SADD, ZADD

### O(N) - Linear
- KEYS pattern - Scans entire keyspace (avoid in production)
- SMEMBERS - Returns all set members
- HGETALL - Returns all hash fields
- LRANGE 0 -1 - Returns entire list

### O(log N) - Logarithmic
Sorted set operations: ZADD, ZRANGE, ZRANK, ZRANGEBYSCORE

### O(M) - Output Size
Range queries where M is the number of returned elements

---

## Redis 7.x New Features

### Redis Functions (7.0+)
- `FUNCTION LOAD` - Load function libraries
- `FCALL` - Execute functions
- Replaces ad-hoc Lua scripts with persistent functions

### Hash Field Expiration (7.4+)
- `HEXPIRE` - Set TTL on individual hash fields
- `HTTL` - Get remaining TTL of hash field
- `HPERSIST` - Remove expiration from hash field

### Other 7.x Additions
- `GETEX` - GET with expiration options
- `LMPOP/ZMPOP` - Pop from multiple lists/sorted sets
- `SINTERCARD` - Intersection cardinality without materializing
- Client-side caching improvements (RESP3)

---

## BudTags-Specific Notes

### Database Selection
| DB | Purpose | Use |
|----|---------|-----|
| 0 | Default (sessions) | Laravel default |
| 1 | **Cache** | `Cache::` facade |
| 2 | Queues (Horizon) | Job processing |

### Common Patterns
1. **API Response Caching**: `Cache::remember()` with day-partitioned keys
2. **Atomic Counters**: `Redis::incr()` for progress tracking
3. **Set Tracking**: `Redis::sadd()/smembers()` for batch operations
4. **Pattern Deletion**: `Redis::command('keys', [...])` + batch delete

---

## External References

- [Official Redis Commands](https://redis.io/commands/)
- [Redis 7.0 Release Notes](https://redis.io/docs/latest/operate/oss_and_stack/release-notes/)
- [Laravel Redis Documentation](https://laravel.com/docs/redis)
