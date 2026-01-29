# QuickBooks Caching Pattern

**Pattern:** Laravel Cache for API Response Caching
**TTL:** Configurable (default 5 minutes for items)
**Strategy:** Cache-aside pattern

---

## Overview

QuickBooks API responses are cached to reduce API calls and improve performance. Caching is especially useful for reference data that changes infrequently (items, payment methods, accounts, etc.).

**Benefits:**
- Reduces API call count (QuickBooks has rate limits)
- Improves page load performance
- Reduces latency for frequently accessed data

---

## Cached Operations

### Items Caching

**Most Common:** Items are cached by default

```php
// Get items with 5-minute cache (300 seconds)
public function get_items_cached(int $ttl = 300): array {
    $cacheKey = "qbo_items_{$this->user->active_org->id}";

    return Cache::remember($cacheKey, $ttl, function () {
        return $this->get_all_items();
    });
}
```

**Usage:**
```php
$qbo = new QuickBooksApi();
$qbo->set_user($user);

// First call: Fetches from QuickBooks API
$items = $qbo->get_items_cached(300);

// Subsequent calls (within 5 min): Returns from cache
$items = $qbo->get_items_cached(300);
```

---

## Cache Keys

### Organization-Scoped Keys

**IMPORTANT:** Cache keys MUST include `org_id` to prevent cross-org data leakage

```php
// ✅ CORRECT - Includes org_id
$cacheKey = "qbo_items_{$this->user->active_org->id}";
$cacheKey = "qbo_customers_{$user->active_org->id}";
$cacheKey = "qbo_payment_methods_{$org->id}";
```

```php
// ❌ WRONG - No org scoping!
$cacheKey = "qbo_items";  // Could return Org A's items to Org B!
```

### Recommended Key Format

```
qbo_{entity_type}_{org_id}_{optional_params}
```

**Examples:**
- `qbo_items_5` - Items for org 5
- `qbo_customers_5_active` - Active customers for org 5
- `qbo_invoices_5_2025-01` - January 2025 invoices for org 5

---

## Cache TTL Guidelines

### Reference Data (Long TTL)

**Data that rarely changes:**
- Payment methods: 1 hour (3600 seconds)
- Accounts: 1 hour (3600 seconds)
- Payment terms: 1 hour (3600 seconds)

```php
$paymentMethods = Cache::remember("qbo_payment_methods_{$orgId}", 3600, function () {
    return $this->get_payment_methods();
});
```

### Transactional Data (Short TTL)

**Data that changes frequently:**
- Items (inventory): 5 minutes (300 seconds)
- Customers: 10 minutes (600 seconds)
- Invoices: 2 minutes (120 seconds)

```php
$items = Cache::remember("qbo_items_{$orgId}", 300, function () {
    return $this->get_all_items();
});
```

### Real-Time Data (No Cache)

**Data that must be current:**
- Invoice creation
- Payment recording
- Credit memo application

```php
// No caching for write operations
$invoice = $qbo->create_invoice($data);
```

---

## Clear Cache

### Manual Cache Clear

```php
public function clearCache(): void {
    $orgId = $this->user->active_org->id;

    Cache::forget("qbo_items_{$orgId}");
    Cache::forget("qbo_customers_{$orgId}");
    Cache::forget("qbo_payment_methods_{$orgId}");
    Cache::forget("qbo_accounts_{$orgId}");

    LogService::store(
        'QuickBooks Cache Cleared',
        "Cache cleared for org {$orgId}"
    );
}
```

**Usage:**
```php
$qbo->clearCache();
```

### When to Clear Cache

**ALWAYS clear cache after:**
- Bulk imports (e.g., importing 100 items from Metrc)
- Major updates (e.g., updating all customer emails)
- Sync operations (e.g., syncing quantities from Metrc)

**Example:**
```php
// Import 100 items
foreach ($metrcItems as $item) {
    $qbo->create_item([...]);
}

// Clear cache so next fetch gets fresh data
$qbo->clearCache();
```

---

## Cache-Aside Pattern

### How It Works

**First Request:**
1. Check cache for key
2. Cache miss → Fetch from QuickBooks API
3. Store in cache with TTL
4. Return data

**Subsequent Requests (within TTL):**
1. Check cache for key
2. Cache hit → Return cached data
3. No API call made

**After TTL Expires:**
1. Check cache for key
2. Cache expired → Fetch from QuickBooks API
3. Update cache
4. Return fresh data

---

## Testing Cache Behavior

### Verify Caching

```php
// Clear cache first
Cache::flush();

// First call - should hit API
$start = microtime(true);
$items1 = $qbo->get_items_cached(300);
$time1 = microtime(true) - $start;  // ~2-3 seconds

// Second call - should hit cache
$start = microtime(true);
$items2 = $qbo->get_items_cached(300);
$time2 = microtime(true) - $start;  // ~0.01 seconds

assert($time2 < $time1);  // Cache is faster!
assert($items1 === $items2);  // Same data
```

### Monitor Cache Hits/Misses

```php
// Enable cache logging in config/cache.php
'log_hits' => true,
'log_misses' => true,
```

---

## Best Practices

✅ **ALWAYS include org_id in cache keys**
✅ **ALWAYS use appropriate TTL for data type**
✅ **ALWAYS clear cache after bulk operations**
✅ **ALWAYS use Cache::remember() for automatic cache-aside**

❌ **NEVER use global cache keys** - Must be org-scoped
❌ **NEVER cache write operations** - Only cache reads
❌ **NEVER use very long TTL for transactional data**
❌ **NEVER forget to clear cache after bulk updates**

---

## Advanced: Selective Cache Invalidation

### Invalidate Specific Entity

```php
// After updating single customer
$qbo->update_customer(['id' => '123', 'name' => 'New Name']);

// Invalidate customer cache only
Cache::forget("qbo_customers_{$orgId}");
// Items cache still valid
```

### Tag-Based Caching (Future Enhancement)

```php
// Using cache tags for easier invalidation
Cache::tags(["qbo", "org_{$orgId}"])->remember("items", 300, function () {
    return $this->get_all_items();
});

// Clear all QuickBooks caches for org
Cache::tags("org_{$orgId}")->flush();
```

---

## Related Patterns

- `categories/items.md` - get_items_cached() method
- `categories/utilities.md` - clearCache() method
- `patterns/logging.md` - Logging cache operations
