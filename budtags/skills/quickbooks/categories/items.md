# QuickBooks Item/Product Operations

**Category:** Item/Product Operations
**Operations:** 8 methods
**Purpose:** Manage QuickBooks items (products/services) and sync quantities from Metrc

---

## Overview

Item operations read, create, and update QuickBooks items and push Metrc
quantities onto mapped QB items. There is no single-item getter, and
`create_item` always starts inventory at 0.

**Key Models:**
- `QboItemMapping` - Maps Metrc item IDs to QuickBooks item IDs (per org)

**See Also:**
- `scenarios/metrc-sync-workflow.md` - Complete Metrc sync guide
- `ENTITY_TYPES.md` - Item type definition

---

## Operations

### 1. `get_items(int $start_at = 1, int $max_count = 100): Collection`

Paginated items (`SELECT * FROM Item`). Logs and returns empty on error.

### 2. `get_all_items(): Collection`

All items, auto-paginated.

### 3. `get_items_cached(string $orgId): Collection`

Cached `get_all_items` for an org (`qbo:items:{orgId}`). Note the parameter is the
**org id**, not a TTL. Backs `GET /quickbooks/items`.

**See:** `patterns/caching.md`.

### 4. `create_item(array $item_data): IPPItem`

Create an item. Always sets `TrackQtyOnHand = true`, `QtyOnHand = 0`, and
`InvStartDate = today` - any `quantity_on_hand` / `inv_start_date` you pass is
ignored.

**Required:** `name`.
**Optional:** `type` (default `'Inventory'`), `cost` (-> `PurchaseCost`),
`income_account_ref`, `expense_account_ref`, `asset_account_ref`.

```php
$item = $qbo->create_item([
    'name' => 'Premium Cannabis Flower',
    'type' => 'Inventory',
    'cost' => 12.50,
    'income_account_ref' => '79',
]);
```

### 5. `update_item(string $item_id, array $data): IPPItem`

Update item fields. Fetches the item first (SyncToken), then applies any of
`UnitPrice`, `PurchaseCost`, `QtyOnHand` (PascalCase keys). Throws on error.

```php
$qbo->update_item('456', ['UnitPrice' => 30.00, 'QtyOnHand' => 120]);
```

### 6. `update_item_quantity(string $item_id, float $new_quantity): IPPItem`

Convenience setter for just `QtyOnHand`. Fetches first, updates, throws on error.

```php
$qbo->update_item_quantity('456', 120);
```

### 7. `delete_item(string $item_id): IPPItem`

Soft delete: fetches the item and sets `Active = false` (QuickBooks best
practice). Returns the updated item; throws on error. There is no hard delete.

```php
$qbo->delete_item('456');
```

### 8. `sync_quantities_from_metrc(array $packages, array $mappings): array`

Sum active Metrc package quantities per Metrc item, then push each total onto the
mapped QB item via `update_item_quantity`. Packages with a `FinishedDate` or
`ArchivedDate` are excluded.

- `$packages` - Metrc packages (from `MetrcApi`)
- `$mappings` - `[metrc_item_id => qbo_item_id]`
- Returns `['synced' => int, 'failed' => int, 'errors' => string[]]`

```php
$packages = $metrc_api->get_cached_packages($facility);
$mappings = ['MetrcItem1' => 'QB456', 'MetrcItem2' => 'QB457'];
$result = $qbo->sync_quantities_from_metrc($packages, $mappings);
// ['synced' => 2, 'failed' => 0, 'errors' => []]
```

**See:** `scenarios/metrc-sync-workflow.md`.

---

## Common Workflows

### Create an Inventory Item
```php
$item = $qbo->create_item([
    'name' => 'Premium Cannabis Flower',
    'type' => 'Inventory',
    'income_account_ref' => '79',
]);
// QtyOnHand starts at 0; set it after with update_item_quantity
$qbo->update_item_quantity($item->Id, 100);
```

### Sync Quantities from Metrc
```php
$packages = $metrc_api->get_cached_packages($facility);
$mappings = QboItemMapping::where('organization_id', $orgId)
    ->pluck('qbo_item_id', 'metrc_item_id')
    ->all();

$result = $qbo->sync_quantities_from_metrc($packages, $mappings);
echo "Synced {$result['synced']}, failed {$result['failed']}";
```

**See:** `scenarios/metrc-sync-workflow.md`
