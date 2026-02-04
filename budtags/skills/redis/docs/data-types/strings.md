# Redis Strings - Deep Dive

Strings are the most fundamental Redis data type, capable of storing any sequence of bytes up to 512 MB.

---

## Internal Representation

### Encodings

| Encoding | Condition | Memory Overhead |
|----------|-----------|-----------------|
| `int` | Integer that fits in long | 8 bytes |
| `embstr` | String ≤ 44 bytes | Single allocation |
| `raw` | String > 44 bytes | Two allocations |

```php
// Check encoding
Redis::object('ENCODING', 'mykey');
// Returns: "int", "embstr", or "raw"
```

### Why 44 Bytes?

Redis object header is 16 bytes (64-bit). SDS (Simple Dynamic String) header is 3 bytes. With 64-byte aligned allocation: 64 - 16 - 3 - 1 (null terminator) = 44 bytes.

---

## Memory Analysis

### Per-Key Overhead

Each key has overhead beyond the value:

| Component | Bytes |
|-----------|-------|
| Key name | Variable |
| Redis object | 16 |
| Dict entry | 24 |
| SDS header | 3-9 |

**Minimum overhead per string key: ~50 bytes**

### Example Calculations

| Scenario | Value Size | Total Memory |
|----------|------------|--------------|
| Counter (int) | 8 bytes | ~60 bytes |
| Short string | 20 bytes | ~70 bytes |
| Medium string | 100 bytes | ~160 bytes |
| 1KB JSON | 1024 bytes | ~1100 bytes |

---

## Use Cases

### 1. Caching Serialized Data

```php
// Cache API response
$data = $api->fetchPackages();
Cache::put('metrc:packages:AU-P-123', serialize($data), 3600);

// Or with JSON (smaller for simple data)
Cache::put('metrc:packages:AU-P-123', json_encode($data), 3600);
```

**Optimization:** Consider compression for large values:
```php
$compressed = gzcompress(json_encode($data), 6);
Redis::set('key', $compressed);

// Retrieve
$data = json_decode(gzuncompress(Redis::get('key')));
```

### 2. Atomic Counters

```php
// Progress tracking in jobs
$total = count($packages);
foreach ($packages as $package) {
    process($package);
    $current = Redis::incr("job:{$jobId}:progress");
    $percent = ($current / $total) * 100;
}
```

**Thread-safe:** INCR is atomic, no race conditions.

### 3. Distributed Locks

```php
// SET with NX and EX is atomic
$acquired = Redis::set(
    "lock:resource",
    $lockValue,
    'NX',           // Only if not exists
    'EX', 30        // 30 second timeout
);

if ($acquired) {
    try {
        // Critical section
    } finally {
        // Only release if we own it
        if (Redis::get("lock:resource") === $lockValue) {
            Redis::del("lock:resource");
        }
    }
}
```

### 4. Rate Limiting

```php
$key = "rate:{$userId}:" . floor(time() / 60);  // Per-minute bucket

$count = Redis::incr($key);
if ($count === 1) {
    Redis::expire($key, 60);
}

if ($count > $limit) {
    throw new RateLimitException();
}
```

### 5. Session Storage

```php
// Laravel uses strings for sessions
$sessionData = serialize(['user_id' => 123, 'csrf' => $token]);
Redis::setex("session:{$sessionId}", 7200, $sessionData);
```

---

## Performance Characteristics

### Command Complexities

| Command | Complexity | Notes |
|---------|------------|-------|
| GET, SET | O(1) | Constant time |
| MGET, MSET | O(N) | N = number of keys |
| INCR, DECR | O(1) | Atomic |
| APPEND | O(1) | Amortized |
| GETRANGE | O(N) | N = returned length |
| SETRANGE | O(1) | For small strings |
| STRLEN | O(1) | Cached length |

### Benchmark Guidelines

| Operation | Ops/sec (typical) |
|-----------|-------------------|
| SET (small) | 100,000+ |
| GET (small) | 150,000+ |
| INCR | 100,000+ |
| MSET (10 keys) | 30,000+ |

---

## Memory Optimization Strategies

### 1. Use Integer Encoding

```php
// This uses int encoding (8 bytes)
Redis::set('counter', 42);

// This uses embstr (larger)
Redis::set('counter', '42');  // String "42"
```

### 2. Combine Related Keys

Instead of:
```php
Redis::set("user:{$id}:name", $name);
Redis::set("user:{$id}:email", $email);
Redis::set("user:{$id}:role", $role);
// 3 keys × ~50 bytes overhead = 150 bytes overhead
```

Use hash:
```php
Redis::hmset("user:{$id}", compact('name', 'email', 'role'));
// 1 key × ~50 bytes overhead = 50 bytes overhead
```

### 3. Compress Large Values

```php
// For values > 1KB, compression often helps
if (strlen($value) > 1024) {
    $value = gzcompress($value, 6);
    Redis::set("compressed:{$key}", $value);
}
```

### 4. Use Binary Protocols

```php
// MessagePack is smaller than JSON
$packed = msgpack_pack($data);
Redis::set($key, $packed);

$data = msgpack_unpack(Redis::get($key));
```

---

## BudTags String Patterns

### API Response Cache

```php
// Current pattern in MetrcApi
$cache_key = "metrc:day-of-packages:{$facility}:{$date}";
$data = Cache::remember($cache_key, null, function() {
    return $this->fetchFromApi();
});
```

### Atomic Progress Counters

```php
// Pattern from SyncLabelsJob
$success_key = "label_group_success:{$id}";
$fail_key = "label_group_fail:{$id}";

foreach ($labels as $label) {
    if ($this->processLabel($label)) {
        Redis::incr($success_key);
    } else {
        Redis::incr($fail_key);
    }
}

Redis::expire($success_key, 3600);
Redis::expire($fail_key, 3600);
```

---

## Anti-Patterns

### 1. Storing Large Objects as Single Keys

```php
// ❌ Bad: 10MB JSON blob
Redis::set('all_packages', json_encode($allPackages));

// ✅ Better: Partition by ID
foreach ($packages as $package) {
    Redis::set("package:{$package['label']}", json_encode($package));
}
```

### 2. Not Setting Expiration

```php
// ❌ Bad: Memory leak
Redis::set('temp_data', $data);

// ✅ Good: Always expire temporary data
Redis::setex('temp_data', 3600, $data);
```

### 3. Polling Instead of Expiration

```php
// ❌ Bad: Checking timestamp manually
if (Redis::get('data_timestamp') < time() - 3600) {
    Redis::del('data');
}

// ✅ Good: Let Redis handle expiration
Redis::setex('data', 3600, $value);
```

---

## Key Takeaways

1. **Strings are versatile** - Cache, counters, locks, sessions
2. **Integer encoding is efficient** - Store numbers as integers
3. **INCR is atomic** - Safe for concurrent counters
4. **SET NX EX is atomic** - Use for distributed locks
5. **Consider hashes** - For related fields, less overhead
6. **Always set TTL** - For temporary data
7. **Compress large values** - Saves memory and bandwidth
