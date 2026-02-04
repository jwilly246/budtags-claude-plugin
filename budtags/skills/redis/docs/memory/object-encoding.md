# Redis Object Encoding

Redis uses different internal encodings to optimize memory based on data characteristics.

---

## Check Encoding

```php
$encoding = Redis::object('ENCODING', 'mykey');
// Returns: "embstr", "int", "listpack", "hashtable", etc.
```

---

## String Encodings

### int

Small integers stored as native integers:

```php
Redis::set('counter', 42);
Redis::object('ENCODING', 'counter'); // "int"

// Range: LONG_MIN to LONG_MAX
// Memory: 8 bytes (64-bit)
```

### embstr

Short strings (≤44 bytes) stored in a single allocation:

```php
Redis::set('short', 'hello world');
Redis::object('ENCODING', 'short'); // "embstr"

// Threshold: 44 bytes
// Memory: Single contiguous block
// Advantage: Better cache performance
```

### raw

Longer strings in separate allocation:

```php
Redis::set('long', str_repeat('x', 100));
Redis::object('ENCODING', 'long'); // "raw"

// Threshold: > 44 bytes
// Memory: SDS string header + data
```

### Memory Comparison

| Value | Encoding | Memory |
|-------|----------|--------|
| `42` | int | 8 bytes |
| `"hello"` | embstr | ~50 bytes |
| `str_repeat('x', 100)` | raw | ~130 bytes |

---

## Hash Encodings

### listpack

Memory-efficient for small hashes:

```php
Redis::hset('small:hash', 'field1', 'value1', 'field2', 'value2');
Redis::object('ENCODING', 'small:hash'); // "listpack"
```

Configuration:
```
hash-max-listpack-entries 512    # Max fields
hash-max-listpack-value 64       # Max field/value length
```

### hashtable

For larger hashes:

```php
// Exceeds entry limit
for ($i = 0; $i < 600; $i++) {
    Redis::hset('large:hash', "field{$i}", "value{$i}");
}
Redis::object('ENCODING', 'large:hash'); // "hashtable"

// OR exceeds value length
Redis::hset('long:value:hash', 'field', str_repeat('x', 100));
Redis::object('ENCODING', 'long:value:hash'); // "hashtable"
```

### Memory Comparison (100 fields)

| Encoding | Memory |
|----------|--------|
| listpack | ~2-3 KB |
| hashtable | ~8-10 KB |

**Savings:** 3-4x with listpack

---

## List Encodings

### listpack / quicklist

Redis 7 uses quicklist (linked list of listpacks):

```php
Redis::rpush('mylist', 'item1', 'item2', 'item3');
Redis::object('ENCODING', 'mylist'); // "listpack" or "quicklist"
```

Configuration:
```
list-max-listpack-size -2    # -2 = 8KB per node (recommended)
list-compress-depth 0        # Compress middle nodes (0 = no compression)
```

Size options:
| Value | Meaning |
|-------|---------|
| -5 | 64 KB per node |
| -4 | 32 KB per node |
| -3 | 16 KB per node |
| -2 | 8 KB per node (default) |
| -1 | 4 KB per node |
| Positive | Exact number of elements per node |

### Compression Depth

```
list-compress-depth 1    # Compress all but head and tail
list-compress-depth 2    # Compress all but head/tail and their neighbors
```

---

## Set Encodings

### intset

For sets containing only integers:

```php
Redis::sadd('int:set', 1, 2, 3, 4, 5);
Redis::object('ENCODING', 'int:set'); // "intset"
```

Configuration:
```
set-max-intset-entries 512    # Max entries for intset
```

### listpack

For small sets with non-integer values (Redis 7.2+):

```php
Redis::sadd('small:set', 'a', 'b', 'c');
Redis::object('ENCODING', 'small:set'); // "listpack"
```

Configuration:
```
set-max-listpack-entries 128
set-max-listpack-value 64
```

### hashtable

For larger sets:

```php
for ($i = 0; $i < 600; $i++) {
    Redis::sadd('large:set', "member{$i}");
}
Redis::object('ENCODING', 'large:set'); // "hashtable"
```

### Memory Comparison (100 elements)

| Content | Encoding | Memory |
|---------|----------|--------|
| Integers only | intset | ~400 bytes |
| Short strings | listpack | ~1-2 KB |
| Long strings | hashtable | ~8-10 KB |

---

## Sorted Set Encodings

### listpack

For small sorted sets:

```php
Redis::zadd('small:zset', 1, 'a', 2, 'b', 3, 'c');
Redis::object('ENCODING', 'small:zset'); // "listpack"
```

Configuration:
```
zset-max-listpack-entries 128
zset-max-listpack-value 64
```

### skiplist

For larger sorted sets:

```php
for ($i = 0; $i < 200; $i++) {
    Redis::zadd('large:zset', $i, "member{$i}");
}
Redis::object('ENCODING', 'large:zset'); // "skiplist"
```

### Memory Comparison (100 elements)

| Encoding | Memory |
|----------|--------|
| listpack | ~3-4 KB |
| skiplist | ~10-15 KB |

---

## Stream Encodings

### listpack

Streams always use radix tree with listpack nodes:

```php
Redis::xadd('mystream', '*', 'field', 'value');
Redis::object('ENCODING', 'mystream'); // Returns stream-specific encoding
```

Configuration:
```
stream-node-max-bytes 4096     # Max bytes per node
stream-node-max-entries 100    # Max entries per node
```

---

## Encoding Optimization Strategies

### 1. Stay Under Thresholds

```php
// ❌ Bad: Large hash that exceeds threshold
$data = [];
for ($i = 0; $i < 1000; $i++) {
    $data["field{$i}"] = "value{$i}";
}
Redis::hmset('large:hash', $data);
// Encoding: hashtable

// ✅ Better: Split into multiple hashes
$chunkSize = 400;
foreach (array_chunk($data, $chunkSize, true) as $i => $chunk) {
    Redis::hmset("hash:chunk:{$i}", $chunk);
}
// Encoding: listpack for each
```

### 2. Use Integers When Possible

```php
// ❌ Bad: String IDs
Redis::sadd('user:ids', 'user_123', 'user_456', 'user_789');
// Encoding: listpack/hashtable

// ✅ Better: Integer IDs
Redis::sadd('user:ids', 123, 456, 789);
// Encoding: intset (much smaller)
```

### 3. Shorten Values

```php
// ❌ Bad: Long JSON values
Redis::hset('config', 'setting', json_encode(['very' => 'long' => 'nested' => 'data']));
// May exceed listpack-value threshold

// ✅ Better: Compress or shorten
Redis::hset('config', 'setting', gzcompress(json_encode($data)));
```

---

## Checking Encoding Across Keys

```php
class EncodingAuditor
{
    public function audit(): array
    {
        $report = [];
        $cursor = 0;

        do {
            [$cursor, $keys] = Redis::scan($cursor, 'COUNT', 1000);

            foreach ($keys as $key) {
                $type = Redis::type($key);
                $encoding = Redis::object('ENCODING', $key);

                $typeKey = "{$type}:{$encoding}";

                if (!isset($report[$typeKey])) {
                    $report[$typeKey] = [
                        'count' => 0,
                        'total_bytes' => 0,
                        'examples' => [],
                    ];
                }

                $report[$typeKey]['count']++;
                $report[$typeKey]['total_bytes'] += Redis::memory('USAGE', $key) ?? 0;

                if (count($report[$typeKey]['examples']) < 3) {
                    $report[$typeKey]['examples'][] = $key;
                }
            }
        } while ($cursor != 0);

        // Flag potential optimizations
        foreach ($report as $typeKey => $data) {
            if (str_contains($typeKey, 'hashtable') && $data['count'] > 100) {
                $report[$typeKey]['suggestion'] = 'Consider splitting into smaller hashes';
            }
            if (str_contains($typeKey, 'raw') && $data['count'] > 1000) {
                $report[$typeKey]['suggestion'] = 'Consider compression for large strings';
            }
        }

        return $report;
    }
}
```

---

## Encoding Quick Reference

| Type | Compact Encoding | Threshold | Full Encoding |
|------|-----------------|-----------|---------------|
| String | int/embstr | 44 bytes | raw |
| Hash | listpack | 512 entries, 64 byte values | hashtable |
| List | listpack | 8KB per node | quicklist |
| Set (ints) | intset | 512 entries | hashtable |
| Set (strings) | listpack | 128 entries, 64 byte values | hashtable |
| Sorted Set | listpack | 128 entries, 64 byte values | skiplist |

---

## Key Takeaways

1. **Compact encodings save 2-5x memory** - Stay under thresholds
2. **intset is most efficient** - Use integers for set members
3. **listpack beats hashtable** - Keep hashes/sets small
4. **embstr is single allocation** - Keep strings ≤44 bytes
5. **Check with OBJECT ENCODING** - Verify your assumptions
6. **Split large collections** - Multiple listpacks > one hashtable
7. **Compress large values** - Stay under listpack-value threshold
8. **Tune thresholds carefully** - Higher = more CPU, lower = more memory
