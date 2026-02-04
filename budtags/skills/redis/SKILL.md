---
name: redis
description: Comprehensive Redis 7.x reference with BudTags-specific patterns. Covers all commands, data types, persistence, memory optimization, performance tuning, high availability, security, and Laravel integration.
version: 2.0.0
category: infrastructure
agent: redis-specialist
auto_activate:
  patterns:
    - "**/Services/**Cache*.php"
    - "**/Jobs/*.php"
  keywords:
    - "Cache::get"
    - "Cache::put"
    - "Cache::forever"
    - "Cache::remember"
    - "Cache::forget"
    - "Redis::sadd"
    - "Redis::smembers"
    - "Redis::incr"
    - "Redis::command"
    - "cache key"
    - "redis"
    - "caching"
    - "rate limit"
    - "distributed lock"
    - "atomic counter"
    - "bulk cache"
---

# Redis Skill

You are now equipped with comprehensive knowledge of Redis caching patterns and best practices in the BudTags codebase. This skill uses **progressive disclosure** to load only the patterns relevant to your current task.

---

## Your Capabilities

When this skill is active, you can:

### BudTags-Specific Patterns
1. **Design Cache Keys**: Create properly scoped, consistent cache keys
2. **Choose TTL Strategy**: Select appropriate TTL (or forever) for different data types
3. **Implement Cache Patterns**: Use Cache facade and Redis facade correctly
4. **Handle Bulk Operations**: Chunk large datasets, rebuild caches efficiently
5. **Create Atomic Counters**: Track progress in background jobs
6. **Manage Cache Invalidation**: Clear pattern-based keys, handle staleness
7. **Implement Rate Limiting**: Use sliding window patterns for API throttling

### Redis Expertise
8. **Command Mastery**: Reference any Redis command with correct syntax and options
9. **Data Type Selection**: Choose optimal data types for any use case
10. **Performance Tuning**: Diagnose slow queries, optimize pipelines, reduce latency
11. **Memory Optimization**: Configure eviction, analyze memory usage, reduce footprint
12. **Persistence Setup**: Configure RDB snapshots, AOF logging, or hybrid approaches
13. **High Availability**: Design replication, sentinel, or cluster architectures
14. **Security Hardening**: Implement ACLs, network security, command restrictions
15. **Advanced Patterns**: Lua scripting, transactions, pub/sub, client-side caching

---

## Available Resources

This skill provides **comprehensive Redis 7.x documentation** organized into 10 categories with 58 reference files:

### BudTags-Specific Patterns (6 files)
- `patterns/cache-facade.md` - Laravel Cache facade operations (get, put, remember, forever)
- `patterns/redis-facade.md` - Low-level Redis facade operations (sadd, smembers, incr, del)
- `patterns/key-naming.md` - BudTags key naming conventions (CRITICAL for consistency)
- `patterns/ttl-strategy.md` - When to use forever vs TTL, decision guide
- `patterns/distributed-locks.md` - Cache::lock patterns for concurrent operations
- `patterns/rate-limiting.md` - Sliding window rate limiting from MetrcApi

### BudTags Scenario Guides (4 files)
- `scenarios/caching-api-responses.md` - fetch_from_cache_or_api pattern (MOST COMMON)
- `scenarios/bulk-cache-operations.md` - Package chunking, cache rebuild strategies
- `scenarios/atomic-counters.md` - Progress tracking with Redis::incr
- `scenarios/pattern-based-deletion.md` - DevController patterns for cache management

### Commands Reference (16 files)
- `docs/commands/index.md` - Command categories overview and quick reference
- `docs/commands/strings.md` - GET, SET, INCR, APPEND, GETRANGE, etc.
- `docs/commands/hashes.md` - HGET, HSET, HMGET, HINCRBY, HSCAN, etc.
- `docs/commands/lists.md` - LPUSH, RPUSH, LPOP, LRANGE, LINDEX, etc.
- `docs/commands/sets.md` - SADD, SMEMBERS, SINTER, SUNION, SDIFF, etc.
- `docs/commands/sorted-sets.md` - ZADD, ZRANGE, ZRANK, ZSCORE, ZINCRBY, etc.
- `docs/commands/keys.md` - KEYS, SCAN, EXISTS, DEL, EXPIRE, TTL, etc.
- `docs/commands/server.md` - INFO, CONFIG, DBSIZE, FLUSHDB, DEBUG, etc.
- `docs/commands/transactions.md` - MULTI, EXEC, DISCARD, WATCH patterns
- `docs/commands/scripting.md` - EVAL, EVALSHA, Lua scripting patterns
- `docs/commands/pub-sub.md` - PUBLISH, SUBSCRIBE, PSUBSCRIBE patterns
- `docs/commands/streams.md` - XADD, XREAD, XREADGROUP, consumer groups
- `docs/commands/geo.md` - GEOADD, GEODIST, GEORADIUS, geospatial queries
- `docs/commands/hyperloglog.md` - PFADD, PFCOUNT, cardinality estimation
- `docs/commands/bitmaps.md` - SETBIT, GETBIT, BITCOUNT, BITOP patterns
- `docs/commands/cluster.md` - CLUSTER commands, slot management

### Data Types Deep Dive (10 files)
- `docs/data-types/index.md` - Type selection guide and comparisons
- `docs/data-types/strings.md` - Binary-safe strings, counters, serialization
- `docs/data-types/hashes.md` - Field-value maps, object storage
- `docs/data-types/lists.md` - Ordered collections, queues, stacks
- `docs/data-types/sets.md` - Unique collections, intersections, unions
- `docs/data-types/sorted-sets.md` - Scored sets, leaderboards, time series
- `docs/data-types/streams.md` - Append-only logs, consumer groups
- `docs/data-types/geospatial.md` - Location data, proximity queries
- `docs/data-types/bitmaps.md` - Bit-level operations, feature flags
- `docs/data-types/hyperloglogs.md` - Probabilistic cardinality

### Persistence (4 files)
- `docs/persistence/index.md` - Persistence strategies overview
- `docs/persistence/rdb.md` - Point-in-time snapshots, BGSAVE
- `docs/persistence/aof.md` - Append-only file, fsync policies
- `docs/persistence/hybrid.md` - RDB+AOF combination strategies

### Memory Optimization (5 files)
- `docs/memory/index.md` - Memory architecture and analysis
- `docs/memory/data-encoding.md` - Internal encodings, memory savings
- `docs/memory/eviction-policies.md` - LRU, LFU, volatile-*, allkeys-*
- `docs/memory/key-expiration.md` - TTL strategies, lazy vs active expiry
- `docs/memory/memory-doctor.md` - Diagnostics and optimization

### Performance Tuning (6 files)
- `docs/performance/index.md` - Performance fundamentals
- `docs/performance/pipelining.md` - Batch commands, reduce RTT
- `docs/performance/connection-pooling.md` - Pool management, sizing
- `docs/performance/slow-commands.md` - Identify and fix slow operations
- `docs/performance/benchmarking.md` - redis-benchmark, load testing
- `docs/performance/latency.md` - Latency diagnosis, optimization

### High Availability (4 files)
- `docs/high-availability/index.md` - HA architecture overview
- `docs/high-availability/replication.md` - Master-replica, REPLICAOF
- `docs/high-availability/sentinel.md` - Automatic failover, monitoring
- `docs/high-availability/cluster.md` - Sharding, hash slots, scaling

### Security (4 files)
- `docs/security/index.md` - Security overview and checklist
- `docs/security/authentication.md` - ACLs, users, passwords
- `docs/security/network.md` - Binding, firewalls, TLS
- `docs/security/commands.md` - Command restrictions, dangerous commands

### Advanced Features (6 files)
- `docs/advanced/index.md` - Advanced features overview
- `docs/advanced/lua-scripting.md` - EVAL, atomicity, script patterns
- `docs/advanced/transactions.md` - MULTI/EXEC, optimistic locking
- `docs/advanced/pub-sub.md` - Real-time messaging patterns
- `docs/advanced/client-caching.md` - Client-side caching, invalidation
- `docs/advanced/modules.md` - RedisJSON, RediSearch, RedisGraph

### Configuration (3 files)
- `docs/configuration/index.md` - Configuration file reference
- `docs/configuration/redis-conf.md` - redis.conf directives
- `docs/configuration/runtime-config.md` - CONFIG GET/SET, live tuning

### Laravel Integration (1 file)
- `docs/laravel-integration.md` - How Laravel wraps Redis (Cache vs Redis facades)

---

## Quick Reference

### Database Configuration (config/database.php)

| DB | Purpose | Connection | Default |
|----|---------|------------|---------|
| 0 | Default (sessions, etc.) | `default` | `REDIS_DB` |
| 1 | **Cache** | `cache` | `REDIS_CACHE_DB` |
| 2 | Queues (Horizon) | `queue` | `REDIS_QUEUE_DB` |

### Key Naming Conventions (CRITICAL)

| Pattern | Example | TTL | Use Case |
|---------|---------|-----|----------|
| `metrc:{entity}:{id}` | `metrc:package:ABC123` | forever | Single cached item |
| `metrc:day-of-{entity}:{license}:{date}` | `metrc:day-of-packages:AU-P-123:1/15/2025` | forever | Day-partitioned lists |
| `metrc:{entity}-available-tags:{license}` | `metrc:package-available-tags:AU-P-123` | 2 min | Fast-changing data |
| `metrc:{entity}:{license}` | `metrc:locations:AU-P-123` | 30 days | Stable reference data |
| `org:{org_id}:{feature}` | `org:abc-123:transfer_selections` | 30 days | Org-scoped user data |
| `{feature}:{id}` | `label_group_success:42` | 1 hour | Temporary counters |

### Cache Time Constants (MetrcApi.php)

```php
const DEFAULT_CACHE_TIME = null;        // Permanent (Cache::forever)
const INACTIVE_CACHE_TIME = 60*60*24*30; // 30 days (inactive/historical)
const PLANT_CACHE_TIME = null;          // Permanent for active plants
```

### Common TTL Values

| Value | Duration | Use Case |
|-------|----------|----------|
| `null` | Forever | Active packages, plants, core entity data |
| `120` | 2 min | Tags, strains, employees (fast-changing) |
| `600` | 10 min | Adjustments (immutable once fetched) |
| `3600` | 1 hour | Counters, temporary tracking |
| `43200` | 12 hours | Items, full package lists |
| `60*60*24*7` | 7 days | Transfer deliveries, transporter details |
| `60*60*24*30` | 30 days | Inactive packages, historical data |

---

## Important Reminders

### Organization Scoping in Keys

```php
// ✅ CORRECT - Include org_id for org-specific data
$key = "org:{$org_id}:transfer_selections";
Cache::put($key, $data, now()->addDays(30));

// ❌ WRONG - Unscoped key allows cross-tenant data access
$key = "transfer_selections";  // Security vulnerability!
```

### Cache vs Redis Facade

```php
// ✅ Use Cache:: for standard get/put/remember
Cache::forever("metrc:package:{$label}", $data);
Cache::remember($key, 3600, fn() => $this->fetchData());

// ✅ Use Redis:: for atomic operations and data structures
Redis::incr("label_group_success:{$id}");
Redis::sadd("metrc:package-labels:{$facility}", ...$labels);
Redis::smembers("metrc:package-labels:{$facility}");

// ✅ Use Redis::command for low-level operations
Redis::command('select', [1]);  // Switch to cache DB
Redis::command('keys', ['*pattern*']);  // Pattern search
Redis::command('dbsize');  // Count keys
```

### Database Selection for Direct Redis Operations

```php
// When using Redis:: directly for cache operations, select DB 1 first
Redis::command('select', [1]);
$keys = Redis::command('keys', ['*day-of-packages*']);
```

### Force Fetch Pattern

```php
// Today's data should always be force-fetched
$packages = $this->fetch_from_cache_or_api(
    $cache_key,
    fn() => $this->fetchFromApi(),
    null,
    $force_fetch || $start_day->isToday(),  // ✅ Force if today
    self::DEFAULT_CACHE_TIME,
);
```

### Cache Invalidation Rules

| Operation | Invalidate |
|-----------|------------|
| Create package | Tags cache, today's package cache |
| Finish package | Active + inactive package caches |
| Move/adjust package | No invalidation (lastModified handles) |
| Create/update item | Items cache |
| Harvest plant | Plant caches, harvest caches |

---

## Verification Checklist

Before committing caching code, verify:

- [ ] Key includes appropriate scope (org_id, license, date)
- [ ] TTL matches data volatility (use constants from MetrcApi)
- [ ] Force fetch for "today" data patterns
- [ ] Cache invalidation on related writes
- [ ] DB selection for direct Redis operations
- [ ] Error handling for Redis unavailability

---

## Pattern Loading Guide

### For BudTags Caching Tasks

#### API Response Caching
- `patterns/cache-facade.md` + `patterns/key-naming.md` + `scenarios/caching-api-responses.md`

#### Background Job Progress
- `patterns/redis-facade.md` + `scenarios/atomic-counters.md`

#### Bulk Cache Operations
- `patterns/cache-facade.md` + `patterns/ttl-strategy.md` + `scenarios/bulk-cache-operations.md`

#### Cache Management/Clearing
- `patterns/redis-facade.md` + `scenarios/pattern-based-deletion.md`

#### Rate Limiting
- `patterns/rate-limiting.md`

### For Redis Deep Dives

#### Understanding a Data Type
- `docs/data-types/index.md` → specific type file → `docs/commands/{type}.md`

#### Performance Optimization
- `docs/performance/index.md` → specific topic (pipelining, slow-commands, latency)

#### Memory Issues
- `docs/memory/index.md` → `docs/memory/eviction-policies.md` or `docs/memory/memory-doctor.md`

#### Persistence Configuration
- `docs/persistence/index.md` → `docs/persistence/rdb.md` or `docs/persistence/aof.md`

#### Security Hardening
- `docs/security/index.md` → specific topic (authentication, network, commands)

#### High Availability Setup
- `docs/high-availability/index.md` → replication, sentinel, or cluster

#### Advanced Patterns
- Lua scripting: `docs/advanced/lua-scripting.md`
- Transactions: `docs/advanced/transactions.md`
- Real-time messaging: `docs/advanced/pub-sub.md`
- Client-side caching: `docs/advanced/client-caching.md`

---

## Your Mission

Help users master Redis in the BudTags codebase by:

### BudTags Caching
1. **Designing consistent key names** that follow established conventions
2. **Choosing appropriate TTLs** based on data characteristics
3. **Using the right facade** (Cache vs Redis) for each operation
4. **Implementing proper invalidation** when data changes
5. **Ensuring organization scoping** to prevent cross-tenant leaks
6. **Handling Redis failures gracefully** with appropriate fallbacks
7. **Referencing real code patterns** from MetrcApi, DevController, and other services

### Redis Expertise
8. **Explaining any Redis command** with syntax, options, and use cases
9. **Recommending optimal data structures** for specific requirements
10. **Diagnosing performance issues** with slow query analysis and benchmarking
11. **Configuring production Redis** for persistence, memory, and availability
12. **Implementing advanced patterns** like Lua scripts, transactions, and pub/sub

**You are a Redis expert with comprehensive knowledge of both Redis internals and BudTags-specific patterns!**
