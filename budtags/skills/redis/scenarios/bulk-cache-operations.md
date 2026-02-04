# Scenario: Bulk Cache Operations

Handling large datasets efficiently requires chunking, batch operations, and careful memory management.

---

## Paginated API Fetching with Caching

### Pattern: Fetch All Pages, Cache Once

From `MetrcApi.php:357-391`:

```php
public function all_active_packages(string $facility, bool $force_fetch = false): array {
    return $this->fetch_from_cache_or_api(
        "metrc:all-active-packages:{$facility}",
        function () use ($facility) {
            $start_date = Carbon::parse($this->get_facility_credentialed_date($facility))->startOfDay();
            $end_date = Carbon::now()->endOfDay();

            $packages = [];
            $pageNum = 1;

            while (true) {
                $res = $this->get('/packages/v2/active', [
                    'licenseNumber' => $facility,
                    'lastModifiedStart' => $start_date->format('c'),
                    'lastModifiedEnd' => $end_date->format('c'),
                    'pageNumber' => $pageNum,
                    'pageSize' => 20,  // Metrc max
                ]);

                $packages = [...$packages, ...$res->json('Data')];

                if ($res->json('Page') >= $res->json('TotalPages')) {
                    break;
                }

                usleep(200000);  // 200ms delay for rate limiting
                $pageNum++;
            }

            return $packages;
        },
        fn($pkg) => "metrc:package:{$pkg['Label']}",  // Also cache individually
        $force_fetch,
        43200,  // 12 hours
    );
}
```

---

## Cache History from Multiple Days

### Pattern: Iterate Days, Check Cache

From `MetrcApi.php:480-517`:

```php
public function get_history_from_cache(string $facility, Carbon $start_day, int $days = 30): array {
    $res = [];
    $seen_ids = [];  // Track IDs to prevent duplicates

    for ($i = 0; $i < $days; $i++) {
        $date = $start_day->isoFormat('M/D/Y');
        $key = "metrc:day-of-packages:{$facility}:{$date}";

        if (Cache::has($key)) {
            $day_packages = Cache::get($key);
            $original_count = count($day_packages);

            // Filter out duplicates (packages seen in more recent days)
            $unique_packages = array_filter($day_packages, function ($pkg) use (&$seen_ids) {
                $id = $pkg['Id'];
                if (isset($seen_ids[$id])) {
                    return false;  // Skip - already have newer version
                }
                $seen_ids[$id] = true;
                return true;
            });

            // Self-healing: clean duplicates from cache
            $unique_packages = array_values($unique_packages);
            if (count($unique_packages) < $original_count) {
                Cache::set($key, $unique_packages, self::DEFAULT_CACHE_TIME);
            }

            $res[] = [
                'date' => new Carbon($start_day),
                'packages' => $unique_packages,
            ];
        }

        $start_day->subDays(1);
    }

    return $res;
}
```

---

## Bulk Cache Deletion

### Pattern: Remove Items from Multiple Day Caches

From `MetrcApi.php:564-602`:

```php
public function remove_packages_from_past_caches(
    string $license,
    array $package_labels,
    int $days_back = 365,
    bool $include_inactive = false
): void {
    if (empty($package_labels)) {
        return;
    }

    $date = now()->copy();
    $labels_set = array_flip($package_labels);  // O(1) lookup

    for ($i = 0; $i < $days_back; $i++) {
        $date_str = $date->isoFormat('M/D/Y');

        // Active packages
        $key = "metrc:day-of-packages:{$license}:{$date_str}";
        if (Cache::has($key)) {
            $packages = collect(Cache::get($key))->filter(
                fn($pkg) => !isset($labels_set[$pkg['Label']])
            );
            Cache::set($key, $packages->values()->toArray(), self::DEFAULT_CACHE_TIME);
        }

        // Inactive packages (if requested)
        if ($include_inactive) {
            $inactive_key = "metrc:day-of-inactive-packages:{$license}:{$date_str}";
            if (Cache::has($inactive_key)) {
                $packages = collect(Cache::get($inactive_key))->filter(
                    fn($pkg) => !isset($labels_set[$pkg['Label']])
                );
                Cache::set($inactive_key, $packages->values()->toArray(), 60*60*24*30);
            }
        }

        $date->subDay();
    }
}
```

---

## Chunked Processing Pattern

### When to Chunk

| Data Size | Strategy |
|-----------|----------|
| < 100 items | Process all at once |
| 100-1000 items | Chunk by 50-100 |
| > 1000 items | Chunk by 100, consider queue jobs |

### Implementation

```php
public function process_large_dataset(array $items): void {
    $chunks = array_chunk($items, 100);

    foreach ($chunks as $index => $chunk) {
        // Process chunk
        foreach ($chunk as $item) {
            $this->processItem($item);
        }

        // Cache progress (optional)
        $processed = ($index + 1) * count($chunk);
        Cache::put("progress:dataset", [
            'processed' => $processed,
            'total' => count($items),
        ], 3600);

        // Prevent memory issues
        gc_collect_cycles();

        // Log progress
        if ($index % 10 === 0) {
            LogService::store('BulkProcess', "Processed {$processed} of " . count($items));
        }
    }
}
```

---

## Cache Rebuild Pattern

### Full Rebuild (DevController style)

```php
public function rebuild_package_cache(string $facility): array {
    // Clear existing cache
    Redis::command('select', [1]);
    $keys = Redis::command('keys', ["*day-of-packages:{$facility}*"]);
    foreach ($keys as $key) {
        Redis::command('del', [$key]);
    }

    // Fetch fresh data day by day
    $results = [];
    $date = now();

    for ($i = 0; $i < 30; $i++) {
        $packages = $this->one_day_of_packages($facility, $date->copy(), true);  // Force fetch
        $results[$date->isoFormat('M/D/Y')] = count($packages);
        $date->subDay();
    }

    return $results;
}
```

### Incremental Rebuild (Today only)

```php
public function refresh_today_cache(string $facility): int {
    $today = now();
    $cache_key = "metrc:day-of-packages:{$facility}:{$today->isoFormat('M/D/Y')}";

    // Force fetch today's data
    Cache::forget($cache_key);
    $packages = $this->one_day_of_packages($facility, $today, true);

    LogService::store('CacheRefresh', "Refreshed {$facility} today cache: " . count($packages) . " packages");

    return count($packages);
}
```

---

## Memory-Efficient Patterns

### Stream Processing

```php
public function export_cached_packages(string $facility, string $outputPath): void {
    $handle = fopen($outputPath, 'w');
    fputcsv($handle, ['Label', 'ProductName', 'Quantity']);

    $date = now();
    for ($i = 0; $i < 30; $i++) {
        $key = "metrc:day-of-packages:{$facility}:{$date->isoFormat('M/D/Y')}";

        if (Cache::has($key)) {
            $packages = Cache::get($key);
            foreach ($packages as $pkg) {
                fputcsv($handle, [
                    $pkg['Label'],
                    $pkg['ProductName'] ?? '',
                    $pkg['Quantity'] ?? 0,
                ]);
            }
            unset($packages);  // Free memory
        }

        $date->subDay();
    }

    fclose($handle);
}
```

---

## Batch Prefetching

### Lab Results Batch Prefetch

From `MetrcApi.php:922-993`:

```php
public function prefetch_lab_results_for_batch(array $tags, string $facility): array {
    if (empty($tags)) {
        return [];
    }

    // Fetch package data for all tags
    $packages = [];
    foreach ($tags as $tag) {
        try {
            $packages[$tag] = $this->package($tag);
        } catch (\Exception $e) {
            continue;  // Skip failures
        }
    }

    // Group by source package (lab results shared among siblings)
    $source_groups = [];
    foreach ($packages as $tag => $pkg) {
        $sources = $pkg['SourcePackageLabels'] ?? '';
        $first_source = trim(explode(',', $sources)[0] ?? '') ?: $tag;

        if (!isset($source_groups[$first_source])) {
            $source_groups[$first_source] = [
                'id' => (int) $pkg['Id'],
                'tags' => [],
            ];
        }
        $source_groups[$first_source]['tags'][] = $tag;
    }

    // Fetch and cache by source (one API call per unique source)
    $results = [];
    foreach ($source_groups as $source_label => $group) {
        $cache_key = "metrc:lab-results-by-source:{$facility}:{$source_label}";

        if (Cache::has($cache_key)) {
            $results[$source_label] = Cache::get($cache_key);
            continue;
        }

        try {
            $lab_data = $this->get('/labtests/v2/results', [
                'packageId' => $group['id'],
                'licenseNumber' => $facility,
            ])->json('Data');

            Cache::put($cache_key, $lab_data, self::DEFAULT_CACHE_TIME);
            Cache::put("metrc:lab-results:{$group['id']}", $lab_data, self::DEFAULT_CACHE_TIME);
            $results[$source_label] = $lab_data;
        } catch (\Exception $e) {
            LogService::store('LabResultsPrefetch', "Failed for source {$source_label}");
        }
    }

    return $results;
}
```

---

## Anti-Patterns

```php
// ❌ WRONG: Loading all data into memory
$allPackages = [];
for ($i = 0; $i < 365; $i++) {
    $allPackages = array_merge($allPackages, Cache::get($key) ?? []);
}
// Memory explosion with large datasets!

// ✅ CORRECT: Process day by day
for ($i = 0; $i < 365; $i++) {
    $dayPackages = Cache::get($key) ?? [];
    foreach ($dayPackages as $pkg) {
        $this->processPackage($pkg);
    }
    unset($dayPackages);  // Free memory
}

// ❌ WRONG: No rate limiting in bulk fetch
while (true) {
    $res = $this->get('/packages/v2/active', [...]);
    if ($res->json('Page') >= $res->json('TotalPages')) break;
    // No delay!
}

// ✅ CORRECT: Add delay between requests
usleep(200000);  // 200ms
```
