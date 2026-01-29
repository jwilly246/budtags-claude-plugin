# LeafLink Product Sync Workflow

Complete guide for syncing product catalog from LeafLink to BudTags.

## Overview

This workflow covers:
- Fetching product catalog from LeafLink
- Enriching products with metadata (brands, categories, etc.)
- Syncing products to local database
- Managing product images
- Handling batches and COA data
- Cache management

---

## Step 1: Fetch Product Catalog

### Basic Product Fetch

```php
use App\Services\Api\LeafLinkApi;

$api = new LeafLinkApi();

// Fetch all products (auto-paginated)
$products = $api->get_inventory_items();

echo "Fetched " . count($products) . " products\n";

foreach ($products as $product) {
    echo "{$product['display_name']} - SKU: {$product['sku']}\n";
    echo "Price: \${$product['unit_price']}\n";
    echo "Stock: {$product['inventory_quantity']}\n";
}
```

### Enriched Product Fetch (With Metadata)

```php
$orgId = request()->user()->active_org->id;

// Get products with brand, category, subcategory, and product line names
$enrichedProducts = $api->get_inventory_items_enriched($orgId);

foreach ($enrichedProducts as $product) {
    echo "{$product['display_name']}\n";
    echo "Brand: {$product['brand_name']}\n";
    echo "Category: {$product['category_name']}\n";
    echo "Subcategory: {$product['subcategory_name']}\n";
    echo "Line: {$product['product_line_name']}\n";
    echo "---\n";
}
```

**Note:** Enriched fetch is cached for 5 minutes by default.

---

## Step 2: Sync Products to Database

### Basic Sync

```php
public function sync_products()
{
    $api = new LeafLinkApi();
    $orgId = request()->user()->active_org->id;

    try {
        // Fetch products from LeafLink
        $leaflinkProducts = $api->get_inventory_items_enriched($orgId);

        $synced = 0;
        $updated = 0;
        $failed = 0;

        foreach ($leaflinkProducts as $product) {
            try {
                $wasUpdated = \App\Models\LeafLinkProduct::updateOrCreate(
                    [
                        'leaflink_id' => $product['id'],
                        'org_id' => $orgId
                    ],
                    [
                        'name' => $product['display_name'],
                        'sku' => $product['sku'],
                        'price' => $product['unit_price'],
                        'quantity' => $product['inventory_quantity'],
                        'unit_denomination' => $product['unit_denomination'] ?? 'each',
                        'brand_name' => $product['brand_name'],
                        'category_name' => $product['category_name'],
                        'subcategory_name' => $product['subcategory_name'],
                        'product_line_name' => $product['product_line_name'],
                        'description' => $product['description'] ?? null,
                        'active' => $product['active'] ?? true,
                        'last_synced_at' => now()
                    ]
                );

                if ($wasUpdated->wasRecentlyCreated) {
                    $synced++;
                } else {
                    $updated++;
                }

            } catch (Exception $e) {
                $failed++;
                LogService::store(
                    'LeafLink Product Sync Error',
                    "Product: {$product['display_name']}\nError: {$e->getMessage()}"
                );
            }
        }

        // Clear cache after sync
        $api->clearCache($orgId);

        LogService::store(
            'LeafLink Product Sync Complete',
            "Created: {$synced}\nUpdated: {$updated}\nFailed: {$failed}"
        );

        return redirect()->back()->with('success', "Synced {$synced} new products, updated {$updated}");

    } catch (Exception $e) {
        LogService::store('LeafLink Sync Error', $e->getMessage());
        return redirect()->back()->with('error', 'Sync failed: ' . $e->getMessage());
    }
}
```

---

## Step 3: Sync Product Images

### Fetch and Store Images

```php
public function sync_product_images(int $leaflinkProductId)
{
    $api = new LeafLinkApi();

    // Get product images from LeafLink
    $response = $api->get('/product-images/', [
        'product' => $leaflinkProductId,
        'limit' => 50
    ]);

    if (!$response->successful()) {
        return;
    }

    $images = $response->json('results');

    foreach ($images as $image) {
        \App\Models\LeafLinkProductImage::updateOrCreate(
            [
                'leaflink_image_id' => $image['id'],
                'leaflink_product_id' => $leaflinkProductId
            ],
            [
                'image_url' => $image['image_url'],
                'thumbnail_url' => $image['thumbnail_url'] ?? null,
                'is_primary' => $image['is_primary'] ?? false,
                'display_order' => $image['display_order'] ?? 0
            ]
        );
    }

    LogService::store(
        'LeafLink Images Synced',
        "Product #{$leaflinkProductId}: " . count($images) . " images"
    );
}
```

### Download Images Locally (Optional)

```php
use Illuminate\Support\Facades\Storage;

public function download_product_images(int $productId)
{
    $images = \App\Models\LeafLinkProductImage::where('leaflink_product_id', $productId)->get();

    foreach ($images as $image) {
        try {
            // Download image content
            $imageContent = file_get_contents($image->image_url);

            // Generate filename
            $filename = "leaflink/products/{$productId}/" . basename($image->image_url);

            // Store in local storage
            Storage::disk('public')->put($filename, $imageContent);

            // Update local path
            $image->update(['local_path' => $filename]);

        } catch (Exception $e) {
            LogService::store(
                'Image Download Error',
                "Image ID: {$image->id}\nURL: {$image->image_url}\nError: {$e->getMessage()}"
            );
        }
    }
}
```

---

## Step 4: Sync Product Batches & COA Data

### Fetch Batches for Product

```php
public function sync_product_batches(int $leaflinkProductId)
{
    $api = new LeafLinkApi();

    $response = $api->get('/product-batches/', [
        'product' => $leaflinkProductId,
        'limit' => 100
    ]);

    if (!$response->successful()) {
        return;
    }

    $batches = $response->json('results');

    foreach ($batches as $batch) {
        $batchModel = \App\Models\LeafLinkBatch::updateOrCreate(
            [
                'leaflink_batch_id' => $batch['id'],
                'leaflink_product_id' => $leaflinkProductId
            ],
            [
                'batch_number' => $batch['batch_number'],
                'quantity' => $batch['quantity'] ?? 0,
                'unit' => $batch['unit'] ?? 'gram',
                'harvest_date' => $batch['harvest_date'] ?? null,
                'test_date' => $batch['test_date'] ?? null,
                'test_results' => $batch['test_results'] ?? null,  // JSON field
            ]
        );

        // Sync batch documents (COAs)
        $this->sync_batch_documents($batch['id']);
    }

    LogService::store(
        'LeafLink Batches Synced',
        "Product #{$leaflinkProductId}: " . count($batches) . " batches"
    );
}
```

### Sync Batch Documents (COAs)

```php
public function sync_batch_documents(int $leaflinkBatchId)
{
    $api = new LeafLinkApi();

    $response = $api->get('/batch-documents/', [
        'batch' => $leaflinkBatchId
    ]);

    if (!$response->successful()) {
        return;
    }

    $documents = $response->json('results');

    foreach ($documents as $doc) {
        \App\Models\LeafLinkBatchDocument::updateOrCreate(
            [
                'leaflink_document_id' => $doc['id'],
                'leaflink_batch_id' => $leaflinkBatchId
            ],
            [
                'document_type' => $doc['document_type'] ?? 'other',
                'document_url' => $doc['document_url'],
                'uploaded_date' => $doc['uploaded_date'] ?? now()
            ]
        );
    }
}
```

---

## Step 5: Sync Metadata (Brands, Categories, etc.)

### Fetch and Cache Brands

```php
public function sync_brands()
{
    $api = new LeafLinkApi();

    // Get company ID
    $company = $api->get('/companies/me/')->json();
    $companyId = $company['id'];

    // Fetch brands for this company
    $brands = $api->get_brands($companyId);

    foreach ($brands as $brand) {
        \App\Models\LeafLinkBrand::updateOrCreate(
            ['leaflink_brand_id' => $brand['id']],
            [
                'name' => $brand['name'],
                'company_id' => $companyId,
                'logo_url' => $brand['logo_url'] ?? null,
                'description' => $brand['description'] ?? null
            ]
        );
    }

    LogService::store('LeafLink Brands Synced', count($brands) . " brands");
}
```

### Fetch Categories and Subcategories

```php
public function sync_categories()
{
    $api = new LeafLinkApi();

    // Fetch categories
    $categories = $api->get_categories();

    foreach ($categories as $category) {
        \App\Models\LeafLinkCategory::updateOrCreate(
            ['leaflink_category_id' => $category['id']],
            [
                'name' => $category['name'],
                'description' => $category['description'] ?? null
            ]
        );
    }

    // Fetch subcategories
    $subcategories = $api->get_subcategories();

    foreach ($subcategories as $subcategory) {
        \App\Models\LeafLinkSubcategory::updateOrCreate(
            ['leaflink_subcategory_id' => $subcategory['id']],
            [
                'name' => $subcategory['name'],
                'category_id' => $subcategory['category'],
                'description' => $subcategory['description'] ?? null
            ]
        );
    }

    LogService::store(
        'LeafLink Categories Synced',
        count($categories) . " categories, " . count($subcategories) . " subcategories"
    );
}
```

---

## Step 6: Selective Sync (Update Only Changed Products)

### Track Last Sync Time

```php
public function incremental_sync()
{
    $api = new LeafLinkApi();
    $orgId = request()->user()->active_org->id;

    // Get last sync time
    $lastSync = \App\Models\LeafLinkSyncLog::where('org_id', $orgId)
        ->latest('synced_at')
        ->first();

    $modifiedSince = $lastSync?->synced_at ?? now()->subDays(30);

    // Fetch only modified products
    $response = $api->get('/products/', [
        'modified__gte' => $modifiedSince->toIso8601String(),
        'limit' => 100,
        'offset' => 0
    ]);

    $modifiedProducts = $response->json('results');

    $synced = 0;

    foreach ($modifiedProducts as $product) {
        \App\Models\LeafLinkProduct::updateOrCreate(
            ['leaflink_id' => $product['id'], 'org_id' => $orgId],
            [
                'name' => $product['display_name'],
                'price' => $product['unit_price'],
                'quantity' => $product['inventory_quantity'],
                'last_synced_at' => now()
            ]
        );

        $synced++;
    }

    // Log this sync
    \App\Models\LeafLinkSyncLog::create([
        'org_id' => $orgId,
        'synced_at' => now(),
        'products_synced' => $synced
    ]);

    LogService::store('LeafLink Incremental Sync', "{$synced} products updated");

    return redirect()->back()->with('success', "Updated {$synced} products");
}
```

---

## Step 7: Cache Management

### Clear Cache After Sync

```php
public function full_sync()
{
    $api = new LeafLinkApi();
    $orgId = request()->user()->active_org->id;

    // Perform sync
    $products = $api->get_inventory_items_enriched($orgId);

    // ... sync products ...

    // Clear cache to force fresh fetch next time
    $api->clearCache($orgId);

    LogService::store('LeafLink Sync', "Cache cleared for org {$orgId}");
}
```

### Force Fresh Fetch (Bypass Cache)

```php
// Method 1: Clear cache first
$api->clearCache($orgId);
$products = $api->get_inventory_items_enriched($orgId);

// Method 2: Use direct API call instead of cached method
$response = $api->get('/products/', ['limit' => 500]);
$products = $response->json('results');
```

---

## Complete Sync Controller

```php
namespace App\Http\Controllers;

use App\Services\Api\LeafLinkApi;
use App\Services\LogService;
use Illuminate\Http\Request;

class LeafLinkSyncController extends Controller
{
    public function sync_all()
    {
        $api = new LeafLinkApi();
        $orgId = request()->user()->active_org->id;

        try {
            // Step 1: Sync metadata
            $this->sync_brands();
            $this->sync_categories();

            // Step 2: Sync products
            $products = $api->get_inventory_items_enriched($orgId);

            $synced = 0;
            $failed = 0;

            foreach ($products as $product) {
                try {
                    // Sync product
                    $productModel = \App\Models\LeafLinkProduct::updateOrCreate(
                        ['leaflink_id' => $product['id'], 'org_id' => $orgId],
                        [
                            'name' => $product['display_name'],
                            'sku' => $product['sku'],
                            'price' => $product['unit_price'],
                            'quantity' => $product['inventory_quantity'],
                            'brand_name' => $product['brand_name'],
                            'category_name' => $product['category_name'],
                            'last_synced_at' => now()
                        ]
                    );

                    // Sync images
                    $this->sync_product_images($product['id']);

                    // Sync batches
                    $this->sync_product_batches($product['id']);

                    $synced++;

                } catch (Exception $e) {
                    $failed++;
                    LogService::store(
                        'LeafLink Product Sync Error',
                        "Product ID: {$product['id']}\nError: {$e->getMessage()}"
                    );
                }
            }

            // Clear cache
            $api->clearCache($orgId);

            LogService::store(
                'LeafLink Full Sync Complete',
                "Synced: {$synced}\nFailed: {$failed}"
            );

            return redirect()->back()->with('success', "Synced {$synced} products");

        } catch (Exception $e) {
            LogService::store('LeafLink Sync Failed', $e->getMessage());
            return redirect()->back()->with('error', 'Sync failed');
        }
    }

    private function sync_brands() { /* ... */ }
    private function sync_categories() { /* ... */ }
    private function sync_product_images($productId) { /* ... */ }
    private function sync_product_batches($productId) { /* ... */ }
}
```

---

## Best Practices

### 1. Schedule Regular Syncs

```php
// app/Console/Kernel.php

protected function schedule(Schedule $schedule)
{
    // Sync products every 6 hours
    $schedule->call(function () {
        $organizations = \App\Models\Organization::all();

        foreach ($organizations as $org) {
            dispatch(new SyncLeafLinkProducts($org->id));
        }
    })->everySixHours();
}
```

### 2. Use Queue for Large Syncs

```php
// Dispatch to queue for async processing
dispatch(new SyncLeafLinkProducts($orgId))->onQueue('leaflink-sync');
```

### 3. Track Sync History

```php
// Create sync log before starting
$syncLog = \App\Models\LeafLinkSyncLog::create([
    'org_id' => $orgId,
    'status' => 'in_progress',
    'started_at' => now()
]);

try {
    // Perform sync...

    $syncLog->update([
        'status' => 'completed',
        'completed_at' => now(),
        'products_synced' => $synced
    ]);
} catch (Exception $e) {
    $syncLog->update([
        'status' => 'failed',
        'error_message' => $e->getMessage()
    ]);
}
```

---

## Troubleshooting

### Products Not Syncing

**Check:**
1. API key is valid (`/companies/me/` returns 200)
2. Products exist in LeafLink (`/products/` returns results)
3. Company ID filter (brands, product lines are company-specific)

### Missing Images

**Solution:** Images may not be available for all products. Handle null image_url gracefully.

### Stale Cache

**Solution:** Clear cache manually: `$api->clearCache($orgId)`

---

**See Also:**
- `OPERATIONS_CATALOG.md` - Product operations reference
- `CODE_EXAMPLES.md` - Sync code examples
- `ERROR_HANDLING.md` - Sync error troubleshooting
