# Scenario: Atomic Counters

Redis atomic counters are essential for tracking progress in concurrent/background jobs without database overhead or race conditions.

---

## Primary Use Case: Label Generation Progress

From `app/Jobs/GeneratePackageLabel.php:52-58`:

```php
use Illuminate\Support\Facades\Redis;

// In job handle() method
try {
    $service->build_label($label, $this->group);

    // Use Redis atomic increment for fast success counting
    $successCount = 1;
    if ($this->group) {
        $key = "label_group_success:{$this->group->id}";
        $successCount = (int) Redis::incr($key);
        Redis::expire($key, 3600);  // Clean up after 1 hour
    }

    broadcast(new LabelCreated($label, $successCount));

} catch (\Exception $e) {
    // Handle failure...
}
```

### Why This Pattern Works

1. **Atomic**: `Redis::incr` is thread-safe - multiple workers won't conflict
2. **Fast**: No database queries needed for counting
3. **Self-cleaning**: `expire` ensures keys are cleaned up automatically
4. **Returns new value**: `incr` returns the new count, useful for broadcasting

---

## Implementation Pattern

### Basic Counter

```php
$key = "counter:{$entity}:{$id}";

// Increment and get new value
$count = (int) Redis::incr($key);

// Set expiration (always do this!)
Redis::expire($key, 3600);  // 1 hour
```

### Counter with Initialization

```php
$key = "progress:{$batchId}";

// incr initializes to 1 if key doesn't exist
$current = (int) Redis::incr($key);

// First increment? Set longer expiration
if ($current === 1) {
    Redis::expire($key, 7200);  // 2 hours for batch jobs
}
```

### Decrement Counter

```php
$key = "remaining:{$jobId}";

// Initialize with total
Redis::set($key, $totalItems);
Redis::expire($key, 3600);

// Decrement as items complete
$remaining = (int) Redis::decr($key);

if ($remaining === 0) {
    // All items processed
    $this->onBatchComplete();
}
```

---

## Progress Tracking Pattern

### Batch Job with Progress Broadcast

```php
class ProcessBatchJob implements ShouldQueue {
    public function handle(): void {
        $total = count($this->items);
        $progressKey = "batch_progress:{$this->batchId}";

        // Initialize
        Redis::set($progressKey, 0);
        Redis::expire($progressKey, 7200);

        foreach ($this->items as $item) {
            try {
                $this->processItem($item);

                // Increment success counter
                $completed = (int) Redis::incr($progressKey);

                // Broadcast every 10 items or on completion
                if ($completed % 10 === 0 || $completed === $total) {
                    broadcast(new BatchProgress($this->batchId, $completed, $total));
                }

            } catch (\Exception $e) {
                // Track failures separately
                Redis::incr("{$progressKey}:failed");
                Redis::expire("{$progressKey}:failed", 7200);
            }
        }
    }
}
```

### Reading Progress

```php
public function get_batch_progress(string $batchId): array {
    $progressKey = "batch_progress:{$batchId}";

    return [
        'completed' => (int) Redis::get($progressKey) ?: 0,
        'failed' => (int) Redis::get("{$progressKey}:failed") ?: 0,
    ];
}
```

---

## Success/Failure Tracking

### Dual Counter Pattern

```php
$baseKey = "label_group:{$groupId}";

// Track successes
Redis::incr("{$baseKey}:success");
Redis::expire("{$baseKey}:success", 3600);

// Track failures
Redis::incr("{$baseKey}:failed");
Redis::expire("{$baseKey}:failed", 3600);

// Get summary
$success = (int) Redis::get("{$baseKey}:success") ?: 0;
$failed = (int) Redis::get("{$baseKey}:failed") ?: 0;
$total = $success + $failed;
```

---

## Rate Counter Pattern

### Track Events Per Time Window

```php
class RateCounter {
    public function increment(string $key): int {
        $fullKey = "rate:{$key}:" . date('Y-m-d-H-i');  // Per-minute bucket

        $count = (int) Redis::incr($fullKey);
        Redis::expire($fullKey, 120);  // Keep 2 minutes

        return $count;
    }

    public function get_rate(string $key, int $minutes = 5): int {
        $total = 0;
        $now = new \DateTime();

        for ($i = 0; $i < $minutes; $i++) {
            $bucket = "rate:{$key}:" . $now->format('Y-m-d-H-i');
            $total += (int) Redis::get($bucket) ?: 0;
            $now->modify('-1 minute');
        }

        return $total;
    }
}

// Usage
$counter = new RateCounter();
$counter->increment("api:calls:{$facility}");
$rate = $counter->get_rate("api:calls:{$facility}", 5);  // Last 5 minutes
```

---

## Comparison: Redis vs Database Counters

| Aspect | Redis Counter | Database Counter |
|--------|---------------|------------------|
| Speed | ~0.1ms | ~10-50ms |
| Concurrency | Atomic (safe) | Requires locking |
| Persistence | Volatile (ok for progress) | Persistent |
| Memory | Minimal | Table row |
| Cleanup | Automatic (expire) | Manual cleanup |

### When to Use Redis

- Progress tracking in jobs
- Rate limiting counters
- Temporary metrics
- Real-time updates

### When to Use Database

- Audit trail required
- Historical analysis
- Business-critical counts
- Long-term persistence

---

## WebSocket Integration

### Broadcasting Counter Updates

```php
// In job
$successCount = (int) Redis::incr("label_group_success:{$groupId}");
Redis::expire("label_group_success:{$groupId}", 3600);

broadcast(new LabelCreated($label, $successCount));

// Event class
class LabelCreated implements ShouldBroadcastNow {
    public function __construct(
        public LabelResults $label,
        public int $successCount,
    ) {}

    public function broadcastOn(): array {
        return [
            new PrivateChannel("org.{$this->label->org_id}"),
        ];
    }
}
```

---

## Cleanup and Maintenance

### Automatic Cleanup (Recommended)

```php
// Always set expire when incrementing
Redis::incr($key);
Redis::expire($key, 3600);  // Never forget this!
```

### Manual Cleanup (Admin)

```php
public function cleanup_old_counters(): int {
    Redis::command('select', [1]);

    $patterns = [
        'label_group_success:*',
        'batch_progress:*',
        'rate:*',
    ];

    $deleted = 0;
    foreach ($patterns as $pattern) {
        $keys = Redis::command('keys', [$pattern]);
        foreach ($keys as $key) {
            // Check TTL - delete if no expiration set
            $ttl = Redis::ttl($key);
            if ($ttl === -1) {  // No expiration
                Redis::del($key);
                $deleted++;
            }
        }
    }

    return $deleted;
}
```

---

## Anti-Patterns

```php
// ❌ WRONG: Forgetting to set expiration
Redis::incr("counter:{$id}");
// Key lives forever, memory leak!

// ✅ CORRECT: Always set expiration
Redis::incr("counter:{$id}");
Redis::expire("counter:{$id}", 3600);

// ❌ WRONG: Using database for high-frequency updates
DB::table('counters')->where('id', $id)->increment('count');
// Slow, locks table, not atomic

// ✅ CORRECT: Use Redis for real-time counters
$count = (int) Redis::incr("counter:{$id}");
// Optionally sync to DB periodically

// ❌ WRONG: String concatenation for counter value
$current = Redis::get($key);
Redis::set($key, $current + 1);
// Race condition! Not atomic!

// ✅ CORRECT: Use atomic incr
$new = Redis::incr($key);
// Atomic, safe for concurrent access
```

---

## Key Naming for Counters

```php
// Pattern: {purpose}:{scope}:{identifier}
"label_group_success:{$groupId}"     // Label generation success
"batch_progress:{$batchId}"          // Batch job progress
"batch_progress:{$batchId}:failed"   // Batch job failures
"rate:api:calls:{$facility}"         // API rate tracking
"online:users:{$orgId}"              // Online user count
```
