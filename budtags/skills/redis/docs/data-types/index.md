# Redis Data Types - Selection Guide

This guide helps you choose the right Redis data type for your use case, with deep dives into each type's internals, performance characteristics, and memory efficiency.

---

## Quick Selection Matrix

| Use Case | Recommended Type | Why |
|----------|------------------|-----|
| Cache single values | **String** | Simple, fast, auto-expiring |
| Counters | **String** (INCR) | Atomic, O(1) |
| Store objects | **Hash** | Memory efficient, field access |
| Unique items | **Set** | Auto-dedup, O(1) membership |
| Ranked/scored data | **Sorted Set** | Auto-ordering, range queries |
| Message queue | **List** or **Stream** | FIFO, blocking operations |
| Event log | **Stream** | Persistence, consumer groups |
| Geolocation | **Geospatial** | Distance, radius queries |
| Unique counts | **HyperLogLog** | Fixed memory, approximate |
| Binary flags | **Bitmap** | 1 bit per flag |

---

## Data Type Files

| Type | File | Primary Use |
|------|------|-------------|
| Strings | [strings.md](./strings.md) | Caching, counters, serialized data |
| Lists | [lists.md](./lists.md) | Queues, stacks, capped logs |
| Sets | [sets.md](./sets.md) | Unique collections, tags |
| Sorted Sets | [sorted-sets.md](./sorted-sets.md) | Rankings, time series |
| Hashes | [hashes.md](./hashes.md) | Objects, grouped counters |
| Streams | [streams.md](./streams.md) | Event sourcing, messaging |
| Geospatial | [geospatial.md](./geospatial.md) | Location-based features |
| HyperLogLog | [hyperloglog.md](./hyperloglog.md) | Cardinality estimation |
| Bitmaps | [bitmaps-bitfields.md](./bitmaps-bitfields.md) | Flags, presence tracking |

---

## Internal Encodings

Redis uses different internal encodings based on data characteristics:

### String Encodings

| Encoding | Condition | Memory |
|----------|-----------|--------|
| `int` | Integer value ≤ 2^63 | 8 bytes |
| `embstr` | String ≤ 44 bytes | Object header + string |
| `raw` | String > 44 bytes | Separate allocation |

### List Encodings

| Encoding | Condition | Memory |
|----------|-----------|--------|
| `listpack` | Elements ≤ 512, each ≤ 64 bytes | Compact |
| `quicklist` | Exceeds limits | Linked list of listpacks |

### Set Encodings

| Encoding | Condition | Memory |
|----------|-----------|--------|
| `intset` | All integers, ≤ 512 elements | Very compact |
| `listpack` | Elements ≤ 128, each ≤ 64 bytes | Compact |
| `hashtable` | Exceeds limits | Full hash table |

### Sorted Set Encodings

| Encoding | Condition | Memory |
|----------|-----------|--------|
| `listpack` | Elements ≤ 128, each ≤ 64 bytes | Compact |
| `skiplist` | Exceeds limits | Skip list + hash table |

### Hash Encodings

| Encoding | Condition | Memory |
|----------|-----------|--------|
| `listpack` | Fields ≤ 512, values ≤ 64 bytes | Compact |
| `hashtable` | Exceeds limits | Full hash table |

---

## Memory Efficiency Comparison

For storing 1 million items:

| Data Type | Use Case | Approximate Memory |
|-----------|----------|-------------------|
| Strings (small) | Cache keys | ~100 MB |
| Hashes (grouped) | Objects | ~40-60 MB |
| Sets (integers) | IDs | ~56 MB |
| Sorted Sets | Rankings | ~80 MB |
| HyperLogLog | Unique count | 12 KB |
| Bitmaps | Flags | 125 KB |

---

## Complexity Comparison

| Operation | String | List | Set | Sorted Set | Hash |
|-----------|--------|------|-----|------------|------|
| Single add | O(1) | O(1) | O(1) | O(log N) | O(1) |
| Single get | O(1) | O(N) | O(1) | O(log N) | O(1) |
| Range get | N/A | O(S+N) | N/A | O(log N + M) | N/A |
| Count | O(1)* | O(1) | O(1) | O(1) | O(1) |
| Delete | O(1) | O(N) | O(1) | O(log N) | O(1) |

*STRLEN for strings

---

## BudTags Current Usage

| Type | Used In | Example |
|------|---------|---------|
| **String** | Cache facade | `Cache::forever('metrc:package:ABC', $data)` |
| **String** | Counters | `Redis::incr('label_group_success:42')` |
| **Set** | Label tracking | `Redis::sadd('metrc:package-labels:AU-P-123', ...)` |

### Potential Optimizations

1. **Hashes for Package Data**
   ```php
   // Instead of separate string keys:
   Cache::forever('metrc:package:ABC123', $fullData);

   // Consider hash for partial access:
   Redis::hmset('pkg:ABC123', [
       'label' => 'ABC123',
       'quantity' => 100,
       'strain' => 'Blue Dream'
   ]);
   // Then: Redis::hget('pkg:ABC123', 'quantity');
   ```

2. **Sorted Sets for Time-Based Data**
   ```php
   // For day-of queries, sorted set by timestamp:
   Redis::zadd('packages:AU-P-123', $timestamp, json_encode($package));
   Redis::zrangebyscore('packages:AU-P-123', $startTime, $endTime);
   ```

3. **HyperLogLog for Analytics**
   ```php
   // Track unique package accesses
   Redis::pfadd('unique:packages:2024-01', $packageLabel);
   $uniqueCount = Redis::pfcount('unique:packages:2024-01');
   ```

---

## Decision Flowchart

```
Need to store data?
│
├─ Single value? ──────────────────────► STRING
│   └─ Need atomic increment? ──────────► STRING (INCR)
│
├─ Multiple related fields? ────────────► HASH
│   └─ Need to access individual fields?
│
├─ Collection of unique items? ─────────► SET
│   └─ Need ordering?
│       └─ By score/time ───────────────► SORTED SET
│       └─ By insertion ────────────────► LIST
│
├─ Queue/Stack? ────────────────────────► LIST
│   └─ Need persistence + consumer groups? ► STREAM
│
├─ Just need unique count? ─────────────► HYPERLOGLOG
│
├─ Binary flags for many items? ────────► BITMAP
│
└─ Location-based queries? ─────────────► GEOSPATIAL (Sorted Set)
```

---

## Key Takeaways

1. **Strings are versatile** - Good default for caching
2. **Hashes save memory** - Use for objects with multiple fields
3. **Sets for uniqueness** - Automatic deduplication
4. **Sorted Sets for ranking** - Built-in ordering
5. **Streams for durability** - When messages must be processed
6. **HyperLogLog for cardinality** - When approximate is okay
7. **Check encoding** - Smaller data uses efficient encodings
