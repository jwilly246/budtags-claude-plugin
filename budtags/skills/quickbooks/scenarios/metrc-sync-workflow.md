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

**Schema (from the real migration):**
```php
Schema::create('qbo_item_mappings', function (Blueprint $table) {
    $table->id();
    $table->string('metrc_item_id'); // METRC item ID
    $table->string('qbo_item_id');   // QuickBooks item ID
    $table->foreignUuid('organization_id')->constrained('organizations')->cascadeOnDelete()->cascadeOnUpdate();
    $table->unique(['organization_id', 'metrc_item_id']);
    $table->timestamps();
});
```

**Important:** The table stores only IDs - `organization_id`, `metrc_item_id`,
`qbo_item_id`. There are no `metrc_item_name` / `qbo_item_name` columns, and the
FK column is `organization_id` (a UUID), not `org_id`. The `QboItemMapping`
model's `$fillable` is exactly `['organization_id', 'metrc_item_id',
'qbo_item_id']`. Display names come from the live Metrc / QuickBooks item lists,
not from this table.

### Creating Item Mappings

**Controller:** `QuickBooksController::save_item_mappings`

**Route:** `POST /quickbooks/item-mappings`

The real endpoint saves a whole set of mappings at once and supports many-to-one:
several Metrc items can map to a single QuickBooks item. It replaces the existing
mappings for each submitted QB item inside a transaction.

```php
public function save_item_mappings(): RedirectResponse
{
    $validated = request()->validate([
        'mappings' => 'required|array',
        'mappings.*.qbo_item_id' => 'required|string',
        'mappings.*.metrc_item_ids' => 'required|array|min:1',
        'mappings.*.metrc_item_ids.*' => 'required|string',
    ]);

    $organizationId = $this->org_id();
    $now = now();

    $totalMappings = DB::transaction(function () use ($validated, $organizationId, $now) {
        // Bulk delete existing mappings for all submitted QB items
        $qboItemIds = collect($validated['mappings'])->pluck('qbo_item_id')->all();

        QboItemMapping::where('organization_id', $organizationId)
            ->whereIn('qbo_item_id', $qboItemIds)
            ->delete();

        // Build all rows (one per Metrc item) for a chunked batch insert
        $rows = [];
        foreach ($validated['mappings'] as $mapping) {
            foreach ($mapping['metrc_item_ids'] as $metrcItemId) {
                $rows[] = [
                    'organization_id' => $organizationId,
                    'qbo_item_id' => $mapping['qbo_item_id'],
                    'metrc_item_id' => $metrcItemId,
                    'created_at' => $now,
                    'updated_at' => $now,
                ];
            }
        }

        foreach (array_chunk($rows, 500) as $chunk) {
            QboItemMapping::insert($chunk);
        }

        return count($rows);
    });

    return redirect()->back()->with('message', "Saved {$totalMappings} QuickBooks item mappings!");
}
```

**Related routes:**
- `POST /quickbooks/item-mappings/clear` -> `clear_item_mappings`
- `GET /quickbooks/item-mappings/list` -> `list_item_mappings` (returns
  `metrc_item_id` / `qbo_item_id` pairs as JSON)

### Frontend: ItemMappingModal

**Location:** `resources/js/Components/ItemMappingView.tsx`

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
1. The controller fetches cached Metrc packages for the selected facility and
   builds a `[metrc_item_id => qbo_item_id]` map from the selected items.
2. `sync_quantities_from_metrc($packages, $mappings)` groups packages by
   `Item.Id` and sums `Quantity`, skipping packages with a `FinishedDate` or
   `ArchivedDate`.
3. For each Metrc item that has a mapping, push the total onto the mapped QB item
   via `update_item_quantity`.
4. Return `['synced', 'failed', 'errors']` (there is no `skipped` counter).
5. The controller writes a `QboSyncLog` row describing the result.

### sync_quantities_from_metrc() Method

**Location:** `QuickBooksApi.php`

**Signature:** `sync_quantities_from_metrc(array $packages, array $mappings): array`

- `$packages` - Metrc package arrays (each package is an array, e.g.
  `$p['Item']['Id']`, `$p['Quantity']`, `$p['FinishedDate']`)
- `$mappings` - `[metrc_item_id => qbo_item_id]`
- Returns `['synced' => int, 'failed' => int, 'errors' => string[]]`

```php
public function sync_quantities_from_metrc(array $packages, array $mappings): array
{
    $synced = 0;
    $failed = 0;
    $errors = [];

    // 1. Sum quantities per Metrc item, ignoring finished/archived packages
    $quantities = collect($packages)
        ->filter(fn (array $p) => !($p['FinishedDate'] ?? false) && !($p['ArchivedDate'] ?? false))
        ->groupBy(fn (array $p) => (string) $p['Item']['Id'])
        ->map(fn ($group) => $group->sum(fn (array $p) => (float) ($p['Quantity'] ?? 0)))
        ->all();

    // 2. Push each mapped total onto its QuickBooks item
    foreach ($quantities as $metrc_item_id => $total_quantity) {
        if (!isset($mappings[$metrc_item_id])) {
            continue; // no mapping for this Metrc item - simply not synced
        }

        $qbo_item_id = (string) $mappings[$metrc_item_id];

        try {
            $this->update_item_quantity($qbo_item_id, $total_quantity);
            $synced++;
        } catch (\Exception $e) {
            $failed++;
            $errors[] = "Item {$qbo_item_id}: ".$e->getMessage();
        }
    }

    return [
        'synced' => $synced,
        'failed' => $failed,
        'errors' => $errors,
    ];
}
```

**Note:** The method itself does not fetch packages, build mappings, or write a
sync log - the controller does all three (see "Running the Sync" below).

---

## Sync Log Tracking

### QboSyncLog Model

**Table:** `qbo_sync_logs`

**Schema (from the real migration):**
```php
Schema::create('qbo_sync_logs', function (Blueprint $table) {
    $table->id();
    $table->foreignUuid('organization_id')->constrained('organizations')->cascadeOnDelete()->cascadeOnUpdate();
    $table->foreignUuid('user_id')->nullable()->constrained('users')->nullOnDelete()->cascadeOnUpdate();
    $table->enum('entity_type', ['items', 'customers', 'invoices', 'accounts', 'all'])->default('all');
    $table->enum('status', ['success', 'failed', 'partial'])->default('success');
    $table->integer('items_synced')->default(0);
    $table->integer('items_failed')->default(0);
    $table->text('error_message')->nullable();
    $table->timestamps();

    $table->index('organization_id');
    $table->index('user_id');
    $table->index('entity_type');
    $table->index('created_at');
});
```

**Important:** The columns are `organization_id` (UUID), `user_id` (nullable
UUID), `entity_type`, `status`, `items_synced`, `items_failed`, and a single
`error_message` text column. There is no `items_skipped` column and no `errors`
JSON column - failures are concatenated into `error_message`. The `QboSyncLog`
model uses the `Prunable` trait and is pruned after 14 days
(`created_at < now()->subDays(14)`).

### Viewing Sync History

```php
$syncLogs = QboSyncLog::where('organization_id', $org->id)
    ->orderBy('created_at', 'desc')
    ->take(10)
    ->get();

foreach ($syncLogs as $log) {
    echo "Sync at {$log->created_at} ({$log->entity_type}): ";
    echo "Synced: {$log->items_synced}, ";
    echo "Failed: {$log->items_failed}\n";

    if ($log->error_message) {
        echo "Errors: {$log->error_message}\n";
    }
}
```

---

## Running the Sync

### Manual Sync (Controller)

**Controller:** `QuickBooksController::sync_quantities`

**Route:** `POST /quickbooks/sync-quantities`

The controller sets up the QuickBooks service with `set_service`, reads cached
Metrc packages for the selected facility, builds the `[metrc_item_id =>
qbo_item_id]` map from the posted `item_ids`, calls
`sync_quantities_from_metrc($packages, $mappings)`, then writes a `QboSyncLog`
row.

```php
public function sync_quantities(QuickBooksApi $api, MetrcApi $metrc_api): RedirectResponse
{
    $validated = request()->validate([
        'item_ids' => 'required|array|min:1',
        'item_ids.*.metrc_item_id' => 'required|string',
        'item_ids.*.qbo_item_id' => 'required|string',
    ]);

    $user = $this->user();
    $facility = $this->license();

    if (!$facility) {
        return redirect()->back()->with('error', 'Please select a facility first');
    }

    try {
        $api->set_service($user);

        // Read cached Metrc packages for the selected facility
        $packages = $metrc_api->get_cached_packages($facility);

        // Build [metrc_item_id => qbo_item_id] from the selected items
        $selectedMappings = [];
        foreach ($validated['item_ids'] as $item) {
            $selectedMappings[(string) $item['metrc_item_id']] = $item['qbo_item_id'];
        }

        $result = $api->sync_quantities_from_metrc($packages, $selectedMappings);

        $api->clear_cache($this->org_id());

        // Derive status: all-good -> success, some-good -> partial, none -> failed
        $status = ($result['failed'] === 0)
            ? 'success'
            : (($result['synced'] > 0) ? 'partial' : 'failed');

        QboSyncLog::create([
            'organization_id' => $this->org_id(),
            'user_id' => $user->id,
            'entity_type' => 'items',
            'status' => $status,
            'items_synced' => $result['synced'],
            'items_failed' => $result['failed'],
            'error_message' => !empty($result['errors'])
                ? implode('; ', array_slice($result['errors'], 0, 3))
                : null,
        ]);

        $message = $result['synced'].' items synced successfully';
        if ($result['failed'] > 0) {
            $message .= ', '.$result['failed'].' failed';
        }

        return redirect()->back()->with('message', $message);
    } catch (Exception $e) {
        QboSyncLog::create([
            'organization_id' => $this->org_id(),
            'user_id' => $user->id,
            'entity_type' => 'items',
            'status' => 'failed',
            'items_synced' => 0,
            'items_failed' => 0,
            'error_message' => $e->getMessage(),
        ]);

        return redirect()->back()->with('error', 'Failed to sync quantities: '.$e->getMessage());
    }
}
```

### Automated Sync (Scheduled Job)

**Create Job:**
```php
php artisan make:job SyncMetrcToQuickBooks
```

**Job Implementation:**

Both services need a user context. Set the QuickBooks service with
`set_service($user)`; set the Metrc service with `set_user($user)` (MetrcApi still
uses `set_user`). A queue job has no HTTP request, so `set_user` must be called
explicitly. The job builds the `[metrc_item_id => qbo_item_id]` map from the
org's stored `QboItemMapping` rows.

```php
<?php

namespace App\Jobs;

use App\Models\Organization;
use App\Models\QboItemMapping;
use App\Services\Api\MetrcApi;
use App\Services\Api\QuickBooksApi;
use App\Services\LogService;

class SyncMetrcToQuickBooks
{
    public function handle(): void
    {
        // Sync for all organizations with QBO connected
        $organizations = Organization::whereHas('qboAccessKeys')->get();

        foreach ($organizations as $org) {
            $user = $org->users()->first(); // Get any user from org
            if (!$user) {
                continue;
            }

            try {
                $metrc = new MetrcApi();
                $metrc->set_user($user);                 // MetrcApi uses set_user
                $packages = $metrc->get_cached_packages($facility);  // facility license string

                $mappings = QboItemMapping::where('organization_id', $org->id)
                    ->pluck('qbo_item_id', 'metrc_item_id')
                    ->all();

                $qbo = new QuickBooksApi();
                $qbo->set_service($user);                // QuickBooksApi uses set_service
                $result = $qbo->sync_quantities_from_metrc($packages, $mappings);

                LogService::store(
                    'QBO Sync',
                    "Org {$org->id}: synced {$result['synced']}, failed {$result['failed']}"
                );
            } catch (\Exception $e) {
                LogService::store('QBO Sync Failed', "Failed for Org {$org->id}: {$e->getMessage()}");
            }
        }
    }
}
```

**Schedule in `routes/console.php`** (Laravel 12 has no `app/Console/Kernel.php`):
```php
use App\Jobs\SyncMetrcToQuickBooks;
use Illuminate\Support\Facades\Schedule;

// Sync every night at 2 AM
Schedule::job(new SyncMetrcToQuickBooks())->dailyAt('02:00');
```

---

## Common Scenarios

### Scenario 1: Initial Setup

```php
// 1. Get Metrc packages for the facility (MetrcApi uses set_user)
$metrcApi = new MetrcApi();
$metrcApi->set_user($user);
$packages = $metrcApi->get_cached_packages($facility); // $facility = license string

// Distinct Metrc items keyed by their ID (packages are arrays)
$metrcItems = collect($packages)
    ->map(fn (array $p) => ['id' => (string) $p['Item']['Id'], 'name' => $p['Item']['Name']])
    ->unique('id')
    ->values();

// 2. Get QuickBooks items (QuickBooksApi uses set_service)
$qbo = new QuickBooksApi();
$qbo->set_service($user);
$qboItems = $qbo->get_items_cached($org->id); // pass the org id

// 3. Create mappings (only IDs are stored)
foreach ($metrcItems as $metrcItem) {
    // Find matching QBO item (by name similarity or manual selection)
    $qboItem = findMatchingQboItem($metrcItem['name'], $qboItems);

    if ($qboItem) {
        QboItemMapping::updateOrCreate(
            ['organization_id' => $org->id, 'metrc_item_id' => $metrcItem['id']],
            ['qbo_item_id' => $qboItem->Id]
        );
    }
}

// 4. Run first sync
$mappings = QboItemMapping::where('organization_id', $org->id)
    ->pluck('qbo_item_id', 'metrc_item_id')
    ->all();
$result = $qbo->sync_quantities_from_metrc($packages, $mappings);
```

---

### Scenario 2: Handling Unmapped Items

`sync_quantities_from_metrc` has no `skipped` counter - any Metrc item without a
mapping is simply not processed. To surface unmapped items, diff the package item
IDs against the stored mapping keys yourself.

```php
$packages = $metrcApi->get_cached_packages($facility);

// All Metrc item IDs present in the packages
$allMetrcItemIds = collect($packages)
    ->map(fn (array $p) => (string) $p['Item']['Id'])
    ->unique();

// Item IDs that already have a mapping
$mappedItemIds = QboItemMapping::where('organization_id', $org->id)
    ->pluck('metrc_item_id');

$unmappedItemIds = $allMetrcItemIds->diff($mappedItemIds);

if ($unmappedItemIds->isNotEmpty()) {
    echo "Warning: {$unmappedItemIds->count()} Metrc items have no mapping.\n";
    echo "Please create mappings for these item IDs:\n";
    foreach ($unmappedItemIds as $itemId) {
        echo "  - {$itemId}\n";
    }
}
```

---

## Troubleshooting

### Issue: Metrc Items Not Synced (No Mapping)

**Cause:** Metrc items don't have corresponding QBO mappings. The sync silently
skips any package whose Metrc item ID is not in the `$mappings` map (there is no
`skipped` counter).

**Solution:**
1. Go to Item Mapping modal in UI
2. Map the unmapped items to QuickBooks items (see Scenario 2 to list them)
3. Re-run sync

---

### Issue: Sync Fails for Some Items

**Check Sync Log:** failures are stored in the single `error_message` text column,
not a JSON array.
```php
$lastSync = QboSyncLog::where('organization_id', $org->id)->latest()->first();

if ($lastSync?->error_message) {
    echo $lastSync->error_message."\n";
}
```

**Common Errors:**
- QuickBooks item not found (item was deleted)
- QuickBooks item is inactive
- SyncToken conflict (rare)

---

### Issue: Quantities Don't Match

**Verify Metrc Quantities:** the sync sums by Metrc `Item.Id` and ignores finished
or archived packages, so mirror that when checking.
```php
$packages = $metrcApi->get_cached_packages($facility);
$metrcItemId = 'MetrcItem123';

$totalQty = collect($packages)
    ->filter(fn (array $p) => !($p['FinishedDate'] ?? false) && !($p['ArchivedDate'] ?? false))
    ->filter(fn (array $p) => (string) $p['Item']['Id'] === $metrcItemId)
    ->sum(fn (array $p) => (float) ($p['Quantity'] ?? 0));

echo "Total Metrc quantity for {$metrcItemId}: {$totalQty}";
```

**Verify QuickBooks Quantity:**
```php
$qboItems = $qbo->get_items_cached($org->id); // pass the org id
$item = collect($qboItems)->firstWhere('Name', 'Cannabis Flower 1oz');

echo "QuickBooks quantity: {$item->QtyOnHand}";
```

---

## Best Practices

1. **Map Items Early** - Set up mappings before first sync
2. **Regular Syncs** - Schedule daily or hourly syncs
3. **Monitor Sync Logs** - Check `items_failed` and `error_message` on each log
4. **Update Mappings** - When adding new Metrc/QBO items
5. **Clear Cache** - Clear QBO items cache after manual item changes

---

## Next Steps

- **[INVOICE_WORKFLOW.md](INVOICE_WORKFLOW.md)** - Create invoices with synced quantities
- **[OPERATIONS_CATALOG.md](../OPERATIONS_CATALOG.md)** - All QuickBooks operations
