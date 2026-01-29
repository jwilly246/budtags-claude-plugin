# Metrc-to-QuickBooks Sync Workflow

Complete guide to syncing inventory quantities from Metrc packages to QuickBooks items in BudTags.

---

## Overview

**Purpose:** Keep QuickBooks inventory quantities in sync with actual Metrc package quantities

**Workflow:**
1. Map Metrc items to QuickBooks items (one-time setup)
2. Sync quantities from Metrc packages to QuickBooks items (ongoing)
3. Track sync results and errors

**Database Models:**
- `QboItemMapping` - Maps Metrc items to QuickBooks items
- `QboSyncLog` - Tracks sync operations

---

## Item Mapping Setup

### Understanding Item Mapping

**Problem:** Metrc and QuickBooks use different item IDs

**Solution:** Create mappings to link them

**Example:**
```
Metrc Item: "Premium Flower - 1oz" (ID: metrc-item-123)
     ↓
QuickBooks Item: "Cannabis Flower 1oz" (ID: qbo-item-456)
```

### QboItemMapping Model

**Table:** `qbo_item_mappings`

**Schema:**
```php
Schema::create('qbo_item_mappings', function (Blueprint $table) {
    $table->id();
    $table->foreignId('org_id')->constrained('organizations');
    $table->string('metrc_item_id');      // Metrc item ID or name
    $table->string('metrc_item_name');    // Metrc item display name
    $table->string('qbo_item_id');        // QuickBooks item ID
    $table->string('qbo_item_name');      // QuickBooks item name
    $table->timestamps();

    $table->unique(['org_id', 'metrc_item_id']);
});
```

### Creating Item Mappings

**Controller:** `QuickBooksController@storeItemMapping`

**Route:** `POST /quickbooks/item-mappings`

```php
public function storeItemMapping(Request $request)
{
    $validated = $request->validate([
        'metrc_item_id' => 'required|string',
        'metrc_item_name' => 'required|string',
        'qbo_item_id' => 'required|string',
        'qbo_item_name' => 'required|string',
    ]);

    QboItemMapping::updateOrCreate(
        [
            'org_id' => auth()->user()->active_org->id,
            'metrc_item_id' => $validated['metrc_item_id']
        ],
        $validated
    );

    return redirect()->back()->with('success', 'Item mapping saved');
}
```

### Frontend: ItemMappingModal

**Location:** `resources/js/Pages/Quickbooks/Modals/ItemMappingModal.tsx`

**Features:**
- Lists all Metrc items (from active packages)
- Shows QuickBooks items dropdown
- Displays existing mappings
- Add/update/delete mappings

**Usage:**
```tsx
<ItemMappingModal
    isOpen={showMappingModal}
    onClose={() => setShowMappingModal(false)}
    metrcItems={metrcItems}
    qboItems={qboItems}
    existingMappings={mappings}
/>
```

---

## Syncing Quantities

### Sync Process Overview

**Steps:**
1. Fetch all active Metrc packages for organization
2. Group packages by `ItemName`, sum `Quantity`
3. For each Metrc item, check if mapping exists
4. If mapped, update QuickBooks item quantity
5. Log results (synced, failed, skipped)

### sync_quantities_from_metrc() Method

**Location:** `QuickBooksApi.php`

```php
public function sync_quantities_from_metrc(): array
{
    $user = auth()->user();
    $org = $user->active_org;

    // 1. Get Metrc packages
    $metrcApi = new MetrcApi();
    $metrcApi->set_user($user);
    $packages = $metrcApi->packages(); // Active packages

    // 2. Group by ItemName, sum Quantity
    $itemQuantities = [];
    foreach ($packages as $package) {
        $itemName = $package->Item->Name;
        if (!isset($itemQuantities[$itemName])) {
            $itemQuantities[$itemName] = 0;
        }
        $itemQuantities[$itemName] += $package->Quantity;
    }

    // 3. Sync each item
    $synced = 0;
    $failed = 0;
    $skipped = 0;
    $errors = [];

    foreach ($itemQuantities as $metrcItemName => $quantity) {
        // Check if mapping exists
        $mapping = QboItemMapping::where('org_id', $org->id)
            ->where('metrc_item_name', $metrcItemName)
            ->first();

        if (!$mapping) {
            $skipped++;
            continue;
        }

        try {
            // Update QuickBooks item quantity
            $this->update_item_quantity($mapping->qbo_item_id, $quantity);
            $synced++;

            LogService::store(
                'QBO Quantity Synced',
                "{$metrcItemName}: {$quantity} units → QBO Item {$mapping->qbo_item_name}"
            );
        } catch (\Exception $e) {
            $failed++;
            $errors[] = "{$metrcItemName}: {$e->getMessage()}";

            LogService::store(
                'QBO Sync Failed',
                "{$metrcItemName}: {$e->getMessage()}"
            );
        }
    }

    // 4. Create sync log
    QboSyncLog::create([
        'org_id' => $org->id,
        'user_id' => $user->id,
        'status' => $failed > 0 ? 'partial' : 'success',
        'items_synced' => $synced,
        'items_failed' => $failed,
        'items_skipped' => $skipped,
        'errors' => $errors
    ]);

    return [
        'synced' => $synced,
        'failed' => $failed,
        'skipped' => $skipped,
        'errors' => $errors
    ];
}
```

---

## Sync Log Tracking

### QboSyncLog Model

**Table:** `qbo_sync_logs`

**Schema:**
```php
Schema::create('qbo_sync_logs', function (Blueprint $table) {
    $table->id();
    $table->foreignId('org_id')->constrained('organizations');
    $table->foreignId('user_id')->constrained();
    $table->enum('status', ['success', 'partial', 'failed']);
    $table->integer('items_synced')->default(0);
    $table->integer('items_failed')->default(0);
    $table->integer('items_skipped')->default(0);
    $table->json('errors')->nullable();
    $table->timestamps();
});
```

### Viewing Sync History

```php
$syncLogs = QboSyncLog::where('org_id', $org->id)
    ->orderBy('created_at', 'desc')
    ->take(10)
    ->get();

foreach ($syncLogs as $log) {
    echo "Sync at {$log->created_at}: ";
    echo "Synced: {$log->items_synced}, ";
    echo "Failed: {$log->items_failed}, ";
    echo "Skipped: {$log->items_skipped}\n";

    if ($log->errors) {
        echo "Errors:\n";
        foreach ($log->errors as $error) {
            echo "  - {$error}\n";
        }
    }
}
```

---

## Running the Sync

### Manual Sync (Controller)

**Controller:** `QuickBooksController@syncQuantities`

**Route:** `POST /quickbooks/sync-quantities`

```php
public function syncQuantities()
{
    $qbo = new QuickBooksApi();
    $qbo->set_user(auth()->user());

    $result = $qbo->sync_quantities_from_metrc();

    if ($result['failed'] > 0) {
        return redirect()->back()->with('warning',
            "Synced {$result['synced']} items, {$result['failed']} failed, {$result['skipped']} skipped"
        );
    }

    return redirect()->back()->with('success',
        "Successfully synced {$result['synced']} items ({$result['skipped']} skipped - no mapping)"
    );
}
```

### Automated Sync (Scheduled Job)

**Create Job:**
```php
php artisan make:job SyncMetrcToQuickBooks
```

**Job Implementation:**
```php
<?php

namespace App\Jobs;

use App\Models\Organization;
use App\Services\Api\QuickBooksApi;

class SyncMetrcToQuickBooks
{
    public function handle()
    {
        // Sync for all organizations with QBO connected
        $organizations = Organization::whereHas('qboAccessKeys')->get();

        foreach ($organizations as $org) {
            $user = $org->users()->first(); // Get any user from org

            try {
                $qbo = new QuickBooksApi();
                $qbo->set_user($user);
                $result = $qbo->sync_quantities_from_metrc();

                \Log::info("QBO Sync for Org {$org->id}", $result);
            } catch (\Exception $e) {
                \Log::error("QBO Sync failed for Org {$org->id}: {$e->getMessage()}");
            }
        }
    }
}
```

**Schedule in `app/Console/Kernel.php`:**
```php
protected function schedule(Schedule $schedule)
{
    // Sync every night at 2 AM
    $schedule->job(new SyncMetrcToQuickBooks())->dailyAt('02:00');

    // Or every hour
    $schedule->job(new SyncMetrcToQuickBooks())->hourly();
}
```

---

## Common Scenarios

### Scenario 1: Initial Setup

```php
// 1. Get Metrc items from active packages
$metrcApi = new MetrcApi();
$metrcApi->set_user($user);
$packages = $metrcApi->packages();
$metrcItems = collect($packages)->pluck('Item.Name', 'Item.Name')->unique();

// 2. Get QuickBooks items
$qbo = new QuickBooksApi();
$qbo->set_user($user);
$qboItems = $qbo->get_items_cached();

// 3. Create mappings (manual or via UI)
foreach ($metrcItems as $metrcItemName) {
    // Find matching QBO item (by name similarity or manual selection)
    $qboItem = findMatchingQboItem($metrcItemName, $qboItems);

    if ($qboItem) {
        QboItemMapping::create([
            'org_id' => $org->id,
            'metrc_item_id' => $metrcItemName,
            'metrc_item_name' => $metrcItemName,
            'qbo_item_id' => $qboItem->Id,
            'qbo_item_name' => $qboItem->Name
        ]);
    }
}

// 4. Run first sync
$result = $qbo->sync_quantities_from_metrc();
```

---

### Scenario 2: Handling Unmapped Items

```php
$result = $qbo->sync_quantities_from_metrc();

if ($result['skipped'] > 0) {
    echo "Warning: {$result['skipped']} items were skipped (no mapping)\n";
    echo "Please create mappings for these items:\n";

    // Get unmapped Metrc items
    $packages = $metrcApi->packages();
    $allMetrcItems = collect($packages)->pluck('Item.Name')->unique();

    $mappedItems = QboItemMapping::where('org_id', $org->id)
        ->pluck('metrc_item_name');

    $unmappedItems = $allMetrcItems->diff($mappedItems);

    foreach ($unmappedItems as $item) {
        echo "  - {$item}\n";
    }
}
```

---

## Troubleshooting

### Issue: Items Skipped (No Mapping)

**Cause:** Metrc items don't have corresponding QBO mappings

**Solution:**
1. Go to Item Mapping modal in UI
2. Map skipped items to QuickBooks items
3. Re-run sync

---

### Issue: Sync Fails for Some Items

**Check Sync Log:**
```php
$lastSync = QboSyncLog::latest()->first();

if ($lastSync->errors) {
    foreach ($lastSync->errors as $error) {
        echo "{$error}\n";
    }
}
```

**Common Errors:**
- QuickBooks item not found (item was deleted)
- QuickBooks item is inactive
- SyncToken conflict (rare)

---

### Issue: Quantities Don't Match

**Verify Metrc Quantities:**
```php
$packages = $metrcApi->packages(); // Active packages only
$itemName = 'Premium Flower - 1oz';

$totalQty = collect($packages)
    ->where('Item.Name', $itemName)
    ->sum('Quantity');

echo "Total Metrc quantity for {$itemName}: {$totalQty}";
```

**Verify QuickBooks Quantity:**
```php
$qboItem = $qbo->get_items_cached();
$item = collect($qboItem)->firstWhere('Name', 'Cannabis Flower 1oz');

echo "QuickBooks quantity: {$item->QtyOnHand}";
```

---

## Best Practices

1. **Map Items Early** - Set up mappings before first sync
2. **Regular Syncs** - Schedule daily or hourly syncs
3. **Monitor Sync Logs** - Check for failed/skipped items
4. **Update Mappings** - When adding new Metrc/QBO items
5. **Clear Cache** - Clear QBO items cache after manual item changes

---

## Next Steps

- **[INVOICE_WORKFLOW.md](INVOICE_WORKFLOW.md)** - Create invoices with synced quantities
- **[OPERATIONS_CATALOG.md](../OPERATIONS_CATALOG.md)** - All QuickBooks operations
