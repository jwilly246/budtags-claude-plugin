# TTL Strategy Guide

Choosing the right TTL (Time To Live) for cached data is crucial for balancing performance, memory usage, and data freshness.

---

## Decision Framework

```
Is this data...
│
├─ Entity that changes via user action? (packages, plants, harvests)
│  └─> Cache FOREVER + Explicit invalidation
│
├─ Entity that changes externally? (tags, employees)
│  └─> Short TTL (2 minutes)
│
├─ Reference data that rarely changes? (locations, categories)
│  └─> Cache FOREVER or long TTL (30 days)
│
├─ Historical/immutable data? (inactive packages, finished harvests)
│  └─> Long TTL (30 days)
│
└─ Temporary tracking data? (counters, progress)
   └─> Short TTL (1 hour) with auto-cleanup
```

---

## TTL Constants (MetrcApi.php)

```php
// Primary cache times
const DEFAULT_CACHE_TIME = null;        // Permanent (Cache::forever)
const INACTIVE_CACHE_TIME = 60*60*24*30; // 30 days (2,592,000 seconds)
const PLANT_CACHE_TIME = null;          // Permanent for active plants

// Common specific TTLs used in codebase
120                   // 2 minutes - strains, employees, fast-changing
600                   // 10 minutes - adjustments
3600                  // 1 hour - temporary counters, adjustment reasons
43200                 // 12 hours - all active packages, items
60*60*24*7            // 7 days - transfer deliveries, transporters
60*60*24*30           // 30 days - inactive packages, historical data
```

---

## When to Use Forever (null TTL)

### Active Entity Data

Data that changes through user actions and is explicitly invalidated:

```php
// Packages - invalidated when created/finished
Cache::forever("metrc:package:{$label}", $package);

// Plants - invalidated when harvested/destroyed
Cache::forever("metrc:plant:{$tag}", $plant);

// Day caches - invalidated on today's operations
Cache::forever("metrc:day-of-packages:{$facility}:{$date}", $packages);
```

### Why Forever Works

1. **Explicit Invalidation**: BudTags invalidates cache on write operations
2. **Force Fetch Today**: Today's data always force-fetched via `$start_day->isToday()`
3. **lastModified Filtering**: Metrc API returns updated entities
4. **Memory Efficiency**: Redis eviction handles memory pressure

### Invalidation Pattern

```php
// After creating package
$this->invalidate_package_caches($facility, [$label]);

// After finishing package
Cache::forget("metrc:day-of-packages:{$facility}:{$today}");
Cache::forget("metrc:day-of-inactive-packages:{$facility}:{$today}");
```

---

## When to Use Short TTL (2-10 minutes)

### Fast-Changing External Data

Data that changes outside BudTags control:

```php
// Available tags (consumed externally)
return $this->fetch_from_cache_or_api(
    "metrc:package-available-tags:{$facility}",
    fn() => $this->get('/packages/v2/types', [...]),
    null,
    false,
    120,  // 2 minutes
);

// Employees (added/removed in Metrc)
return $this->fetch_from_cache_or_api(
    "metrc:employees:{$facility}",
    fn() => $this->get('/employees/v2/?licenseNumber='.$facility)->json('Data'),
    null,
    false,
    120,  // 2 minutes
);

// Strains (created/modified in Metrc)
return $this->fetch_from_cache_or_api(
    "metrc:strains:{$facility}",
    fn() => $this->get('/strains/v2/active?licenseNumber='.$facility)->json('Data'),
    fn($strain) => "metrc:strain:{$strain['Id']}",
    false,
    120,  // 2 minutes
);
```

---

## When to Use Long TTL (30 days)

### Historical/Immutable Data

Data that won't change or is rarely accessed:

```php
// Inactive packages (finished, won't change)
const INACTIVE_CACHE_TIME = 60*60*24*30; // 30 days

return $this->fetch_from_cache_or_api(
    "metrc:day-of-inactive-packages:{$facility}:{$date}",
    fn() => $this->get('/packages/v2/inactive', [...]),
    fn($pkg) => "metrc:inactive-package:{$pkg['Label']}",
    false,
    self::INACTIVE_CACHE_TIME,  // 30 days
);
```

### User Preferences/Memory

Data that should persist but can be rebuilt:

```php
// Transfer selection memory (TransferSelectionMemoryService.php)
private const TTL_DAYS = 30;

Cache::put(
    $this->cache_key($org_id),
    $data,
    now()->addDays(self::TTL_DAYS)  // 30 days
);
```

---

## When to Use Medium TTL (1-12 hours)

### Semi-Stable Reference Data

```php
// All active items (rarely change during day)
return $this->fetch_from_cache_or_api(
    "metrc:active-items:{$facility}",
    fn() => $this->fetchAllItems($facility),
    fn($item) => "metrc:item:{$item['Id']}",
    $force_fetch,
    43200,  // 12 hours
);

// Adjustment reasons (immutable, rarely checked)
return $this->fetch_from_cache_or_api(
    "metrc:adjustment-reasons:{$facility}",
    fn() => $this->get('/packages/v2/adjust/reasons', [...]),
    null,
    false,
    3600,  // 1 hour
);
```

### Temporary Counters

```php
// Job progress counters (GeneratePackageLabel.php)
$key = "label_group_success:{$this->group->id}";
Redis::incr($key);
Redis::expire($key, 3600);  // 1 hour cleanup
```

---

## Special Case: Transfer Data

Transfer-related data uses 7-day TTL since it's accessed during delivery windows:

```php
// Delivery details
return $this->fetch_from_cache_or_api(
    "metrc:transfer-deliveries:{$transfer_id}",
    fn() => $this->get("/transfers/v2/{$transfer_id}/deliveries")->json('Data'),
    fn($delivery) => "metrc:transfer-delivery:{$delivery['Id']}",
    false,
    60*60*24*7,  // 7 days
);

// Wholesale pricing
return $this->fetch_from_cache_or_api(
    "metrc:transfer-delivery-packages-wholesale:{$delivery_id}",
    fn() => $this->get("/transfers/v2/deliveries/{$delivery_id}/packages/wholesale")->json('Data'),
    fn($pkg) => "metrc:transfer-delivery-package-wholesale:{$pkg['PackageLabel']}",
    false,
    60*60*24*7,  // 7 days
);
```

---

## Anti-Patterns

```php
// ❌ WRONG: Magic numbers without context
Cache::put($key, $data, 7200);

// ✅ CORRECT: Use constants or explain
Cache::put($key, $data, 60*60*2);  // 2 hours - session data

// ❌ WRONG: Forever for externally-changing data
Cache::forever("metrc:employees:{$facility}", $employees);  // Can change in Metrc!

// ✅ CORRECT: Short TTL for external data
Cache::put("metrc:employees:{$facility}", $employees, 120);

// ❌ WRONG: Short TTL for user-controlled data
Cache::put("metrc:package:{$label}", $package, 300);  // Wasteful API calls!

// ✅ CORRECT: Forever with invalidation
Cache::forever("metrc:package:{$label}", $package);
// Then invalidate on write:
Cache::forget("metrc:package:{$label}");
```

---

## TTL Reference Table

| Data Type | TTL | Reason |
|-----------|-----|--------|
| Active packages/plants | forever | Invalidated on user action |
| Day caches (active) | forever | Force-fetched for today |
| Day caches (inactive) | 30 days | Historical, rarely accessed |
| Tags (available) | 2 min | Consumed externally |
| Employees | 2 min | Changed in Metrc |
| Strains | 2 min | Changed in Metrc |
| Items (full list) | 12 hours | Semi-stable |
| Categories | forever | Rarely change |
| Locations | forever | Rarely change |
| Adjustment reasons | 1 hour | Immutable reference |
| Transfer deliveries | 7 days | Access during delivery window |
| Job counters | 1 hour | Temporary tracking |
| User preferences | 30 days | Persistent but rebuildable |
