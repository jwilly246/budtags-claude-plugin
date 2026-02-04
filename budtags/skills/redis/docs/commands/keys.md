# Redis Key Commands

Key commands manage the key namespace: existence checks, expiration, type inspection, iteration, and database operations.

---

## Existence & Type

### EXISTS

Checks if keys exist.

```
EXISTS key [key ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - count of existing keys |
| **Complexity** | O(N) where N is keys checked |

```php
// Single key
$exists = Redis::exists('mykey');  // 0 or 1

// Multiple keys
$count = Redis::exists('key1', 'key2', 'key3');  // 0-3
```

---

### TYPE

Returns the type of value at a key.

```
TYPE key
```

| Aspect | Details |
|--------|---------|
| **Returns** | String: none, string, list, set, zset, hash, stream |
| **Complexity** | O(1) |

```php
$type = Redis::type('mykey');  // "string", "hash", etc.
```

---

## Deletion

### DEL

Synchronously deletes keys.

```
DEL key [key ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of keys deleted |
| **Complexity** | O(N) for strings, O(M) for collections where M is elements |

```php
// BudTags pattern: batch delete
Redis::del($key1, $key2, $key3);
Redis::del(...$keys);
```

---

### UNLINK

Asynchronously deletes keys (non-blocking).

```
UNLINK key [key ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of keys unlinked |
| **Complexity** | O(1) for each key, actual reclaim happens in background |

Preferred for large collections to avoid blocking.

```php
// Better for large keys
Redis::unlink('large_hash', 'big_list');
```

---

## Expiration

### EXPIRE

Sets key expiration in seconds.

```
EXPIRE key seconds [NX|XX|GT|LT]
```

| Option | Description |
|--------|-------------|
| `NX` | Only set if key has no expiration |
| `XX` | Only set if key has existing expiration |
| `GT` | Only set if new expiry > current expiry |
| `LT` | Only set if new expiry < current expiry |

| Aspect | Details |
|--------|---------|
| **Returns** | 1 if set, 0 if key doesn't exist or condition not met |
| **Complexity** | O(1) |

```php
Redis::expire('session:abc', 3600);  // 1 hour
```

---

### PEXPIRE

Sets expiration in milliseconds.

```
PEXPIRE key milliseconds [NX|XX|GT|LT]
```

---

### EXPIREAT

Sets expiration at Unix timestamp (seconds).

```
EXPIREAT key unix-time-seconds [NX|XX|GT|LT]
```

```php
Redis::expireat('cache:data', strtotime('+1 day'));
```

---

### PEXPIREAT

Sets expiration at Unix timestamp (milliseconds).

```
PEXPIREAT key unix-time-milliseconds [NX|XX|GT|LT]
```

---

### TTL

Returns remaining time to live in seconds.

```
TTL key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer: TTL, -1 (no expiration), -2 (key doesn't exist) |
| **Complexity** | O(1) |

```php
$ttl = Redis::ttl('mykey');
if ($ttl == -2) {
    // Key doesn't exist
} elseif ($ttl == -1) {
    // No expiration set
} else {
    // Expires in $ttl seconds
}
```

---

### PTTL

Returns remaining TTL in milliseconds.

```
PTTL key
```

---

### EXPIRETIME

Returns absolute expiration time (Unix timestamp, seconds).

```
EXPIRETIME key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Unix timestamp, -1 (no expiration), -2 (doesn't exist) |
| **Since** | Redis 7.0 |

---

### PEXPIRETIME

Returns absolute expiration time (Unix timestamp, milliseconds).

```
PEXPIRETIME key
```

---

### PERSIST

Removes expiration from a key.

```
PERSIST key
```

| Aspect | Details |
|--------|---------|
| **Returns** | 1 if timeout removed, 0 if key doesn't exist or has no timeout |
| **Complexity** | O(1) |

---

## Key Search

### KEYS

Returns keys matching a pattern.

```
KEYS pattern
```

| Pattern | Matches |
|---------|---------|
| `*` | All keys |
| `h?llo` | hello, hallo, hxllo |
| `h*llo` | hllo, heeeello |
| `h[ae]llo` | hello, hallo |
| `h[^e]llo` | hallo, hbllo (not hello) |
| `h[a-b]llo` | hallo, hbllo |

| Aspect | Details |
|--------|---------|
| **Returns** | Array of matching keys |
| **Complexity** | O(N) where N is total keys in database |

**Warning:** Blocks Redis. Never use in production on large databases.

```php
// BudTags pattern: DevController cache clearing
Redis::command('select', [1]);  // Select cache DB
$keys = Redis::command('keys', ['*day-of-packages*']);
```

---

### SCAN

Iterates over keys safely.

```
SCAN cursor [MATCH pattern] [COUNT count] [TYPE type]
```

| Option | Description |
|--------|-------------|
| `cursor` | Start with 0, use returned cursor for next call |
| `MATCH` | Pattern filter |
| `COUNT` | Hint for keys per iteration (default 10) |
| `TYPE` | Filter by value type (Redis 6.0+) |

| Aspect | Details |
|--------|---------|
| **Returns** | Array [next_cursor, [keys]] |
| **Complexity** | O(1) per call, O(N) for full iteration |

```php
// Safe iteration
$cursor = 0;
$allKeys = [];
do {
    [$cursor, $keys] = Redis::scan($cursor, 'MATCH', 'user:*', 'COUNT', 100);
    $allKeys = array_merge($allKeys, $keys);
} while ($cursor != 0);

// Filter by type
[$cursor, $keys] = Redis::scan(0, 'TYPE', 'hash', 'COUNT', 100);
```

---

### RANDOMKEY

Returns a random key.

```
RANDOMKEY
```

| Aspect | Details |
|--------|---------|
| **Returns** | Key name or nil if database is empty |
| **Complexity** | O(1) |

---

## Key Manipulation

### RENAME

Renames a key.

```
RENAME key newkey
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(1) |
| **Note** | Overwrites newkey if exists |

---

### RENAMENX

Renames only if newkey doesn't exist.

```
RENAMENX key newkey
```

| Aspect | Details |
|--------|---------|
| **Returns** | 1 if renamed, 0 if newkey exists |
| **Complexity** | O(1) |

---

### COPY

Copies value to another key.

```
COPY source destination [DB destination-db] [REPLACE]
```

| Aspect | Details |
|--------|---------|
| **Returns** | 1 if copied, 0 if destination exists (without REPLACE) |
| **Complexity** | O(N) where N is size of value |
| **Since** | Redis 6.2 |

---

### MOVE

Moves key to another database.

```
MOVE key db
```

| Aspect | Details |
|--------|---------|
| **Returns** | 1 if moved, 0 if key doesn't exist or exists in destination |
| **Complexity** | O(1) |

---

## Serialization

### DUMP

Serializes key value.

```
DUMP key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Serialized value or nil |
| **Complexity** | O(1) to access, O(N) to serialize |

---

### RESTORE

Deserializes and creates key.

```
RESTORE key ttl serialized-value [REPLACE] [ABSTTL] [IDLETIME seconds] [FREQ frequency]
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(1) to create, O(N) for large values |

Useful for migrating keys between Redis instances.

---

## Database Commands

### SELECT

Switches to a different database.

```
SELECT index
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(1) |

```php
// BudTags: Switch to cache DB before key operations
Redis::command('select', [1]);  // DB 1 = cache
$keys = Redis::command('keys', ['pattern*']);
```

---

### DBSIZE

Returns number of keys in current database.

```
DBSIZE
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - key count |
| **Complexity** | O(1) |

```php
Redis::command('select', [1]);
$count = Redis::command('dbsize');
```

---

### FLUSHDB

Removes all keys from current database.

```
FLUSHDB [ASYNC|SYNC]
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(N) |

**Warning:** Destructive operation!

---

### FLUSHALL

Removes all keys from all databases.

```
FLUSHALL [ASYNC|SYNC]
```

**Warning:** Very destructive!

---

### SWAPDB

Swaps two databases.

```
SWAPDB index1 index2
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(N) |

---

## Object Inspection

### OBJECT ENCODING

Returns internal encoding of value.

```
OBJECT ENCODING key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Encoding name or nil |
| **Complexity** | O(1) |

```php
Redis::object('ENCODING', 'mykey');
// "embstr", "int", "raw", "ziplist", "listpack", "hashtable", etc.
```

---

### OBJECT REFCOUNT

Returns reference count.

```
OBJECT REFCOUNT key
```

---

### OBJECT IDLETIME

Returns seconds since last access.

```
OBJECT IDLETIME key
```

---

### OBJECT FREQ

Returns LFU frequency counter.

```
OBJECT FREQ key
```

---

## Memory Analysis

### MEMORY USAGE

Estimates memory used by a key.

```
MEMORY USAGE key [SAMPLES count]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - bytes, or nil |
| **Complexity** | O(N) where N is samples |

```php
$bytes = Redis::memory('USAGE', 'mykey');
```

---

### TOUCH

Updates last access time.

```
TOUCH key [key ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of existing keys touched |
| **Complexity** | O(N) |

---

## BudTags Patterns

### Pattern-Based Cache Clearing

```php
// DevController approach
public function clear_cache($pattern)
{
    Redis::command('select', [1]);  // Cache DB
    $keys = Redis::command('keys', ["*{$pattern}*"]);

    $deleted = 0;
    foreach (array_chunk($keys, 1000) as $chunk) {
        $deleted += Redis::del(...$chunk);
    }

    return $deleted;
}
```

### Safe Iteration for Large Key Sets

```php
public function iterate_keys($pattern, callable $callback)
{
    Redis::command('select', [1]);
    $cursor = 0;

    do {
        [$cursor, $keys] = Redis::scan($cursor, 'MATCH', $pattern, 'COUNT', 100);
        foreach ($keys as $key) {
            $callback($key);
        }
    } while ($cursor != 0);
}
```

### Key Existence with Fallback

```php
public function get_or_create($key, $ttl, callable $generator)
{
    if (Redis::exists($key)) {
        return Redis::get($key);
    }

    $value = $generator();
    Redis::setex($key, $ttl, $value);
    return $value;
}
```

---

## Performance Notes

| Command | Complexity | Production Safe |
|---------|------------|-----------------|
| EXISTS | O(N) | Yes |
| DEL | O(N) | Yes (small keys) |
| UNLINK | O(1) | Yes (background) |
| KEYS | O(N) | **No** |
| SCAN | O(1) per call | Yes |
| TYPE | O(1) | Yes |
| TTL/PTTL | O(1) | Yes |
| EXPIRE | O(1) | Yes |

**Best Practices:**
- Never use KEYS in production - use SCAN
- Use UNLINK for large collections
- Set appropriate TTLs to manage memory
- Use SELECT carefully - databases are independent
- Monitor key counts with DBSIZE
