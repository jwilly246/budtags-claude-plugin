# Inventory - LeafLink API Category

Reference for inventory, facility and batch endpoints. Endpoints checked against the official spec; behaviour lines verified 2026-10-16 on the sandbox (raw files in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/`). On write behaviour, `patterns/verified-behavior.md` wins.

---

## Where Brand Inventory Lives

**A brand's sellable inventory is on the product (listing) object**, not a separate endpoint: "The inventory level is defined on the product object." [doc:brands_api_inventory.txt]

| Field | Meaning |
|-------|---------|
| `quantity` | Inventory level |
| `reserved_qty` | Reserved by orders in Submitted or Accepted |
| `available_inventory` | `quantity - reserved_qty` (writable) |

Set it with `PATCH /products/{id}/` and `quantity` or `available_inventory`. All three count **listing units** (one unit = denomination x unit_of_measure; one case = `unit_multiplier` units). Verified 2026-10-16 (sandbox, w_b_inventory.txt, w_c_units.txt)

There is **no `/inventory-items/` endpoint**. The batch-level item API is `/inventory/items/` (BETA).

---

## Collection Reference

**OpenAPI Schema:** `schemas/openapi-inventory.json`
**Company Compatibility:**
- Seller companies: product `quantity` fields (above); `/inventory/items/` + `/inventory/facilities/` (BETA) for batch/facility detail
- Buyer companies: `/retailer-inventory/*` for POS inventory

---

## Endpoint Overview

### Inventory Items (Seller, BETA)

"This API is in active development and is subject to change." [spec]

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory/items/` | List items (non-archived unless `include_archived`) |
| POST | `/inventory/items/` | Create item (`batch`, `is_archived`, `facility`, `product`, `quantity` required) |
| GET | `/inventory/items/{id}/` | Get item |
| PATCH | `/inventory/items/{id}/` | Update `quantity` / `is_archived` |

Item fields: `id`, `facility`, `inventory`, `product`, `quantity`, `quantity_in_product_uom`, `reserved_qty`, `reserved_qty_in_product_uom`, `batch`, `is_archived`.

### Facilities (BETA)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory/facilities/` | List facilities (`id`, `name`, `description`) |
| GET | `/inventory/facilities/{id}/` | Get facility |

### Retailer Inventory (Buyer/POS)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/retailer-inventory/` | List retailer inventory |
| POST | `/retailer-inventory/` | Create retailer inventory |
| GET | `/retailer-inventory/{id}/` | Get retailer inventory |
| PATCH | `/retailer-inventory/{id}/` | Update retailer inventory |
| DELETE | `/retailer-inventory/{id}/` | Delete retailer inventory |

Fields: `is_low`, `source`, `name`, `sku`, `brand`, `quantity`, `company`, `unit_of_measure` (all required on POST).

### Batches

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/batches/` | List batches |
| POST | `/batches/` | Create batch (`owner`, `production_batch_number`, `batch_date`, `testing_source` required) |
| GET | `/batches/{id}/` | Get batch |
| PATCH | `/batches/{id}/` | Update batch |
| DELETE | `/batches/{id}/` | Delete batch |

Batch fields: `id`, `owner`, `production_batch_number`, `batch_date`, `thc`, `thca`, `total_thc`, `cbd`, `cbda`, `cbg`, `cbn`, `total_cannabinoids`, `cannabinoid_unit`, `testing_source`, `documents`, `is_from_api`. A batch has no quantity. Link it to a listing with `/product-batches/` (see `categories/products.md`).

### Batch Documents (COAs, Test Results)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/batch-documents/` | List batch documents |
| POST | `/batch-documents/` | Upload document (multipart: `document`, `batch` required; `summary`) |
| GET | `/batch-documents/{id}/` | Get document |
| DELETE | `/batch-documents/{id}/` | Delete document |

---

## Common Use Cases

### 1. Get Seller Inventory (product level)

```php
$response = $api->get('/products/', [
    'fields_include' => 'id,sku,quantity,reserved_qty,available_inventory,listing_state',
    'archived' => 'false',
    'limit' => 500,                   // max 500
]);

$listings = $response->json('results');
```

### 2. Update Inventory Quantity

```php
// Listing units, not grams. Read listing_state back: thresholds can flip it.
$response = $api->patch("/products/{$productId}/", [
    'quantity' => '150',
]);

$listingState = $response->json('listing_state');
```

Or set `available_inventory`; LeafLink derives `quantity` (`available_inventory` 30 with nothing reserved -> `quantity` 30). Verified 2026-10-16 (sandbox, r2_t4_inventory_mgmt.txt T4x)

### 3. Batch-Level Items (BETA)

```php
$items = $api->get('/inventory/items/', [
    'product' => $productId,
    'include_archived' => 'false',
])->json('results');

$api->patch("/inventory/items/{$itemId}/", ['quantity' => '150']);
```

### 4. Manage Retailer Inventory (Buyers)

```php
$response = $api->get('/retailer-inventory/', [
    'company' => $companyId,
    'limit' => 100,
]);
```

### 5. Create Batch with COA

```php
$batch = $api->post('/batches/', [
    'owner' => $companyId,
    'production_batch_number' => 'Batch-2025-001',
    'batch_date' => '2025-01-01',
    'testing_source' => $testingSource,
    'thc' => '22.5',
    'cannabinoid_unit' => $unit,
])->json();

// Upload COA (multipart)
Http::withHeaders($api->headers())
    ->attach('document', $pdfContents, 'coa.pdf')
    ->post($baseUrl . '/batch-documents/', ['batch' => $batch['id']]);

// Link the batch to a listing
$api->post('/product-batches/', ['product' => $productId, 'batch' => $batch['id']]);
```

---

## Available Filters

### Inventory Items (`/inventory/items/`)
- `product` - Product ID
- `include_archived`

### Batches (`/batches/`)
- `batch_date__gt/gte/lt/lte`
- `id`, `owner`, `company_slug`, `production_batch_number`, `products`
- cannabinoid values: `thc`, `thca`, `total_thc`, `cbd`, `cbda`, `cbg`, `cbn`, `total_cannabinoids`

### Retailer Inventory (`/retailer-inventory/`)
- `company`

There are no `quantity__gt`, `created_date__*` or `harvest_date__*` filters in the spec.

---

## Important Notes

### How Orders Move Inventory

Verified 2026-10-16 (sandbox, w_b_inventory.txt); matches the docs' event table [doc:brands_api_inventory.txt].

| Order event | `quantity` | `reserved_qty` |
|-------------|-----------|----------------|
| Created as Submitted | no change | + line qty |
| Accepted | no change | no change |
| Fulfilled | - line qty | - line qty (released) |
| Shipped | no change | no change |
| Submitted/Accepted rejected | no change | - line qty [doc] |
| Rejected after Fulfilled (Shipped: per [doc]) | + line qty (given back) | no change |

- `reserved_qty` equalled the sum of open Submitted/Accepted/Backorder line quantities on all 3,217 listings checked. Verified 2026-10-16 (sandbox, r2_reserve.txt)
- A listing's `modified` does not move on these order-driven changes, only on API edits. Verified 2026-10-16 (sandbox, w_b_inventory.txt)
- LeafLink's recommended sync procedures [doc:brands_api_inventory.txt]:
  - Export orders from Fulfilled, consider inventory reserved immediately; sync with `quantity`.
  - Export orders from Submitted, consider inventory reserved immediately; sync with `available_inventory`.
  - Export orders from Submitted, don't consider inventory reserved until Fulfilled; sync with `quantity`.
- Pushing gross on-hand `quantity` after LeafLink already deducted a Fulfilled order re-inflates the listing until the stock really leaves.

### Inventory Management Modes and Thresholds

- `inventory_management`: 1 Managed, 2 Unlimited, 3 Inherited [spec]. Unlimited and Inherited still accept `quantity` and `available_inventory` PATCHes; the mode does not change. Verified 2026-10-16 (sandbox, r2_t4_inventory_mgmt.txt)
- Threshold fields (`threshold_value`, `threshold_action`, `reverse_threshold_value`, `reverse_threshold_action`) flip `listing_state` on a quantity PATCH, and beat a hand-set state sent in the same PATCH. Read `listing_state` from the PATCH response. Verified 2026-10-16 (sandbox, r2_t3_thresholds.txt, r3_g_threshold_response.txt)

### Seller vs Buyer Inventory

**Seller inventory** (product `quantity` fields; `/inventory/items/` BETA):
- What buyers can order
- Moved automatically by order events (table above)

**Retailer inventory** (`/retailer-inventory/`):
- Point-of-sale inventory at retail locations

---

## Related Resources

- **Patterns:** `patterns/verified-behavior.md` - Proven write behaviour (wins on conflicts)
- **Scenarios:** `scenarios/inventory-workflow.md` - Inventory management workflows
- **Patterns:** `patterns/company-scoping.md` - Seller vs buyer inventory
- **Schema:** `schemas/openapi-inventory.json`

---

## Quick Reference

```php
// Seller inventory = product fields
$api->get('/products/', ['fields_include' => 'id,quantity,reserved_qty,available_inventory']);

// Update quantity (listing units), read back listing_state
$api->patch("/products/{$id}/", ['quantity' => '150'])->json('listing_state');

// Batch-level items (BETA)
$api->get('/inventory/items/', ['product' => $id]);

// Retailer inventory
$api->get('/retailer-inventory/', ['company' => $companyId]);
```
