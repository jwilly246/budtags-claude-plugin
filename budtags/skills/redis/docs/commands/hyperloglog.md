# Redis HyperLogLog Commands

HyperLogLog is a probabilistic data structure for estimating cardinality (unique element count) with minimal memory usage.

---

## Overview

| Feature | Details |
|---------|---------|
| **Memory** | ~12 KB per HyperLogLog |
| **Accuracy** | Standard error of 0.81% |
| **Max elements** | No practical limit |
| **Use case** | Counting unique items (visitors, IPs, etc.) |

Trade-off: Small memory footprint for approximate (not exact) counts.

---

## Commands

### PFADD

Adds elements to a HyperLogLog.

```
PFADD key element [element ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | 1 if cardinality changed, 0 otherwise |
| **Complexity** | O(1) per element |
| **Creates** | Key if doesn't exist |

```php
// Track unique page visitors
Redis::pfadd('visitors:2024-01-15', 'user:123', 'user:456', 'user:789');

// Add more visitors
Redis::pfadd('visitors:2024-01-15', 'user:123');  // Returns 0 (duplicate)
Redis::pfadd('visitors:2024-01-15', 'user:999');  // Returns 1 (new)
```

---

### PFCOUNT

Returns the approximate cardinality.

```
PFCOUNT key [key ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - approximate unique count |
| **Complexity** | O(1) single key, O(N) multiple keys |

```php
// Get unique visitor count
$uniqueVisitors = Redis::pfcount('visitors:2024-01-15');

// Get combined count across multiple days (union)
$weeklyUnique = Redis::pfcount(
    'visitors:2024-01-15',
    'visitors:2024-01-16',
    'visitors:2024-01-17'
);
```

---

### PFMERGE

Merges multiple HyperLogLogs into one.

```
PFMERGE destkey sourcekey [sourcekey ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(N) where N is source keys |

```php
// Merge daily counts into weekly
Redis::pfmerge('visitors:week:2024-03',
    'visitors:2024-01-15',
    'visitors:2024-01-16',
    'visitors:2024-01-17',
    'visitors:2024-01-18',
    'visitors:2024-01-19',
    'visitors:2024-01-20',
    'visitors:2024-01-21'
);

// Get weekly unique count
$weeklyUnique = Redis::pfcount('visitors:week:2024-03');
```

---

## Use Cases

### Unique Visitor Tracking

```php
class UniqueVisitorTracker
{
    public function trackVisit(string $pageId, string $visitorId): void
    {
        $today = date('Y-m-d');

        // Track per-page visitors
        Redis::pfadd("visitors:page:{$pageId}:{$today}", $visitorId);

        // Track site-wide visitors
        Redis::pfadd("visitors:site:{$today}", $visitorId);
    }

    public function getDailyUnique(string $pageId, string $date): int
    {
        return Redis::pfcount("visitors:page:{$pageId}:{$date}");
    }

    public function getSiteUnique(string $date): int
    {
        return Redis::pfcount("visitors:site:{$date}");
    }

    public function getWeeklyUnique(string $pageId): int
    {
        $keys = [];
        for ($i = 0; $i < 7; $i++) {
            $date = date('Y-m-d', strtotime("-{$i} days"));
            $keys[] = "visitors:page:{$pageId}:{$date}";
        }
        return Redis::pfcount(...$keys);
    }
}
```

### Unique IP Tracking

```php
class UniqueIpCounter
{
    public function recordIp(string $ip): void
    {
        $hour = date('Y-m-d-H');
        Redis::pfadd("ips:{$hour}", $ip);
        Redis::expire("ips:{$hour}", 86400);  // Keep 24 hours
    }

    public function getUniqueIpsLastHour(): int
    {
        $hour = date('Y-m-d-H');
        return Redis::pfcount("ips:{$hour}");
    }

    public function getUniqueIpsLast24Hours(): int
    {
        $keys = [];
        for ($i = 0; $i < 24; $i++) {
            $hour = date('Y-m-d-H', strtotime("-{$i} hours"));
            $keys[] = "ips:{$hour}";
        }
        return Redis::pfcount(...$keys);
    }
}
```

### Search Term Cardinality

```php
class SearchAnalytics
{
    public function trackSearch(string $term, string $userId): void
    {
        $today = date('Y-m-d');

        // Track users who searched this term
        Redis::pfadd("search:users:{$term}:{$today}", $userId);

        // Track unique search terms today
        Redis::pfadd("search:terms:{$today}", $term);
    }

    public function getUniqueSearchers(string $term, string $date): int
    {
        return Redis::pfcount("search:users:{$term}:{$date}");
    }

    public function getUniqueTermsToday(): int
    {
        return Redis::pfcount("search:terms:" . date('Y-m-d'));
    }
}
```

### API Endpoint Analytics

```php
class ApiAnalytics
{
    public function trackRequest(string $endpoint, string $clientId): void
    {
        $key = "api:clients:{$endpoint}:" . date('Y-m-d');
        Redis::pfadd($key, $clientId);
        Redis::expire($key, 86400 * 7);  // Keep 7 days
    }

    public function getUniqueClients(string $endpoint, string $date): int
    {
        return Redis::pfcount("api:clients:{$endpoint}:{$date}");
    }

    public function getMonthlyUniqueClients(string $endpoint): int
    {
        $keys = [];
        for ($i = 0; $i < 30; $i++) {
            $date = date('Y-m-d', strtotime("-{$i} days"));
            $keys[] = "api:clients:{$endpoint}:{$date}";
        }
        return Redis::pfcount(...$keys);
    }
}
```

---

## HyperLogLog vs Sets

| Feature | HyperLogLog | Set |
|---------|-------------|-----|
| Memory | ~12 KB fixed | Grows with elements |
| Accuracy | ~0.81% error | Exact |
| Operations | Add, Count, Merge | Full set operations |
| Retrieve elements | No | Yes |
| Check membership | No | Yes |

**Use HyperLogLog when:**
- Only need count, not individual elements
- Counting millions+ of elements
- Memory efficiency is critical
- ~1% error is acceptable

**Use Set when:**
- Need to check membership
- Need to retrieve elements
- Need exact count
- Smaller element sets

---

## Memory Comparison

Counting 1 million unique users:

| Data Structure | Memory Usage |
|----------------|--------------|
| HyperLogLog | ~12 KB |
| Set (integers) | ~56 MB |
| Set (UUIDs) | ~80+ MB |

HyperLogLog uses **~4700x less memory** than a set for this use case.

---

## Accuracy Example

```php
// Add 1 million random elements
for ($i = 0; $i < 1_000_000; $i++) {
    Redis::pfadd('test:hll', "element:{$i}");
}

$estimated = Redis::pfcount('test:hll');
// Typically returns 992,000 - 1,008,000 (±0.81% of 1,000,000)
```

---

## Combining HyperLogLogs

### Daily to Weekly Rollup

```php
// End of day: merge into weekly
Redis::pfmerge(
    'visitors:week:' . date('W'),
    'visitors:day:' . date('Y-m-d')
);

// End of week: merge into monthly
Redis::pfmerge(
    'visitors:month:' . date('Y-m'),
    ...array_map(
        fn($d) => "visitors:day:{$d}",
        $this->getDaysInWeek()
    )
);
```

### Cross-Source Deduplication

```php
// Count unique users across all platforms
$totalUnique = Redis::pfcount(
    'users:web',
    'users:mobile',
    'users:api'
);
// Automatically deduplicates across sources
```

---

## Best Practices

1. **Use for large cardinalities** - Not worth it for small sets
2. **Acceptable error** - Ensure ~1% error is okay for use case
3. **Time-based keys** - Partition by day/hour for rollups
4. **Set expiration** - Clean up old HyperLogLogs
5. **Combine with PFMERGE** - For aggregate counts
6. **Don't mix with other commands** - HyperLogLog has its own structure

---

## Performance Notes

| Aspect | Details |
|--------|---------|
| PFADD | O(1) - constant time |
| PFCOUNT (single) | O(1) - constant time |
| PFCOUNT (multiple) | O(N) - merges on-the-fly |
| PFMERGE | O(N) - N = number of sources |
| Memory per HLL | 12,304 bytes (fixed) |

**Optimization Tips:**
- Pre-merge for frequently queried combinations
- Use PFMERGE instead of repeated PFCOUNT on same keys
- Partition by time for efficient expiration
