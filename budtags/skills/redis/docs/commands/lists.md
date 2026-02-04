# Redis List Commands

Redis lists are linked lists of string values, optimized for head/tail operations. Ideal for queues, stacks, and capped collections.

---

## Core Push/Pop Commands

### LPUSH

Prepends elements to the head (left) of a list.

```
LPUSH key element [element ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - length of list after push |
| **Complexity** | O(1) for each element |
| **Creates** | Key if it doesn't exist |

```php
Redis::lpush('mylist', 'value1', 'value2');
```

---

### RPUSH

Appends elements to the tail (right) of a list.

```
RPUSH key element [element ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - length of list after push |
| **Complexity** | O(1) for each element |
| **Creates** | Key if it doesn't exist |

```php
Redis::rpush('mylist', 'value1', 'value2');
```

---

### LPOP

Removes and returns elements from the head (left).

```
LPOP key [count]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string (single) or array (multiple), nil if empty |
| **Complexity** | O(N) where N is number of elements returned |
| **Deletes** | Key if last element popped |

```php
$item = Redis::lpop('mylist');
$items = Redis::lpop('mylist', 5);  // Pop 5 elements
```

---

### RPOP

Removes and returns elements from the tail (right).

```
RPOP key [count]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string (single) or array (multiple), nil if empty |
| **Complexity** | O(N) where N is number of elements returned |
| **Deletes** | Key if last element popped |

---

### LPUSHX / RPUSHX

Push only if the list exists.

```
LPUSHX key element [element ...]
RPUSHX key element [element ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - length of list (0 if key doesn't exist) |
| **Complexity** | O(1) for each element |

---

## Range Commands

### LRANGE

Returns elements in the specified range.

```
LRANGE key start stop
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of elements |
| **Complexity** | O(S+N) where S is start offset, N is elements returned |

Negative indices: -1 = last element, -2 = second to last, etc.

```php
// Get all elements
$all = Redis::lrange('mylist', 0, -1);

// Get first 10
$first10 = Redis::lrange('mylist', 0, 9);

// Get last 5
$last5 = Redis::lrange('mylist', -5, -1);
```

---

### LINDEX

Returns element at specified index.

```
LINDEX key index
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string or nil if out of range |
| **Complexity** | O(N) where N is elements to traverse |

---

### LSET

Sets element at specified index.

```
LSET key index element
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(N) for head/tail, O(N) for middle |
| **Error** | If index out of range |

---

### LLEN

Returns the length of the list.

```
LLEN key
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - list length (0 if key doesn't exist) |
| **Complexity** | O(1) |

---

## Modification Commands

### LINSERT

Inserts element before or after a pivot element.

```
LINSERT key BEFORE|AFTER pivot element
```

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - list length, -1 if pivot not found, 0 if key doesn't exist |
| **Complexity** | O(N) where N is elements to traverse |

---

### LREM

Removes elements matching value.

```
LREM key count element
```

| Count | Behavior |
|-------|----------|
| > 0 | Remove first `count` matching from head |
| < 0 | Remove first `abs(count)` matching from tail |
| = 0 | Remove all matching elements |

| Aspect | Details |
|--------|---------|
| **Returns** | Integer - number removed |
| **Complexity** | O(N+M) where N is list length, M is matches |
| **Deletes** | Key if last element removed |

---

### LTRIM

Trims list to specified range (removes elements outside range).

```
LTRIM key start stop
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(N) where N is elements removed |
| **Deletes** | Key if all elements trimmed |

**Capped list pattern:**
```php
// Keep only last 100 items
Redis::lpush('logs', $logEntry);
Redis::ltrim('logs', 0, 99);
```

---

### LPOS

Returns index of matching elements (Redis 6.0.6+).

```
LPOS key element [RANK rank] [COUNT num-matches] [MAXLEN len]
```

| Option | Description |
|--------|-------------|
| `RANK rank` | Start from Nth match (negative = from tail) |
| `COUNT num` | Return up to N matches |
| `MAXLEN len` | Compare only first len elements |

| Aspect | Details |
|--------|---------|
| **Returns** | Integer (single) or array (COUNT > 1), nil if not found |
| **Complexity** | O(N) |

---

## Move Commands

### LMOVE

Atomically pops from one list and pushes to another.

```
LMOVE source destination LEFT|RIGHT LEFT|RIGHT
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string - the moved element |
| **Complexity** | O(1) |
| **Deletes** | Source key if last element moved |
| **Since** | Redis 6.2 |

```php
// Pop from right of source, push to left of destination
Redis::lmove('source', 'dest', 'RIGHT', 'LEFT');
```

---

### LMPOP

Pops elements from the first non-empty list (Redis 7.0+).

```
LMPOP numkeys key [key ...] LEFT|RIGHT [COUNT count]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array [key_name, [elements]] or nil |
| **Complexity** | O(N+M) where N is keys, M is elements |
| **Since** | Redis 7.0 |

---

## Blocking Commands

### BLPOP

Blocking left pop - waits for elements if list is empty.

```
BLPOP key [key ...] timeout
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array [key, element] or nil on timeout |
| **Complexity** | O(N) where N is number of keys |
| **Timeout** | 0 = wait indefinitely |
| **Deletes** | Key if last element popped |

**Queue consumer pattern:**
```php
// Wait up to 30 seconds for a job
[$key, $job] = Redis::blpop('job_queue', 30);
```

---

### BRPOP

Blocking right pop.

```
BRPOP key [key ...] timeout
```

Same behavior as BLPOP but pops from tail.

---

### BLMOVE

Blocking version of LMOVE.

```
BLMOVE source destination LEFT|RIGHT LEFT|RIGHT timeout
```

| Aspect | Details |
|--------|---------|
| **Returns** | Bulk string or nil on timeout |
| **Since** | Redis 6.2 |

---

### BLMPOP

Blocking version of LMPOP (Redis 7.0+).

```
BLMPOP timeout numkeys key [key ...] LEFT|RIGHT [COUNT count]
```

---

## Deprecated Commands

| Command | Replacement |
|---------|-------------|
| `RPOPLPUSH source dest` | `LMOVE source dest RIGHT LEFT` |
| `BRPOPLPUSH source dest timeout` | `BLMOVE source dest RIGHT LEFT timeout` |

---

## Use Cases

### Queue (FIFO)
```php
// Producer
Redis::rpush('queue', $job);

// Consumer
$job = Redis::lpop('queue');
// Or blocking:
[$key, $job] = Redis::blpop('queue', 30);
```

### Stack (LIFO)
```php
// Push
Redis::lpush('stack', $item);

// Pop
$item = Redis::lpop('stack');
```

### Capped Log/History
```php
// Add entry
Redis::lpush('logs', json_encode($entry));

// Keep last 1000 entries
Redis::ltrim('logs', 0, 999);

// Get recent entries
$recent = Redis::lrange('logs', 0, 49);
```

### Reliable Queue (with backup)
```php
// Consumer with backup list
$job = Redis::lmove('pending', 'processing', 'LEFT', 'RIGHT');

// Process job...

// On success, remove from processing
Redis::lrem('processing', 1, $job);

// On failure, move back to pending
Redis::lmove('processing', 'pending', 'LEFT', 'RIGHT');
```

---

## Performance Notes

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Push/Pop at ends | O(1) | Very fast |
| Access by index | O(N) | Linear scan |
| LRANGE full list | O(N) | Returns all elements |
| Insert/Remove middle | O(N) | Requires traversal |

**Best practices:**
- Use for head/tail access patterns only
- For random access, consider sorted sets or hashes
- Set max length with LTRIM to prevent unbounded growth
- Use blocking commands for efficient queue consumption
