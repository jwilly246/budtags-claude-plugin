# Metrc API Inventory Management Best Practices

## Overview

Effective inventory management is critical for cannabis compliance. Metrc provides several endpoints for tracking packages as they move through different states in your facility's inventory.

This guide covers **best practices** for syncing your software's inventory with Metrc, tracking active/inactive packages, and optimizing API usage.

---

## Inventory State Endpoints

Metrc categorizes packages into different inventory states based on their status:

| Endpoint | Description | Use Case |
|----------|-------------|----------|
| `/packages/v1/active` | Packages currently in active inventory | Default inventory view, label printing |
| `/packages/v1/inactive` | Packages that have been Finished or Discontinued | Historical tracking, compliance reporting |
| `/packages/v1/onhold` | Packages with holds placed (failed lab tests, etc.) | QA workflows, problem resolution |
| `/packages/v1/intransit` | Packages currently in outgoing transfers | Shipping/receiving workflows |

---

## Best Practices for Inventory Syncing

### 1. Active vs Inactive Endpoints

**When to use `/active`:**
- ✅ Initial inventory sync (first-time setup)
- ✅ Daily/hourly inventory refresh
- ✅ Label printing workflows
- ✅ Current inventory reports

**When to use `/inactive`:**
- ✅ Historical tracking and analytics
- ✅ Compliance audits (show finished packages)
- ✅ Finding packages that left inventory
- ❌ NOT for regular inventory sync (wastes API calls)

**Key Insight:**
Packages can **only** leave active inventory via:
1. **Finishing** a package
2. **Discontinuing** a package
3. **Outgoing transfers**

If you're tracking active inventory, you don't need to poll `/inactive` regularly - only fetch it when you need historical data.

---

## The LastModified Filter (CRITICAL)

###

 **Why LastModified Matters**

Metrc **requires** a date range filter for most endpoints using the `lastModifiedStart` and `lastModifiedEnd` parameters. This isn't just a query optimization - it's a **data integrity requirement**.

**⚠️ CRITICAL RULE: Always request data in chronological order (oldest to newest)**

### The Problem with Reverse Chronological Ordering

**DON'T DO THIS:**
```javascript
// ❌ WRONG - Fetching newest first, then older data
const today = new Date();
const yesterday = new Date(today);
yesterday.setDate(yesterday.getDate() - 1);

// First request (newest)
const newestPackages = await fetchPackages(yesterday, today);

// Second request (older)
const olderPackages = await fetchPackages(twoD aysAgo, yesterday);
```

**Why this is bad:**
1. Package A is modified at 2:00 PM (in "newest" set)
2. You fetch the "newest" set at 2:05 PM
3. Package A is modified again at 2:10 PM (still in "newest" set)
4. You fetch the "older" set at 2:15 PM
5. **You miss the 2:10 PM update to Package A** because it's no longer in the timeframe you already fetched

**The LastModified field can only move forward** - it never goes backward. If you request data in reverse chronological order, updates can "move" a record within the most recent set you already fetched, causing you to miss it.

### Correct Approach: Chronological Ordering

**✅ CORRECT:**
```javascript
// Always fetch oldest to newest
const lastSync = new Date('2025-01-01'); // Your last successful sync
const now = new Date();

// Fetch in chronological order
const packages = await fetchPackages(lastSync, now);

// Store last sync time for next run
await saveLastSyncTime(now);
```

**Why this works:**
- You start from your last known sync point
- You move forward in time
- Any record modified during your fetch will have a newer lastModified timestamp
- You'll catch it in the next sync (no missed records)

---

## Incremental Sync Strategy

### Initial Sync (First-Time Setup)

```javascript
async function initialInventorySync(facility) {
  // Fetch large date range (e.g., last 365 days)
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - 365);

  const packages = await axios.get('/packages/v1/active', {
    params: {
      licenseNumber: facility,
      lastModifiedStart: startDate.toISOString(),
      lastModifiedEnd: endDate.toISOString()
    }
  });

  // Store in database with lastModified timestamps
  await db.packages.insertMany(packages.data.map(pkg => ({
    ...pkg,
    syncedAt: new Date()
  })));

  // Save last sync time
  await db.syncStatus.upsert({
    facility,
    lastSyncTime: endDate,
    type: 'active_packages'
  });

  return packages.data;
}
```

### Incremental Sync (Ongoing)

```javascript
async function incrementalInventorySync(facility) {
  // Get last successful sync time
  const lastSync = await db.syncStatus.findOne({
    facility,
    type: 'active_packages'
  });

  const startDate = lastSync?.lastSyncTime || new Date('2025-01-01');
  const endDate = new Date();

  // Fetch only changes since last sync
  const packages = await axios.get('/packages/v1/active', {
    params: {
      licenseNumber: facility,
      lastModifiedStart: startDate.toISOString(),
      lastModifiedEnd: endDate.toISOString()
    }
  });

  // Update or insert changed packages
  for (const pkg of packages.data) {
    await db.packages.upsert({
      where: { Label: pkg.Label },
      update: { ...pkg, syncedAt: new Date() },
      create: { ...pkg, syncedAt: new Date() }
    });
  }

  // Update last sync time
  await db.syncStatus.update({
    where: { facility, type: 'active_packages' },
    data: { lastSyncTime: endDate }
  });

  return packages.data;
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

As mentioned in Metrc documentation, packages can only leave active inventory via **three methods**:

### Method 1: Finishing or Discontinuing

```javascript
// Packages that were finished/discontinued
const inactivePackages = await axios.get('/packages/v1/inactive', {
  params: {
    licenseNumber: facility,
    lastModifiedStart: lastSync.toISOString(),
    lastModifiedEnd: new Date().toISOString()
  }
});

// Mark as inactive in your database
for (const pkg of inactivePackages.data) {
  await db.packages.update({
    where: { Label: pkg.Label },
    data: {
      status: pkg.FinishedDate ? 'finished' : 'discontinued',
      finishedAt: pkg.FinishedDate,
      discontinuedAt: pkg.ArchivedDate
    }
  });
}
```

### Method 2: Outgoing Transfers (Cascading API Calls)

**⚠️ Note:** This requires **multiple cascading API calls** and is subject to rate limiting.

```javascript
async function trackOutgoingTransfers(facility) {
  // Step 1: Get all outgoing transfers
  const transfers = await axios.get('/transfers/v1/outgoing', {
    params: { licenseNumber: facility }
  });

  for (const transfer of transfers.data) {
    // Step 2: Get deliveries for this transfer
    const deliveries = await axios.get(`/transfers/v1/${transfer.Id}/deliveries`);

    for (const delivery of deliveries.data) {
      // Step 3: Get packages in this delivery
      const packages = await axios.get(`/transfers/v1/deliveries/${delivery.Id}/packages`);

      // Mark packages as in transit
      for (const pkg of packages.data) {
        await db.packages.update({
          where: { Label: pkg.PackageLabel },
          data: {
            status: 'in_transit',
            transferId: transfer.Id,
            deliveryId: delivery.Id
          }
        });
      }

      // Rate limiting consideration: Add delay between calls
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }
}
```

**Performance Note:** This cascading approach requires:
- 1 call for `/outgoing`
- N calls for `/transfers/{id}/deliveries` (one per transfer)
- M calls for `/deliveries/{id}/packages` (one per delivery)

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
public function get_history_from_cache($facility, $date, $num_of_days) {
    $cache_key = "packages:{$facility}:{$date->format('Y-m-d')}:{$num_of_days}";

    return Cache::remember($cache_key, now()->addHours(1), function() use ($facility, $date, $num_of_days) {
        $days_of_packages = [];

        for ($i = 0; $i < $num_of_days; $i++) {
            $current_date = (clone $date)->subDays($i);

            // Fetch from Metrc API
            $packages = $this->one_day_of_packages($facility, $current_date);

            $days_of_packages[] = [
                'date' => $current_date,
                'packages' => $packages
            ];
        }

        return $days_of_packages;
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

**❌ BAD - Fetching all active packages every time:**
```javascript
// Fetches thousands of packages unnecessarily
const packages = await axios.get('/packages/v1/active', {
  params: { licenseNumber: facility }
});
```

**✅ GOOD - Use lastModified filter:**
```javascript
// Only fetch changes in last 15 minutes
const fifteenMinutesAgo = new Date();
fifteenMinutesAgo.setMinutes(fifteenMinutesAgo.getMinutes() - 15);

const packages = await axios.get('/packages/v1/active', {
  params: {
    licenseNumber: facility,
    lastModifiedStart: fifteenMinutesAgo.toISOString(),
    lastModifiedEnd: new Date().toISOString()
  }
});
```

**Impact:**
- **Without filter:** 5000+ packages returned (5 MB+ payload)
- **With filter:** 10-50 packages returned (50 KB payload)
- **100x reduction** in data transferred

### Use Webhooks (If Available)

Some Metrc service tiers support webhooks. Instead of polling `/active` every 15 minutes:

**Polling Approach:**
```javascript
// Runs every 15 minutes
setInterval(async () => {
  await incrementalInventorySync(facility);
}, 15 * 60 * 1000);

// Result: 96 API calls per day (4 per hour × 24 hours)
```

**Webhook Approach:**
```javascript
// Metrc POSTs to your endpoint when packages change
app.post('/webhooks/metrc/package-updated', async (req, res) => {
  const { packageLabel, eventType } = req.body;

  // Fetch only the specific changed package
  const pkg = await fetchPackageByLabel(packageLabel);

  await db.packages.upsert({ where: { Label: packageLabel }, ...pkg });

  res.status(200).send('OK');
});

// Result: Only 1 API call per actual change (10-50 per day typical)
```

**Consult your Metrc agreement** to determine if you have webhook access.

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

**Solution:** Only fetch inactive packages:
- During initial sync
- When generating compliance reports
- When user explicitly requests historical data

### 4. Not Caching Results

**Problem:** Re-fetching the same data multiple times within short timeframes.

**Solution:** Implement Redis/database caching with appropriate TTL.

### 5. Ignoring Outgoing Transfers

**Problem:** Packages "disappear" from active inventory without explanation.

**Solution:** Implement outgoing transfer tracking to maintain inventory accuracy.

---

## Related Patterns

- **[Object Limiting](./object-limiting.md)** - Handle 10 object limit per request
- **[Rate Limiting](./rate-limiting.md)** - Avoid 429 responses with proper throttling
- **[Transfer Workflows](./transfer-workflows.md)** - Complete guide to tracking transfers
- **[Pagination](./pagination.md)** - Handle large result sets efficiently

---

## Quick Reference

```
✅ DO:
- Use lastModifiedStart/End filters for all syncs
- Fetch data in chronological order (oldest to newest)
- Cache results with appropriate TTL
- Track outgoing transfers to understand inventory changes
- Use incremental syncing (every 5-15 minutes)

❌ DON'T:
- Fetch all active packages without filters
- Request data in reverse chronological order
- Poll inactive packages unnecessarily
- Ignore outgoing transfers
- Sync less than hourly for active inventory
```
