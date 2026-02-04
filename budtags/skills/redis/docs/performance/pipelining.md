# Redis Pipelining

Pipelining sends multiple commands to Redis without waiting for individual responses, dramatically reducing round-trip overhead.

---

## The Problem

### Without Pipelining

```
Client          Redis
  │               │
  │──── GET A ───>│
  │<─── value ────│  RTT 1
  │               │
  │──── GET B ───>│
  │<─── value ────│  RTT 2
  │               │
  │──── GET C ───>│
  │<─── value ────│  RTT 3
```

**100 commands = 100 round trips**

### With Pipelining

```
Client                    Redis
  │                         │
  │──── GET A ─────────────>│
  │──── GET B ─────────────>│
  │──── GET C ─────────────>│
  │<─── value A ────────────│
  │<─── value B ────────────│  1 RTT
  │<─── value C ────────────│
```

**100 commands = 1 round trip**

---

## Laravel Implementation

### Basic Pipeline

```php
$results = Redis::pipeline(function ($pipe) {
    $pipe->set('key1', 'value1');
    $pipe->set('key2', 'value2');
    $pipe->get('key1');
    $pipe->get('key2');
});

// $results = [true, true, 'value1', 'value2']
```

### Pipeline with Keys Array

```php
$keys = ['user:1', 'user:2', 'user:3', 'user:4', 'user:5'];

$results = Redis::pipeline(function ($pipe) use ($keys) {
    foreach ($keys as $key) {
        $pipe->get($key);
    }
});

// Results in same order as commands
$users = array_combine($keys, $results);
```

### Named Results Pattern

```php
class PipelineHelper
{
    public static function named(array $commands): array
    {
        $names = array_keys($commands);

        $results = Redis::pipeline(function ($pipe) use ($commands) {
            foreach ($commands as $command) {
                $command($pipe);
            }
        });

        return array_combine($names, $results);
    }
}

// Usage
$data = PipelineHelper::named([
    'user' => fn($p) => $p->hgetall('user:123'),
    'settings' => fn($p) => $p->hgetall('settings:123'),
    'recent' => fn($p) => $p->lrange('recent:123', 0, 9),
]);

// $data['user'], $data['settings'], $data['recent']
```

---

## Performance Impact

### Benchmark Comparison

| Commands | Without Pipeline | With Pipeline | Speedup |
|----------|-----------------|---------------|---------|
| 10 | ~10ms | ~1ms | 10x |
| 100 | ~100ms | ~2ms | 50x |
| 1,000 | ~1,000ms | ~10ms | 100x |
| 10,000 | ~10,000ms | ~50ms | 200x |

*Assumes 1ms network latency per round trip*

### Real-World Example

```php
// ❌ Without pipelining: ~500ms for 500 keys
$values = [];
foreach ($keys as $key) {
    $values[$key] = Redis::get($key);
}

// ✅ With pipelining: ~5ms for 500 keys
$results = Redis::pipeline(function ($pipe) use ($keys) {
    foreach ($keys as $key) {
        $pipe->get($key);
    }
});
$values = array_combine($keys, $results);
```

---

## Use Cases

### 1. Bulk Data Loading

```php
class BulkLoader
{
    public function loadUsers(array $users): void
    {
        Redis::pipeline(function ($pipe) use ($users) {
            foreach ($users as $user) {
                $pipe->hmset("user:{$user['id']}", [
                    'name' => $user['name'],
                    'email' => $user['email'],
                ]);
                $pipe->expire("user:{$user['id']}", 3600);
            }
        });
    }
}
```

### 2. Batch Counter Updates

```php
class CounterBatch
{
    public function incrementMany(array $counters): array
    {
        return Redis::pipeline(function ($pipe) use ($counters) {
            foreach ($counters as $key => $amount) {
                $pipe->incrby($key, $amount);
            }
        });
    }
}

// Usage
$results = $batch->incrementMany([
    'page:views:home' => 1,
    'page:views:about' => 1,
    'api:calls:total' => 5,
]);
```

### 3. Multi-Key Cache Fetch

```php
class CacheFetcher
{
    public function getMany(array $keys): array
    {
        $results = Redis::pipeline(function ($pipe) use ($keys) {
            foreach ($keys as $key) {
                $pipe->get($key);
            }
        });

        $data = [];
        foreach ($keys as $i => $key) {
            if ($results[$i] !== null) {
                $data[$key] = unserialize($results[$i]);
            }
        }

        return $data;
    }
}
```

### 4. Dashboard Data Aggregation

```php
class DashboardLoader
{
    public function loadStats(int $userId): array
    {
        $results = Redis::pipeline(function ($pipe) use ($userId) {
            $pipe->get("stats:user:{$userId}:views");
            $pipe->get("stats:user:{$userId}:clicks");
            $pipe->zcard("followers:{$userId}");
            $pipe->zcard("following:{$userId}");
            $pipe->lrange("notifications:{$userId}", 0, 4);
        });

        return [
            'views' => (int) $results[0],
            'clicks' => (int) $results[1],
            'followers' => $results[2],
            'following' => $results[3],
            'notifications' => $results[4],
        ];
    }
}
```

### 5. Pattern-Based Deletion

```php
class PatternDeleter
{
    public function deletePattern(string $pattern, int $batchSize = 1000): int
    {
        $deleted = 0;
        $cursor = 0;

        do {
            [$cursor, $keys] = Redis::scan($cursor, 'MATCH', $pattern, 'COUNT', $batchSize);

            if (!empty($keys)) {
                // Delete in batches via pipeline
                Redis::pipeline(function ($pipe) use ($keys) {
                    foreach ($keys as $key) {
                        $pipe->unlink($key);
                    }
                });
                $deleted += count($keys);
            }
        } while ($cursor != 0);

        return $deleted;
    }
}
```

---

## Chunked Pipelines

For very large operations, chunk to avoid memory issues:

```php
class ChunkedPipeline
{
    public function setMany(array $data, int $chunkSize = 1000): void
    {
        foreach (array_chunk($data, $chunkSize, true) as $chunk) {
            Redis::pipeline(function ($pipe) use ($chunk) {
                foreach ($chunk as $key => $value) {
                    $pipe->set($key, $value);
                }
            });
        }
    }

    public function getMany(array $keys, int $chunkSize = 1000): array
    {
        $results = [];

        foreach (array_chunk($keys, $chunkSize) as $chunk) {
            $chunkResults = Redis::pipeline(function ($pipe) use ($chunk) {
                foreach ($chunk as $key) {
                    $pipe->get($key);
                }
            });

            foreach ($chunk as $i => $key) {
                $results[$key] = $chunkResults[$i];
            }
        }

        return $results;
    }
}
```

---

## Pipeline vs MGET/MSET

### When to Use MGET/MSET

```php
// Simple string key-value operations
$values = Redis::mget(['key1', 'key2', 'key3']);
Redis::mset(['key1' => 'val1', 'key2' => 'val2']);
```

### When to Use Pipeline

```php
// Mixed operations
Redis::pipeline(function ($pipe) {
    $pipe->get('key1');
    $pipe->hgetall('hash1');
    $pipe->lrange('list1', 0, -1);
    $pipe->incr('counter');
});

// Operations with TTL
Redis::pipeline(function ($pipe) {
    $pipe->set('key1', 'value1');
    $pipe->expire('key1', 3600);
});
```

---

## Transactions vs Pipelines

| Feature | Pipeline | Transaction (MULTI/EXEC) |
|---------|----------|-------------------------|
| Round trips | 1 | 1 |
| Atomic | No | Yes |
| Can be interrupted | Yes | No |
| WATCH support | No | Yes |
| Use case | Performance | Consistency |

### Transaction Pipeline

```php
// Atomic pipeline with MULTI/EXEC
$results = Redis::transaction(function ($tx) {
    $tx->incr('counter1');
    $tx->incr('counter2');
    $tx->decr('counter3');
});
// All succeed or all fail
```

---

## Error Handling

```php
try {
    $results = Redis::pipeline(function ($pipe) use ($keys) {
        foreach ($keys as $key) {
            $pipe->get($key);
        }
    });

    // Check individual results for errors
    foreach ($results as $i => $result) {
        if ($result instanceof \Exception) {
            Log::error("Pipeline command {$i} failed", [
                'key' => $keys[$i],
                'error' => $result->getMessage(),
            ]);
        }
    }
} catch (\Exception $e) {
    Log::error("Pipeline failed", ['error' => $e->getMessage()]);
}
```

---

## BudTags Usage

### Metrc Cache Warming

```php
class MetrcCacheWarmer
{
    public function warmPackageCache(string $facility, array $packages): void
    {
        $chunks = array_chunk($packages, 500);

        foreach ($chunks as $chunk) {
            Redis::pipeline(function ($pipe) use ($facility, $chunk) {
                foreach ($chunk as $package) {
                    $key = "metrc:{$facility}:package:{$package['Id']}";
                    $pipe->setex($key, 3600, json_encode($package));
                }
            });
        }
    }
}
```

### Batch Counter Updates

```php
class SyncProgressTracker
{
    public function updateCounters(string $syncId, array $updates): void
    {
        Redis::pipeline(function ($pipe) use ($syncId, $updates) {
            foreach ($updates as $field => $increment) {
                $pipe->hincrby("sync:{$syncId}:progress", $field, $increment);
            }
            $pipe->expire("sync:{$syncId}:progress", 86400);
        });
    }
}
```

---

## Key Takeaways

1. **Reduces round trips** - 10-200x faster for bulk operations
2. **Use for multiple commands** - Not single operations
3. **Chunk large batches** - Avoid memory issues
4. **Results in order** - Same order as commands
5. **Not atomic** - Use transactions if needed
6. **Combine with SCAN** - For pattern operations
7. **Works with all commands** - Not just GET/SET
8. **Monitor memory** - Large pipelines buffer in memory
