# Redis Commands Quick Reference

Essential Redis commands used in BudTags, with Laravel syntax.

---

## String Commands

### GET / SET

```php
// Via Cache facade (recommended)
Cache::put($key, $value, $ttl);     // SET with TTL
Cache::forever($key, $value);        // SET without TTL
$value = Cache::get($key);           // GET
$value = Cache::get($key, $default); // GET with default

// Via Redis facade
Redis::set($key, $value);
Redis::get($key);
```

### INCR / DECR (Atomic)

```php
$new = Redis::incr($key);            // Increment by 1
$new = Redis::incrby($key, 5);       // Increment by N
$new = Redis::decr($key);            // Decrement by 1
$new = Redis::decrby($key, 5);       // Decrement by N
```

### EXPIRE / TTL

```php
Redis::expire($key, $seconds);       // Set expiration
Redis::expireat($key, $timestamp);   // Set expiration at timestamp
$ttl = Redis::ttl($key);             // Get remaining TTL (-1 = no expiry, -2 = doesn't exist)
```

---

## Key Commands

### EXISTS / DEL

```php
// Via Cache facade
$exists = Cache::has($key);
Cache::forget($key);

// Via Redis facade
$exists = Redis::exists($key);
Redis::del($key);
Redis::del($key1, $key2, $key3);     // Delete multiple
```

### KEYS (Pattern Search)

```php
// WARNING: O(N) - use sparingly in production
Redis::command('select', [1]);       // Select cache DB first!
$keys = Redis::command('keys', ['pattern*']);
$keys = Redis::command('keys', ['*substring*']);
$keys = Redis::command('keys', ['prefix:*:suffix']);
```

### SCAN (Safe Alternative to KEYS)

```php
// For production use when iterating large keyspaces
$cursor = 0;
do {
    [$cursor, $keys] = Redis::scan($cursor, ['MATCH' => 'pattern*', 'COUNT' => 100]);
    foreach ($keys as $key) {
        // Process key
    }
} while ($cursor != 0);
```

---

## Set Commands

### SADD / SMEMBERS

```php
// Add members
Redis::sadd($key, 'member1');
Redis::sadd($key, 'member1', 'member2', 'member3');
Redis::sadd($key, ...$array);

// Get all members
$members = Redis::smembers($key);
```

### SISMEMBER / SREM

```php
// Check membership
$exists = Redis::sismember($key, 'member');

// Remove member
Redis::srem($key, 'member');
Redis::srem($key, 'member1', 'member2');
```

### SCARD

```php
// Count members
$count = Redis::scard($key);
```

---

## Database Commands

### SELECT

```php
// Switch database (0=default, 1=cache, 2=queue)
Redis::command('select', [1]);
```

### DBSIZE

```php
// Count keys in current database
$count = Redis::command('dbsize');
```

### FLUSHDB / FLUSHALL

```php
// Clear current database
Redis::command('flushdb');

// Clear ALL databases (dangerous!)
Redis::command('flushall');

// Via Cache facade (clears cache DB only)
Cache::flush();
```

---

## Hash Commands

```php
// Set field
Redis::hset($key, 'field', 'value');

// Get field
$value = Redis::hget($key, 'field');

// Get all fields
$hash = Redis::hgetall($key);

// Set multiple fields
Redis::hmset($key, ['field1' => 'val1', 'field2' => 'val2']);

// Increment field
Redis::hincrby($key, 'counter', 1);
```

---

## Sorted Set Commands

```php
// Add with score
Redis::zadd($key, $score, $member);
Redis::zadd($key, $score1, $member1, $score2, $member2);

// Get by rank range
$members = Redis::zrange($key, 0, -1);              // All, ascending
$members = Redis::zrevrange($key, 0, 9);            // Top 10, descending

// Get with scores
$members = Redis::zrange($key, 0, -1, ['WITHSCORES' => true]);

// Remove by score range
Redis::zremrangebyscore($key, $min, $max);

// Count members
$count = Redis::zcard($key);
```

---

## List Commands

```php
// Push
Redis::lpush($key, $value);          // Left (head)
Redis::rpush($key, $value);          // Right (tail)

// Pop
$value = Redis::lpop($key);          // Left
$value = Redis::rpop($key);          // Right

// Range
$items = Redis::lrange($key, 0, -1); // All
$items = Redis::lrange($key, 0, 9);  // First 10

// Length
$length = Redis::llen($key);
```

---

## Transaction Commands

```php
// Multi/Exec (atomic block)
Redis::multi();
Redis::incr('counter1');
Redis::incr('counter2');
$results = Redis::exec();

// Pipeline (batch without atomicity)
$results = Redis::pipeline(function ($pipe) {
    $pipe->incr('counter1');
    $pipe->incr('counter2');
});
```

---

## Info Commands

```php
// Server info
$info = Redis::info();
$memory = Redis::info('memory');
$stats = Redis::info('stats');

// Specific metrics
$usedMemory = $info['used_memory_human'];
$connectedClients = $info['connected_clients'];
```

---

## Command Patterns in BudTags

| Operation | Command | Example |
|-----------|---------|---------|
| Cache value | `Cache::put` | `Cache::put($key, $data, 3600)` |
| Cache forever | `Cache::forever` | `Cache::forever($key, $data)` |
| Get cached | `Cache::get` | `Cache::get($key, [])` |
| Remember pattern | `Cache::remember` | `Cache::remember($key, 3600, fn() => ...)` |
| Invalidate | `Cache::forget` | `Cache::forget($key)` |
| Atomic counter | `Redis::incr` | `Redis::incr($key)` |
| Set expiration | `Redis::expire` | `Redis::expire($key, 3600)` |
| Track unique | `Redis::sadd` | `Redis::sadd($key, ...$items)` |
| Get unique | `Redis::smembers` | `Redis::smembers($key)` |
| Pattern search | `Redis::command` | `Redis::command('keys', ['*pattern*'])` |
| Select DB | `Redis::command` | `Redis::command('select', [1])` |
| DB size | `Redis::command` | `Redis::command('dbsize')` |
