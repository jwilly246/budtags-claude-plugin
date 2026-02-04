# Redis Data Types

Redis supports multiple data types, each optimized for different use cases. BudTags primarily uses Strings, Sets, and Sorted Sets.

---

## Strings

The most basic Redis type. Can store text, numbers, or serialized data.

### Operations Used in BudTags

```php
// Via Cache facade (recommended for most cases)
Cache::put($key, $value, $ttl);    // SET with expiration
Cache::get($key);                   // GET
Cache::forever($key, $value);       // SET without expiration

// Via Redis facade (for atomic operations)
Redis::incr($key);                  // Increment integer
Redis::decr($key);                  // Decrement integer
Redis::expire($key, $seconds);      // Set expiration
```

### Characteristics

- Maximum size: 512 MB
- Can store any serializable data (Laravel auto-serializes)
- Atomic increment/decrement for counters
- TTL can be set per key

---

## Sets

Unordered collections of unique strings. Used for tracking unique items.

### Operations Used in BudTags

```php
// Add members to set
Redis::sadd("metrc:package-labels:{$facility}", ...$labels);

// Get all members
$labels = Redis::smembers("metrc:package-labels:{$facility}");

// Check membership
$exists = Redis::sismember($key, $member);

// Remove member
Redis::srem($key, $member);

// Delete entire set
Redis::del($key);
```

### Use Cases

- Tracking package labels being processed
- Preventing duplicate operations
- Maintaining lists of unique IDs

### Characteristics

- Automatic deduplication
- O(1) add, remove, check membership
- No ordering guarantee

---

## Sorted Sets

Like sets, but each member has a score for ordering.

### Potential Use Cases

```php
// Add with score (timestamp for rate limiting)
Redis::zadd($key, time(), $requestId);

// Remove old entries (sliding window)
Redis::zremrangebyscore($key, '-inf', $windowStart);

// Count entries in range
$count = Redis::zcard($key);

// Get entries with scores
$entries = Redis::zrange($key, 0, -1, ['WITHSCORES' => true]);
```

### Characteristics

- Ordered by score
- O(log N) for most operations
- Ideal for rate limiting, leaderboards, time-series

---

## Hashes

Maps of field-value pairs. Like a mini key-value store within a key.

### Potential Use Cases

```php
// Store object fields
Redis::hset("user:{$id}", 'name', $name);
Redis::hset("user:{$id}", 'email', $email);

// Get single field
$name = Redis::hget("user:{$id}", 'name');

// Get all fields
$user = Redis::hgetall("user:{$id}");

// Increment field
Redis::hincrby("user:{$id}", 'visits', 1);
```

### Characteristics

- Memory efficient for small objects
- Individual field access without full deserialization
- Atomic field operations

---

## Lists

Ordered collections (doubly-linked lists).

### Potential Use Cases

```php
// Add to list
Redis::lpush($key, $value);  // Left (head)
Redis::rpush($key, $value);  // Right (tail)

// Pop from list
$item = Redis::lpop($key);   // Left
$item = Redis::rpop($key);   // Right

// Get range
$items = Redis::lrange($key, 0, -1);  // All items
$items = Redis::lrange($key, 0, 9);   // First 10
```

### Characteristics

- O(1) push/pop at ends
- O(N) for middle access
- Ideal for queues, logs, message streams

---

## Data Type Selection Guide

| Need | Type | Example |
|------|------|---------|
| Cache a value | String | `Cache::put('key', $data)` |
| Counter | String | `Redis::incr('counter')` |
| Unique set of IDs | Set | `Redis::sadd('labels', ...)` |
| Ranked/scored items | Sorted Set | Rate limiting windows |
| Object with fields | Hash | User session data |
| Queue/stack | List | Job queues |

---

## BudTags Usage Summary

| Type | Usage in Codebase |
|------|-------------------|
| **Strings** | Primary - all Cache:: operations, counters |
| **Sets** | Package label tracking during bulk operations |
| **Sorted Sets** | Not currently used (could improve rate limiting) |
| **Hashes** | Not currently used |
| **Lists** | Horizon queues (automatic) |

---

## Memory Considerations

| Type | Memory Efficiency |
|------|-------------------|
| String (small) | ~90 bytes overhead |
| String (large) | Linear with content |
| Set (small) | Ziplist encoding (compact) |
| Set (large) | Hash table |
| Sorted Set | Skip list + hash table |
| Hash (small) | Ziplist encoding |
| Hash (large) | Hash table |

### Best Practices

1. Use appropriate types for access patterns
2. Keep keys short but descriptive
3. Set TTL on temporary data
4. Monitor memory with `Redis::info('memory')`
