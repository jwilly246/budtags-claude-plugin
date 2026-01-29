# QuickBooks Item/Product Operations

**Category:** Item/Product Operations
**Operations:** 7 methods
**Purpose:** Manage QuickBooks items (products/services) and sync with Metrc

---

## Overview

Item operations manage QuickBooks inventory and service items. Includes integration with Metrc for cannabis product mapping and quantity synchronization.

**Key Models:**
- `QboItemMapping` - Maps Metrc items to QuickBooks items

**See Also:**
- `scenarios/metrc-sync-workflow.md` - Complete Metrc sync guide
- `ENTITY_TYPES.md` - Item type definition

---

## Operations

### 22. `get_items(int $start_at = 1, int $max_count = 100)`
Get paginated list of items

**Returns:** Array of Item objects

### 23. `get_all_items()`
Get ALL items with automatic pagination

**Returns:** Array of all Item objects

### 24. `get_items_cached(int $ttl = 300)`
Get items with caching (default 5min TTL)

**Usage:**
```php
$items = $qbo->get_items_cached(300); // Cache for 5 minutes
```

**See:** `patterns/caching.md` for cache strategy

### 25. `get_item(string $id)`
Get single item by QuickBooks ID

**Returns:** Item object or `null`

### 26. `create_item(array $data)`
Create new item (product or service)

**Required:**
- `name` - Item name
- `type` - 'Inventory' or 'Service'

**Optional:**
- `income_account_ref` - Income account ID
- `expense_account_ref` - Expense account ID
- `asset_account_ref` - Asset account ID (inventory only)
- `quantity_on_hand` - Initial quantity
- `inv_start_date` - Inventory start date

**Returns:** Created Item object

### 27. `update_item(array $data)`
Update existing item

**Required:** `id` - QuickBooks item ID

**Important:** Fetches current item first for SyncToken

**Returns:** Updated Item object

### 28. `sync_quantities_from_metrc()`
Sync inventory quantities from Metrc to QuickBooks

**Usage:**
```php
$result = $qbo->sync_quantities_from_metrc();
// Returns: ['synced' => 15, 'failed' => 0, 'skipped' => 3]
```

**Process:**
1. Load QboItemMapping for current org
2. Fetch package quantities from Metrc
3. Update QuickBooks item quantities
4. Log sync results

**Returns:** Array with sync statistics

**See:** `scenarios/metrc-sync-workflow.md` for complete workflow

---

## Common Workflows

### Create Inventory Item
```php
$item = $qbo->create_item([
    'name' => 'Premium Cannabis Flower',
    'type' => 'Inventory',
    'quantity_on_hand' => 100,
    'inv_start_date' => '2025-01-01',
    'income_account_ref' => '79'  // Sales Income
]);
```

### Sync Quantities from Metrc
```php
// First, ensure item mappings exist in QboItemMapping table
// Then sync quantities
$result = $qbo->sync_quantities_from_metrc();

if ($result['synced'] > 0) {
    echo "Successfully synced {$result['synced']} items";
}
```

**See:** `scenarios/metrc-sync-workflow.md`
