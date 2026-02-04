# Redis Skill

Comprehensive Redis caching patterns for BudTags, extracted from real codebase usage.

## Quick Start

This skill provides guidance on:

- **Cache Facade** - High-level caching (get, put, remember, forever)
- **Redis Facade** - Low-level operations (incr, sadd, smembers)
- **Key Naming** - Consistent, scoped key conventions
- **TTL Strategy** - When to cache forever vs with expiration
- **Distributed Locks** - Preventing race conditions
- **Rate Limiting** - API throttling patterns

## Directory Structure

```
redis/
├── SKILL.md              # Main entry point (~400 lines)
├── README.md             # This file
├── patterns/
│   ├── cache-facade.md   # Cache::get/put/remember/forever
│   ├── redis-facade.md   # Redis::sadd/smembers/incr/del
│   ├── key-naming.md     # BudTags key conventions
│   ├── ttl-strategy.md   # TTL decision guide
│   ├── distributed-locks.md  # Cache::lock patterns
│   └── rate-limiting.md  # Sliding window throttling
├── scenarios/
│   ├── caching-api-responses.md   # fetch_from_cache_or_api
│   ├── bulk-cache-operations.md   # Chunking strategies
│   ├── atomic-counters.md         # Progress tracking
│   └── pattern-based-deletion.md  # Cache clearing
└── docs/
    ├── data-types.md           # Redis data types
    ├── commands-quick-ref.md   # Essential commands
    └── laravel-integration.md  # Laravel + Redis
```

## Key Codebase References

| File | Patterns |
|------|----------|
| `app/Services/Api/MetrcApi.php` | Cache facade, TTL constants, force fetch |
| `app/Jobs/GeneratePackageLabel.php` | Redis::incr for atomic counters |
| `app/Http/Controllers/DevController.php` | Pattern-based deletion, DB selection |
| `app/Services/TransferSelectionMemoryService.php` | Org-scoped caching |
| `config/database.php` | Redis DB configuration |

## Critical Rules

1. **Organization Scope** - Always include `org_id` or `license` in keys
2. **DB Selection** - Use `Redis::command('select', [1])` for cache DB
3. **Force Fetch** - Always force-fetch "today" data
4. **TTL Constants** - Use MetrcApi constants, not magic numbers

## Slash Command

Use `/redis-help` to invoke the Redis assistant for quick questions.
