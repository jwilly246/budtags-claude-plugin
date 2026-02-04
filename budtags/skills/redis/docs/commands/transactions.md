# Redis Transaction Commands

Redis transactions execute a group of commands atomically. All commands in a transaction are serialized and executed sequentially - no other client can interrupt.

---

## Core Commands

### MULTI

Starts a transaction block.

```
MULTI
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(1) |

After MULTI, all commands are queued (not executed). Use EXEC to execute.

```php
Redis::multi();
Redis::set('key1', 'value1');
Redis::incr('counter');
Redis::lpush('list', 'item');
$results = Redis::exec();
// $results = ['OK', 1, 1]
```

---

### EXEC

Executes all queued commands.

```
EXEC
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of command results, or nil if WATCH failed |
| **Complexity** | Depends on queued commands |

Commands execute atomically - no other client can run commands in between.

---

### DISCARD

Cancels a transaction.

```
DISCARD
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(N) where N is queued commands |

Discards all queued commands and exits transaction mode.

```php
Redis::multi();
Redis::set('key1', 'value1');
Redis::discard();  // Nothing executed
```

---

### WATCH

Enables optimistic locking.

```
WATCH key [key ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(1) per key |

Monitors keys for changes. If any watched key is modified before EXEC, the transaction aborts (EXEC returns nil).

```php
// Optimistic locking pattern
Redis::watch('balance');

$balance = Redis::get('balance');
if ($balance < $amount) {
    Redis::unwatch();
    throw new InsufficientFundsException();
}

Redis::multi();
Redis::decrby('balance', $amount);
$result = Redis::exec();

if ($result === null) {
    // Another client modified balance - retry
}
```

---

### UNWATCH

Removes all watches.

```
UNWATCH
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(N) where N is watched keys |

Automatically called after EXEC or DISCARD.

---

## Laravel Pipeline (Alternative)

Laravel provides a pipeline method for batching commands without atomicity guarantees:

```php
// Pipeline: batch commands without atomicity
$results = Redis::pipeline(function ($pipe) {
    $pipe->set('key1', 'value1');
    $pipe->incr('counter');
    $pipe->get('key1');
});
// Sends all commands at once, receives all responses
```

**Pipeline vs Transaction:**

| Feature | Pipeline | Transaction (MULTI/EXEC) |
|---------|----------|--------------------------|
| Atomicity | No | Yes |
| Isolation | No | Yes |
| Performance | Fastest | Fast |
| Use Case | Batch operations | Atomic operations |

---

## Transaction Behavior

### Error Handling

**Command Queue Errors:**
If a command has syntax errors during queuing, EXEC will refuse to execute:

```php
Redis::multi();
Redis::set('key', 'value');
Redis::incr();  // Wrong number of arguments - error queued
$result = Redis::exec();  // Returns error, no commands executed
```

**Runtime Errors:**
If a command fails at execution time (wrong type, etc.), other commands still execute:

```php
Redis::multi();
Redis::set('key', 'string_value');
Redis::incr('key');  // Will fail - not an integer
Redis::set('key2', 'value2');  // Will still execute
$results = Redis::exec();
// ['OK', error, 'OK']
```

### No Rollback

Redis does NOT support rollback. If a command fails during EXEC, previously executed commands in the transaction are NOT undone.

---

## WATCH Pattern: Check-and-Set

```php
class AtomicBalance
{
    public function transfer(string $from, string $to, int $amount): bool
    {
        $maxRetries = 5;

        for ($i = 0; $i < $maxRetries; $i++) {
            // Watch source account
            Redis::watch($from);

            $balance = (int) Redis::get($from);

            if ($balance < $amount) {
                Redis::unwatch();
                throw new Exception('Insufficient funds');
            }

            // Attempt atomic transfer
            Redis::multi();
            Redis::decrby($from, $amount);
            Redis::incrby($to, $amount);
            $result = Redis::exec();

            if ($result !== null) {
                return true;  // Success
            }

            // Watched key was modified - retry
            usleep(random_int(1000, 10000));  // Small backoff
        }

        throw new Exception('Transfer failed after retries');
    }
}
```

---

## Common Patterns

### Atomic Counter with Conditional Update

```php
function incrementIfBelow(string $key, int $maxValue): ?int
{
    while (true) {
        Redis::watch($key);

        $current = (int) Redis::get($key) ?: 0;

        if ($current >= $maxValue) {
            Redis::unwatch();
            return null;  // Already at max
        }

        Redis::multi();
        Redis::incr($key);
        $result = Redis::exec();

        if ($result !== null) {
            return $current + 1;
        }
        // Retry if WATCH failed
    }
}
```

### Atomic List Transfer

```php
function moveListItem(string $source, string $dest): ?string
{
    Redis::watch($source);

    $item = Redis::lindex($source, 0);
    if ($item === null) {
        Redis::unwatch();
        return null;
    }

    Redis::multi();
    Redis::lpop($source);
    Redis::rpush($dest, $item);
    $result = Redis::exec();

    return $result !== null ? $item : null;
}
```

### Batch Operations with Transaction

```php
function updateUserProfile(string $userId, array $data): void
{
    $key = "user:{$userId}";

    Redis::multi();

    // Update profile fields
    Redis::hmset($key, $data);

    // Update timestamp
    Redis::hset($key, 'updated_at', now()->toIso8601String());

    // Update search index
    Redis::sadd('users:active', $userId);

    // Set expiration
    Redis::expire($key, 86400);

    Redis::exec();
}
```

---

## When to Use Transactions

**Use MULTI/EXEC when:**
- Multiple commands must execute atomically
- You need isolation from other clients
- Order of operations matters

**Use WATCH when:**
- You need optimistic locking
- Check-and-set operations
- Concurrent modifications possible

**Use Pipeline when:**
- Batching for performance
- Atomicity not required
- Independent operations

**Use Lua Scripts when:**
- Complex logic needed
- Multiple reads and writes
- Better than WATCH for complex cases

---

## Comparison: Transaction vs Lua Script

| Feature | Transaction | Lua Script |
|---------|-------------|------------|
| Atomicity | Yes | Yes |
| Logic | Sequential commands only | Full programming |
| Network | Multiple round-trips | Single round-trip |
| Conditional | WATCH only | Full conditionals |
| Performance | Good | Better for complex ops |
| Debugging | Easy | Harder |

```php
// Transaction: simple atomic batch
Redis::multi();
Redis::incr('counter');
Redis::expire('counter', 3600);
Redis::exec();

// Lua: complex atomic logic
$script = <<<'LUA'
    local current = redis.call('GET', KEYS[1]) or 0
    if tonumber(current) < tonumber(ARGV[1]) then
        return redis.call('INCR', KEYS[1])
    end
    return current
LUA;

Redis::eval($script, 1, 'counter', 100);
```

---

## Performance Notes

| Aspect | Details |
|--------|---------|
| Transaction overhead | Minimal - commands queued in memory |
| WATCH overhead | O(1) per key |
| EXEC latency | Sum of all command latencies |
| Blocking | Transactions don't block other clients during queue |

**Best Practices:**
- Keep transactions short
- Avoid expensive operations in transactions
- Use UNWATCH when aborting early
- Consider Lua scripts for complex logic
- Implement retry logic with WATCH
