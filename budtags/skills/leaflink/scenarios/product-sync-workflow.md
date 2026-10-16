# LeafLink Product Sync Workflow

Guide for syncing the product catalog (listings) between LeafLink and BudTags. Fields are the real ProductResponse fields from the official spec; behaviour lines verified 2026-10-16 on the sandbox (raw files in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/`). On write behaviour, `patterns/verified-behavior.md` wins.

## Overview

This workflow covers:
- Fetching the product catalog from LeafLink
- Storing every field you will ever push back, losslessly
- Product images, batches and COA documents
- Metadata (brands, categories)
- Incremental sync
- Pushing changes back without damaging LeafLink data

**Golden rule:** never push a field you import lossily. A field stored in a normal form (a unit word, the first strain only, a reformatted phone) and pushed back overwrites LeafLink with the damaged value.

---

## Step 1: Fetch Product Catalog

### Full Walk

```php
use App\Services\Api\LeafLinkApi;

$api = new LeafLinkApi();

$listings = [];
$offset = 0;
$limit = 500;   // max 500 (1000 -> 400)

do {
    $response = $api->get('/products/', [
        'limit' => $limit,
        'offset' => $offset,
        'include_children' => 'strains',
    ]);

    foreach ($response->json('results') as $p) {
        $listings[$p['id']] = $p;   // dedupe by id
    }

    $offset += $limit;
} while ($response->json('next') !== null);

// /products/ ignores ordering and id__gt, so pages are not in a stable order.
if (count($listings) < $response->json('count')) {
    // a row moved between pages: walk again or fill the gap by modified__gte
}
```

`ordering`, `id__gt`, `id__gte` and `id__in` are IGNORED on `/products/` (whole list, same order). Verified 2026-10-16 (sandbox, r3_a_param_sweep.txt, r2_t9_pagination.txt)

### Fields That Matter

| Field | Shape |
|-------|-------|
| `unit_of_measure` | Milligram / Gram / Kilogram / Ounce / Pound / Unit / Liter / Milliliter |
| `unit_denomination` | read: `{id, value, name, label}`; write: integer id |
| `unit_multiplier` | units per case (integer) |
| `sell_in_unit_of_measure` | `"Case"` or `null` |
| `base_units_per_unit` | decimal string |
| `quantity`, `reserved_qty`, `available_inventory` | listing units |
| `wholesale_price`, `sale_price`, `retail_price` | `{amount, currency}`; per case when multiplier > 1 |
| `strains` | ids on write; objects with `include_children=strains` |
| `product_data_items` | `[{spec_type, dosage_unit, decimal_value, max_decimal_value, text_value}]` |
| `listing_state` | Available / Archived / Sample / Backorder / Internal / Unavailable |
| `inventory_management` | 1 Managed, 2 Unlimited, 3 Inherited |
| `threshold_value`, `threshold_action`, `reverse_threshold_value`, `reverse_threshold_action` | auto-flip of `listing_state` |
| `modified`, `last_edit` | both move on API price/qty edits |

---

## Step 2: Sync Products to Database

```php
foreach ($listings as $p) {
    $local = $org->listings()->firstOrNew(['leaflink_product_id' => $p['id']]);

    $local->fill([
        'name' => $p['name'],
        'sku' => $p['sku'],
        'wholesale_price' => $p['wholesale_price']['amount'],
        'sale_price' => $p['sale_price']['amount'],
        'quantity' => $p['quantity'],                         // listing units
        'unit_of_measure' => $p['unit_of_measure'],           // the word
        'unit_denomination_id' => $p['unit_denomination']['id'], // the id, separately
        'unit_multiplier' => $p['unit_multiplier'],
        'sell_in_unit_of_measure' => $p['sell_in_unit_of_measure'],
        'strain_ids' => array_column($p['strains'] ?? [], 'id'),  // the WHOLE list
        'listing_state' => $p['listing_state'],
        'inventory_management' => $p['inventory_management'],
        'leaflink_modified' => $p['modified'],
        'leaflink_last_edit' => $p['last_edit'],
    ]);

    $local->save();
}
```

- `unit_of_measure` and `unit_denomination` are two fields. Storing only the word (or defaulting the denomination to "each") later sends id 1 ("One") on a push. Verified 2026-10-16 (sandbox, w_c_units.txt: words and strings are rejected, only ids work)
- Keep the full strain list: `strains` is a whole-list replace on PATCH, so pushing one id drops the others. Verified 2026-10-16 (sandbox, w_h_strains.txt)

---

## Step 3: Sync Product Images

```php
$images = $api->get('/product-images/', [
    'product' => $leaflinkProductId,   // honoured
])->json('results');

foreach ($images as $image) {
    // fields: id, image (URL), product, position
    $local->images()->updateOrCreate(
        ['leaflink_image_id' => $image['id']],
        ['url' => $image['image'], 'position' => $image['position']]
    );
}
```

Up to 5 images per product [spec]. `product` filter on `/product-images/` is honoured. Verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)

---

## Step 4: Sync Product Batches & COA Data

```php
// 1. Product <-> batch assignments (fields: id, product, batch).
//    The spec lists only limit/offset for this endpoint, so filter on our side.
$assignments = collect($api->get('/product-batches/', ['limit' => 500])->json('results'))
    ->where('product', $leaflinkProductId);

foreach ($assignments as $a) {
    // 2. The batch itself: production_batch_number, batch_date, thc, cbd, total_cannabinoids,
    //    cannabinoid_unit, testing_source, documents (no quantity on a batch)
    $batch = $api->get("/batches/{$a['batch']}/")->json();

    // 3. COA documents: id, batch, document (file URL), summary, created_on, modified
    foreach ($batch['documents'] ?? [] as $doc) {
        // store $doc
    }
}
```

`ordering` is IGNORED on `/product-batches/`. Verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)

---

## Step 5: Sync Metadata (Brands, Categories, etc.)

### Brands

```php
// /companies/me/ is not in the spec; use /brands/. The `company` filter is IGNORED
// (returns every brand the key sees). Verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)
$brands = $api->get('/brands/')->json('results');   // id, name, company, description, image, banner
```

### Categories and Subcategories

```php
$categories = $api->get('/product-categories/')->json('results');      // id, name, slug, description
$subcategories = $api->get('/product-subcategories/')->json('results'); // + category
```

A `sub_category` that does not belong to the `category` is refused: 400 `"Subcategory does not belong to category"`. Verified 2026-10-16 (sandbox, r2_t6_category_pair.txt)

---

## Step 6: Selective Sync (Update Only Changed Products)

```php
$since = $org->leaflink_products_synced_at ?? now()->subDays(30);

$response = $api->get('/products/', [
    'modified__gte' => $since->utc()->format('Y-m-d\TH:i:s\Z'),   // honoured
    'limit' => 500,
    'offset' => 0,
]);
```

- `modified__gte` and `created_on__gte/__lt` are honoured on `/products/`. Verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)
- `modified` and `last_edit` both move on API price and quantity edits. Verified 2026-10-16 (sandbox, w_c_units.txt, r2_t4_inventory_mgmt.txt T4y)
- `modified` does NOT move when orders reserve or deduct stock, so an incremental walk will not see order-driven `quantity`/`reserved_qty` changes. Verified 2026-10-16 (sandbox, w_b_inventory.txt). Re-read quantities on a full walk.

---

## Step 7: Push Changes Back

```php
// Changed fields only; PATCH is partial, omitted fields are kept.
$payload = ['wholesale_price' => ['amount' => '320.00', 'currency' => 'USD']];

// A unit change rides as a group: word + denomination id + multiplier (+ sell_in, price)
$payload += [
    'unit_of_measure' => 'Gram',
    'unit_denomination' => 11,
    'unit_multiplier' => 28,
    'sell_in_unit_of_measure' => 'Case',   // null or "" to clear; multiplier 1 alone keeps "Case"
];

$response = $api->patch("/products/{$id}/", $payload);

// Thresholds can flip the state on a quantity push: record what LeafLink says
$local->listing_state = $response->json('listing_state');
```

- Omitted fields (units, multiplier, strains) are kept. Verified 2026-10-16 (sandbox, w_c_units.txt C2, C3; w_h_strains.txt H3)
- `sell_in_unit_of_measure` clears only with `null` or `""`. Verified 2026-10-16 (sandbox, w_c_sellin_clear.txt)
- The PATCH response already shows a threshold flip. Verified 2026-10-16 (sandbox, r3_g_threshold_response.txt)
- `strains` and `product_data_items` replace the whole list: send the full list or leave the key out.

---

## Complete Sync Controller

```php
namespace App\Http\Controllers;

use App\Services\Api\LeafLinkApi;
use App\Services\LogService;

class LeafLinkSyncController extends Controller
{
    public function sync_all()
    {
        $api = new LeafLinkApi();
        $org = request()->user()->active_org;

        try {
            $this->sync_metadata($api);            // brands, categories (Step 5)
            $listings = $this->fetch_all($api);    // Step 1 (dedupe by id)

            $synced = 0;
            $failed = 0;

            foreach ($listings as $p) {
                try {
                    $this->store_listing($org, $p); // Step 2 (lossless fields)
                    $synced++;
                } catch (\Exception $e) {
                    $failed++;
                    LogService::store('LeafLink Product Sync Error', "Product ID: {$p['id']}\nError: {$e->getMessage()}");
                }
            }

            LogService::store('LeafLink Full Sync Complete', "Synced: {$synced}\nFailed: {$failed}");

            return redirect()->back()->with('message', "Synced {$synced} products");
        } catch (\Exception $e) {
            LogService::store('LeafLink Sync Failed', $e->getMessage());
            return redirect()->back()->with('error', 'Sync failed');
        }
    }
}
```

---

## Best Practices

### 1. Schedule Regular Syncs

```php
// routes/console.php
Schedule::job(new SyncLeafLinkProducts($orgId))->everySixHours();
```

### 2. Use Queue for Large Syncs

```php
dispatch(new SyncLeafLinkProducts($orgId))->onQueue('leaflink-sync');
```

### 3. Never Retry Writes Blindly

GETs can be retried. A POST that timed out may already exist on LeafLink (product lines and payments cannot be deleted or are not idempotent): read back by a natural key before re-sending.

---

## Troubleshooting

### Products Not Syncing

**Check:**
1. API key is valid (`/products/?limit=1` returns 200)
2. Products exist in LeafLink (`/products/` returns results)
3. A filter that "works" but returns everything is probably ignored (see `patterns/filtering.md`)

### Wrong Unit or "One" After a Push

**Cause:** the denomination was stored as a word or not stored; the push sent id 1. **Fix:** store `unit_denomination['id']` and send the id with the unit group.

### Listing Hidden After a Quantity Push

**Cause:** LeafLink thresholds. **Fix:** read `listing_state` from the PATCH response; see `categories/products.md`.

### Missing Images

Not every product has images. Handle an empty list.

---

**See Also:**
- `patterns/verified-behavior.md` - Proven write behaviour
- `categories/products.md` - Product endpoints and filters
- `patterns/error-handling.md` - Error troubleshooting
