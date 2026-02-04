# Redis Hash Commands

Redis hashes are maps of field-value pairs, ideal for representing objects and grouping related data. They're more memory-efficient than storing each field as a separate key.

---

## Core Commands

### HSET

Sets field values in a hash.

```
HSET key field value [field value ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of fields added (not updated) |
| **Complexity** | O(1) for each field |
| **Creates** | Key if it doesn't exist |

```php
// Set single field
Redis::hset('user:1', 'name', 'John');

// Set multiple fields
Redis::hset('user:1', 'name', 'John', 'email', 'john@example.com', 'age', '30');

// Or with array
Redis::hmset('user:1', ['name' => 'John', 'email' => 'john@example.com']);
```

---

### HGET

Returns the value of a field.

```
HGET key field
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string or nil |
| **Complexity** | O(1) |

```php
$name = Redis::hget('user:1', 'name');
```

---

### HMGET

Returns values of multiple fields.

```
HMGET key field [field ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of values (nil for missing fields) |
| **Complexity** | O(N) where N is fields requested |

```php
$values = Redis::hmget('user:1', 'name', 'email', 'age');
// Returns: ['John', 'john@example.com', '30']
```

---

### HGETALL

Returns all fields and values.

```
HGETALL key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of field-value pairs |
| **Complexity** | O(N) where N is hash size |

```php
$user = Redis::hgetall('user:1');
// Returns: ['name' => 'John', 'email' => 'john@example.com', ...]
```

**Warning:** Avoid on large hashes. Use HSCAN instead.

---

### HDEL

Deletes fields from a hash.

```
HDEL key field [field ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of fields removed |
| **Complexity** | O(N) where N is fields deleted |
| **Deletes** | Key if last field removed |

```php
Redis::hdel('user:1', 'temporary_field');
```

---

### HEXISTS

Tests if a field exists.

```
HEXISTS key field
```

| Aspect | Details |
|--------|---------|
| **Returns** | 1 if exists, 0 if not |
| **Complexity** | O(1) |

---

### HLEN

Returns the number of fields.

```
HLEN key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number of fields |
| **Complexity** | O(1) |

---

### HKEYS

Returns all field names.

```
HKEYS key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of field names |
| **Complexity** | O(N) |

---

### HVALS

Returns all values.

```
HVALS key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of values |
| **Complexity** | O(N) |

---

## Atomic Counter Commands

### HINCRBY

Increments an integer field value.

```
HINCRBY key field increment
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - new value |
| **Complexity** | O(1) |
| **Creates** | Field with value=increment if doesn't exist |

```php
// Track statistics
Redis::hincrby('stats:2024-01', 'page_views', 1);
Redis::hincrby('stats:2024-01', 'api_calls', 1);
Redis::hincrby('stats:2024-01', 'errors', 1);

// Get all stats
$stats = Redis::hgetall('stats:2024-01');
```

---

### HINCRBYFLOAT

Increments a floating-point field value.

```
HINCRBYFLOAT key field increment
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string - new value |
| **Complexity** | O(1) |

---

## Conditional Commands

### HSETNX

Sets a field only if it doesn't exist.

```
HSETNX key field value
```

| Aspect | Details |
|--------|---------|
| **Returns** | 1 if set, 0 if field existed |
| **Complexity** | O(1) |

---

## String Length

### HSTRLEN

Returns the length of a field's value.

```
HSTRLEN key field
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - string length (0 if missing) |
| **Complexity** | O(1) |

---

## Random Access

### HRANDFIELD

Returns random fields (Redis 6.2+).

```
HRANDFIELD key [count [WITHVALUES]]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Single field or array |
| **Complexity** | O(N) where N is count |

---

## Field Expiration (Redis 7.4+)

### HEXPIRE

Sets TTL on individual hash fields.

```
HEXPIRE key seconds field [field ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of results per field |
| **Since** | Redis 7.4 |

---

### HPEXPIRE

Sets TTL in milliseconds.

```
HPEXPIRE key milliseconds field [field ...]
```

---

### HEXPIREAT

Sets expiration at Unix timestamp (seconds).

```
HEXPIREAT key unix-time-seconds field [field ...]
```

---

### HPEXPIREAT

Sets expiration at Unix timestamp (milliseconds).

```
HPEXPIREAT key unix-time-milliseconds field [field ...]
```

---

### HTTL

Returns remaining TTL of a field in seconds.

```
HTTL key field
```

---

### HPTTL

Returns remaining TTL in milliseconds.

```
HPTTL key field
```

---

### HEXPIRETIME

Returns absolute expiration time (Unix seconds).

```
HEXPIRETIME key field [field ...]
```

---

### HPEXPIRETIME

Returns absolute expiration time (Unix milliseconds).

```
HPEXPIRETIME key field [field ...]
```

---

### HPERSIST

Removes expiration from fields.

```
HPERSIST key field [field ...]
```

---

## GET-and-Modify Commands (Redis 7.4+)

### HGETDEL

Gets value and deletes field atomically.

```
HGETDEL key field
```

---

### HGETEX

Gets value and optionally sets expiration.

```
HGETEX key field [field ...] [EX|PX|EXAT|PXAT seconds|milliseconds]
```

---

### HSETEX

Sets value with expiration.

```
HSETEX key [EX|PX|EXAT|PXAT ...] field value [field value ...]
```

---

## Iteration

### HSCAN

Iterates over hash fields safely.

```
HSCAN key cursor [MATCH pattern] [COUNT count]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array [cursor, [field, value, ...]] |
| **Complexity** | O(1) per call |

```php
$cursor = 0;
$fields = [];
do {
    [$cursor, $batch] = Redis::hscan('large_hash', $cursor, 'COUNT', 100);
    $fields = array_merge($fields, $batch);
} while ($cursor != 0);
```

---

## Deprecated Commands

| Deprecated | Replacement |
|------------|-------------|
| `HMSET key field value [...]` | `HSET key field value [...]` |

---

## Use Cases

### Object Storage

```php
// Store user object
Redis::hset('user:1',
    'name', 'John Doe',
    'email', 'john@example.com',
    'role', 'admin',
    'created_at', now()->toIso8601String()
);

// Retrieve full object
$user = Redis::hgetall('user:1');

// Retrieve specific fields
$info = Redis::hmget('user:1', 'name', 'email');

// Update single field
Redis::hset('user:1', 'last_login', now()->toIso8601String());
```

### Counter Grouping

```php
// Group related counters
$key = "metrics:page:{$pageId}";

Redis::hincrby($key, 'views', 1);
Redis::hincrby($key, 'unique_visitors', 1);
Redis::hincrby($key, 'shares', 1);

// Get all metrics at once
$metrics = Redis::hgetall($key);
```

### Configuration Storage

```php
// Store feature flags
Redis::hset('config:features',
    'dark_mode', 'enabled',
    'beta_features', 'disabled',
    'max_upload_size', '10485760'
);

// Check single flag
$darkMode = Redis::hget('config:features', 'dark_mode');

// Get all flags
$features = Redis::hgetall('config:features');
```

### Session Data

```php
// Store session data
$sessionKey = "session:{$sessionId}";
Redis::hset($sessionKey,
    'user_id', $userId,
    'ip', $request->ip(),
    'user_agent', $request->userAgent(),
    'last_activity', time()
);

// Set session expiry on the whole hash
Redis::expire($sessionKey, 3600);
```

### Memory-Efficient Key-Value (Hash Trick)

Store many small objects efficiently by grouping into hashes:

```php
// Instead of: SET object:1234 value
// Use: HSET object:12 34 value

function getHashKeyField($key) {
    preg_match('/^(.+):(\d+)$/', $key, $matches);
    $id = $matches[2];
    return [
        'hash' => $matches[1] . ':' . substr($id, 0, -2),
        'field' => substr($id, -2) ?: '00'
    ];
}

// Store
$hkf = getHashKeyField('object:1234');
Redis::hset($hkf['hash'], $hkf['field'], $value);

// Retrieve
$value = Redis::hget($hkf['hash'], $hkf['field']);
```

This can reduce memory by 5-10x for millions of small objects.

---

## Performance Characteristics

| Command | Complexity | Notes |
|---------|------------|-------|
| HSET, HGET | O(1) | Single field operations |
| HMGET, HMSET | O(N) | N = number of fields |
| HGETALL | O(N) | Returns all - careful with large hashes |
| HINCRBY | O(1) | Atomic counter updates |
| HSCAN | O(1) per call | Safe for large hashes |

**Memory Efficiency:**
- Small hashes (≤512 entries, ≤64 byte values) use ziplist/listpack encoding
- Significantly more memory-efficient than separate keys
- Configure limits with `hash-max-listpack-entries` and `hash-max-listpack-value`

**Best Practices:**
- Use hashes for related data instead of separate keys
- Use HMGET to batch field retrieval
- Use HINCRBY for atomic counters
- Avoid HGETALL on large hashes
- Consider hash grouping trick for millions of small objects
