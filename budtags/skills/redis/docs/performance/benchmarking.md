# Redis Benchmarking

Tools and techniques for measuring Redis performance.

---

## redis-benchmark

### Basic Usage

```bash
# Default benchmark (50 clients, 100K requests)
redis-benchmark

# Custom configuration
redis-benchmark -h localhost -p 6379 -c 50 -n 100000
```

### Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `-h` | Host | 127.0.0.1 |
| `-p` | Port | 6379 |
| `-c` | Concurrent connections | 50 |
| `-n` | Total requests | 100000 |
| `-d` | Data size (bytes) | 3 |
| `-t` | Specific tests | all |
| `-q` | Quiet mode (just RPS) | off |
| `-P` | Pipeline requests | 1 |
| `--csv` | CSV output | off |

### Specific Command Tests

```bash
# Test specific commands
redis-benchmark -t get,set,lpush,lpop -q

# Output:
# SET: 110000 requests per second
# GET: 120000 requests per second
# LPUSH: 115000 requests per second
# LPOP: 115000 requests per second
```

### Pipeline Benchmark

```bash
# Test with pipelining (16 commands per request)
redis-benchmark -t set,get -P 16 -q

# Output:
# SET: 850000 requests per second
# GET: 900000 requests per second
```

### Larger Data Sizes

```bash
# Test with 1KB values
redis-benchmark -t set,get -d 1024 -q

# Test with 10KB values
redis-benchmark -t set,get -d 10240 -q
```

---

## Expected Baseline Performance

### Single Node (Modern Hardware)

| Operation | Ops/sec | Notes |
|-----------|---------|-------|
| GET/SET (small) | 100K-150K | ~10μs latency |
| INCR | 100K-150K | Atomic counter |
| LPUSH/LPOP | 100K-150K | List operations |
| HSET/HGET | 80K-120K | Hash operations |
| ZADD | 50K-80K | Sorted set add |
| ZRANGE (10) | 60K-100K | Sorted set range |

### With Pipelining

| Pipeline Size | Multiplier |
|--------------|------------|
| 1 (no pipeline) | 1x |
| 10 | 5-8x |
| 50 | 8-12x |
| 100 | 10-15x |

---

## Laravel Benchmark Script

### Basic Benchmark

```php
class RedisBenchmark
{
    public function run(int $iterations = 10000): array
    {
        $results = [];

        // String operations
        $results['set'] = $this->benchmark(
            fn() => Redis::set('bench:key', 'value'),
            $iterations
        );

        $results['get'] = $this->benchmark(
            fn() => Redis::get('bench:key'),
            $iterations
        );

        // Counter operations
        $results['incr'] = $this->benchmark(
            fn() => Redis::incr('bench:counter'),
            $iterations
        );

        // Hash operations
        $results['hset'] = $this->benchmark(
            fn() => Redis::hset('bench:hash', 'field', 'value'),
            $iterations
        );

        $results['hget'] = $this->benchmark(
            fn() => Redis::hget('bench:hash', 'field'),
            $iterations
        );

        // List operations
        $results['lpush'] = $this->benchmark(
            fn() => Redis::lpush('bench:list', 'value'),
            $iterations
        );

        // Cleanup
        Redis::del('bench:key', 'bench:counter', 'bench:hash', 'bench:list');

        return $results;
    }

    private function benchmark(callable $operation, int $iterations): array
    {
        $start = microtime(true);

        for ($i = 0; $i < $iterations; $i++) {
            $operation();
        }

        $elapsed = microtime(true) - $start;

        return [
            'iterations' => $iterations,
            'total_ms' => round($elapsed * 1000, 2),
            'ops_per_sec' => round($iterations / $elapsed),
            'avg_ms' => round(($elapsed / $iterations) * 1000, 4),
        ];
    }
}
```

### Pipeline vs Non-Pipeline Comparison

```php
class PipelineBenchmark
{
    public function compare(int $operations = 1000): array
    {
        // Without pipeline
        $start = microtime(true);
        for ($i = 0; $i < $operations; $i++) {
            Redis::set("bench:np:{$i}", $i);
        }
        $noPipelineTime = microtime(true) - $start;

        // With pipeline
        $start = microtime(true);
        Redis::pipeline(function ($pipe) use ($operations) {
            for ($i = 0; $i < $operations; $i++) {
                $pipe->set("bench:p:{$i}", $i);
            }
        });
        $pipelineTime = microtime(true) - $start;

        // Cleanup
        Redis::pipeline(function ($pipe) use ($operations) {
            for ($i = 0; $i < $operations; $i++) {
                $pipe->del("bench:np:{$i}", "bench:p:{$i}");
            }
        });

        return [
            'operations' => $operations,
            'no_pipeline_ms' => round($noPipelineTime * 1000, 2),
            'pipeline_ms' => round($pipelineTime * 1000, 2),
            'speedup' => round($noPipelineTime / $pipelineTime, 2) . 'x',
        ];
    }
}
```

---

## Latency Monitoring

### LATENCY Commands

```bash
# Enable latency monitoring
redis-cli CONFIG SET latency-monitor-threshold 100

# Get latency history
redis-cli LATENCY HISTORY command

# Get latest latency samples
redis-cli LATENCY LATEST

# Get latency doctor report
redis-cli LATENCY DOCTOR
```

### Laravel Latency Check

```php
class LatencyMonitor
{
    public function measure(int $samples = 100): array
    {
        $latencies = [];

        for ($i = 0; $i < $samples; $i++) {
            $start = hrtime(true);
            Redis::ping();
            $latencies[] = (hrtime(true) - $start) / 1e6; // Convert to ms
        }

        sort($latencies);

        return [
            'samples' => $samples,
            'min_ms' => round(min($latencies), 3),
            'max_ms' => round(max($latencies), 3),
            'avg_ms' => round(array_sum($latencies) / $samples, 3),
            'p50_ms' => round($latencies[(int) ($samples * 0.5)], 3),
            'p95_ms' => round($latencies[(int) ($samples * 0.95)], 3),
            'p99_ms' => round($latencies[(int) ($samples * 0.99)], 3),
        ];
    }
}
```

---

## Memory Benchmark

```php
class MemoryBenchmark
{
    public function measureKeyOverhead(): array
    {
        $results = [];

        // Baseline memory
        $baseline = Redis::info('memory')['used_memory'];

        // Test string keys
        $stringMem = $this->measureType('string', function ($i) {
            Redis::set("bench:string:{$i}", 'value');
        }, 10000);

        // Test hash keys
        $hashMem = $this->measureType('hash', function ($i) {
            Redis::hset("bench:hash:{$i}", 'field', 'value');
        }, 10000);

        // Test in single hash (bucketing)
        Redis::del('bench:bucket');
        $bucketStart = Redis::info('memory')['used_memory'];
        for ($i = 0; $i < 10000; $i++) {
            Redis::hset('bench:bucket', "field:{$i}", 'value');
        }
        $bucketMem = Redis::info('memory')['used_memory'] - $bucketStart;
        Redis::del('bench:bucket');

        return [
            'string_keys_10k' => $this->formatBytes($stringMem),
            'hash_keys_10k' => $this->formatBytes($hashMem),
            'single_hash_10k_fields' => $this->formatBytes($bucketMem),
            'savings_with_bucketing' => round((1 - $bucketMem / $hashMem) * 100, 1) . '%',
        ];
    }

    private function measureType(string $type, callable $creator, int $count): int
    {
        $start = Redis::info('memory')['used_memory'];

        for ($i = 0; $i < $count; $i++) {
            $creator($i);
        }

        $used = Redis::info('memory')['used_memory'] - $start;

        // Cleanup
        Redis::pipeline(function ($pipe) use ($type, $count) {
            for ($i = 0; $i < $count; $i++) {
                $pipe->del("bench:{$type}:{$i}");
            }
        });

        return $used;
    }

    private function formatBytes(int $bytes): string
    {
        return round($bytes / 1024, 2) . ' KB';
    }
}
```

---

## Artisan Benchmark Command

```php
// app/Console/Commands/RedisBenchmarkCommand.php
class RedisBenchmarkCommand extends Command
{
    protected $signature = 'redis:benchmark
        {--iterations=10000 : Number of iterations per test}
        {--pipeline : Include pipeline comparison}';

    protected $description = 'Run Redis performance benchmarks';

    public function handle(): void
    {
        $iterations = $this->option('iterations');

        $this->info("Running Redis benchmark ({$iterations} iterations)...\n");

        // Basic operations
        $benchmark = new RedisBenchmark();
        $results = $benchmark->run($iterations);

        $this->table(
            ['Operation', 'Total (ms)', 'Ops/sec', 'Avg (ms)'],
            collect($results)->map(fn($r, $op) => [
                $op,
                $r['total_ms'],
                number_format($r['ops_per_sec']),
                $r['avg_ms'],
            ])->toArray()
        );

        // Pipeline comparison
        if ($this->option('pipeline')) {
            $this->info("\nPipeline comparison (1000 operations):\n");

            $pipeline = new PipelineBenchmark();
            $comparison = $pipeline->compare(1000);

            $this->table(
                ['Metric', 'Value'],
                [
                    ['Without pipeline', $comparison['no_pipeline_ms'] . 'ms'],
                    ['With pipeline', $comparison['pipeline_ms'] . 'ms'],
                    ['Speedup', $comparison['speedup']],
                ]
            );
        }

        // Latency
        $this->info("\nLatency measurement:\n");
        $latency = (new LatencyMonitor())->measure(100);

        $this->table(
            ['Metric', 'Value'],
            [
                ['Min', $latency['min_ms'] . 'ms'],
                ['Max', $latency['max_ms'] . 'ms'],
                ['Average', $latency['avg_ms'] . 'ms'],
                ['P95', $latency['p95_ms'] . 'ms'],
                ['P99', $latency['p99_ms'] . 'ms'],
            ]
        );
    }
}
```

---

## Performance Targets

### BudTags Recommendations

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| GET latency | < 1ms | > 5ms | > 10ms |
| SET latency | < 1ms | > 5ms | > 10ms |
| P99 latency | < 5ms | > 10ms | > 50ms |
| Ops/sec | > 50K | < 20K | < 5K |

### Monitoring Alerts

```php
Schedule::call(function () {
    $latency = (new LatencyMonitor())->measure(100);

    if ($latency['p99_ms'] > 10) {
        Log::warning('Redis P99 latency high', $latency);
    }

    if ($latency['p99_ms'] > 50) {
        Log::error('Redis P99 latency critical', $latency);
    }
})->everyFiveMinutes();
```

---

## Key Takeaways

1. **redis-benchmark** - Quick baseline testing
2. **Pipeline multiplier** - 10-15x with batching
3. **Measure latency** - P95/P99 matter more than average
4. **Test your patterns** - Benchmark actual usage
5. **Memory overhead** - Test key structure efficiency
6. **Set targets** - Define acceptable thresholds
7. **Monitor continuously** - Not just one-time tests
8. **Compare clients** - phpredis vs Predis
