# LeafLink Inventory Workflow

Guide for managing stock levels, facilities and batches with LeafLink. Endpoints checked against the official spec; behaviour lines verified 2026-10-16 on the sandbox (raw files in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/`). On write behaviour, `patterns/verified-behavior.md` wins.

## Overview

This workflow covers:
- Reading seller inventory (it lives on the product/listing)
- Updating inventory quantities
- Facilities and batch-level items (BETA)
- Managing retailer inventory (POS integration)
- Batch tracking
- Inventory reconciliation against LeafLink's own order deductions

**Key fact:** a brand's inventory is the product's `quantity` / `reserved_qty` / `available_inventory` [doc:brands_api_inventory.txt]. There is no `/inventory-items/` endpoint.

---

## Step 1: Fetch Inventory

### Get All Seller Inventory

```php
use App\Services\Api\LeafLinkApi;

$api = new LeafLinkApi();

$response = $api->get('/products/', [
    'fields_include' => 'id,sku,name,quantity,reserved_qty,available_inventory,listing_state,inventory_management,unit_of_measure,unit_denomination,unit_multiplier',
    'archived' => 'false',
    'limit' => 500,      // max 500
    'offset' => 0,
]);

foreach ($response->json('results') as $listing) {
    echo "{$listing['name']}: {$listing['quantity']} on hand, {$listing['reserved_qty']} reserved\n";
}
```

- All three quantities count **listing units** (one unit = denomination x unit_of_measure, e.g. Gram / id 11 = 28 g); one case = `unit_multiplier` units. Verified 2026-10-16 (sandbox, w_b_inventory.txt, w_c_units.txt)
- `/products/` ignores `ordering` and `id__gt`: dedupe by `id` across pages. Verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)

### Batch-Level Items (BETA)

```php
$response = $api->get('/inventory/items/', [
    'product' => 123,          // spec filters: product, include_archived
]);

foreach ($response->json('results') as $item) {
    // id, facility, product, batch, quantity, quantity_in_product_uom,
    // reserved_qty, reserved_qty_in_product_uom, is_archived
}
```

"This API is in active development and is subject to change." [spec]

---

## Step 2: Update Inventory Quantities

### Update One Listing

```php
$response = $api->patch("/products/{$productId}/", [
    'quantity' => '50',        // listing units
]);

if ($response->successful()) {
    $listing = $response->json();

    // Thresholds can flip the state on a quantity push; the response already shows it
    $localListing->update(['listing_state' => $listing['listing_state']]);

    LogService::store(
        'LeafLink Inventory Updated',
        "Product #{$listing['id']}: quantity {$listing['quantity']}, state {$listing['listing_state']}"
    );
}
```

- `quantity` or `available_inventory` can be sent; LeafLink derives the other from `reserved_qty` [doc:brands_api_inventory.txt]. Verified 2026-10-16 (sandbox, r2_t4_inventory_mgmt.txt T4x)
- A quantity-only PATCH keeps every other field (units, multiplier, price). Verified 2026-10-16 (sandbox, w_c_units.txt C3)
- Threshold flip shows in the PATCH response and beats a `listing_state` sent in the same PATCH. Verified 2026-10-16 (sandbox, r2_t3_thresholds.txt, r3_g_threshold_response.txt)
- Unlimited (2) and Inherited (3) listings accept the quantity too; the mode does not change. Verified 2026-10-16 (sandbox, r2_t4_inventory_mgmt.txt)

### Bulk Inventory Update

```php
public function bulk_update_inventory(array $updates)
{
    $api = new LeafLinkApi();

    $success = 0;
    $failed = 0;

    foreach ($updates as $update) {
        try {
            $response = $api->patch("/products/{$update['product_id']}/", [
                'quantity' => (string) $update['new_quantity'],   // listing units
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
                "Product ID: {$update['product_id']}\nError: {$e->getMessage()}"
            );
        }
    }

    LogService::store('Bulk Inventory Update', "Success: {$success}\nFailed: {$failed}");

    return ['success' => $success, 'failed' => $failed];
}
```

---

## Step 3: Facilities

### List All Facilities (BETA)

```php
$facilities = $api->get('/inventory/facilities/')->json('results');

foreach ($facilities as $facility) {
    echo "{$facility['id']}: {$facility['name']} - {$facility['description']}\n";
}
```

### Get Facility Details

```php
$facility = $api->get("/inventory/facilities/{$facilityId}/")->json();
```

Facilities carry only `id`, `name`, `description` in the spec. Licences live on `/licenses/` and on the product's `license`.

---

## Step 4: Retailer Inventory (POS Integration)

### Sync Retailer Inventory from POS

```php
public function sync_pos_inventory()
{
    $api = new LeafLinkApi();
    $companyId = 123;  // Your company ID

    $posInventory = $this->fetch_pos_inventory();  // Your POS integration

    $synced = 0;

    foreach ($posInventory as $posItem) {
        try {
            // All eight fields are required on POST [spec]
            $response = $api->post('/retailer-inventory/', [
                'company' => $companyId,
                'source' => 'BioTrack',
                'name' => $posItem['product_name'],
                'sku' => $posItem['sku'],
                'brand' => $posItem['brand_name'],
                'quantity' => $posItem['quantity'],
                'unit_of_measure' => $posItem['unit'],
                'is_low' => $posItem['quantity'] < 10,
            ]);

            if ($response->successful()) {
                $synced++;
            }
        } catch (Exception $e) {
            LogService::store('POS Sync Error', "SKU: {$posItem['sku']}\nError: {$e->getMessage()}");
        }
    }

    LogService::store('POS Inventory Synced', "{$synced} items synced to LeafLink");

    return $synced;
}
```

### List Retailer Inventory

```php
$response = $api->get('/retailer-inventory/', [
    'company' => 123,          // the only filter in the spec
    'limit' => 100,
]);

$lowStockItems = collect($response->json('results'))->where('is_low', true);
```

### Update Retailer Inventory Quantity

```php
$response = $api->patch("/retailer-inventory/{$retailerInventoryId}/", [
    'quantity' => 25,
    'is_low' => false,
]);
```

---

## Step 5: Batch Tracking

### List Batches

```php
$response = $api->get('/batches/', [
    'products' => 123,          // spec filter name is `products`
    'limit' => 50,
]);

foreach ($response->json('results') as $batch) {
    echo "Batch: {$batch['production_batch_number']} ({$batch['batch_date']})\n";
    echo "THC: {$batch['thc']} {$batch['cannabinoid_unit']}, CBD: {$batch['cbd']}\n";
}
```

### Create New Batch

```php
$response = $api->post('/batches/', [
    'owner' => $companyId,
    'production_batch_number' => 'BATCH-2025-001',
    'batch_date' => '2025-01-01',
    'testing_source' => $testingSource,
    'thc' => '22.5',
    'cbd' => '0.8',
    'total_cannabinoids' => '25.3',
    'cannabinoid_unit' => $unit,
]);

$batch = $response->json();

// Link to a listing
$api->post('/product-batches/', ['product' => 123, 'batch' => $batch['id']]);
```

A batch has no quantity field [spec]; stock is counted on the listing.

---

## Step 6: Inventory Reconciliation

### What LeafLink Does by Itself

Verified 2026-10-16 (sandbox, w_b_inventory.txt); matches the docs' event table [doc:brands_api_inventory.txt].

| Order event | `quantity` | `reserved_qty` |
|-------------|-----------|----------------|
| Created as Submitted | no change | + line qty |
| Accepted | no change | no change |
| Fulfilled | - line qty | - line qty (released) |
| Shipped | no change | no change |
| Rejected after Fulfilled | + line qty (given back) | no change |

`reserved_qty` = sum of open Submitted/Accepted/Backorder line quantities (3,217 of 3,217 listings matched). Verified 2026-10-16 (sandbox, r2_reserve.txt)

### Compare LeafLink vs Local Inventory

```php
public function reconcile_inventory()
{
    $api = new LeafLinkApi();

    $leaflink = collect($this->fetch_all_listings($api))->keyBy('id');   // Step 1, deduped
    $local = $org->listings()->get()->keyBy('leaflink_product_id');

    $discrepancies = [];

    foreach ($leaflink as $productId => $listing) {
        $localItem = $local->get($productId);

        if (!$localItem) {
            $discrepancies[] = ['product_id' => $productId, 'issue' => 'Missing from local database'];
            continue;
        }

        // Expected LeafLink quantity = our on-hand (in listing units)
        // minus lines LeafLink already deducted at Fulfilled that have not left our stock yet.
        $expected = $localItem->on_hand_listing_units - $localItem->fulfilled_not_shipped_units;

        if ((float) $listing['quantity'] != (float) $expected) {
            $discrepancies[] = [
                'product_id' => $productId,
                'issue' => 'Quantity mismatch',
                'expected_qty' => $expected,
                'leaflink_qty' => $listing['quantity'],
            ];
        }
    }

    return $discrepancies;
}
```

Pushing gross on-hand after LeafLink already deducted a Fulfilled order re-inflates the listing until the stock really leaves. LeafLink's own recommended procedures [doc:brands_api_inventory.txt]:
- Export orders from Fulfilled, consider inventory reserved immediately; sync with `quantity`.
- Export orders from Submitted, consider inventory reserved immediately; sync with `available_inventory`.
- Export orders from Submitted, don't consider inventory reserved until Fulfilled; sync with `quantity`.

A listing's `modified` does not move on these order-driven changes, so a `modified__gte` walk misses them. Verified 2026-10-16 (sandbox, w_b_inventory.txt)

---

## Step 7: Low Stock Alerts

LeafLink has its own per-listing settings: `low_inventory_alert_threshold`, `should_alert_on_low_inventory` (both seen on sandbox reads, not in the spec), and the `threshold_*` fields that flip `listing_state`. Verified 2026-10-16 (sandbox, r3_g_threshold_response.txt, r2_t3_thresholds.txt)

```php
public function check_low_stock(int $threshold = 10)
{
    $api = new LeafLinkApi();

    $listings = $api->get('/products/', [
        'fields_include' => 'id,name,available_inventory,listing_state',
        'archived' => 'false',
        'limit' => 500,
    ])->json('results');

    return array_filter($listings, fn ($l) => (float) $l['available_inventory'] < $threshold);
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

        $response = $api->get('/products/', [
            'fields_include' => 'id,name,quantity,reserved_qty,available_inventory,listing_state',
            'limit' => 100,
            'offset' => 0,
        ]);

        return Inertia::render('Leaflink/Inventory', [
            'inventory' => $response->json('results'),
            'totalCount' => $response->json('count'),
        ]);
    }

    public function update(Request $request)
    {
        $values = $request->validate([
            'product_id' => 'required|integer',
            'quantity' => 'required|numeric|min:0',
        ]);

        $api = new LeafLinkApi();
        $response = $api->patch("/products/{$values['product_id']}/", [
            'quantity' => (string) $values['quantity'],
        ]);

        if ($response->successful()) {
            LogService::store(
                'Inventory Quantity Updated',
                "Product #{$values['product_id']}: {$values['quantity']} (state {$response->json('listing_state')})"
            );

            return redirect()->back()->with('message', 'Inventory updated');
        }

        return redirect()->back()->with('error', 'Failed to update inventory');
    }
}
```

---

## Best Practices

### 1. Regular Inventory Audits

Schedule a daily reconciliation (Step 6) and alert on discrepancies.

### 2. Track Inventory Movements

```php
$response = $api->patch("/products/{$productId}/", ['quantity' => (string) $newQty]);

LogService::store(
    'Inventory Adjustment',
    "Product #{$productId}: {$oldQty} → {$newQty}, state {$response->json('listing_state')}"
);
```

### 3. Push Listing Units

Convert Metrc on-hand into listing units (divide by the listing's base units per unit) before pushing. Pushing grams to a Gram/28 listing overstates stock 28x.

---

**See Also:**
- `patterns/verified-behavior.md` - Proven write behaviour
- `categories/inventory.md` - Inventory endpoints
- `scenarios/product-sync-workflow.md` - Product sync
- `patterns/error-handling.md` - Troubleshooting
