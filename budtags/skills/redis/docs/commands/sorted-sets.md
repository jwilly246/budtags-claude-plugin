# Redis Sorted Set Commands

Sorted sets are collections of unique strings ordered by associated floating-point scores. They combine set membership semantics with ranking capabilities.

---

## Core Commands

### ZADD

Adds members with scores to a sorted set.

```
ZADD key [NX|XX] [GT|LT] [CH] [INCR] score member [score member ...]
```

| Option | Description |
|--------|-------------|
| `NX` | Only add new elements (don't update existing) |
| `XX` | Only update existing elements (don't add new) |
| `GT` | Only update if new score > current score |
| `LT` | Only update if new score < current score |
| `CH` | Return changed count (added + updated) instead of just added |
| `INCR` | Increment score (like ZINCRBY) |

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - elements added (or changed with CH) |
| **Complexity** | O(log N) for each element |
| **Creates** | Key if it doesn't exist |

```php
// Add single member
Redis::zadd('leaderboard', 100, 'player1');

// Add multiple
Redis::zadd('leaderboard', 100, 'player1', 200, 'player2', 150, 'player3');

// Update only if higher score
Redis::zadd('leaderboard', 'GT', 250, 'player1');
```

---

### ZREM

Removes members from a sorted set.

```
ZREM key member [member ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of elements removed |
| **Complexity** | O(M log N) where M is members, N is set size |
| **Deletes** | Key if last member removed |

---

### ZSCORE

Returns the score of a member.

```
ZSCORE key member
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string (score) or nil |
| **Complexity** | O(1) |

---

### ZMSCORE

Returns scores of multiple members (Redis 6.2+).

```
ZMSCORE key member [member ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of scores (nil for missing) |
| **Complexity** | O(N) |

---

### ZCARD

Returns the number of members.

```
ZCARD key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - cardinality |
| **Complexity** | O(1) |

---

### ZCOUNT

Counts members with scores in a range.

```
ZCOUNT key min max
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - count of members in range |
| **Complexity** | O(log N) |

Use `-inf` and `+inf` for unbounded ranges. Prefix with `(` for exclusive bounds.

```php
// Count scores 0-100 inclusive
$count = Redis::zcount('scores', 0, 100);

// Count scores > 50 and <= 100
$count = Redis::zcount('scores', '(50', 100);
```

---

### ZINCRBY

Increments a member's score.

```
ZINCRBY key increment member
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string - new score |
| **Complexity** | O(log N) |
| **Creates** | Member with score=increment if doesn't exist |

```php
// Increment player score
$newScore = Redis::zincrby('leaderboard', 50, 'player1');
```

---

## Range Commands

### ZRANGE

Returns members in a range (unified command since Redis 6.2).

```
ZRANGE key start stop [BYSCORE|BYLEX] [REV] [LIMIT offset count] [WITHSCORES]
```

| Option | Description |
|--------|-------------|
| (default) | Range by index (0-based) |
| `BYSCORE` | Range by score |
| `BYLEX` | Range lexicographically (same-score members) |
| `REV` | Reverse order |
| `LIMIT` | Pagination (only with BYSCORE/BYLEX) |
| `WITHSCORES` | Include scores in output |

| Aspect | Details |
|--------|---------|
| **Returns** | Array of members (with scores if WITHSCORES) |
| **Complexity** | O(log N + M) where M is elements returned |

```php
// Get all members (ascending score)
$all = Redis::zrange('leaderboard', 0, -1);

// Get top 10 (descending score)
$top10 = Redis::zrange('leaderboard', 0, 9, 'REV');

// Get with scores
$withScores = Redis::zrange('leaderboard', 0, -1, 'WITHSCORES');

// Get by score range
$inRange = Redis::zrange('leaderboard', 100, 500, 'BYSCORE');

// Get by score range with limit
$paged = Redis::zrange('leaderboard', 0, 100, 'BYSCORE', 'LIMIT', 0, 10);
```

---

### ZRANK

Returns the rank (index) of a member (ascending order).

```
ZRANK key member
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer (0-based rank) or nil |
| **Complexity** | O(log N) |

---

### ZREVRANK

Returns the rank in descending order.

```
ZREVRANK key member
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer (0-based rank) or nil |
| **Complexity** | O(log N) |

```php
// Get player's position on leaderboard (1st = rank 0)
$rank = Redis::zrevrank('leaderboard', 'player1');
$position = $rank + 1;  // Convert to 1-based
```

---

## Pop Commands

### ZPOPMIN

Removes and returns lowest-scoring members.

```
ZPOPMIN key [count]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of [member, score] pairs |
| **Complexity** | O(log N * M) where M is count |
| **Deletes** | Key if last member popped |

---

### ZPOPMAX

Removes and returns highest-scoring members.

```
ZPOPMAX key [count]
```

---

### BZPOPMIN / BZPOPMAX

Blocking versions of ZPOPMIN/ZPOPMAX.

```
BZPOPMIN key [key ...] timeout
BZPOPMAX key [key ...] timeout
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array [key, member, score] or nil |
| **Timeout** | 0 = wait indefinitely |

---

### ZMPOP (Redis 7.0+)

Pops from first non-empty sorted set.

```
ZMPOP numkeys key [key ...] MIN|MAX [COUNT count]
```

---

## Remove by Range Commands

### ZREMRANGEBYRANK

Removes members by rank range.

```
ZREMRANGEBYRANK key start stop
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number removed |
| **Complexity** | O(log N + M) |

```php
// Remove bottom 10
Redis::zremrangebyrank('leaderboard', 0, 9);
```

---

### ZREMRANGEBYSCORE

Removes members by score range.

```
ZREMRANGEBYSCORE key min max
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number removed |
| **Complexity** | O(log N + M) |

```php
// Rate limiting: remove old timestamps
Redis::zremrangebyscore($key, '-inf', $windowStart);
```

---

### ZREMRANGEBYLEX

Removes members by lexicographical range (same-score members).

```
ZREMRANGEBYLEX key min max
```

---

## Set Operations

### ZINTER

Returns intersection of sorted sets.

```
ZINTER numkeys key [key ...] [WEIGHTS weight ...] [AGGREGATE SUM|MIN|MAX] [WITHSCORES]
```

| Option | Description |
|--------|-------------|
| `WEIGHTS` | Multiply scores by weight per set |
| `AGGREGATE` | How to combine scores: SUM (default), MIN, MAX |

---

### ZINTERSTORE

Stores intersection in destination.

```
ZINTERSTORE destination numkeys key [key ...] [WEIGHTS ...] [AGGREGATE ...]
```

---

### ZINTERCARD (Redis 7.0+)

Returns intersection cardinality without materializing.

```
ZINTERCARD numkeys key [key ...] [LIMIT limit]
```

---

### ZUNION

Returns union of sorted sets.

```
ZUNION numkeys key [key ...] [WEIGHTS ...] [AGGREGATE ...] [WITHSCORES]
```

---

### ZUNIONSTORE

Stores union in destination.

```
ZUNIONSTORE destination numkeys key [key ...] [WEIGHTS ...] [AGGREGATE ...]
```

---

### ZDIFF

Returns difference of sorted sets.

```
ZDIFF numkeys key [key ...] [WITHSCORES]
```

---

### ZDIFFSTORE

Stores difference in destination.

```
ZDIFFSTORE destination numkeys key [key ...]
```

---

## Other Commands

### ZLEXCOUNT

Counts members in lexicographical range.

```
ZLEXCOUNT key min max
```

---

### ZRANGESTORE

Stores range result in destination (Redis 6.2+).

```
ZRANGESTORE dst src start stop [BYSCORE|BYLEX] [REV] [LIMIT ...]
```

---

### ZRANDMEMBER

Returns random members (Redis 6.2+).

```
ZRANDMEMBER key [count [WITHSCORES]]
```

---

### ZSCAN

Iterates over members safely.

```
ZSCAN key cursor [MATCH pattern] [COUNT count]
```

---

## Deprecated Commands

| Deprecated | Replacement |
|------------|-------------|
| `ZRANGEBYSCORE` | `ZRANGE ... BYSCORE` |
| `ZREVRANGEBYSCORE` | `ZRANGE ... BYSCORE REV` |
| `ZRANGEBYLEX` | `ZRANGE ... BYLEX` |
| `ZREVRANGEBYLEX` | `ZRANGE ... BYLEX REV` |
| `ZREVRANGE` | `ZRANGE ... REV` |

---

## Use Cases

### Leaderboards

```php
// Add/update score
Redis::zadd('leaderboard', $score, $playerId);

// Get top 10
$top10 = Redis::zrange('leaderboard', 0, 9, 'REV', 'WITHSCORES');

// Get player rank
$rank = Redis::zrevrank('leaderboard', $playerId);

// Increment score
Redis::zincrby('leaderboard', $points, $playerId);
```

### Rate Limiting (Sliding Window)

```php
$key = "rate_limit:{$userId}";
$now = time();
$windowStart = $now - 60;  // 60-second window

// Add current request
Redis::zadd($key, $now, uniqid());

// Remove old entries
Redis::zremrangebyscore($key, '-inf', $windowStart);

// Count requests in window
$count = Redis::zcard($key);

// Set expiration
Redis::expire($key, 60);

if ($count > $limit) {
    // Rate limited
}
```

### Time-Based Data

```php
// Store events with timestamps
Redis::zadd('events', time(), json_encode($event));

// Get events in time range
$events = Redis::zrange('events', $startTime, $endTime, 'BYSCORE');

// Get recent events
$recent = Redis::zrange('events', 0, 9, 'REV');
```

### Priority Queue

```php
// Add jobs with priority (lower = higher priority)
Redis::zadd('priority_queue', $priority, json_encode($job));

// Get highest priority job
[$job] = Redis::zpopmin('priority_queue');

// Or blocking
[$key, $job, $priority] = Redis::bzpopmin('priority_queue', 30);
```

---

## Performance Characteristics

| Command | Complexity | Notes |
|---------|------------|-------|
| ZADD, ZREM | O(log N) | Skip list operations |
| ZSCORE, ZRANK | O(log N) | Fast lookups |
| ZRANGE | O(log N + M) | M = elements returned |
| ZINCRBY | O(log N) | Atomic score update |
| Set operations | O(N*K + M log M) | K=sets, N=elements, M=result |

**Best practices:**
- Use for naturally ranked data
- ZINCRBY is atomic - great for concurrent updates
- Use ZRANGEBYSCORE for time-based queries
- Consider cardinality commands (*CARD) when you only need counts
- Use ZSCAN for iterating large sorted sets
