# LeafLink Inventory Workflow

Guide for managing inventory, facilities, and stock levels with LeafLink.

## Overview

This workflow covers:
- Tracking inventory across facilities
- Updating inventory quantities
- Managing retailer inventory (POS integration)
- Batch tracking
- Inventory reconciliation

---

## Step 1: Fetch Inventory Items

### Get All Inventory

```php
use App\Services\Api\LeafLinkApi;

$api = new LeafLinkApi();

// Fetch all inventory items
$response = $api->get('/inventory-items/', [
    'limit' => 100,
    'offset' => 0
]);

$inventoryItems = $response->json('results');

foreach ($inventoryItems as $item) {
    echo "Product ID: {$item['product']}\n";
    echo "Facility: {$item['facility']}\n";
    echo "Quantity: {$item['quantity']} {$item['unit']}\n";
    echo "---\n";
}
```

### Filter by Facility

```php
$response = $api->get('/inventory-items/', [
    'facility' => 456,  // Facility ID
    'limit' => 100
]);

$facilityInventory = $response->json('results');
```

### Filter by Product

```php
$response = $api->get('/inventory-items/', [
    'product' => 123,  // Product ID
    'limit' => 50
]);

$productInventory = $response->json('results');
```

---

## Step 2: Update Inventory Quantities

### Update Single Inventory Item

```php
$inventoryItemId = 789;

$response = $api->patch("/inventory-items/{$inventoryItemId}/", [
    'quantity' => 50  // New quantity
]);

if ($response->successful()) {
    $item = $response->json();

    LogService::store(
        'LeafLink Inventory Updated',
        "Item #{$item['id']}: Quantity updated to {$item['quantity']}"
    );
}
```

### Bulk Inventory Update

```php
public function bulk_update_inventory(array $updates)
{
    $api = new LeafLinkApi();

    $success = 0;
    $failed = 0;

    foreach ($updates as $update) {
        try {
            $response = $api->patch("/inventory-items/{$update['item_id']}/", [
                'quantity' => $update['new_quantity']
            ]);

            if ($response->successful()) {
                $success++;
            } else {
                $failed++;
            }
        } catch (Exception $e) {
            $failed++;
            LogService::store(
                'Inventory Update Error',
                "Item ID: {$update['item_id']}\nError: {$e->getMessage()}"
            );
        }
    }

    LogService::store(
        'Bulk Inventory Update',
        "Success: {$success}\nFailed: {$failed}"
    );

    return ['success' => $success, 'failed' => $failed];
}
```

---

## Step 3: Manage Facilities

### List All Facilities

```php
$response = $api->get('/facilities/', [
    'company' => 123  // Your company ID
]);

$facilities = $response->json('results');

foreach ($facilities as $facility) {
    echo "{$facility['name']}\n";
    echo "Address: {$facility['address']['street']}, {$facility['address']['city']}\n";
    echo "License: {$facility['license']}\n";
    echo "---\n";
}
```

### Get Facility Details

```php
$facilityId = 456;

$response = $api->get("/facilities/{$facilityId}/");

if ($response->successful()) {
    $facility = $response->json();

    echo "Facility: {$facility['name']}\n";
    echo "Address: " . json_encode($facility['address'], JSON_PRETTY_PRINT) . "\n";
}
```

---

## Step 4: Retailer Inventory (POS Integration)

### Sync Retailer Inventory from POS

```php
public function sync_pos_inventory()
{
    $api = new LeafLinkApi();
    $companyId = 123;  // Your company ID

    // Get inventory from your POS system (e.g., BioTrack, METRC)
    $posInventory = $this->fetch_pos_inventory();  // Your POS integration

    $synced = 0;

    foreach ($posInventory as $posItem) {
        try {
            // Create or update retailer inventory in LeafLink
            $response = $api->post('/retailer-inventory/', [
                'company' => $companyId,
                'source' => 'BioTrack',  // or 'METRC', 'Dutchie', etc.
                'name' => $posItem['product_name'],
                'sku' => $posItem['sku'],
                'brand' => $posItem['brand_name'],
                'quantity' => $posItem['quantity'],
                'unit_of_measure' => $posItem['unit'] ?? 'grams',
                'is_low' => $posItem['quantity'] < 10  // Low stock threshold
            ]);

            if ($response->successful()) {
                $synced++;
            }
        } catch (Exception $e) {
            LogService::store(
                'POS Sync Error',
                "SKU: {$posItem['sku']}\nError: {$e->getMessage()}"
            );
        }
    }

    LogService::store('POS Inventory Synced', "{$synced} items synced to LeafLink");

    return $synced;
}
```

### List Retailer Inventory

```php
$response = $api->get('/retailer-inventory/', [
    'company' => 123,
    'is_low' => true,  // Only show low stock items
    'limit' => 100
]);

$lowStockItems = $response->json('results');

foreach ($lowStockItems as $item) {
    echo "{$item['name']} - {$item['sku']}\n";
    echo "Brand: {$item['brand']}\n";
    echo "Quantity: {$item['quantity']} {$item['unit_of_measure']}\n";
    echo "Source: {$item['source']}\n";
    echo "---\n";
}
```

### Update Retailer Inventory Quantity

```php
$retailerInventoryId = 789;

$response = $api->patch("/retailer-inventory/{$retailerInventoryId}/", [
    'quantity' => 25,
    'is_low' => false  // No longer low stock
]);

if ($response->successful()) {
    LogService::store(
        'Retailer Inventory Updated',
        "Item #{$retailerInventoryId}: Quantity updated to 25"
    );
}
```

---

## Step 5: Batch Tracking

### List Batches

```php
$response = $api->get('/batches/', [
    'product' => 123,  // Product ID
    'limit' => 50
]);

$batches = $response->json('results');

foreach ($batches as $batch) {
    echo "Batch: {$batch['batch_number']}\n";
    echo "Quantity: {$batch['quantity']} {$batch['unit']}\n";
    echo "Harvest Date: {$batch['harvest_date']}\n";

    if (isset($batch['test_results'])) {
        echo "THC: {$batch['test_results']['thc_percent']}%\n";
        echo "CBD: {$batch['test_results']['cbd_percent']}%\n";
    }

    echo "---\n";
}
```

### Create New Batch

```php
$response = $api->post('/batches/', [
    'product' => 123,
    'batch_number' => 'BATCH-2025-001',
    'quantity' => 1000,
    'unit' => 'grams',
    'harvest_date' => '2025-01-01',
    'test_date' => '2025-01-10',
    'test_results' => [
        'thc_percent' => 22.5,
        'cbd_percent' => 0.8,
        'total_cannabinoids' => 25.3,
        'terpenes' => [
            'myrcene' => 1.2,
            'limonene' => 0.8
        ]
    ]
]);

if ($response->successful()) {
    $batch = $response->json();

    LogService::store(
        'LeafLink Batch Created',
        "Batch #{$batch['batch_number']} created for product #{$batch['product']}"
    );
}
```

### Update Batch Quantity

```php
$batchId = 456;

$response = $api->patch("/batches/{$batchId}/", [
    'quantity' => 750  // Updated quantity after sales
]);

if ($response->successful()) {
    LogService::store('Batch Quantity Updated', "Batch #{$batchId}: 750 grams remaining");
}
```

---

## Step 6: Inventory Reconciliation

### Compare LeafLink vs Local Inventory

```php
public function reconcile_inventory()
{
    $api = new LeafLinkApi();
    $orgId = request()->user()->active_org->id;

    // Get LeafLink inventory
    $response = $api->get('/inventory-items/', ['limit' => 500]);
    $leaflinkInventory = collect($response->json('results'))->keyBy('product');

    // Get local inventory
    $localInventory = \App\Models\LeafLinkProduct::where('org_id', $orgId)
        ->get()
        ->keyBy('leaflink_id');

    $discrepancies = [];

    foreach ($leaflinkInventory as $productId => $leaflinkItem) {
        $localItem = $localInventory->get($productId);

        if (!$localItem) {
            $discrepancies[] = [
                'product_id' => $productId,
                'issue' => 'Missing from local database',
                'leaflink_qty' => $leaflinkItem['quantity']
            ];
            continue;
        }

        if ($localItem->quantity != $leaflinkItem['quantity']) {
            $discrepancies[] = [
                'product_id' => $productId,
                'issue' => 'Quantity mismatch',
                'local_qty' => $localItem->quantity,
                'leaflink_qty' => $leaflinkItem['quantity'],
                'difference' => $leaflinkItem['quantity'] - $localItem->quantity
            ];
        }
    }

    LogService::store(
        'Inventory Reconciliation',
        "Found " . count($discrepancies) . " discrepancies:\n" .
        json_encode($discrepancies, JSON_PRETTY_PRINT)
    );

    return $discrepancies;
}
```

### Auto-Sync Discrepancies

```php
public function fix_discrepancies(array $discrepancies)
{
    $fixed = 0;

    foreach ($discrepancies as $discrepancy) {
        $productId = $discrepancy['product_id'];
        $correctQty = $discrepancy['leaflink_qty'];

        try {
            // Update local quantity to match LeafLink
            \App\Models\LeafLinkProduct::where('leaflink_id', $productId)
                ->update(['quantity' => $correctQty]);

            $fixed++;
        } catch (Exception $e) {
            LogService::store(
                'Reconciliation Fix Error',
                "Product ID: {$productId}\nError: {$e->getMessage()}"
            );
        }
    }

    LogService::store('Inventory Reconciliation Fixed', "{$fixed} discrepancies resolved");

    return $fixed;
}
```

---

## Step 7: Low Stock Alerts

### Check for Low Stock Items

```php
public function check_low_stock(int $threshold = 10)
{
    $api = new LeafLinkApi();

    $response = $api->get('/inventory-items/', [
        'limit' => 500
    ]);

    $inventoryItems = $response->json('results');

    $lowStockItems = array_filter($inventoryItems, function ($item) use ($threshold) {
        return $item['quantity'] < $threshold;
    });

    if (count($lowStockItems) > 0) {
        LogService::store(
            'Low Stock Alert',
            count($lowStockItems) . " items below {$threshold} units:\n" .
            json_encode($lowStockItems, JSON_PRETTY_PRINT)
        );

        // Send notification
        // Mail::to($manager)->send(new LowStockAlert($lowStockItems));
    }

    return $lowStockItems;
}
```

---

## Complete Inventory Controller

```php
namespace App\Http\Controllers;

use App\Services\Api\LeafLinkApi;
use App\Services\LogService;
use Illuminate\Http\Request;
use Inertia\Inertia;

class LeafLinkInventoryController extends Controller
{
    public function index()
    {
        $api = new LeafLinkApi();

        $response = $api->get('/inventory-items/', [
            'limit' => 100,
            'offset' => 0
        ]);

        $inventory = $response->json('results');
        $totalCount = $response->json('count');

        return Inertia::render('Leaflink/Inventory', [
            'inventory' => $inventory,
            'totalCount' => $totalCount
        ]);
    }

    public function update(Request $request)
    {
        $values = $request->validate([
            'item_id' => 'required|integer',
            'quantity' => 'required|numeric|min:0'
        ]);

        $api = new LeafLinkApi();
        $response = $api->patch("/inventory-items/{$values['item_id']}/", [
            'quantity' => $values['quantity']
        ]);

        if ($response->successful()) {
            LogService::store(
                'Inventory Quantity Updated',
                "Item #{$values['item_id']}: {$values['quantity']}"
            );

            return redirect()->back()->with('success', 'Inventory updated');
        }

        return redirect()->back()->with('error', 'Failed to update inventory');
    }

    public function reconcile()
    {
        $discrepancies = $this->reconcile_inventory();

        return Inertia::render('Leaflink/InventoryReconciliation', [
            'discrepancies' => $discrepancies
        ]);
    }

    public function sync_pos()
    {
        $synced = $this->sync_pos_inventory();

        return redirect()->back()->with('success', "Synced {$synced} items from POS");
    }

    private function reconcile_inventory() { /* ... */ }
    private function sync_pos_inventory() { /* ... */ }
}
```

---

## Best Practices

### 1. Regular Inventory Audits

Schedule daily reconciliation:

```php
// app/Console/Kernel.php

protected function schedule(Schedule $schedule)
{
    $schedule->call(function () {
        $controller = new LeafLinkInventoryController();
        $discrepancies = $controller->reconcile_inventory();

        if (count($discrepancies) > 0) {
            // Alert management
        }
    })->daily();
}
```

### 2. Track Inventory Movements

```php
// Log all quantity changes
$api->patch("/inventory-items/{$itemId}/", ['quantity' => $newQty]);

LogService::store(
    'Inventory Adjustment',
    "Item #{$itemId}: {$oldQty} → {$newQty} (Change: {$diff})"
);
```

### 3. Maintain Minimum Stock Levels

```php
if ($item['quantity'] < $minimumStock) {
    // Trigger reorder
    dispatch(new CreatePurchaseOrder($item['product']));
}
```

---

**See Also:**
- `OPERATIONS_CATALOG.md` - Inventory operations
- `PRODUCT_SYNC_WORKFLOW.md` - Product sync
- `ERROR_HANDLING.md` - Troubleshooting
