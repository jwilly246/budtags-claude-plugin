# Redis Scripting Commands

Redis supports server-side scripting with Lua. Scripts execute atomically and can perform complex operations in a single round-trip.

---

## Lua Script Execution

### EVAL

Executes a Lua script.

```
EVAL script numkeys [key ...] [arg ...]
```

| Parameter | Description |
|-----------|-------------|
| `script` | Lua source code |
| `numkeys` | Number of keys that follow |
| `key ...` | Keys accessible as KEYS[1], KEYS[2], etc. |
| `arg ...` | Arguments accessible as ARGV[1], ARGV[2], etc. |

| Aspect | Details |
|--------|---------|
| **Returns** | Script return value |
| **Complexity** | Depends on script |
| **Atomicity** | Entire script is atomic |

```php
// Simple script
$result = Redis::eval("return redis.call('GET', KEYS[1])", 1, 'mykey');

// Script with multiple keys and arguments
$script = <<<'LUA'
    local current = redis.call('GET', KEYS[1])
    if current == ARGV[1] then
        return redis.call('SET', KEYS[1], ARGV[2])
    end
    return nil
LUA;
$result = Redis::eval($script, 1, 'mykey', 'expected', 'newvalue');
```

---

### EVALSHA

Executes a cached script by SHA1 hash.

```
EVALSHA sha1 numkeys [key ...] [arg ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Script return value |
| **Complexity** | Depends on script |
| **Error** | NOSCRIPT if script not cached |

```php
// Load script first
$sha = Redis::script('LOAD', $script);

// Execute by SHA (more efficient)
$result = Redis::evalsha($sha, 1, 'mykey', 'arg1');
```

---

### EVAL_RO / EVALSHA_RO

Read-only versions that can run on replicas.

```
EVAL_RO script numkeys [key ...] [arg ...]
EVALSHA_RO sha1 numkeys [key ...] [arg ...]
```

| Aspect | Details |
|--------|---------|
| **Since** | Redis 7.0 |
| **Use** | Read-only scripts on replicas |

---

## Script Management

### SCRIPT LOAD

Loads a script into cache.

```
SCRIPT LOAD script
```

| Aspect | Details |
|--------|---------|
| **Returns** | SHA1 hash (40 characters) |
| **Complexity** | O(N) where N is script length |

```php
$sha = Redis::script('LOAD', $script);
// Returns: "2a42fb57..."
```

---

### SCRIPT EXISTS

Checks if scripts are cached.

```
SCRIPT EXISTS sha1 [sha1 ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Array of 1s and 0s |
| **Complexity** | O(N) |

```php
$exists = Redis::script('EXISTS', $sha1, $sha2);
// Returns: [1, 0]
```

---

### SCRIPT FLUSH

Clears script cache.

```
SCRIPT FLUSH [ASYNC|SYNC]
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Complexity** | O(N) |

---

### SCRIPT KILL

Terminates a running script.

```
SCRIPT KILL
```

| Aspect | Details |
|--------|---------|
| **Returns** | OK |
| **Note** | Only works if script hasn't written yet |

Use when a script is taking too long. Cannot kill scripts that have already performed writes.

---

### SCRIPT DEBUG

Sets debugging mode.

```
SCRIPT DEBUG YES|SYNC|NO
```

For development only. Never use in production.

---

## Redis Functions (Redis 7.0+)

Functions are persistent, reusable script libraries.

### FUNCTION LOAD

Creates a function library.

```
FUNCTION LOAD [REPLACE] function-code
```

| Aspect | Details |
|--------|---------|
| **Returns** | Library name |
| **Since** | Redis 7.0 |

```lua
-- Function code with library registration
#!lua name=mylib

local function my_function(keys, args)
    return redis.call('GET', keys[1])
end

redis.register_function('my_function', my_function)
```

```php
Redis::function('LOAD', $functionCode);
```

---

### FCALL

Invokes a function.

```
FCALL function-name numkeys [key ...] [arg ...]
```

| Aspect | Details |
|--------|---------|
| **Returns** | Function return value |
| **Since** | Redis 7.0 |

```php
$result = Redis::fcall('my_function', 1, 'mykey');
```

---

### FCALL_RO

Read-only function call (can run on replicas).

```
FCALL_RO function-name numkeys [key ...] [arg ...]
```

---

### FUNCTION LIST

Lists all functions.

```
FUNCTION LIST [LIBRARYNAME pattern] [WITHCODE]
```

---

### FUNCTION DELETE

Deletes a library.

```
FUNCTION DELETE library-name
```

---

### FUNCTION FLUSH

Deletes all libraries.

```
FUNCTION FLUSH [ASYNC|SYNC]
```

---

### FUNCTION DUMP / RESTORE

Serializes/deserializes all functions.

```
FUNCTION DUMP
FUNCTION RESTORE payload [FLUSH|APPEND|REPLACE]
```

---

### FUNCTION KILL

Terminates a running function.

```
FUNCTION KILL
```

---

### FUNCTION STATS

Returns execution statistics.

```
FUNCTION STATS
```

---

## Lua Scripting Guide

### Calling Redis Commands

```lua
-- redis.call: raises error on failure
local value = redis.call('GET', KEYS[1])

-- redis.pcall: returns error as value
local result, err = redis.pcall('GET', KEYS[1])
```

### Data Type Conversions

| Redis | Lua |
|-------|-----|
| integer | number |
| bulk string | string |
| array | table (1-indexed) |
| nil | false |
| status (OK) | table with 'ok' field |
| error | table with 'err' field |

### Returning Values

```lua
-- Return string
return "hello"

-- Return number
return 42

-- Return array
return {1, 2, 3}

-- Return nil
return nil  -- converts to false

-- Return Redis status
return redis.status_reply("OK")

-- Return Redis error
return redis.error_reply("Something went wrong")
```

---

## Common Patterns

### Atomic Increment with Limit

```lua
local current = tonumber(redis.call('GET', KEYS[1])) or 0
local limit = tonumber(ARGV[1])

if current >= limit then
    return nil
end

return redis.call('INCR', KEYS[1])
```

```php
$script = <<<'LUA'
local current = tonumber(redis.call('GET', KEYS[1])) or 0
local limit = tonumber(ARGV[1])
if current >= limit then return nil end
return redis.call('INCR', KEYS[1])
LUA;

$result = Redis::eval($script, 1, 'counter', 100);
```

### Compare and Swap

```lua
local current = redis.call('GET', KEYS[1])
if current == ARGV[1] then
    redis.call('SET', KEYS[1], ARGV[2])
    return 1
end
return 0
```

### Rate Limiter

```lua
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Remove old entries
redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window)

-- Count current entries
local count = redis.call('ZCARD', key)

if count >= limit then
    return 0  -- Rate limited
end

-- Add new entry
redis.call('ZADD', key, now, now .. '-' .. math.random())
redis.call('EXPIRE', key, window)

return 1  -- Allowed
```

### Atomic Get and Delete

```lua
local value = redis.call('GET', KEYS[1])
if value then
    redis.call('DEL', KEYS[1])
end
return value
```

### Bulk Update with Transaction

```lua
local updates = cjson.decode(ARGV[1])
for _, update in ipairs(updates) do
    redis.call('HSET', KEYS[1], update.field, update.value)
end
return #updates
```

---

## Laravel Integration

### Script Class Pattern

```php
class RedisScripts
{
    private static array $scripts = [];

    public static function incrementWithLimit(): string
    {
        return self::$scripts['increment_limit'] ??= Redis::script('LOAD', <<<'LUA'
            local current = tonumber(redis.call('GET', KEYS[1])) or 0
            local limit = tonumber(ARGV[1])
            if current >= limit then return nil end
            return redis.call('INCR', KEYS[1])
        LUA);
    }

    public static function runIncrementWithLimit(string $key, int $limit): ?int
    {
        try {
            return Redis::evalsha(self::incrementWithLimit(), 1, $key, $limit);
        } catch (\Exception $e) {
            if (str_contains($e->getMessage(), 'NOSCRIPT')) {
                // Script was flushed, reload and retry
                unset(self::$scripts['increment_limit']);
                return Redis::evalsha(self::incrementWithLimit(), 1, $key, $limit);
            }
            throw $e;
        }
    }
}
```

### Fallback Pattern

```php
function evalWithFallback(string $sha, string $script, int $numkeys, ...$args)
{
    try {
        return Redis::evalsha($sha, $numkeys, ...$args);
    } catch (\Exception $e) {
        if (str_contains($e->getMessage(), 'NOSCRIPT')) {
            return Redis::eval($script, $numkeys, ...$args);
        }
        throw $e;
    }
}
```

---

## Best Practices

### Do's

1. **Use KEYS array for all keys** - Enables cluster compatibility
2. **Keep scripts focused** - One purpose per script
3. **Cache SHA1 hashes** - Avoid reloading scripts
4. **Handle NOSCRIPT errors** - Scripts may be flushed
5. **Use read-only variants** - For replica compatibility

### Don'ts

1. **Don't hardcode keys** - Always use KEYS[n]
2. **Avoid long-running scripts** - They block Redis
3. **Don't use non-deterministic functions** - Breaks replication
4. **Avoid excessive memory usage** - Lua has memory limits

### Non-Deterministic Functions to Avoid

```lua
-- Don't use these in scripts:
math.random()     -- Use ARGV to pass random values
os.time()         -- Use redis.call('TIME') or pass as ARGV
io.*              -- No I/O allowed
```

---

## Performance Notes

| Aspect | Details |
|--------|---------|
| Compilation | Scripts compiled once, cached |
| Execution | Single-threaded, blocks Redis |
| Network | Single round-trip for complex operations |
| Memory | Lua has memory limits (~1GB default) |

**When to use scripts:**
- Complex atomic operations
- Multiple dependent commands
- Reduce network round-trips
- Conditional logic

**When NOT to use scripts:**
- Simple single commands
- Very long-running operations
- Heavy computation
