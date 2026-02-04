# Redis String Commands

Strings are the most basic Redis data type, storing sequences of bytes including text, serialized objects, and binary data. Maximum size: 512 MB per value.

---

## Core Commands

### GET

Returns the string value of a key.

```
GET key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string reply, or nil if key doesn't exist |
| **Complexity** | O(1) |

```php
// Laravel
$value = Cache::get('mykey');
$value = Redis::get('mykey');
```

---

### SET

Sets the string value of a key, creating it if it doesn't exist.

```
SET key value [NX | XX] [GET] [EX seconds | PX milliseconds | EXAT timestamp | PXAT timestamp | KEEPTTL]
```

| Option | Description |
|--------|-------------|
| `NX` | Only set if key does NOT exist |
| `XX` | Only set if key DOES exist |
| `GET` | Return the old value (or nil) |
| `EX seconds` | Set expiration in seconds |
| `PX milliseconds` | Set expiration in milliseconds |
| `EXAT timestamp` | Set expiration at Unix timestamp (seconds) |
| `PXAT timestamp` | Set expiration at Unix timestamp (milliseconds) |
| `KEEPTTL` | Retain existing TTL |

| Aspect | Details |
|--------|---------|
| **Returns** | OK, nil (if NX/XX failed), or old value (if GET used) |
| **Complexity** | O(1) |

```php
// Laravel Cache (uses SET with EX)
Cache::put('mykey', 'value', 3600);  // 1 hour TTL
Cache::forever('mykey', 'value');     // No TTL

// Redis facade
Redis::set('mykey', 'value');
Redis::set('mykey', 'value', 'EX', 3600);
Redis::set('mykey', 'value', 'NX');  // Only if not exists
```

---

### APPEND

Appends a string to the value of a key. Creates key if it doesn't exist.

```
APPEND key value
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - length of string after append |
| **Complexity** | O(1) |

---

### GETRANGE

Returns a substring of the string stored at key.

```
GETRANGE key start end
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string - the substring |
| **Complexity** | O(N) where N is length of returned string |

Negative offsets count from the end (-1 = last character).

---

### SETRANGE

Overwrites part of a string at specified offset.

```
SETRANGE key offset value
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - length of string after modification |
| **Complexity** | O(1) (not counting copy cost for large strings) |

---

### STRLEN

Returns the length of the string value.

```
STRLEN key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - string length, or 0 if key doesn't exist |
| **Complexity** | O(1) |

---

## Atomic Counter Commands

### INCR

Increments the integer value by one. Uses 0 as initial value if key doesn't exist.

```
INCR key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - value after increment |
| **Complexity** | O(1) |
| **Error** | If value is not an integer or out of range |

```php
// BudTags pattern for progress tracking
$count = Redis::incr("label_group_success:{$id}");
```

---

### INCRBY

Increments by specified amount.

```
INCRBY key increment
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - value after increment |
| **Complexity** | O(1) |

```php
Redis::incrby('counter', 10);
```

---

### INCRBYFLOAT

Increments by floating-point amount.

```
INCRBYFLOAT key increment
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string - value after increment |
| **Complexity** | O(1) |

---

### DECR

Decrements the integer value by one.

```
DECR key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - value after decrement |
| **Complexity** | O(1) |

---

### DECRBY

Decrements by specified amount.

```
DECRBY key decrement
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - value after decrement |
| **Complexity** | O(1) |

---

## Multi-Key Commands

### MGET

Atomically returns values of multiple keys.

```
MGET key [key ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of values (nil for non-existent keys) |
| **Complexity** | O(N) where N is number of keys |

```php
$values = Redis::mget(['key1', 'key2', 'key3']);
```

---

### MSET

Atomically sets multiple key-value pairs.

```
MSET key value [key value ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK (always succeeds) |
| **Complexity** | O(N) where N is number of keys |

```php
Redis::mset(['key1' => 'val1', 'key2' => 'val2']);
```

---

### MSETNX

Sets multiple keys only if NONE of them exist.

```
MSETNX key value [key value ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | 1 if all keys set, 0 if any key existed |
| **Complexity** | O(N) |

Atomic: either all keys are set, or none.

---

## GET-and-Modify Commands

### GETEX

Returns value and optionally sets expiration.

```
GETEX key [EX seconds | PX milliseconds | EXAT timestamp | PXAT timestamp | PERSIST]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string or nil |
| **Complexity** | O(1) |
| **Since** | Redis 6.2 |

---

### GETDEL

Returns value and deletes the key.

```
GETDEL key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string or nil |
| **Complexity** | O(1) |
| **Since** | Redis 6.2 |

---

### GETSET (Deprecated)

Returns old value and sets new value. **Use `SET key value GET` instead.**

```
GETSET key value
```

---

## Deprecated Commands

| Command | Replacement |
|---------|-------------|
| `SETEX key seconds value` | `SET key value EX seconds` |
| `PSETEX key ms value` | `SET key value PX ms` |
| `SETNX key value` | `SET key value NX` |
| `GETSET key value` | `SET key value GET` |
| `SUBSTR key start end` | `GETRANGE key start end` |

---

## Laravel Integration

### Cache Facade (Recommended for most cases)

```php
// Basic operations
Cache::put('key', $data, $seconds);
Cache::forever('key', $data);
$value = Cache::get('key', $default);

// Remember pattern (BudTags standard)
$data = Cache::remember($key, $ttl, function() {
    return $this->fetchFromApi();
});

// Forget
Cache::forget('key');
```

### Redis Facade (For atomic operations)

```php
// Counters
Redis::incr('counter');
Redis::incrby('counter', 10);

// Direct SET with options
Redis::set('key', 'value', 'EX', 3600, 'NX');

// Multi-key
Redis::mget(['key1', 'key2']);
Redis::mset(['key1' => 'val1', 'key2' => 'val2']);
```

---

## Use Cases

| Use Case | Commands | BudTags Example |
|----------|----------|-----------------|
| **Caching** | GET, SET | API response caching |
| **Counters** | INCR, INCRBY | Progress tracking in jobs |
| **Rate Limiting** | INCR + EXPIRE | API throttling |
| **Distributed Locks** | SET NX EX | Cache::lock() |
| **Sessions** | GET, SET | Laravel session driver |
