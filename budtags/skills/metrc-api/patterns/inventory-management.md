# Metrc API Inventory Management Best Practices

## Overview

Effective inventory management is critical for cannabis compliance. Metrc provides several endpoints for tracking packages as they move through different states in your facility's inventory.

This guide covers **best practices** for syncing your software's inventory with Metrc, tracking active/inactive packages, and optimizing API usage.

---

## Inventory State Endpoints

Metrc categorizes packages into different inventory states based on their status:

| Endpoint | Description | Use Case |
|----------|-------------|----------|
| `/packages/v2/active` | Packages currently in active inventory | Default inventory view, label printing |
| `/packages/v2/inactive` | Packages that have been Finished or Discontinued | Historical tracking, compliance reporting |
| `/packages/v2/onhold` | Packages with holds placed (failed lab tests, etc.) | QA workflows, problem resolution |
| `/packages/v2/intransit` | Packages currently in outgoing transfers | Shipping/receiving workflows |

---

## Best Practices for Inventory Syncing

### 1. Active vs Inactive Endpoints

**When to use `/active`:**
- Initial inventory sync (first-time setup)
- Daily/hourly inventory refresh
- Label printing workflows
- Current inventory reports

**When to use `/inactive`:**
- Historical tracking and analytics
- Compliance audits (show finished packages)
- Finding packages that left inventory
- NOT for regular inventory sync (wastes API calls)

**Key Insight:**
Packages can **only** leave active inventory via:
1. **Finishing** a package
2. **Discontinuing** a package
3. **Outgoing transfers**

If you're tracking active inventory, you don't need to poll `/inactive` regularly - only fetch it when you need historical data.

---

## The LastModified Filter (CRITICAL)

### Why LastModified Matters

Metrc **requires** a date range filter for most endpoints using the `lastModifiedStart` and `lastModifiedEnd` parameters. This isn't just a query optimization - it's a **data integrity requirement**.

**CRITICAL RULE: Always request data in chronological order (oldest to newest)**

### The Problem with Reverse Chronological Ordering

**DON'T DO THIS:**
```php
// ❌ WRONG - Fetching newest first, then older data
$today = now();
$yesterday = now()->subDay();
$twoDaysAgo = now()->subDays(2);

// First request (newest)
$newestPackages = $api->one_day_of_packages($facility, $today->format('Y-m-d'));

// Second request (older)
$olderPackages = $api->one_day_of_packages($facility, $yesterday->format('Y-m-d'));
```

**Why this is bad:**
1. Package A is modified at 2:00 PM (in "newest" set)
2. You fetch the "newest" set at 2:05 PM
3. Package A is modified again at 2:10 PM (still in "newest" set)
4. You fetch the "older" set at 2:15 PM
5. **You miss the 2:10 PM update to Package A** because it's no longer in the timeframe you already fetched

**The LastModified field can only move forward** - it never goes backward. If you request data in reverse chronological order, updates can "move" a record within the most recent set you already fetched, causing you to miss it.

### Correct Approach: Chronological Ordering

**CORRECT:**
```php
// Always fetch oldest to newest
$lastSync = SyncStatus::where('facility', $facility)
    ->where('type', 'active_packages')
    ->value('last_sync_time') ?? now()->subYear();

$packages = $api->one_day_of_packages($facility, $lastSync->format('Y-m-d'));

// Store last sync time for next run
SyncStatus::updateOrCreate(
    ['facility' => $facility, 'type' => 'active_packages'],
    ['last_sync_time' => now()]
);
```

**Why this works:**
- You start from your last known sync point
- You move forward in time
- Any record modified during your fetch will have a newer lastModified timestamp
- You'll catch it in the next sync (no missed records)

---

## Incremental Sync Strategy

### Initial Sync (First-Time Setup)

```php
public function initial_inventory_sync(string $facility): array
{
    $api = app(\App\Services\Api\MetrcApi::class);
    $api->set_user(request()->user());
    $license = session('license');

    // Fetch large date range (e.g., last 365 days)
    $startDate = now()->subYear();
    $endDate = now();
    $allPackages = [];

    // Use the day-by-day public method
    $currentDate = clone $startDate;
    while ($currentDate->lte($endDate)) {
        $packages = $api->one_day_of_packages($facility, $currentDate->format('Y-m-d'));
        $allPackages = array_merge($allPackages, $packages);
        $currentDate->addDay();
    }

    // Store in database
    foreach ($allPackages as $package) {
        Package::updateOrCreate(
            ['Label' => $package['Label']],
            [...$package, 'synced_at' => now()]
        );
    }

    // Save last sync time
    SyncStatus::updateOrCreate(
        ['facility' => $facility, 'type' => 'active_packages'],
        ['last_sync_time' => $endDate]
    );

    LogService::store('Package Sync', "Initial sync complete. Total packages: " . count($allPackages));

    return $allPackages;
}
```

### Incremental Sync (Ongoing)

```php
public function incremental_inventory_sync(string $facility): array
{
    $api = app(\App\Services\Api\MetrcApi::class);
    $api->set_user(request()->user());

    // Get last successful sync time
    $lastSync = SyncStatus::where('facility', $facility)
        ->where('type', 'active_packages')
        ->value('last_sync_time') ?? now()->subDay();

    $endDate = now();

    // Fetch only changes since last sync using day-by-day
    $currentDate = Carbon::parse($lastSync);
    $changedPackages = [];

    while ($currentDate->lte($endDate)) {
        $packages = $api->one_day_of_packages($facility, $currentDate->format('Y-m-d'));
        $changedPackages = array_merge($changedPackages, $packages);
        $currentDate->addDay();
    }

    // Update or insert changed packages
    foreach ($changedPackages as $package) {
        Package::updateOrCreate(
            ['Label' => $package['Label']],
            [...$package, 'synced_at' => now()]
        );
    }

    // Update last sync time
    SyncStatus::updateOrCreate(
        ['facility' => $facility, 'type' => 'active_packages'],
        ['last_sync_time' => $endDate]
    );

    LogService::store('Package Sync', "Incremental sync complete. Changed packages: " . count($changedPackages));

    return $changedPackages;
}
```

### Sync Frequency Recommendations

| Update Frequency | Use Case | LastModified Range |
|------------------|----------|-------------------|
| Real-time | Label printing, sales | Last 5 minutes |
| Every 15 minutes | Active inventory tracking | Last 15 minutes |
| Hourly | General inventory sync | Last hour |
| Daily | Historical data, analytics | Last 24 hours |

**Best Practice:** Use 5-15 minute incremental syncs for active inventory + hourly full validation sync.

---

## Tracking Packages Leaving Inventory

Packages can only leave active inventory via **three methods**:

### Method 1: Finishing or Discontinuing

```php
// Packages that were finished/discontinued
$inactivePackages = $api->get("/packages/v2/inactive", [
    'licenseNumber' => $license,
    'lastModifiedStart' => $lastSync->format('Y-m-d'),
    'lastModifiedEnd' => now()->format('Y-m-d'),
]);

// Mark as inactive in your database
foreach ($inactivePackages as $package) {
    Package::where('Label', $package['Label'])->update([
        'status' => $package['FinishedDate'] ? 'finished' : 'discontinued',
        'finished_at' => $package['FinishedDate'],
    ]);
}
```

### Method 2: Outgoing Transfers (Cascading API Calls)

**Note:** This requires **multiple cascading API calls** and is subject to rate limiting.

```php
public function track_outgoing_transfers(string $facility): array
{
    $api = app(\App\Services\Api\MetrcApi::class);
    $api->set_user(request()->user());
    $license = session('license');
    $transferredPackages = [];

    // Step 1: Get all outgoing transfers
    $transfers = $api->fetch_transfers_bulk($facility, 'outgoing');

    foreach ($transfers as $transfer) {
        try {
            // Step 2: Get deliveries for this transfer
            $deliveries = $api->get("/transfers/v2/{$transfer['Id']}/deliveries", [
                'licenseNumber' => $license,
            ]);

            foreach ($deliveries as $delivery) {
                // Step 3: Get packages in this delivery
                $packages = $api->get("/transfers/v2/deliveries/{$delivery['Id']}/packages", [
                    'licenseNumber' => $license,
                ]);

                // Mark packages as in transit
                foreach ($packages as $package) {
                    Package::where('Label', $package['PackageLabel'])->update([
                        'status' => 'in_transit',
                        'transfer_id' => $transfer['Id'],
                    ]);
                }

                $transferredPackages = array_merge($transferredPackages, $packages);
            }
        } catch (\Exception $e) {
            LogService::store('transfer_tracking_error', "Error processing transfer {$transfer['Id']}: " . $e->getMessage());
        }
    }

    return $transferredPackages;
}
```

**Performance Note:** This cascading approach requires:
- 1 call for outgoing transfers
- N calls for deliveries (one per transfer)
- M calls for packages (one per delivery)

Be mindful of rate limits when syncing large numbers of transfers.

### Method 3: State-Sanctioned Manual Methods

Metrc documentation notes that some **State-sanctioned methods** for removing packages from inventory cannot be tracked via the API. These require manual adjustments from users:

- Physical destruction under State supervision
- Regulatory seizures
- Other jurisdiction-specific removal methods

**Best Practice:** Implement manual adjustment workflows in your UI for these cases.

---

## Caching Strategies

### Redis Caching Pattern

```php
// Example from BudTags MetrcApi service
public function get_history_from_cache(string $facility, Carbon $date, int $num_of_days): array
{
    $cacheKey = "packages:{$facility}:{$date->format('Y-m-d')}:{$num_of_days}";

    return Cache::remember($cacheKey, now()->addHours(1), function () use ($facility, $date, $num_of_days) {
        $daysOfPackages = [];

        for ($i = 0; $i < $num_of_days; $i++) {
            $currentDate = (clone $date)->subDays($i);
            $packages = $this->one_day_of_packages($facility, $currentDate->format('Y-m-d'));

            $daysOfPackages[] = [
                'date' => $currentDate,
                'packages' => $packages,
            ];
        }

        return $daysOfPackages;
    });
}
```

**Cache Invalidation:**
- Invalidate cache when user explicitly refreshes (`force_refresh` parameter)
- Set reasonable TTL (1-2 hours for active inventory)
- Longer TTL for inactive inventory (24 hours+)

---

## Performance Optimization

### Reduce API Calls with Smart Filtering

**BAD - Fetching all active packages every time:**
```php
// Fetches thousands of packages unnecessarily
$packages = $api->get("/packages/v2/active", [
    'licenseNumber' => $license,
]);
```

**GOOD - Use lastModified filter:**
```php
// Only fetch changes in last 15 minutes
$packages = $api->get("/packages/v2/active", [
    'licenseNumber' => $license,
    'lastModifiedStart' => now()->subMinutes(15)->format('Y-m-d\TH:i:s'),
    'lastModifiedEnd' => now()->format('Y-m-d\TH:i:s'),
]);
```

**Impact:**
- **Without filter:** 5000+ packages returned (5 MB+ payload)
- **With filter:** 10-50 packages returned (50 KB payload)
- **100x reduction** in data transferred

---

## Common Pitfalls

### 1. Not Using LastModified Filter

**Problem:** Fetching all active packages repeatedly wastes API calls and bandwidth.

**Solution:** Always use `lastModifiedStart` and `lastModifiedEnd` for incremental syncing.

### 2. Reverse Chronological Ordering

**Problem:** Fetching newest data first causes missed updates.

**Solution:** Always fetch in chronological order (oldest to newest).

### 3. Polling Inactive Packages Unnecessarily

**Problem:** Checking `/inactive` every 15 minutes when active inventory hasn't changed.

**Solution:** Only fetch inactive packages during initial sync, compliance reports, or when user explicitly requests historical data.

### 4. Not Caching Results

**Problem:** Re-fetching the same data multiple times within short timeframes.

**Solution:** Implement Redis/database caching with appropriate TTL.

### 5. Ignoring Outgoing Transfers

**Problem:** Packages "disappear" from active inventory without explanation.

**Solution:** Implement outgoing transfer tracking to maintain inventory accuracy.

---

## Related Patterns

- **[Object Limiting](./object-limiting.md)** - Handle 10 object limit per request
- **[Error Handling](./error-handling.md)** - Comprehensive error handling strategies
- **[Transfer Workflows](./transfer-workflows.md)** - Complete guide to tracking transfers
- **[Pagination](./pagination.md)** - Handle large result sets efficiently

---

## Quick Reference

```
DO:
- Use lastModifiedStart/End filters for all syncs
- Fetch data in chronological order (oldest to newest)
- Cache results with appropriate TTL
- Track outgoing transfers to understand inventory changes
- Use incremental syncing (every 5-15 minutes)

DON'T:
- Fetch all active packages without filters
- Request data in reverse chronological order
- Poll inactive packages unnecessarily
- Ignore outgoing transfers
- Sync less than hourly for active inventory
```
