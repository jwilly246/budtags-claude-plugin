# Redis Functions (Redis 7+)

Redis Functions provide reusable, named server-side logic with better management than EVAL.

---

## Why Functions Over Scripts?

| Feature | EVAL/EVALSHA | Functions |
|---------|--------------|-----------|
| Persistence | No | Yes (with RDB/AOF) |
| Naming | SHA1 hash | Human-readable name |
| Grouping | None | Libraries |
| Replication | On call | With data |
| Management | Manual | Built-in commands |

---

## Creating Functions

### Basic Function

```lua
#!lua name=mylib

-- Simple counter function
redis.register_function('increment_counter', function(keys, args)
    local key = keys[1]
    local amount = tonumber(args[1]) or 1

    local current = redis.call('GET', key)
    current = tonumber(current) or 0
    current = current + amount

    redis.call('SET', key, current)
    return current
end)
```

### Loading Functions

```bash
# Load from file
cat mylib.lua | redis-cli -x FUNCTION LOAD REPLACE

# Or inline
redis-cli FUNCTION LOAD "#!lua name=mylib\n redis.register_function('myfunc', function(keys, args) return 'hello' end)"
```

### PHP Loading

```php
class FunctionLoader
{
    public function load(string $libraryCode): void
    {
        Redis::function('LOAD', 'REPLACE', $libraryCode);
    }

    public function loadFromFile(string $path): void
    {
        $code = file_get_contents($path);
        $this->load($code);
    }
}
```

---

## Calling Functions

### FCALL Command

```php
// FCALL function_name numkeys key1 key2 ... arg1 arg2 ...
$result = Redis::fcall('increment_counter', 1, 'mycounter', 5);
```

### FCALL_RO (Read-Only)

```php
// Read-only version, can run on replicas
$result = Redis::fcall_ro('get_stats', 1, 'stats:key');
```

---

## Library Example

### Complete Library

```lua
#!lua name=budtags

-- Rate limiter function
redis.register_function('rate_limit', function(keys, args)
    local key = keys[1]
    local limit = tonumber(args[1])
    local window = tonumber(args[2])

    local current = tonumber(redis.call('GET', key)) or 0

    if current >= limit then
        return {allowed = false, remaining = 0}
    end

    local newCount = redis.call('INCR', key)

    if newCount == 1 then
        redis.call('EXPIRE', key, window)
    end

    return {allowed = true, remaining = limit - newCount}
end)

-- Atomic counter with max
redis.register_function('bounded_incr', function(keys, args)
    local key = keys[1]
    local max = tonumber(args[1])
    local amount = tonumber(args[2]) or 1

    local current = tonumber(redis.call('GET', key)) or 0

    if current >= max then
        return current
    end

    local newValue = math.min(current + amount, max)
    redis.call('SET', key, newValue)
    return newValue
end)

-- Compare and swap
redis.register_function('cas', function(keys, args)
    local key = keys[1]
    local expected = args[1]
    local newValue = args[2]

    local current = redis.call('GET', key)

    if current == expected then
        redis.call('SET', key, newValue)
        return 1
    end

    return 0
end)

-- Get multiple hash fields with defaults
redis.register_function{
    function_name = 'hget_defaults',
    callback = function(keys, args)
        local hashKey = keys[1]
        local results = {}

        for i = 1, #args, 2 do
            local field = args[i]
            local default = args[i + 1]

            local value = redis.call('HGET', hashKey, field)
            if value == false then
                value = default
            end

            table.insert(results, value)
        end

        return results
    end,
    flags = {'no-writes'}  -- Can run on replica
}
```

---

## Function Management

### List Functions

```php
// List all libraries
$libraries = Redis::function('LIST');

// List with code
$libraries = Redis::function('LIST', 'WITHCODE');

// List specific library
$library = Redis::function('LIST', 'LIBRARYNAME', 'mylib');
```

### Delete Functions

```php
// Delete library
Redis::function('DELETE', 'mylib');

// Flush all functions
Redis::function('FLUSH');
Redis::function('FLUSH', 'ASYNC');  // Non-blocking
```

### Dump and Restore

```php
// Dump for backup
$dump = Redis::function('DUMP');

// Restore on another instance
Redis::function('RESTORE', $dump);
Redis::function('RESTORE', $dump, 'REPLACE');  // Overwrite existing
```

---

## Function Flags

```lua
redis.register_function{
    function_name = 'readonly_func',
    callback = function(keys, args)
        return redis.call('GET', keys[1])
    end,
    flags = {'no-writes', 'allow-stale'}
}
```

| Flag | Description |
|------|-------------|
| `no-writes` | Function doesn't write, can run on replica |
| `allow-stale` | Can run on stale replica |
| `no-cluster` | Error if called in cluster mode |
| `allow-oom` | Allow when OOM |
| `raw-arguments` | Don't parse arguments |

---

## Error Handling

```lua
redis.register_function('safe_operation', function(keys, args)
    local key = keys[1]

    -- Validate input
    if not key then
        return redis.error_reply('ERR missing key')
    end

    local success, result = pcall(function()
        return redis.call('GET', key)
    end)

    if not success then
        redis.log(redis.LOG_WARNING, 'Operation failed: ' .. tostring(result))
        return redis.error_reply('ERR operation failed')
    end

    return result
end)
```

---

## Laravel Integration

### Function Manager Service

```php
class RedisFunctions
{
    private bool $loaded = false;

    public function ensureLoaded(): void
    {
        if ($this->loaded) {
            return;
        }

        // Check if library exists
        $libraries = Redis::function('LIST', 'LIBRARYNAME', 'budtags');

        if (empty($libraries)) {
            $this->loadLibrary();
        }

        $this->loaded = true;
    }

    private function loadLibrary(): void
    {
        $code = file_get_contents(resource_path('redis/budtags.lua'));
        Redis::function('LOAD', 'REPLACE', $code);
    }

    public function rateLimit(string $key, int $limit, int $window): array
    {
        $this->ensureLoaded();
        return Redis::fcall('rate_limit', 1, $key, $limit, $window);
    }

    public function boundedIncr(string $key, int $max, int $amount = 1): int
    {
        $this->ensureLoaded();
        return Redis::fcall('bounded_incr', 1, $key, $max, $amount);
    }

    public function compareAndSwap(string $key, string $expected, string $new): bool
    {
        $this->ensureLoaded();
        return (bool) Redis::fcall('cas', 1, $key, $expected, $new);
    }
}
```

### Service Provider

```php
// AppServiceProvider.php
public function boot(): void
{
    // Load Redis functions on first use
    $this->app->singleton(RedisFunctions::class);
}
```

---

## Migration from EVAL

### Before (EVAL)

```php
$script = <<<'LUA'
    local key = KEYS[1]
    local limit = ARGV[1]
    -- ... logic ...
LUA;

$sha = Redis::script('LOAD', $script);
$result = Redis::evalsha($sha, 1, 'key', 100);
```

### After (Functions)

```lua
-- In library file
redis.register_function('rate_limit', function(keys, args)
    local key = keys[1]
    local limit = args[1]
    -- ... logic ...
end)
```

```php
// Load once at deploy
Redis::function('LOAD', 'REPLACE', $libraryCode);

// Call by name
$result = Redis::fcall('rate_limit', 1, 'key', 100);
```

---

## Key Takeaways

1. **Named functions** - Human-readable names instead of SHA
2. **Libraries** - Group related functions
3. **Persistence** - Functions survive restarts
4. **Replication** - Functions replicate with data
5. **Flags** - Mark read-only functions for replica execution
6. **FCALL_RO** - Explicitly read-only calls
7. **Better management** - LIST, DELETE, DUMP, RESTORE
8. **Deploy once** - Load at deployment, not runtime
