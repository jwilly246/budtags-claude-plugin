# Distributed Locks

Distributed locks prevent race conditions when multiple processes need exclusive access to a resource. Laravel provides `Cache::lock()` for Redis-backed atomic locking.

---

## When to Use Locks

| Scenario | Lock? | Why |
|----------|-------|-----|
| Concurrent API calls for same resource | Yes | Prevent duplicate requests |
| Batch job processing same items | Yes | Prevent duplicate processing |
| Counter increments | No | Redis::incr is atomic |
| Cache reads | No | Reads don't conflict |
| Cache writes (single process) | No | Single writer is safe |

---

## Basic Lock Pattern

```php
use Illuminate\Support\Facades\Cache;

// Acquire lock, execute, release automatically
$lock = Cache::lock("processing:package:{$label}", 30);  // 30 second timeout

if ($lock->get()) {
    try {
        // Critical section - only one process at a time
        $this->processPackage($label);
    } finally {
        $lock->release();
    }
} else {
    // Lock not acquired - another process is working on this
    LogService::store('Lock', "Package {$label} already being processed");
}
```

---

## Lock with Blocking

```php
// Block up to 10 seconds waiting for lock
$lock = Cache::lock("sync:facility:{$facility}", 60);

if ($lock->block(10)) {  // Wait up to 10 seconds
    try {
        $this->syncFacilityData($facility);
    } finally {
        $lock->release();
    }
} else {
    throw new Exception("Could not acquire lock for {$facility}");
}
```

---

## Closure-Based Lock (Recommended)

```php
// Cleaner syntax - auto-releases on completion or exception
Cache::lock("import:batch:{$batchId}", 120)->block(30, function () use ($batchId) {
    $this->importBatch($batchId);
});

// Returns result from closure
$result = Cache::lock("api:call:{$endpoint}", 60)->block(10, function () use ($endpoint) {
    return $this->makeApiCall($endpoint);
});
```

---

## BudTags Use Cases

### Preventing Duplicate Package Processing

```php
public function process_package(string $label): void {
    $lock = Cache::lock("process:package:{$label}", 120);

    if (!$lock->get()) {
        LogService::store('Duplicate', "Package {$label} already being processed, skipping");
        return;
    }

    try {
        // Fetch from Metrc
        $package = $this->metrcApi->package($label);

        // Process...

    } finally {
        $lock->release();
    }
}
```

### Preventing Duplicate Label Generation

```php
public function generate_labels(array $tags, string $facility): void {
    foreach ($tags as $tag) {
        $lockKey = "label:generate:{$facility}:{$tag}";

        $lock = Cache::lock($lockKey, 300);  // 5 min lock for label generation

        if ($lock->get()) {
            try {
                GeneratePackageLabel::dispatch($this->group, $this->options, $tag, $this->user, $facility);
            } finally {
                $lock->release();
            }
        } else {
            // Already generating this label
            LogService::store('Label', "Skipping duplicate generation for {$tag}");
        }
    }
}
```

### Serializing Metrc API Calls

```php
// Ensure only one process calls Metrc for a facility at a time
public function fetch_all_packages(string $facility): array {
    $lock = Cache::lock("metrc:fetch:{$facility}", 300);

    return $lock->block(60, function () use ($facility) {
        return $this->metrcApi->all_active_packages($facility, true);
    });
}
```

---

## Lock Timeouts

| Lock Duration | Use Case |
|---------------|----------|
| 10-30 seconds | Quick operations, API calls |
| 60-120 seconds | Data processing, imports |
| 300+ seconds | Long-running batch jobs |

```php
// Quick operation
Cache::lock("quick:op", 10)->block(5, fn() => $this->quickOp());

// Import job
Cache::lock("import:job", 300)->block(30, fn() => $this->importJob());
```

---

## Owner Tokens

For scenarios where you need to verify lock ownership:

```php
// Get lock with owner token
$lock = Cache::lock("resource:{$id}", 120);
$owner = $lock->owner();  // Unique token

if ($lock->get()) {
    // Store owner for later verification
    session(['lock_owner' => $owner]);

    // ... later ...

    // Only release if we're still the owner
    if (session('lock_owner') === $lock->owner()) {
        $lock->release();
    }
}
```

---

## Force Release (Admin)

```php
// Force release a lock (use sparingly, admin operations only)
public function force_release_lock(string $key): void {
    Cache::lock($key)->forceRelease();
    LogService::store('Admin', "Force-released lock: {$key}");
}
```

---

## Anti-Patterns

```php
// ❌ WRONG: Forgetting to release lock
$lock = Cache::lock("resource", 60);
if ($lock->get()) {
    $this->process();
    // Lock never released! Will timeout after 60s
}

// ✅ CORRECT: Always release in finally
$lock = Cache::lock("resource", 60);
if ($lock->get()) {
    try {
        $this->process();
    } finally {
        $lock->release();
    }
}

// ❌ WRONG: Lock timeout shorter than operation
$lock = Cache::lock("long:job", 10);  // 10 second lock
$lock->block(5, function () {
    $this->importData();  // Takes 60 seconds! Lock expires mid-operation
});

// ✅ CORRECT: Lock timeout > operation duration
$lock = Cache::lock("long:job", 120);  // 2 minute lock
$lock->block(30, function () {
    $this->importData();
});

// ❌ WRONG: Using lock for read operations
$lock = Cache::lock("read:data", 10);
$lock->block(5, fn() => Cache::get($key));  // Unnecessary!

// ✅ CORRECT: Just read, no lock needed
$data = Cache::get($key);
```

---

## Lock Key Naming

Follow the same conventions as cache keys:

```php
// Pattern: {action}:{entity}:{scope}
"process:package:{$label}"
"sync:facility:{$facility}"
"import:batch:{$batchId}"
"label:generate:{$facility}:{$tag}"
"metrc:fetch:{$facility}"
```
