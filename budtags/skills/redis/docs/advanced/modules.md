# Redis Modules

Extend Redis functionality with loadable modules.

---

## Overview

Redis Modules add new:
- Data types
- Commands
- Capabilities

Popular modules:
- **RediSearch** - Full-text search
- **RedisJSON** - Native JSON support
- **RedisTimeSeries** - Time-series data
- **RedisBloom** - Probabilistic data structures
- **RedisGraph** - Graph database

---

## Module Management

### Loading Modules

```
# redis.conf
loadmodule /path/to/module.so

# Multiple modules
loadmodule /path/to/redisearch.so
loadmodule /path/to/rejson.so
```

### Runtime Loading

```bash
# Load module
redis-cli MODULE LOAD /path/to/module.so

# List loaded modules
redis-cli MODULE LIST

# Unload module
redis-cli MODULE UNLOAD modulename
```

---

## RedisJSON

### Basic Operations

```php
// Set JSON
Redis::command('JSON.SET', ['user:1', '$', '{"name":"John","age":30}']);

// Get JSON
$user = Redis::command('JSON.GET', ['user:1']);

// Get specific path
$name = Redis::command('JSON.GET', ['user:1', '$.name']);

// Update nested value
Redis::command('JSON.SET', ['user:1', '$.age', '31']);

// Increment number
Redis::command('JSON.NUMINCRBY', ['user:1', '$.age', 1]);

// Append to array
Redis::command('JSON.ARRAPPEND', ['user:1', '$.tags', '"new-tag"']);
```

### Laravel Wrapper

```php
class RedisJson
{
    public function set(string $key, mixed $value, string $path = '$'): bool
    {
        return Redis::command('JSON.SET', [$key, $path, json_encode($value)]) === 'OK';
    }

    public function get(string $key, string $path = '$'): mixed
    {
        $result = Redis::command('JSON.GET', [$key, $path]);
        return $result ? json_decode($result, true) : null;
    }

    public function update(string $key, string $path, mixed $value): bool
    {
        return Redis::command('JSON.SET', [$key, $path, json_encode($value)]) === 'OK';
    }

    public function delete(string $key, string $path = '$'): int
    {
        return Redis::command('JSON.DEL', [$key, $path]);
    }
}
```

---

## RediSearch

### Create Index

```php
// Create index on hash keys
Redis::command('FT.CREATE', [
    'idx:users',
    'ON', 'HASH',
    'PREFIX', '1', 'user:',
    'SCHEMA',
    'name', 'TEXT', 'SORTABLE',
    'email', 'TEXT',
    'age', 'NUMERIC', 'SORTABLE',
    'created_at', 'NUMERIC',
]);
```

### Search

```php
// Full-text search
$results = Redis::command('FT.SEARCH', [
    'idx:users',
    '@name:John',
]);

// With filters
$results = Redis::command('FT.SEARCH', [
    'idx:users',
    '@name:John @age:[25 35]',
]);

// With sorting
$results = Redis::command('FT.SEARCH', [
    'idx:users',
    '*',
    'SORTBY', 'age', 'DESC',
    'LIMIT', '0', '10',
]);
```

### Laravel Search Service

```php
class RedisSearch
{
    public function search(string $index, string $query, array $options = []): array
    {
        $args = [$index, $query];

        if (isset($options['sortBy'])) {
            $args = array_merge($args, ['SORTBY', $options['sortBy'], $options['sortDir'] ?? 'ASC']);
        }

        if (isset($options['limit'])) {
            $args = array_merge($args, ['LIMIT', $options['offset'] ?? 0, $options['limit']]);
        }

        $result = Redis::command('FT.SEARCH', $args);

        return $this->parseSearchResults($result);
    }

    private function parseSearchResults(array $result): array
    {
        $total = $result[0];
        $docs = [];

        for ($i = 1; $i < count($result); $i += 2) {
            $key = $result[$i];
            $fields = $result[$i + 1];

            $doc = ['_key' => $key];
            for ($j = 0; $j < count($fields); $j += 2) {
                $doc[$fields[$j]] = $fields[$j + 1];
            }
            $docs[] = $doc;
        }

        return [
            'total' => $total,
            'docs' => $docs,
        ];
    }
}
```

---

## RedisTimeSeries

### Basic Operations

```php
// Create time series
Redis::command('TS.CREATE', ['temp:sensor1', 'RETENTION', 86400000]);

// Add sample
Redis::command('TS.ADD', ['temp:sensor1', '*', 23.5]);

// Add with specific timestamp
Redis::command('TS.ADD', ['temp:sensor1', time() * 1000, 24.0]);

// Get range
$data = Redis::command('TS.RANGE', [
    'temp:sensor1',
    '-',      // Start (- = beginning)
    '+',      // End (+ = now)
    'COUNT', 100,
]);

// Aggregation
$data = Redis::command('TS.RANGE', [
    'temp:sensor1',
    time() * 1000 - 3600000,  // Last hour
    '+',
    'AGGREGATION', 'avg', 60000,  // 1 minute buckets
]);
```

### Laravel Time Series

```php
class TimeSeries
{
    public function add(string $key, float $value, ?int $timestamp = null): void
    {
        $ts = $timestamp ?? '*';
        Redis::command('TS.ADD', [$key, $ts, $value]);
    }

    public function range(string $key, int $from, int $to, ?array $aggregation = null): array
    {
        $args = [$key, $from, $to];

        if ($aggregation) {
            $args = array_merge($args, [
                'AGGREGATION',
                $aggregation['type'],
                $aggregation['bucket'],
            ]);
        }

        return Redis::command('TS.RANGE', $args);
    }

    public function getLastHour(string $key, string $aggregation = 'avg'): array
    {
        return $this->range(
            $key,
            (time() - 3600) * 1000,
            time() * 1000,
            ['type' => $aggregation, 'bucket' => 60000]
        );
    }
}
```

---

## RedisBloom

### Bloom Filter

```php
// Create bloom filter
Redis::command('BF.RESERVE', ['users:seen', 0.01, 1000000]);

// Add item
Redis::command('BF.ADD', ['users:seen', 'user:123']);

// Check existence (may have false positives)
$exists = Redis::command('BF.EXISTS', ['users:seen', 'user:123']);
```

### Count-Min Sketch

```php
// Create sketch
Redis::command('CMS.INITBYPROB', ['page:views', 0.001, 0.01]);

// Increment counter
Redis::command('CMS.INCRBY', ['page:views', 'home', 1, 'about', 1]);

// Query counts
$counts = Redis::command('CMS.QUERY', ['page:views', 'home', 'about']);
```

---

## Checking Module Availability

```php
class ModuleChecker
{
    public function isLoaded(string $moduleName): bool
    {
        $modules = Redis::command('MODULE', ['LIST']);

        foreach ($modules as $module) {
            if ($module[1] === $moduleName) {
                return true;
            }
        }

        return false;
    }

    public function getLoadedModules(): array
    {
        $modules = Redis::command('MODULE', ['LIST']);

        return array_map(fn($m) => [
            'name' => $m[1],
            'version' => $m[3],
        ], $modules);
    }
}

// Usage
if ($checker->isLoaded('search')) {
    // Use RediSearch
}
```

---

## BudTags Considerations

### When to Use Modules

| Use Case | Module | Alternative |
|----------|--------|-------------|
| Full-text search | RediSearch | Elasticsearch |
| Complex JSON | RedisJSON | Serialize to string |
| Time-series | RedisTimeSeries | Sorted sets |
| Bloom filters | RedisBloom | External library |

### Deployment Considerations

1. **Redis Stack** - Pre-bundled modules
2. **Manual loading** - Add to redis.conf
3. **Cloud providers** - May not support all modules
4. **Persistence** - Module data persists with RDB/AOF

---

## Key Takeaways

1. **Extend capabilities** - Add new data types/commands
2. **loadmodule** - Configure in redis.conf
3. **MODULE LIST** - Check loaded modules
4. **Redis Stack** - Bundles popular modules
5. **Cloud limitations** - Not all providers support modules
6. **Wrapper classes** - Create Laravel-friendly interfaces
7. **Check availability** - Verify module before using
8. **Consider alternatives** - Modules add complexity
