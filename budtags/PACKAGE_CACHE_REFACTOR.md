# Package Cache Refactor - Complete Change Documentation

**Branch:** `package-cache-refactor`
**Merged:** January 31, 2026
**Commits:** 4 work units (WU-01 through WU-04)

---

## Executive Summary

This refactor replaces the "invalidate entire cache on any change" approach with **surgical cache updates** that only modify the affected packages. The key improvements:

1. **Threshold-based fetching** - Large facilities (>5000 packages) no longer bulk-fetch everything
2. **Surgical updates** - Individual package changes update only that package in cache
3. **Transfer tracking** - Outgoing transfers are now properly detected and removed from cache
4. **Permanent caching** - Changed from 12-hour TTL to permanent cache (updated surgically)

---

## Commit 1: WU-01 - Threshold Detection & Smart Fetching

**Commit:** `7c9fdfb6`
**Files Modified:**
- `app/Services/Api/MetrcApi.php` (+57 lines, -15 lines)
- `tests/Feature/MetrcApiPackageCacheTest.php` (new, +391 lines)

### Constants Added

```php
const BULK_FETCH_THRESHOLD = 5000;   // Max packages for bulk fetch
const RATE_LIMIT_DELAY = 200000;     // 200ms in microseconds (5 req/sec)
```

### Method Rewritten: `all_active_packages()`

**Before:**
- Fetched ALL packages from facility's credentialed date
- Used while(true) loop with no upper bound
- 12-hour TTL (43200 seconds)

**After:**
- Calculates start date as `max(credentialed_date, 2_years_ago)`
- Probes Metrc for TotalPages first (20 items/page)
- **If estimated > 5000 packages:** Fetches today only (placeholder for incremental sync)
- **If estimated <= 5000 packages:** Paginated bulk fetch
- Uses `DEFAULT_CACHE_TIME` (permanent)

### Method Updated: `invalidate_package_caches()`

Added bulk cache key invalidation as **first line**:
```php
Cache::forget("metrc:all-active-packages:{$facility}");
```

---

## Commit 2: WU-02 - Surgical Cache Update Methods

**Commit:** `3757a286`
**Files Modified:**
- `app/Services/Api/MetrcApi.php` (+214 lines)
- `tests/Feature/MetrcApiPackageCacheTest.php` (+468 lines)

### New Methods Added

#### `sync_packages_to_cache(string $facility): array`
**Purpose:** Cron-based incremental sync (fetches today's changes, merges into cache)

**Logic:**
1. Fetch today's active packages from Metrc
2. Fetch today's inactive packages (finished/discontinued)
3. Traverse outgoing transfers to find transferred packages
4. Merge: remove inactive/transferred, add/update active
5. Returns stats: `['added' => int, 'updated' => int, 'removed' => int]`

#### `get_transferred_package_labels(string $facility, string $start, string $end): array`
**Purpose:** 3-level transfer chain traversal

**Chain:** `transfers → deliveries → packages`
- Fetches `/transfers/v2/outgoing`
- For each transfer, fetches `/transfers/v2/{id}/deliveries`
- For each delivery, fetches `/transfers/v2/deliveries/{id}/packages`
- Returns array of package labels that left via transfer

#### `add_package_to_cache(string $facility, string $label): void`
**Purpose:** Called after package creation
- Fetches fresh package data from `/packages/v2/{label}`
- Appends to bulk cache
- Invalidates available-tags cache

#### `update_package_in_cache(string $facility, string $label): void`
**Purpose:** Called after move/adjust/change/remediate
- Fetches fresh package data from Metrc
- Updates in place (or removes if no longer exists)

#### `remove_package_from_cache(string $facility, string $label): void`
**Purpose:** Called after finish/discontinue
- Removes from bulk cache (no Metrc API call needed)
- Forgets individual package cache

#### `update_packages_in_cache(string $facility, array $labels): void`
**Purpose:** Bulk helper for split/combine operations
- Iterates labels, calls `update_package_in_cache` with rate limiting

---

## Commit 3: WU-03 - SyncMetrcPackages Job Rewrite

**Commit:** `19e2991b`
**Files Modified:**
- `app/Jobs/SyncMetrcPackages.php` (+10 lines, -10 lines)
- `tests/Feature/SyncMetrcPackagesJobTest.php` (new, +219 lines)

### Changes

**Before:**
```php
$api->one_day_of_packages($this->facility, Carbon::today(), true);
$api->one_day_of_inactive_packages($this->facility, Carbon::today());
```

**After:**
```php
$stats = $api->sync_packages_to_cache($this->facility);
LogService::store(
    'SyncMetrcPackages',
    "Facility {$this->facility}: +{$stats['added']} added, ~{$stats['updated']} updated, -{$stats['removed']} removed"
);
```

**Timeout:** Increased from 300 to 600 seconds (transfer traversal can take time)

---

## Commit 4: WU-04 - Controller Surgical Updates

**Commit:** `e39db1dd`
**Files Modified:**
- `app/Http/Controllers/MetrcController.php` (+52 lines, -37 lines)

### `get_packages()` Simplified

**Removed:** The "always fetch today's packages" merge logic (lines 1748-1760)
```php
// REMOVED - no longer needed with surgical updates
if (!$force_refresh) {
    $today_packages = $api->one_day_of_packages($facility, Carbon::today());
    // ... merge logic
}
```

**Now:** Bulk cache is the single source of truth

### Invalidation Replacements

| Controller Method | Before | After |
|-------------------|--------|-------|
| `adjust_package` | `invalidate_package_caches($license, [$tag])` | `update_package_in_cache($license, $tag)` |
| `create_packages_from_harvest` | `invalidate_package_caches($license)` | Loop: `add_package_to_cache($license, $tag)` |
| `create_packages_from_packages` | `invalidate_package_caches($license)` | Loop: `add_package_to_cache($license, $tag)` |
| `submit_for_testing` | `invalidate_package_caches($license)` | Loop: `add_package_to_cache($license, $tag)` |
| `finish_packages` | `invalidate_package_caches($license)` | Loop: `remove_package_from_cache($license, $label)` |
| `unfinish_packages` | `invalidate_package_caches($license)` | Loop: `add_package_to_cache($license, $label)` |
| `move_packages` | `invalidate_package_caches($license)` | Loop: `update_package_in_cache($license, $label)` |
| `change_package_item` | `invalidate_package_caches($license)` | Loop: `update_package_in_cache($license, $label)` |

### set_user() Additions

Added `$api->set_user(request()->user())` calls where missing before surgical method calls (required for API authentication when methods fetch from Metrc).

---

## Cache Key Reference

| Key Pattern | Purpose | TTL |
|-------------|---------|-----|
| `metrc:all-active-packages:{facility}` | Bulk package cache | Permanent |
| `metrc:package:{label}` | Individual package | Permanent |
| `metrc:package-available-tags:{facility}` | Available tags | Invalidated on package create |

---

## Test Files Created

1. **`tests/Feature/MetrcApiPackageCacheTest.php`** (~859 lines total)
   - Threshold detection tests
   - Cache behavior tests
   - Surgical method tests
   - Transfer traversal tests

2. **`tests/Feature/SyncMetrcPackagesJobTest.php`** (219 lines)
   - Job execution tests
   - Multi-tenancy safety tests
   - Stats logging verification

---

## Important Implementation Details

### Rate Limiting
All Metrc API calls respect the 5 req/sec rate limit using `usleep(200000)` (200ms delay) between calls.

### Null Handling
All Metrc responses use null coalescing: `->json('Data') ?? []` to handle potential null responses.

### Cache Miss Behavior
Surgical methods check for cache existence first and log a skip message if the bulk cache doesn't exist yet (graceful degradation).

### LogService Usage
All cache operations use `LogService::store()` (never `Log::`) per BudTags conventions.

---

## Migration Notes

- No database migrations required
- No frontend changes required
- Cache will naturally populate on first access
- Existing caches will be replaced on first surgical update or sync job run

---

## Verification Commands

```bash
# Run all package cache tests
php artisan test --filter=MetrcApiPackageCacheTest

# Run sync job tests
php artisan test --filter=SyncMetrcPackagesJobTest

# Static analysis
./vendor/bin/phpstan analyse app/Services/Api/MetrcApi.php app/Jobs/SyncMetrcPackages.php app/Http/Controllers/MetrcController.php --memory-limit=512M

# Code style
./vendor/bin/pint app/Services/Api/MetrcApi.php app/Jobs/SyncMetrcPackages.php app/Http/Controllers/MetrcController.php
```
