# Redis Lua Scripting

Execute atomic operations with Lua scripts using EVAL and EVALSHA.

---

## Why Use Lua Scripts?

1. **Atomicity** - Script runs without interruption
2. **Reduced round trips** - Multiple operations in one call
3. **Complex logic** - Conditionals and loops server-side
4. **Consistency** - All-or-nothing execution

---

## Basic Syntax

### EVAL Command

```php
$result = Redis::eval(
    $script,      // Lua script
    $numKeys,     // Number of KEYS arguments
    $key1, $key2, // KEYS[1], KEYS[2]...
    $arg1, $arg2  // ARGV[1], ARGV[2]...
);
```

### Simple Example

```php
// Increment and get in one atomic operation
$script = <<<'LUA'
    local current = redis.call('GET', KEYS[1])
    current = tonumber(current) or 0
    current = current + tonumber(ARGV[1])
    redis.call('SET', KEYS[1], current)
    return current
LUA;

$result = Redis::eval($script, 1, 'counter', 5);
// Returns new value after increment
```

---

## KEYS and ARGV

| Variable | Purpose | Example |
|----------|---------|---------|
| KEYS[n] | Key names (1-indexed) | `KEYS[1]` = first key |
| ARGV[n] | Additional arguments | `ARGV[1]` = first arg |

```php
// Script expects 2 keys and 1 argument
$script = <<<'LUA'
    local source = KEYS[1]
    local dest = KEYS[2]
    local count = tonumber(ARGV[1])

    for i = 1, count do
        local val = redis.call('RPOP', source)
        if val then
            redis.call('LPUSH', dest, val)
        end
    end
    return count
LUA;

Redis::eval($script, 2, 'source:list', 'dest:list', 10);
```

---

## Common Patterns

### 1. Compare and Set (CAS)

```php
$casScript = <<<'LUA'
    local current = redis.call('GET', KEYS[1])
    if current == ARGV[1] then
        redis.call('SET', KEYS[1], ARGV[2])
        return 1
    end
    return 0
LUA;

class CompareAndSet
{
    private string $script;

    public function __construct()
    {
        $this->script = $casScript;
    }

    public function cas(string $key, mixed $expected, mixed $newValue): bool
    {
        return (bool) Redis::eval(
            $this->script,
            1,
            $key,
            (string) $expected,
            (string) $newValue
        );
    }
}
```

### 2. Rate Limiter

```php
$rateLimitScript = <<<'LUA'
    local key = KEYS[1]
    local limit = tonumber(ARGV[1])
    local window = tonumber(ARGV[2])

    local current = tonumber(redis.call('GET', key)) or 0

    if current >= limit then
        return 0  -- Rate limit exceeded
    end

    current = redis.call('INCR', key)

    if current == 1 then
        redis.call('EXPIRE', key, window)
    end

    return limit - current  -- Remaining requests
LUA;

class LuaRateLimiter
{
    public function isAllowed(string $identifier, int $limit = 100, int $windowSeconds = 60): int
    {
        global $rateLimitScript;

        $remaining = Redis::eval(
            $rateLimitScript,
            1,
            "ratelimit:{$identifier}",
            $limit,
            $windowSeconds
        );

        return (int) $remaining;
    }
}
```

### 3. Acquire Lock with Timeout

```php
$lockScript = <<<'LUA'
    local key = KEYS[1]
    local token = ARGV[1]
    local ttl = tonumber(ARGV[2])

    local current = redis.call('GET', key)

    if current == false then
        redis.call('SET', key, token, 'PX', ttl)
        return 1
    end

    return 0
LUA;

$unlockScript = <<<'LUA'
    local key = KEYS[1]
    local token = ARGV[1]

    if redis.call('GET', key) == token then
        redis.call('DEL', key)
        return 1
    end

    return 0
LUA;

class LuaLock
{
    public function acquire(string $name, string $token, int $ttlMs = 10000): bool
    {
        global $lockScript;
        return (bool) Redis::eval($lockScript, 1, "lock:{$name}", $token, $ttlMs);
    }

    public function release(string $name, string $token): bool
    {
        global $unlockScript;
        return (bool) Redis::eval($unlockScript, 1, "lock:{$name}", $token);
    }
}
```

### 4. Moving Items Between Lists Atomically

```php
$moveScript = <<<'LUA'
    local source = KEYS[1]
    local dest = KEYS[2]
    local value = ARGV[1]

    local removed = redis.call('LREM', source, 0, value)

    if removed > 0 then
        redis.call('RPUSH', dest, value)
        return 1
    end

    return 0
LUA;
```

### 5. Conditional Update

```php
$conditionalUpdate = <<<'LUA'
    local key = KEYS[1]
    local field = ARGV[1]
    local expected = ARGV[2]
    local newValue = ARGV[3]

    local current = redis.call('HGET', key, field)

    if current == expected then
        redis.call('HSET', key, field, newValue)
        return 1
    end

    return 0
LUA;
```

---

## Script Caching with EVALSHA

### Load and Execute

```php
class ScriptCache
{
    private array $shas = [];

    public function register(string $name, string $script): string
    {
        $sha = Redis::script('LOAD', $script);
        $this->shas[$name] = $sha;
        return $sha;
    }

    public function execute(string $name, int $numKeys, ...$args): mixed
    {
        if (!isset($this->shas[$name])) {
            throw new \Exception("Script not registered: {$name}");
        }

        try {
            return Redis::evalsha($this->shas[$name], $numKeys, ...$args);
        } catch (\Exception $e) {
            if (str_contains($e->getMessage(), 'NOSCRIPT')) {
                // Script not in cache, re-register
                // This would need the original script...
                throw $e;
            }
            throw $e;
        }
    }
}
```

### Script Management

```php
// Load script and get SHA
$sha = Redis::script('LOAD', $script);

// Execute by SHA
$result = Redis::evalsha($sha, 1, 'key', 'arg1');

// Check if scripts exist
$exists = Redis::script('EXISTS', $sha1, $sha2);
// Returns: [true, false]

// Flush all scripts
Redis::script('FLUSH');

// Kill running script
Redis::script('KILL');
```

---

## Redis Library Functions

Available in Lua scripts:

| Function | Description |
|----------|-------------|
| `redis.call()` | Execute command, raises error on failure |
| `redis.pcall()` | Execute command, returns error object |
| `redis.log()` | Write to Redis log |
| `redis.sha1hex()` | SHA1 hash |
| `redis.error_reply()` | Create error response |
| `redis.status_reply()` | Create status response |

### Error Handling

```lua
local result = redis.pcall('HGET', KEYS[1], 'field')

if type(result) == 'table' and result.err then
    return redis.error_reply('Operation failed: ' .. result.err)
end

return result
```

### Logging

```lua
redis.log(redis.LOG_WARNING, 'Something happened')
-- Levels: LOG_DEBUG, LOG_VERBOSE, LOG_NOTICE, LOG_WARNING
```

---

## Data Type Conversion

| Lua Type | Redis Reply |
|----------|-------------|
| number | Integer |
| string | Bulk string |
| table (array) | Array |
| table (with single `ok` field) | Status |
| table (with single `err` field) | Error |
| nil | Null bulk |
| true | Integer 1 |
| false | Null bulk |

---

## Best Practices

### 1. Keep Scripts Short

```lua
-- ✅ Good: Simple, focused
local val = redis.call('GET', KEYS[1])
return tonumber(val) or 0

-- ❌ Bad: Too complex, hard to debug
-- (Long scripts with lots of logic)
```

### 2. Use KEYS for All Key Names

```lua
-- ✅ Good: All keys in KEYS array
local a = redis.call('GET', KEYS[1])
local b = redis.call('GET', KEYS[2])

-- ❌ Bad: Hardcoded key names
local a = redis.call('GET', 'hardcoded:key')
```

### 3. Handle Nil Values

```lua
local val = redis.call('GET', KEYS[1])
if val == false then
    return nil
end
return val
```

### 4. Use EVALSHA in Production

```php
// Preload scripts at startup
$sha = Redis::script('LOAD', $script);

// Use EVALSHA for execution
Redis::evalsha($sha, 1, $key);
```

---

## Limitations

1. **No external calls** - Can't access network, filesystem
2. **No global state** - Each execution is isolated
3. **Blocking** - Long scripts block Redis
4. **Debugging is hard** - Use redis.log() for debugging
5. **Script timeout** - Default 5 seconds (`lua-time-limit`)

---

## Key Takeaways

1. **Atomic execution** - Scripts run without interruption
2. **KEYS array** - All key names must be in KEYS
3. **EVALSHA** - Cache scripts for performance
4. **Error handling** - Use redis.pcall() when needed
5. **Keep short** - Long scripts block Redis
6. **Type conversion** - Understand Lua to Redis mapping
7. **No external access** - Pure Redis operations only
