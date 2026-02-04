# Redis HyperLogLog - Deep Dive

HyperLogLog (HLL) is a probabilistic data structure for cardinality estimation - counting unique elements with constant memory.

---

## Concept

### What It Solves

**Problem:** Counting unique items (e.g., unique visitors) in large datasets requires O(N) memory with exact counting.

**Solution:** HyperLogLog provides approximate counts using only ~12 KB, regardless of cardinality.

### Accuracy

- **Standard error:** 0.81%
- **Memory:** Fixed 12 KB per key
- **Max cardinality:** 2^64 elements

Example accuracy:
| Actual Count | Estimated Range (99%) |
|--------------|----------------------|
| 1,000 | 970 - 1,030 |
| 100,000 | 97,000 - 103,000 |
| 10,000,000 | 9,700,000 - 10,300,000 |

---

## Commands

### PFADD - Add Elements

```php
// Add single element
Redis::pfadd('visitors', 'user123');

// Add multiple elements
Redis::pfadd('visitors', 'user123', 'user456', 'user789');

// Returns 1 if internal state changed, 0 otherwise
$changed = Redis::pfadd('visitors', 'user123');
```

### PFCOUNT - Get Cardinality

```php
// Count single HLL
$count = Redis::pfcount('visitors');

// Count union of multiple HLLs
$totalUnique = Redis::pfcount('visitors:day1', 'visitors:day2', 'visitors:day3');
```

### PFMERGE - Merge HLLs

```php
// Merge multiple HLLs into destination
Redis::pfmerge('visitors:week', 'visitors:mon', 'visitors:tue', 'visitors:wed');

// The destination contains union of all unique elements
$weeklyUnique = Redis::pfcount('visitors:week');
```

---

## Use Cases

### 1. Unique Visitor Counting

```php
class UniqueVisitorCounter
{
    public function trackVisit(string $userId, ?string $sessionId = null): void
    {
        $identifier = $userId ?: $sessionId ?: request()->ip();
        $today = date('Y-m-d');

        Redis::pipeline(function ($pipe) use ($identifier, $today) {
            // Daily count
            $pipe->pfadd("visitors:{$today}", $identifier);

            // Monthly count
            $pipe->pfadd("visitors:" . date('Y-m'), $identifier);

            // Set expiration
            $pipe->expire("visitors:{$today}", 86400 * 90); // 90 days
        });
    }

    public function getDailyCount(string $date): int
    {
        return Redis::pfcount("visitors:{$date}");
    }

    public function getWeeklyCount(string $startDate): int
    {
        $keys = [];
        $current = strtotime($startDate);

        for ($i = 0; $i < 7; $i++) {
            $keys[] = "visitors:" . date('Y-m-d', $current);
            $current += 86400;
        }

        return Redis::pfcount(...$keys);
    }

    public function getMonthlyCount(string $month): int
    {
        return Redis::pfcount("visitors:{$month}");
    }
}
```

### 2. Feature Usage Tracking

```php
class FeatureUsageTracker
{
    public function trackUsage(string $feature, int $userId): void
    {
        $today = date('Y-m-d');

        Redis::pfadd("feature:{$feature}:{$today}", $userId);
    }

    public function getUniqueUsersToday(string $feature): int
    {
        return Redis::pfcount("feature:{$feature}:" . date('Y-m-d'));
    }

    public function getUniqueUsersThisWeek(string $feature): int
    {
        $keys = [];
        for ($i = 0; $i < 7; $i++) {
            $keys[] = "feature:{$feature}:" . date('Y-m-d', strtotime("-{$i} days"));
        }

        return Redis::pfcount(...$keys);
    }

    public function compareFeatures(array $features): array
    {
        $result = [];
        $today = date('Y-m-d');

        foreach ($features as $feature) {
            $result[$feature] = Redis::pfcount("feature:{$feature}:{$today}");
        }

        return $result;
    }
}
```

### 3. Search Query Uniqueness

```php
class SearchAnalytics
{
    public function logSearch(string $query, int $userId): void
    {
        $normalized = strtolower(trim($query));
        $today = date('Y-m-d');

        Redis::pipeline(function ($pipe) use ($normalized, $userId, $today) {
            // Unique users searching
            $pipe->pfadd("search:users:{$today}", $userId);

            // Unique queries
            $pipe->pfadd("search:queries:{$today}", $normalized);

            // Users per query (for popular queries)
            $pipe->pfadd("search:query:{$normalized}:{$today}", $userId);
        });
    }

    public function getDailyStats(string $date): array
    {
        return [
            'unique_searchers' => Redis::pfcount("search:users:{$date}"),
            'unique_queries' => Redis::pfcount("search:queries:{$date}"),
        ];
    }

    public function getQueryPopularity(string $query, string $date): int
    {
        $normalized = strtolower(trim($query));
        return Redis::pfcount("search:query:{$normalized}:{$date}");
    }
}
```

### 4. Event Attendance / Reach

```php
class EventReach
{
    public function trackView(string $eventId, string $userId): void
    {
        Redis::pfadd("event:reach:{$eventId}", $userId);
    }

    public function getReach(string $eventId): int
    {
        return Redis::pfcount("event:reach:{$eventId}");
    }

    public function getCombinedReach(array $eventIds): int
    {
        $keys = array_map(fn($id) => "event:reach:{$id}", $eventIds);
        return Redis::pfcount(...$keys);
    }

    public function getCampaignReach(string $campaignId, array $eventIds): void
    {
        $keys = array_map(fn($id) => "event:reach:{$id}", $eventIds);

        // Merge all event HLLs into campaign HLL
        Redis::pfmerge("campaign:reach:{$campaignId}", ...$keys);
    }
}
```

### 5. A/B Test Unique Participants

```php
class ABTestTracker
{
    public function recordParticipant(string $testId, string $variant, string $userId): void
    {
        Redis::pfadd("abtest:{$testId}:{$variant}:participants", $userId);
    }

    public function recordConversion(string $testId, string $variant, string $userId): void
    {
        Redis::pfadd("abtest:{$testId}:{$variant}:conversions", $userId);
    }

    public function getResults(string $testId, array $variants): array
    {
        $results = [];

        foreach ($variants as $variant) {
            $participants = Redis::pfcount("abtest:{$testId}:{$variant}:participants");
            $conversions = Redis::pfcount("abtest:{$testId}:{$variant}:conversions");

            $results[$variant] = [
                'participants' => $participants,
                'conversions' => $conversions,
                'conversion_rate' => $participants > 0
                    ? round(($conversions / $participants) * 100, 2)
                    : 0,
            ];
        }

        return $results;
    }
}
```

---

## Memory Comparison

| Method | 1M Unique Items | 100M Unique Items |
|--------|-----------------|-------------------|
| **Set** | ~64 MB | ~6.4 GB |
| **HyperLogLog** | 12 KB | 12 KB |

Savings: **5,000x - 500,000x** less memory

---

## Performance Characteristics

| Command | Complexity |
|---------|------------|
| PFADD | O(1) |
| PFCOUNT (single) | O(1) |
| PFCOUNT (multiple) | O(N) where N = number of keys |
| PFMERGE | O(N) where N = number of keys |

All operations are extremely fast regardless of cardinality.

---

## BudTags Usage Opportunities

### Unique Package Access Tracking

```php
class PackageAccessTracker
{
    public function trackAccess(string $facility, string $packageId, int $userId): void
    {
        $today = date('Y-m-d');

        Redis::pipeline(function ($pipe) use ($facility, $packageId, $userId, $today) {
            // Unique users accessing packages today
            $pipe->pfadd("facility:{$facility}:users:{$today}", $userId);

            // Unique packages accessed today
            $pipe->pfadd("facility:{$facility}:packages:{$today}", $packageId);

            // Set TTL
            $pipe->expire("facility:{$facility}:users:{$today}", 86400 * 30);
            $pipe->expire("facility:{$facility}:packages:{$today}", 86400 * 30);
        });
    }

    public function getDailyStats(string $facility, string $date): array
    {
        return [
            'unique_users' => Redis::pfcount("facility:{$facility}:users:{$date}"),
            'unique_packages' => Redis::pfcount("facility:{$facility}:packages:{$date}"),
        ];
    }
}
```

### API Endpoint Usage

```php
class ApiUsageTracker
{
    public function track(string $endpoint, int $orgId): void
    {
        $hour = date('Y-m-d-H');
        Redis::pfadd("api:{$endpoint}:orgs:{$hour}", $orgId);
    }

    public function getUniqueOrgsLastHour(string $endpoint): int
    {
        return Redis::pfcount("api:{$endpoint}:orgs:" . date('Y-m-d-H'));
    }
}
```

---

## Limitations

1. **Approximate** - Not exact counts (0.81% error)
2. **No retrieval** - Cannot get actual elements back
3. **No removal** - Cannot remove elements once added
4. **Fixed memory** - 12 KB even for small cardinalities

### When NOT to Use HyperLogLog

- Need exact counts
- Need to retrieve the actual elements
- Need to remove elements
- Small cardinalities where Set is acceptable

---

## Key Takeaways

1. **Constant memory** - Always ~12 KB regardless of cardinality
2. **~0.81% error** - Acceptable for analytics use cases
3. **PFCOUNT unions** - Count across multiple HLLs
4. **PFMERGE** - Combine HLLs for aggregation
5. **Great for analytics** - Unique visitors, events, queries
6. **Set TTL separately** - Use EXPIRE on the key
7. **No element retrieval** - Only counts, not members
8. **Massive savings** - 5,000x+ memory reduction vs sets
