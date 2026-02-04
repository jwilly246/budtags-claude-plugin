# Redis Sets - Deep Dive

Sets are unordered collections of unique strings with O(1) membership tests and powerful set operations.

---

## Internal Representation

### Encodings

| Encoding | Condition | Memory |
|----------|-----------|--------|
| `intset` | All integers, ≤ 512 elements | Very compact |
| `listpack` | ≤ 128 elements, each ≤ 64 bytes | Compact |
| `hashtable` | Exceeds limits | Full hash table |

Configuration:
```
set-max-intset-entries 512
set-max-listpack-entries 128
set-max-listpack-value 64
```

### Intset

For sets containing only integers, Redis uses a sorted array:
- Binary search for membership: O(log N)
- Very memory efficient
- Automatically upgrades encoding as needed

---

## Memory Analysis

### Integer Set (intset)
1,000 integers:
```
Header: 8 bytes
Data: 1000 × 8 bytes = 8,000 bytes
Total: ~8 KB
```

### String Set (hashtable)
1,000 strings (avg 10 chars):
```
Hash table: ~2 KB
Dict entries: 1000 × 24 = 24 KB
Strings: 1000 × ~20 = 20 KB
Total: ~46 KB
```

**Intset is 5-6x more efficient!**

---

## Use Cases

### 1. Unique Item Tracking

```php
class UniqueTracker
{
    public function track(string $category, string $item): bool
    {
        // Returns 1 if new, 0 if already exists
        return Redis::sadd("unique:{$category}", $item) === 1;
    }

    public function isTracked(string $category, string $item): bool
    {
        return Redis::sismember("unique:{$category}", $item) === 1;
    }

    public function getCount(string $category): int
    {
        return Redis::scard("unique:{$category}");
    }

    public function getAll(string $category): array
    {
        return Redis::smembers("unique:{$category}");
    }
}
```

### 2. Tag System

```php
class TagSystem
{
    public function addTags(string $itemId, array $tags): void
    {
        // Add tags to item
        Redis::sadd("item:{$itemId}:tags", ...$tags);

        // Add item to each tag's set
        foreach ($tags as $tag) {
            Redis::sadd("tag:{$tag}:items", $itemId);
        }
    }

    public function getTags(string $itemId): array
    {
        return Redis::smembers("item:{$itemId}:tags");
    }

    public function getItemsByTag(string $tag): array
    {
        return Redis::smembers("tag:{$tag}:items");
    }

    public function getItemsWithAllTags(array $tags): array
    {
        $keys = array_map(fn($t) => "tag:{$t}:items", $tags);
        return Redis::sinter(...$keys);
    }

    public function getItemsWithAnyTag(array $tags): array
    {
        $keys = array_map(fn($t) => "tag:{$t}:items", $tags);
        return Redis::sunion(...$keys);
    }
}
```

### 3. Online Users

```php
class OnlineUsers
{
    public function setOnline(int $userId): void
    {
        Redis::sadd('users:online', $userId);
    }

    public function setOffline(int $userId): void
    {
        Redis::srem('users:online', $userId);
    }

    public function isOnline(int $userId): bool
    {
        return Redis::sismember('users:online', $userId) === 1;
    }

    public function getOnlineCount(): int
    {
        return Redis::scard('users:online');
    }

    public function getRandomOnlineUsers(int $count): array
    {
        return Redis::srandmember('users:online', $count);
    }
}
```

### 4. Lottery/Random Selection

```php
class Lottery
{
    public function enter(string $lotteryId, string $participantId): void
    {
        Redis::sadd("lottery:{$lotteryId}", $participantId);
    }

    public function selectWinner(string $lotteryId): ?string
    {
        // Pop random winner (removes from set)
        return Redis::spop("lottery:{$lotteryId}");
    }

    public function selectWinners(string $lotteryId, int $count): array
    {
        return Redis::spop("lottery:{$lotteryId}", $count);
    }

    public function peekPotentialWinners(string $lotteryId, int $count): array
    {
        // Random without removing
        return Redis::srandmember("lottery:{$lotteryId}", $count);
    }
}
```

---

## Set Operations

### Intersection (Common Elements)

```php
// Users who visited both pages
$page1Visitors = 'visitors:page1';
$page2Visitors = 'visitors:page2';

// Get intersection
$common = Redis::sinter($page1Visitors, $page2Visitors);

// Store result
Redis::sinterstore('visitors:both', $page1Visitors, $page2Visitors);

// Just count (Redis 7.0+)
$count = Redis::sintercard(2, $page1Visitors, $page2Visitors);
```

### Union (All Elements)

```php
// All visitors across pages
$allVisitors = Redis::sunion('visitors:page1', 'visitors:page2', 'visitors:page3');

// Store result
Redis::sunionstore('visitors:all', 'visitors:page1', 'visitors:page2');
```

### Difference (Unique to First)

```php
// Users who visited page1 but not page2
$unique = Redis::sdiff('visitors:page1', 'visitors:page2');

// New users (visited today, not yesterday)
$newUsers = Redis::sdiff('visitors:today', 'visitors:yesterday');
```

---

## Performance Characteristics

### Command Complexities

| Command | Intset | Listpack | Hashtable |
|---------|--------|----------|-----------|
| SADD | O(N)* | O(N) | O(1) |
| SREM | O(N)* | O(N) | O(1) |
| SISMEMBER | O(log N) | O(N) | O(1) |
| SCARD | O(1) | O(1) | O(1) |
| SMEMBERS | O(N) | O(N) | O(N) |
| SPOP | O(1) | O(1) | O(1) |

*Intset maintains sorted order

### Set Operation Complexities

| Operation | Complexity |
|-----------|------------|
| SINTER | O(N × M) where N = smallest set, M = sets |
| SUNION | O(N) where N = total elements |
| SDIFF | O(N) where N = total elements |
| SINTERCARD | O(N × M) + early exit with LIMIT |

---

## BudTags Usage

### Package Label Tracking

```php
// Current pattern in bulk operations
class LabelTracker
{
    public function trackLabels(string $facility, array $labels): void
    {
        if (!empty($labels)) {
            Redis::sadd("metrc:package-labels:{$facility}", ...$labels);
        }
    }

    public function getTrackedLabels(string $facility): array
    {
        return Redis::smembers("metrc:package-labels:{$facility}");
    }

    public function isLabelTracked(string $facility, string $label): bool
    {
        return Redis::sismember("metrc:package-labels:{$facility}", $label) === 1;
    }

    public function clearTracking(string $facility): void
    {
        Redis::del("metrc:package-labels:{$facility}");
    }

    public function getTrackedCount(string $facility): int
    {
        return Redis::scard("metrc:package-labels:{$facility}");
    }
}
```

### Preventing Duplicate Operations

```php
class DuplicateGuard
{
    public function canProcess(string $operation, string $itemId): bool
    {
        // Returns true only if this is new (not a duplicate)
        return Redis::sadd("processed:{$operation}", $itemId) === 1;
    }

    public function markProcessed(string $operation, string $itemId): void
    {
        Redis::sadd("processed:{$operation}", $itemId);
    }

    public function reset(string $operation): void
    {
        Redis::del("processed:{$operation}");
    }
}
```

---

## Anti-Patterns

### 1. Using SMEMBERS on Large Sets

```php
// ❌ Bad: Can return millions of items
$all = Redis::smembers('huge_set');

// ✅ Better: Use SSCAN for iteration
$cursor = 0;
do {
    [$cursor, $batch] = Redis::sscan('huge_set', $cursor, 'COUNT', 1000);
    processBatch($batch);
} while ($cursor != 0);
```

### 2. Storing Non-Unique Data

```php
// ❌ Wasteful: Sets auto-deduplicate, list might be better
foreach ($duplicateAllowed as $item) {
    Redis::sadd('items', $item);
}

// ✅ If order matters and duplicates allowed, use list
foreach ($duplicateAllowed as $item) {
    Redis::rpush('items', $item);
}
```

### 3. Not Using SINTERCARD

```php
// ❌ Bad: Materializes full intersection
$count = count(Redis::sinter('set1', 'set2'));

// ✅ Better (Redis 7.0+): Just count
$count = Redis::sintercard(2, 'set1', 'set2');

// Even better with limit
$hasCommon = Redis::sintercard(2, 'set1', 'set2', 'LIMIT', 1) > 0;
```

---

## Key Takeaways

1. **Automatic deduplication** - Perfect for unique items
2. **O(1) membership** - SISMEMBER is constant time
3. **Use integer IDs** - Intset encoding is very efficient
4. **Powerful set operations** - SINTER, SUNION, SDIFF
5. **SSCAN for large sets** - Avoid SMEMBERS
6. **SINTERCARD (7.0+)** - Count without materializing
7. **SPOP is random** - Good for lotteries/sampling
