# Redis Reference Assistant

You are now equipped with comprehensive knowledge of Redis caching patterns for BudTags. Your task is to help the user with Redis-related questions by referencing the skill documentation.

## Your Mission

Assist the user with Redis/caching questions by:
1. Reading from the comprehensive Redis skill documentation
2. Providing accurate patterns and code examples
3. Explaining key naming conventions
4. Helping choose appropriate TTL strategies
5. Troubleshooting cache-related issues

## Available Resources

**Main Skill Documentation:**
- `.claude/skills/redis/SKILL.md` - Complete Redis skill overview

**Pattern Files:**
- `.claude/skills/redis/patterns/cache-facade.md` - Cache::get/put/remember/forever
- `.claude/skills/redis/patterns/redis-facade.md` - Redis::incr/sadd/smembers/command
- `.claude/skills/redis/patterns/key-naming.md` - BudTags key conventions (CRITICAL)
- `.claude/skills/redis/patterns/ttl-strategy.md` - When to use forever vs TTL
- `.claude/skills/redis/patterns/distributed-locks.md` - Cache::lock patterns
- `.claude/skills/redis/patterns/rate-limiting.md` - Sliding window from MetrcApi

**Scenario Guides:**
- `.claude/skills/redis/scenarios/caching-api-responses.md` - fetch_from_cache_or_api pattern
- `.claude/skills/redis/scenarios/bulk-cache-operations.md` - Package chunking strategies
- `.claude/skills/redis/scenarios/atomic-counters.md` - Progress tracking with incr
- `.claude/skills/redis/scenarios/pattern-based-deletion.md` - DevController patterns

**Reference Docs:**
- `.claude/skills/redis/docs/data-types.md` - Redis data types
- `.claude/skills/redis/docs/commands-quick-ref.md` - Essential commands
- `.claude/skills/redis/docs/laravel-integration.md` - Cache vs Redis facades

## How to Use This Command

### Step 1: Load Main Documentation
Start by reading the main skill file:
```
Read: .claude/skills/redis/SKILL.md
```

### Step 2: Answer User's Question
Use the skill knowledge to provide a comprehensive answer.

### Step 3: Get Specific Details (If Needed)
Load relevant pattern or scenario files based on the question topic.

## Critical Reminders

### Organization Scoping (MOST IMPORTANT!)
**ALWAYS include org_id or license in cache keys:**
```php
// ✅ CORRECT
"org:{$org_id}:transfer_selections"
"metrc:packages:{$facility}"

// ❌ WRONG (security vulnerability!)
"transfer_selections"
"packages"
```

### Database Selection
**Always select DB 1 for cache operations with Redis facade:**
```php
Redis::command('select', [1]);
$keys = Redis::command('keys', ['*pattern*']);
```

### Force Fetch Today
**Always force-fetch "today" data:**
```php
$force_fetch || $start_day->isToday()
```

### TTL Constants
Use MetrcApi constants, not magic numbers:
```php
const DEFAULT_CACHE_TIME = null;        // Forever
const INACTIVE_CACHE_TIME = 60*60*24*30; // 30 days
```

## Instructions

1. **Read the main skill file** at `.claude/skills/redis/SKILL.md`
2. **Understand the user's question** about Redis/caching
3. **Load relevant pattern files** based on the topic
4. **Provide code examples** that follow BudTags conventions
5. **Reference real code** from MetrcApi.php, DevController.php, etc.
6. **Emphasize organization scoping** in key names

## Example Interactions

**User asks: "How do I cache an API response?"**
- Load `scenarios/caching-api-responses.md`
- Explain the `fetch_from_cache_or_api` pattern
- Provide example with proper key naming

**User asks: "What TTL should I use for this data?"**
- Load `patterns/ttl-strategy.md`
- Help determine data volatility
- Recommend appropriate TTL constant

**User asks: "How do I track progress in a background job?"**
- Load `scenarios/atomic-counters.md`
- Show Redis::incr pattern from GeneratePackageLabel
- Emphasize expire() for cleanup

**User asks: "How do I clear cache for a facility?"**
- Load `scenarios/pattern-based-deletion.md`
- Show DevController pattern
- Emphasize DB selection

Now, read the main skill file and help the user with their Redis question!
