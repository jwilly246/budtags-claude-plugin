# Scenario: Pattern-Based Deletion

Pattern-based deletion allows clearing multiple cache keys that match a wildcard pattern. This is essential for cache management and debugging.

---

## DevController Pattern

From `app/Http/Controllers/DevController.php:94-110`:

```php
public function forget_cache(): RedirectResponse {
    request()->validate([
        'key' => 'string|required',
    ]);

    $k = request()->key;
    $k = "*{$k}*";  // Wrap in wildcards

    Redis::command('select', [1]);  // Switch to cache DB
    $keys = Redis::command('keys', [$k]);

    foreach ($keys as $key) {
        Redis::command('del', [$key]);
    }

    $count = count($keys);

    return redirect()->back()->with('message', "Deleted {$count} items from the cache.");
}
```

### Key Points

1. **DB Selection**: Must select DB 1 (cache) before operations
2. **Pattern Wrapping**: Wrap user input in wildcards for flexible matching
3. **Iteration**: Delete keys one at a time (no bulk delete with patterns)
4. **Feedback**: Return count of deleted keys

---

## Common Deletion Patterns

### Clear All Facility Data

```php
public function clear_facility_cache(string $facility): int {
    Redis::command('select', [1]);

    $patterns = [
        "*:{$facility}",           // metrc:packages:AU-P-000001
        "*:{$facility}:*",         // metrc:day-of-packages:AU-P-000001:1/15/2025
    ];

    $deleted = 0;
    foreach ($patterns as $pattern) {
        $keys = Redis::command('keys', [$pattern]);
        foreach ($keys as $key) {
            Redis::command('del', [$key]);
            $deleted++;
        }
    }

    return $deleted;
}
```

### Clear Day Caches

```php
public function clear_day_caches(string $facility, ?Carbon $date = null): int {
    Redis::command('select', [1]);

    $datePattern = $date ? $date->isoFormat('M/D/Y') : '*';
    $patterns = [
        "metrc:day-of-packages:{$facility}:{$datePattern}",
        "metrc:day-of-inactive-packages:{$facility}:{$datePattern}",
        "metrc:day-of-plants:{$facility}:{$datePattern}",
        "metrc:day-of-harvests:{$facility}:{$datePattern}",
    ];

    $deleted = 0;
    foreach ($patterns as $pattern) {
        $keys = Redis::command('keys', [$pattern]);
        foreach ($keys as $key) {
            Redis::command('del', [$key]);
            $deleted++;
        }
    }

    return $deleted;
}
```

### Clear Entity Type

```php
public function clear_entity_cache(string $entity): int {
    Redis::command('select', [1]);

    $pattern = "metrc:{$entity}:*";
    $keys = Redis::command('keys', [$pattern]);

    foreach ($keys as $key) {
        Redis::command('del', [$key]);
    }

    return count($keys);
}

// Usage
$deleted = $this->clear_entity_cache('package');  // All package caches
$deleted = $this->clear_entity_cache('plant');    // All plant caches
```

---

## Cache Statistics Helper

From `DevController.php:46-55`:

```php
public function get_cache_stats(): array {
    try {
        Redis::command('select', [1]);

        $keyCount = Redis::command('dbsize');

        $facilitiesWithHistory = collect(Redis::command('keys', ['*day-of-packages*']))
            ->map(fn($key) => preg_replace("/^.+day-of-packages:([a-zA-Z0-9\-]+):.+$/", '$1', $key))
            ->unique()
            ->values();

        return [
            'key_count' => $keyCount,
            'facilities_with_history' => $facilitiesWithHistory,
        ];

    } catch (Exception $e) {
        return [
            'key_count' => 0,
            'facilities_with_history' => [],
        ];
    }
}
```

---

## Flush All Cache

From `DevController.php:89-93`:

```php
public function clear_cache(): RedirectResponse {
    Cache::flush();

    return redirect()->back()->with('message', 'Flushed the entire app cache');
}
```

**Warning**: This clears ALL cached data. Use sparingly in production.

---

## Safe Deletion Patterns

### Preview Before Delete

```php
public function preview_deletion(string $pattern): array {
    Redis::command('select', [1]);

    $fullPattern = "*{$pattern}*";
    $keys = Redis::command('keys', [$fullPattern]);

    return [
        'pattern' => $fullPattern,
        'count' => count($keys),
        'sample' => array_slice($keys, 0, 10),  // Show first 10
    ];
}

// Usage: Preview what would be deleted
$preview = $this->preview_deletion('day-of-packages:AU-P-000001');
// Returns: { pattern: "*day-of-packages:AU-P-000001*", count: 30, sample: [...] }
```

### Confirm Before Large Deletion

```php
public function delete_with_confirmation(string $pattern, bool $confirmed = false): array {
    $preview = $this->preview_deletion($pattern);

    if (!$confirmed) {
        return [
            'action' => 'preview',
            'message' => "Would delete {$preview['count']} keys. Pass confirmed=true to proceed.",
            ...$preview,
        ];
    }

    if ($preview['count'] > 1000) {
        return [
            'action' => 'blocked',
            'message' => "Refusing to delete {$preview['count']} keys. Use batch deletion for large operations.",
        ];
    }

    $deleted = $this->delete_by_pattern($pattern);

    return [
        'action' => 'deleted',
        'count' => $deleted,
    ];
}
```

---

## Batch Deletion for Large Datasets

```php
public function batch_delete(string $pattern, int $batchSize = 100): array {
    Redis::command('select', [1]);

    $fullPattern = "*{$pattern}*";
    $totalDeleted = 0;
    $batches = 0;

    while (true) {
        $keys = Redis::command('keys', [$fullPattern]);

        if (empty($keys)) {
            break;
        }

        $batch = array_slice($keys, 0, $batchSize);

        foreach ($batch as $key) {
            Redis::command('del', [$key]);
            $totalDeleted++;
        }

        $batches++;

        // Prevent runaway deletion
        if ($batches > 100) {
            LogService::store('CacheDeletion', "Batch limit reached, stopping. Deleted {$totalDeleted} keys.");
            break;
        }

        // Small delay to prevent overwhelming Redis
        usleep(10000);  // 10ms
    }

    return [
        'deleted' => $totalDeleted,
        'batches' => $batches,
    ];
}
```

---

## Invalidation Helpers from MetrcApi

### Specific Entity Invalidation

```php
// From MetrcApi.php:612-621
public function invalidate_package_caches(string $facility, array $labels = []): void {
    $today = now()->isoFormat('M/D/Y');

    Cache::forget("metrc:day-of-packages:{$facility}:{$today}");
    Cache::forget("metrc:day-of-inactive-packages:{$facility}:{$today}");
    Cache::forget("metrc:package-available-tags:{$facility}");

    foreach ($labels as $label) {
        Cache::forget("metrc:package:{$label}");
    }
}

// From MetrcApi.php:643-647
public function invalidate_harvest_caches(string $facility): void {
    $today = now()->isoFormat('M/D/Y');

    Cache::forget("metrc:day-of-harvests:{$facility}:{$today}");
    Cache::forget("metrc:day-of-inactive-harvests:{$facility}:{$today}");
}
```

---

## Anti-Patterns

```php
// ❌ WRONG: Forgetting to select cache DB
$keys = Redis::command('keys', ['*pattern*']);  // Searches wrong DB!

// ✅ CORRECT: Always select DB 1
Redis::command('select', [1]);
$keys = Redis::command('keys', ['*pattern*']);

// ❌ WRONG: Using Cache::flush() liberally
Cache::flush();  // Deletes EVERYTHING

// ✅ CORRECT: Use targeted deletion
$this->delete_by_pattern('specific:pattern');

// ❌ WRONG: No limits on large deletions
$keys = Redis::command('keys', ['*']);  // Could be millions!
foreach ($keys as $key) {
    Redis::command('del', [$key]);
}

// ✅ CORRECT: Batch with limits
$this->batch_delete('pattern', 100);

// ❌ WRONG: Using keys command in production loops
// KEYS is O(N) and blocks Redis during execution
while (true) {
    $keys = Redis::command('keys', ['*']);  // Dangerous!
}

// ✅ CORRECT: Use SCAN for production (if needed)
// But prefer targeted Cache::forget() calls
```

---

## Key Patterns for Deletion

| Goal | Pattern | Example |
|------|---------|---------|
| All facility data | `*:{facility}*` | `*:AU-P-000001*` |
| Specific day | `*:{facility}:{date}` | `*:AU-P-000001:1/15/2025` |
| All day caches | `*day-of-*` | `*day-of-packages*` |
| Entity type | `metrc:{entity}:*` | `metrc:package:*` |
| Inactive data | `*inactive*` | `*inactive-packages*` |
| Temporary counters | `*_success:*` | `*label_group_success:*` |
