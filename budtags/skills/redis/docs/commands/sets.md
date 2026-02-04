# Redis Set Commands

Redis sets are unordered collections of unique strings. They support O(1) membership tests and set operations (union, intersection, difference).

---

## Core Commands

### SADD

Adds members to a set.

```
SADD key member [member ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of elements added (excludes existing) |
| **Complexity** | O(1) for each element |
| **Creates** | Key if it doesn't exist |

```php
// BudTags pattern: tracking package labels
Redis::sadd("metrc:package-labels:{$facility}", ...$labels);

// Add single member
Redis::sadd('myset', 'value1');

// Add multiple members
Redis::sadd('myset', 'value1', 'value2', 'value3');
```

---

### SREM

Removes members from a set.

```
SREM key member [member ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of elements removed |
| **Complexity** | O(N) where N is number of members |
| **Deletes** | Key if last member removed |

```php
Redis::srem('myset', 'value1');
Redis::srem('myset', 'value1', 'value2');
```

---

### SMEMBERS

Returns all members of a set.

```
SMEMBERS key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of all members |
| **Complexity** | O(N) where N is set cardinality |

```php
// BudTags pattern: get tracked labels
$labels = Redis::smembers("metrc:package-labels:{$facility}");
```

**Warning:** Avoid on large sets in production. Use SSCAN instead.

---

### SISMEMBER

Tests if a member exists in a set.

```
SISMEMBER key member
```

| Aspect | Details |
|--------|---------|
| **Returns** | 1 if member exists, 0 if not |
| **Complexity** | O(1) |

```php
$exists = Redis::sismember('myset', 'value1');
```

---

### SMISMEMBER

Tests multiple members at once (Redis 6.2+).

```
SMISMEMBER key member [member ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of 1s and 0s for each member |
| **Complexity** | O(N) where N is members checked |

---

### SCARD

Returns the number of members in a set.

```
SCARD key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - set cardinality (0 if key doesn't exist) |
| **Complexity** | O(1) |

```php
$count = Redis::scard('myset');
```

---

## Random Access Commands

### SPOP

Removes and returns random members.

```
SPOP key [count]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string (single) or array (multiple), nil if empty |
| **Complexity** | O(1) single, O(N) multiple |
| **Deletes** | Key if last member popped |

```php
$random = Redis::spop('myset');      // Remove 1 random
$random = Redis::spop('myset', 5);   // Remove 5 random
```

---

### SRANDMEMBER

Returns random members WITHOUT removing them.

```
SRANDMEMBER key [count]
```

| Count | Behavior |
|-------|----------|
| Positive | Return up to `count` unique members |
| Negative | Return `abs(count)` members (may repeat) |

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string (no count) or array (with count) |
| **Complexity** | O(N) where N is count |

---

## Set Operations

### SINTER

Returns intersection of multiple sets.

```
SINTER key [key ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of members in ALL sets |
| **Complexity** | O(N*M) where N is smallest set, M is number of sets |

```php
// Find common elements
$common = Redis::sinter('set1', 'set2', 'set3');
```

---

### SINTERSTORE

Stores intersection in destination key.

```
SINTERSTORE destination key [key ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - cardinality of result |
| **Complexity** | O(N*M) |

---

### SINTERCARD

Returns cardinality of intersection without materializing (Redis 7.0+).

```
SINTERCARD numkeys key [key ...] [LIMIT limit]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - intersection cardinality |
| **Complexity** | O(N*M) |
| **LIMIT** | Stop counting after limit reached |

More efficient when you only need the count, not the members.

---

### SUNION

Returns union of multiple sets.

```
SUNION key [key ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of members in ANY set |
| **Complexity** | O(N) where N is total elements |

```php
$all = Redis::sunion('set1', 'set2', 'set3');
```

---

### SUNIONSTORE

Stores union in destination key.

```
SUNIONSTORE destination key [key ...]
```

---

### SDIFF

Returns difference (members in first set but not in others).

```
SDIFF key [key ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of members in first set not in others |
| **Complexity** | O(N) where N is total elements |

```php
// Find elements unique to set1
$unique = Redis::sdiff('set1', 'set2');
```

---

### SDIFFSTORE

Stores difference in destination key.

```
SDIFFSTORE destination key [key ...]
```

---

## Movement Commands

### SMOVE

Atomically moves a member from one set to another.

```
SMOVE source destination member
```

| Aspect | Details |
|--------|---------|
| **Returns** | 1 if moved, 0 if source didn't contain member |
| **Complexity** | O(1) |

---

## Iteration

### SSCAN

Iterates over set members safely.

```
SSCAN key cursor [MATCH pattern] [COUNT count]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array [next_cursor, [members]] |
| **Complexity** | O(1) per call, O(N) for full iteration |

**Safe iteration pattern:**
```php
$cursor = 0;
$members = [];
do {
    [$cursor, $batch] = Redis::sscan('myset', $cursor, 'COUNT', 100);
    $members = array_merge($members, $batch);
} while ($cursor != 0);
```

---

## BudTags Patterns

### Tracking Unique Items

```php
// Track package labels being processed
Redis::sadd("metrc:package-labels:{$facility}", ...$labels);

// Check if label already processed
if (Redis::sismember("metrc:package-labels:{$facility}", $label)) {
    // Skip duplicate
}

// Get all tracked labels
$labels = Redis::smembers("metrc:package-labels:{$facility}");

// Clean up
Redis::del("metrc:package-labels:{$facility}");
```

### Preventing Duplicate Operations

```php
// Add to set returns 1 if new, 0 if duplicate
$isNew = Redis::sadd("processed:today", $itemId);
if ($isNew) {
    // Process item
}
```

### Tag/Category Management

```php
// Add tags to item
Redis::sadd("item:{$id}:tags", 'organic', 'premium', 'local');

// Find items with all specified tags (intersection)
Redis::sinterstore('result', 'tag:organic', 'tag:premium');

// Find items with any specified tag (union)
Redis::sunionstore('result', 'tag:organic', 'tag:premium');
```

---

## Use Cases

| Use Case | Commands | Example |
|----------|----------|---------|
| **Unique tracking** | SADD, SISMEMBER | Prevent duplicate processing |
| **Membership test** | SISMEMBER | Check if user has permission |
| **Tags/categories** | SADD, SMEMBERS | Item tagging system |
| **Common elements** | SINTER | Find mutual friends |
| **All elements** | SUNION | Aggregate tags |
| **Unique elements** | SDIFF | Find new items |
| **Random selection** | SRANDMEMBER | Pick random winners |

---

## Performance Characteristics

| Command | Complexity | Notes |
|---------|------------|-------|
| SADD, SREM | O(1) per element | Very fast |
| SISMEMBER | O(1) | Constant time lookup |
| SMEMBERS | O(N) | Returns all - careful with large sets |
| SINTER | O(N*M) | Can be expensive with many/large sets |
| SSCAN | O(1) per call | Safe for large sets |

**Best practices:**
- Use SISMEMBER for membership tests (O(1))
- Use SSCAN instead of SMEMBERS for large sets
- Store intersection/union results if needed repeatedly
- Consider SINTERCARD when you only need the count
- Remember: sets auto-deduplicate
