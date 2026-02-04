# Redis Transactions

Atomic command execution with MULTI/EXEC and optimistic locking with WATCH.

---

## Basic Transactions

### MULTI/EXEC

```php
$results = Redis::multi()
    ->set('key1', 'value1')
    ->set('key2', 'value2')
    ->incr('counter')
    ->exec();

// $results = [true, true, 1]
```

### Laravel Transaction Helper

```php
$results = Redis::transaction(function ($redis) {
    $redis->set('key1', 'value1');
    $redis->set('key2', 'value2');
    $redis->incr('counter');
});
```

---

## Transaction Guarantees

### What MULTI/EXEC Provides

1. **Isolation** - Commands queued, executed together
2. **All-or-nothing execution** - Either all run or none
3. **Sequential execution** - No interleaving with other clients

### What It Does NOT Provide

1. **Rollback** - No undo if command fails
2. **Abort on error** - Syntax errors abort, runtime errors don't

---

## Optimistic Locking with WATCH

### Pattern: Check-and-Set

```php
class OptimisticLock
{
    public function updateIfUnchanged(string $key, callable $modifier): bool
    {
        $maxRetries = 3;

        for ($i = 0; $i < $maxRetries; $i++) {
            Redis::watch($key);

            $current = Redis::get($key);
            $new = $modifier($current);

            $result = Redis::multi()
                ->set($key, $new)
                ->exec();

            if ($result !== null) {
                return true;  // Success
            }

            // Transaction aborted due to WATCH, retry
        }

        return false;  // Failed after retries
    }
}

// Usage
$lock = new OptimisticLock();
$success = $lock->updateIfUnchanged('balance', function ($current) {
    return $current - 100;  // Deduct 100
});
```

### WATCH Behavior

```php
Redis::watch('key1', 'key2');  // Watch multiple keys

// If any watched key changes before EXEC...
Redis::multi()
    ->set('key1', 'new1')
    ->set('key2', 'new2')
    ->exec();
// ...returns null (transaction aborted)

Redis::unwatch();  // Cancel WATCH without transaction
```

---

## Common Patterns

### 1. Atomic Transfer

```php
class AtomicTransfer
{
    public function transfer(string $from, string $to, int $amount): bool
    {
        $maxRetries = 5;

        for ($i = 0; $i < $maxRetries; $i++) {
            Redis::watch($from);

            $balance = (int) Redis::get($from);

            if ($balance < $amount) {
                Redis::unwatch();
                return false;  // Insufficient funds
            }

            $result = Redis::multi()
                ->decrby($from, $amount)
                ->incrby($to, $amount)
                ->exec();

            if ($result !== null) {
                return true;
            }
        }

        throw new \Exception('Transfer failed after retries');
    }
}
```

### 2. Unique ID Generation

```php
class UniqueIdGenerator
{
    public function nextId(string $sequence): int
    {
        while (true) {
            Redis::watch($sequence);

            $current = (int) Redis::get($sequence);
            $next = $current + 1;

            $result = Redis::multi()
                ->set($sequence, $next)
                ->exec();

            if ($result !== null) {
                return $next;
            }
        }
    }
}
```

### 3. Conditional Update

```php
class ConditionalUpdater
{
    public function updateIfValue(string $key, string $expected, string $new): bool
    {
        Redis::watch($key);

        $current = Redis::get($key);

        if ($current !== $expected) {
            Redis::unwatch();
            return false;
        }

        $result = Redis::multi()
            ->set($key, $new)
            ->exec();

        return $result !== null;
    }
}
```

### 4. Increment with Ceiling

```php
class BoundedCounter
{
    public function incrementUpTo(string $key, int $max, int $amount = 1): int
    {
        while (true) {
            Redis::watch($key);

            $current = (int) Redis::get($key);

            if ($current >= $max) {
                Redis::unwatch();
                return $current;
            }

            $new = min($current + $amount, $max);

            $result = Redis::multi()
                ->set($key, $new)
                ->exec();

            if ($result !== null) {
                return $new;
            }
        }
    }
}
```

---

## Error Handling

### Syntax Errors (Queue Time)

```php
try {
    Redis::multi()
        ->set('key', 'value')
        ->invalidcommand('arg')  // Syntax error
        ->exec();
} catch (\Exception $e) {
    // Transaction aborted, nothing executed
}
```

### Runtime Errors

```php
$results = Redis::multi()
    ->set('string_key', 'value')
    ->lpush('string_key', 'item')  // Wrong type error
    ->set('another_key', 'value')
    ->exec();

// $results = [true, RedisException, true]
// SET succeeded, LPUSH failed (wrong type), SET succeeded
```

---

## Transactions vs Lua Scripts

| Feature | MULTI/EXEC | Lua Script |
|---------|------------|------------|
| Atomicity | Yes | Yes |
| Conditional logic | No (use WATCH) | Yes |
| Complex operations | Limited | Full |
| Read-modify-write | Needs WATCH | Built-in |
| Network round trips | 2+ | 1 |

### When to Use Each

**Use MULTI/EXEC:**
- Simple command batches
- No conditional logic needed
- Pipeline with atomicity guarantee

**Use Lua Scripts:**
- Read-modify-write patterns
- Complex conditional logic
- Need to reduce round trips

---

## Pipeline vs Transaction

```php
// Pipeline: Multiple commands, NOT atomic
$results = Redis::pipeline(function ($pipe) {
    $pipe->set('a', '1');
    $pipe->set('b', '2');
});

// Transaction: Multiple commands, atomic
$results = Redis::transaction(function ($tx) {
    $tx->set('a', '1');
    $tx->set('b', '2');
});
```

| Feature | Pipeline | Transaction |
|---------|----------|-------------|
| Batched | Yes | Yes |
| Atomic | No | Yes |
| Interruptible | Yes | No |
| Use case | Performance | Consistency |

---

## DISCARD

Cancel a transaction before EXEC:

```php
Redis::multi();
Redis::set('key1', 'value1');
Redis::set('key2', 'value2');
Redis::discard();  // Cancel, nothing executed
```

---

## BudTags Usage

### Atomic Status Update

```php
class SyncStatusManager
{
    public function updateProgress(string $syncId, array $updates): bool
    {
        $key = "sync:{$syncId}:progress";

        Redis::watch($key);

        $current = Redis::hgetall($key);

        // Validate state transition
        if (!$this->canTransition($current, $updates)) {
            Redis::unwatch();
            return false;
        }

        $result = Redis::multi()
            ->hmset($key, $updates)
            ->expire($key, 86400)
            ->exec();

        return $result !== null;
    }

    private function canTransition(array $current, array $updates): bool
    {
        // State machine logic
        return true;
    }
}
```

---

## Key Takeaways

1. **MULTI/EXEC** - Queue commands, execute atomically
2. **WATCH** - Abort if watched keys change
3. **No rollback** - Runtime errors don't undo previous commands
4. **Retry pattern** - WATCH failures should retry
5. **DISCARD** - Cancel queued transaction
6. **Lua for complex** - Use scripts for read-modify-write
7. **Pipeline for speed** - Use transactions for consistency
8. **UNWATCH** - Cancel watch without transaction
