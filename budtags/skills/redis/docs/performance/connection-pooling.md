# Redis Connection Pooling

Efficient connection management reduces overhead and improves performance.

---

## Connection Basics

### Connection Overhead

Each new Redis connection:
1. TCP handshake (1-2 RTT)
2. Redis AUTH (if enabled)
3. Redis SELECT (if using non-default DB)
4. Memory allocation on Redis server

**Cost:** ~1-5ms per new connection

### Connection Limits

```php
// Check current connections
$info = Redis::info('clients');
$connected = $info['connected_clients'];
$blocked = $info['blocked_clients'];
$maxClients = $info['maxclients'];
```

---

## Laravel Configuration

### config/database.php

```php
'redis' => [
    'client' => env('REDIS_CLIENT', 'phpredis'),  // phpredis is faster

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', Str::slug(env('APP_NAME', 'laravel'), '_').'_database_'),
    ],

    'default' => [
        'url' => env('REDIS_URL'),
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'username' => env('REDIS_USERNAME'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', '6379'),
        'database' => env('REDIS_DB', '0'),

        // Connection pooling settings
        'read_timeout' => 60,
        'persistent' => true,           // Enable persistent connections
        'persistent_id' => 'default',   // Identifier for persistent connection
    ],

    'cache' => [
        'url' => env('REDIS_URL'),
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'username' => env('REDIS_USERNAME'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', '6379'),
        'database' => env('REDIS_CACHE_DB', '1'),
        'persistent' => true,
        'persistent_id' => 'cache',
    ],
],
```

---

## Persistent Connections

### How They Work

```
Without persistent:
Request 1: Connect → Commands → Disconnect
Request 2: Connect → Commands → Disconnect
Request 3: Connect → Commands → Disconnect

With persistent:
Request 1: Connect → Commands → (keep open)
Request 2: Reuse    → Commands → (keep open)
Request 3: Reuse    → Commands → (keep open)
```

### phpredis Configuration

```php
'default' => [
    // ...
    'persistent' => true,
    'persistent_id' => 'myapp',  // Unique ID per connection config
],
```

### Benefits

| Metric | Without Persistent | With Persistent |
|--------|-------------------|-----------------|
| Connection time | 1-5ms | 0ms (reused) |
| Memory per request | New allocation | Reused |
| Server connections | Request × concurrent | Fixed pool |

---

## Connection Per Database

### Multiple Database Connections

```php
// config/database.php
'redis' => [
    'default' => [
        'database' => '0',
        'persistent_id' => 'default',
    ],
    'cache' => [
        'database' => '1',
        'persistent_id' => 'cache',
    ],
    'queue' => [
        'database' => '2',
        'persistent_id' => 'queue',
    ],
    'sessions' => [
        'database' => '0',
        'persistent_id' => 'sessions',
    ],
],
```

### Usage

```php
// Uses 'default' connection (DB 0)
Redis::get('key');

// Uses 'cache' connection (DB 1)
Redis::connection('cache')->get('key');

// Uses 'queue' connection (DB 2)
Redis::connection('queue')->lpush('jobs', $job);
```

---

## phpredis vs Predis

### Performance Comparison

| Client | Connection Speed | Command Speed | Memory |
|--------|-----------------|---------------|--------|
| phpredis | Fast (C extension) | ~100K ops/sec | Lower |
| Predis | Slower (PHP) | ~30K ops/sec | Higher |

### phpredis (Recommended)

```php
// config/database.php
'redis' => [
    'client' => 'phpredis',  // C extension, much faster
],
```

Installation:
```bash
pecl install redis
# Add extension=redis.so to php.ini
```

### Predis (Fallback)

```php
'redis' => [
    'client' => 'predis',  // Pure PHP, no extension needed
],
```

Installation:
```bash
composer require predis/predis
```

---

## Connection Timeouts

### Configuration

```php
'default' => [
    // Connection timeout (seconds to establish connection)
    'timeout' => 5,

    // Read timeout (seconds to wait for response)
    'read_timeout' => 60,

    // Retry interval (milliseconds between reconnection attempts)
    'retry_interval' => 100,
],
```

### Handling Timeouts

```php
try {
    $value = Redis::get('key');
} catch (\RedisException $e) {
    if (str_contains($e->getMessage(), 'timed out')) {
        Log::warning('Redis timeout', ['error' => $e->getMessage()]);
        // Fallback logic
    }
    throw $e;
}
```

---

## Connection Health Monitoring

### Health Check

```php
class RedisHealthCheck
{
    public function check(): array
    {
        try {
            $start = microtime(true);
            $pong = Redis::ping();
            $latency = (microtime(true) - $start) * 1000;

            $info = Redis::info('clients');

            return [
                'healthy' => $pong === true || $pong === 'PONG',
                'latency_ms' => round($latency, 2),
                'connected_clients' => $info['connected_clients'],
                'blocked_clients' => $info['blocked_clients'],
                'max_clients' => Redis::config('GET', 'maxclients')['maxclients'],
            ];
        } catch (\Exception $e) {
            return [
                'healthy' => false,
                'error' => $e->getMessage(),
            ];
        }
    }
}
```

### Connection Pool Status

```php
class ConnectionMonitor
{
    public function getStatus(): array
    {
        $info = Redis::info('clients');

        $utilization = $info['connected_clients'] / ($info['maxclients'] ?? 10000);

        return [
            'connected' => $info['connected_clients'],
            'blocked' => $info['blocked_clients'],
            'max' => $info['maxclients'] ?? 10000,
            'utilization' => round($utilization * 100, 2) . '%',
            'warning' => $utilization > 0.8,
        ];
    }
}
```

---

## Worker Process Connections

### Queue Workers

Each queue worker maintains its own connection:

```php
// Horizon worker processes
// 3 supervisors × 3 processes = 9 Redis connections minimum
```

### Supervisor Configuration

```php
// config/horizon.php
'environments' => [
    'production' => [
        'supervisor-1' => [
            'connection' => 'redis',
            'queue' => ['default'],
            'balance' => 'auto',
            'processes' => 3,  // 3 connections
            'tries' => 3,
        ],
    ],
],
```

### Total Connection Calculation

```
Web servers: PHP-FPM processes × servers
Queue workers: Horizon processes × servers
Scheduled tasks: 1 per artisan process
Other services: Pulse, Reverb, etc.

Example:
- 2 web servers × 50 PHP-FPM workers = 100
- 2 queue servers × 10 Horizon processes = 20
- Scheduled tasks = 2
- Other = 5
Total: ~127 connections
```

---

## Redis Server Configuration

### maxclients

```
# redis.conf
maxclients 10000
```

### TCP Keepalive

```
# redis.conf
tcp-keepalive 300    # Send keepalive every 300 seconds
```

### Timeout

```
# redis.conf
timeout 0            # Disable idle timeout (0 = never)
# OR
timeout 300          # Close idle connections after 300 seconds
```

---

## Connection Best Practices

### 1. Use Persistent Connections

```php
'persistent' => true,
'persistent_id' => 'unique_per_config',
```

### 2. Set Appropriate Timeouts

```php
'timeout' => 5,        // Quick fail on connection issues
'read_timeout' => 60,  // Allow for slow operations
```

### 3. Monitor Connection Count

```php
Schedule::call(function () {
    $clients = Redis::info('clients')['connected_clients'];
    $max = Redis::config('GET', 'maxclients')['maxclients'];

    if ($clients > $max * 0.8) {
        Log::warning("Redis connections at {$clients}/{$max}");
    }
})->everyMinute();
```

### 4. Use Separate Connections for Different Purposes

```php
// Different persistent IDs for different use cases
'cache' => ['persistent_id' => 'cache'],
'queue' => ['persistent_id' => 'queue'],
'sessions' => ['persistent_id' => 'sessions'],
```

### 5. Handle Connection Failures

```php
class ResilientRedis
{
    public function get(string $key, mixed $default = null): mixed
    {
        try {
            return Redis::get($key) ?? $default;
        } catch (\RedisException $e) {
            Log::error('Redis connection failed', ['error' => $e->getMessage()]);
            return $default;
        }
    }
}
```

---

## Key Takeaways

1. **Use phpredis** - 3x faster than Predis
2. **Enable persistent connections** - Eliminates connection overhead
3. **Unique persistent_id** - Per connection configuration
4. **Monitor client count** - Stay under maxclients limit
5. **Set read_timeout** - Prevent hanging on slow operations
6. **Calculate total connections** - Account for workers and processes
7. **Use connection pooling** - Reduce per-request overhead
8. **Handle failures gracefully** - Fallback when Redis unavailable
