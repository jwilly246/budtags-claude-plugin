# Products & Catalog - LeafLink API Category

Reference for product catalog (listing) endpoints. Endpoints and fields checked against the official spec; behaviour lines verified 2026-10-16 on the sandbox (raw files in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/`). On write behaviour, `patterns/verified-behavior.md` wins.

---

## Collection Reference

**OpenAPI Schemas:**
- `schemas/openapi-products-core.json` - Core product CRUD
- `schemas/openapi-products-metadata.json` - Images, batches, strains, product lines

**Company Compatibility:** Seller companies manage listings (buyers have read-only access)

---

## Endpoint Overview

### Products (Core)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products/` | List products |
| POST | `/products/` | Create product |
| GET | `/products/{id}/` | Get product details |
| PATCH | `/products/{id}/` | Update product (partial) |
| DELETE | `/products/{id}/` | **Archive** product (spec: "Archive a product"). Listings cannot be deleted. |

### Product Batches (product to batch assignments)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/product-batches/` | List assignments (`id`, `product`, `batch`) |
| POST | `/product-batches/` | Assign a batch (`product`, `batch` required) |
| GET | `/product-batches/{id}/` | Get assignment |
| DELETE | `/product-batches/{id}/` | Remove assignment |

### Product Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/product-categories/` | List categories |
| GET | `/product-categories/{id}/` | Get category |
| GET | `/product-subcategories/` | List subcategories (each has a `category`) |
| GET | `/product-subcategories/{id}/` | Get subcategory |

### Product Lines

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/product-lines/` | List product lines |
| POST | `/product-lines/` | Create product line |
| GET | `/product-lines/{id}/` | Get product line |
| PATCH | `/product-lines/{id}/` | Update product line |

There is no DELETE for product lines, so a duplicate POST cannot be undone.

### Product Images

"Each product may have up to 5 images." [spec]

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/product-images/` | List images (`id`, `image`, `product`, `position`) |
| POST | `/product-images/` | Upload image (multipart: `image`, `product`, `position` required) |
| GET | `/product-images/{id}/` | Get image |
| DELETE | `/product-images/{id}/` | Delete image |

### Strains

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/strains/` | List strains |
| POST | `/strains/` | Create strain (`name`, `strain_classification` required) |
| GET | `/strains/{id}/` | Get strain |

The spec has no strain PATCH.

---

## Common Use Cases

### 1. Create Product

Required by the spec: `name`, `description`, `retail_price`, `wholesale_price`, `sale_price`, `minimum_order`, `maximum_order`, `listing_state`, `inventory_management`, `unit_of_measure`, `unit_denomination`, `category`, `sub_category`, `seller`, `brand`, `manufacturer`, `strain_classification`, `sku`, `license`. `strains` is required for Flower.

```php
$response = $api->post('/products/', [
    'name' => 'Blue Dream 28g',
    'description' => 'Premium Blue Dream flower',
    'sku' => 'BD-28',                                     // seller's unique id, no commas
    'retail_price' => ['amount' => '0.00', 'currency' => 'USD'],
    'wholesale_price' => ['amount' => '300.00', 'currency' => 'USD'], // per case when multiplier > 1
    'sale_price' => ['amount' => '0.00', 'currency' => 'USD'],
    'minimum_order' => '1',
    'maximum_order' => null,          // key REQUIRED; null = no maximum
    'listing_state' => 'Internal',
    'inventory_management' => 1,      // 1 Managed, 2 Unlimited, 3 Inherited
    'quantity' => '280',              // listing units, not grams
    'unit_of_measure' => 'Gram',      // the unit word
    'unit_denomination' => 11,        // numeric id ("28"); see the id table
    'unit_multiplier' => 28,          // units per case
    'sell_in_unit_of_measure' => 'Case',
    'category' => 1,
    'sub_category' => 8,              // must belong to category
    'seller' => $companyId,
    'brand' => $brandId,
    'manufacturer' => $companyId,
    'strain_classification' => 'hybrid',
    'license' => $licenseId,
    'strains' => [4572],              // strain ids
]);

$productId = $response->json('id');
```

- `maximum_order` key absent -> 400 `"This field is required."`; `null` is accepted. Verified 2026-10-16 (sandbox, r2_t5_max_order.txt)
- An inactive brand forces the listing archived: 400 `"This product must remain archived because the brand ... is not active."`. Verified 2026-10-16 (sandbox, w_c_units.txt C0)

### 2. Upload Product Image

```php
// multipart/form-data with image, product, position; max 5 images per product
$response = Http::withHeaders($api->headers())
    ->attach('image', $fileContents, 'product.jpg')
    ->post($baseUrl . '/product-images/', [
        'product' => $productId,
        'position' => 1,
    ]);
```

### 3. Fetch Products with Filters

```php
$response = $api->get('/products/', [
    'category' => 5,                    // comma list allowed
    'listing_state' => 'Available',
    'archived' => 'false',
    'name' => 'Blue Dream',             // case insensitive
    'modified__gte' => '2026-10-01T00:00:00Z',
    'include_children' => 'strains',    // or images, volume_discounts
    'limit' => 100,
]);

$products = $response->json('results');
```

### 4. Update Product Price

```php
// PATCH is partial: omitted fields keep their values
$response = $api->patch("/products/{$productId}/", [
    'wholesale_price' => ['amount' => '320.00', 'currency' => 'USD'],
]);
```

A price-only PATCH kept every unit field and the multiplier; `modified` and `last_edit` both moved. Verified 2026-10-16 (sandbox, w_c_units.txt C2)

### 5. Get Categories and Subcategories

```php
$categories = $api->get('/product-categories/')->json('results');
$subcategories = $api->get('/product-subcategories/')->json('results'); // each has 'category'
$productLines = $api->get('/product-lines/', ['brand' => $brandId])->json('results');
```

`/product-lines/?company=` is IGNORED (returns every line). Verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)

---

## Available Filters (`GET /products/`)

From the spec. An ignored filter returns the whole list with a 200; full honoured/ignored table in `patterns/filtering.md`.

### Text Filters
- `name` - case insensitive
- `search` - search term
- `display_name`
- `sku` - one or more SKUs, comma separated (honoured; verified 2026-10-16, sandbox, r3_a_param_sweep.txt)
- `seller_internal_id`

### Relationship Filters (comma lists)
- `category`, `sub_category`, `sub_category__isnull`
- `product_line`, `brand`, `company`, `company_slug`
- `strains` - strain ids
- `parent`, `parent__isnull`, `has_children`
- `license`, `license__isnull`, `license__type`
- `external_id_key` + `external_id_values` (use together)

### Status Filters
- `listing_state` - Available, Archived, Sample, Backorder, Internal, Unavailable (honoured; verified 2026-10-16, sandbox, r3_a_param_sweep.txt)
- `archived` - true/false
- `buyer`, `s2s_connected`

### Date Filters
- `created_on__gt/gte/lt/lte` (honoured)
- `modified__gt/gte/lt/lte` (honoured)
- `last_edit__gt/gte/lt/lte`

### Ignored on /products/
- `id__gt`, `id__gte`, `id__in` and `ordering` (`id` and `-id` return the same order). Verified 2026-10-16 (sandbox, r3_a_param_sweep.txt, r2_t9_pagination.txt). There is no id cursor and no server ordering for offset walks: dedupe by `id` and check the total against `count`.

### Response Shaping
- `fields_include`, `fields_exclude`, `include_children` (`images`, `volume_discounts`, `strains`)

---

## Important Notes

### Unit Fields (root cause of the 10-15 denomination bug)

`unit_of_measure` and `unit_denomination` are **two separate fields**. Store both. Never send one without the other and the price/multiplier.

- `unit_of_measure`: Milligram, Gram, Kilogram, Ounce, Pound, Unit, Liter, Milliliter [spec].
- `unit_denomination` is **written as a numeric id only**: `"Gram"` and `"28"` -> 400 `"Value must be id of an existing UnitDenomination."`; `11` works. Reads return `{"id": 11, "value": "28.00000", "name": "Twenty-Eight", "label": "28"}`. Verified 2026-10-16 (sandbox, w_c_units.txt). Id table: `patterns/verified-behavior.md`.
- `unit_multiplier` is not reset when omitted. Verified 2026-10-16 (sandbox, w_c_units.txt C2, C3)
- `unit_multiplier: 1` alone keeps `sell_in_unit_of_measure: "Case"`; only `null` or `""` clears it. Verified 2026-10-16 (sandbox, w_c_units.txt C4, w_c_sellin_clear.txt)
- Never send `unit_of_measure: "Case"` (release 2.27.0). Sell cases with `sell_in_unit_of_measure: "Case"` + `unit_multiplier`.

### Quantity = Listing Units

`quantity`, `reserved_qty` and `available_inventory` count listing units (one unit = denomination x unit_of_measure; Gram / id 11 = 28 g, `base_units_per_unit` "28"). One case = `unit_multiplier` units. Verified 2026-10-16 (sandbox, w_b_inventory.txt, w_c_units.txt). Push listing units, never raw Metrc grams.

### Lists Replace

- `strains`: whole-list replace; `[]` clears; omitted keeps. Verified 2026-10-16 (sandbox, w_h_strains.txt)
- `product_data_items`: "The list in the request will replace any existing product data items." [spec]

### Thresholds Flip listing_state

With `threshold_value` / `threshold_action` / `reverse_threshold_value` / `reverse_threshold_action` set, a quantity PATCH changes `listing_state` by itself, and beats a hand-set state in the same PATCH. The PATCH response already shows the new state: read it back after every quantity push. Verified 2026-10-16 (sandbox, r2_t3_thresholds.txt, r3_g_threshold_response.txt)

### Other Create/Update Rules

- Category/sub-category mismatch -> 400 `"Subcategory does not belong to category"` (sub alone or with a non-matching category). Verified 2026-10-16 (sandbox, r2_t6_category_pair.txt)
- Unlimited (2) and Inherited (3) listings accept `quantity` and `available_inventory`; the mode does not change. Verified 2026-10-16 (sandbox, r2_t4_inventory_mgmt.txt)
- `modified` and `last_edit` move on API price and quantity edits, but `modified` does NOT move when orders change quantity or `reserved_qty`. Verified 2026-10-16 (sandbox, w_c_units.txt, w_b_inventory.txt)
- Archive with `PATCH {"listing_state": "Archived"}` (or `DELETE`, which archives). Verified 2026-10-16 (sandbox, w_cleanup.txt)

### Company Scoping

- Only **seller companies** can create/update products
- **Buyer companies** can browse products (read-only)
- All products are company-scoped (tied to seller)

### Product Hierarchy

```
Brand
└── Product Line (optional grouping)
    └── Product (listing)
        ├── Category + Sub-category (both required, must match)
        ├── Strains (array of ids; required for Flower)
        ├── Images (up to 5)
        └── Batches (via /product-batches/ assignments)
```

### Trailing Slash Required

```php
// ❌ Wrong
$api->get('/products')

// ✅ Correct
$api->get('/products/')
```

---

## Related Resources

- **Patterns:** `patterns/verified-behavior.md` - Proven write behaviour (wins on conflicts)
- **Scenarios:** `scenarios/product-sync-workflow.md` - Product catalog synchronization
- **Patterns:** `patterns/company-scoping.md` - Seller vs buyer access
- **Patterns:** `patterns/filtering.md` - Honoured vs ignored filters
- **Schemas:** `schemas/openapi-products-core.json`, `schemas/openapi-products-metadata.json`

---

## Quick Reference

```php
// Create product (full required list above)
$api->post('/products/', [..., 'unit_of_measure' => 'Gram', 'unit_denomination' => 11, 'maximum_order' => null]);

// Update price (partial PATCH)
$api->patch("/products/{$id}/", ['wholesale_price' => ['amount' => '30.00', 'currency' => 'USD']]);

// Push quantity (listing units), then read listing_state from the response
$state = $api->patch("/products/{$id}/", ['quantity' => '140'])->json('listing_state');

// Replace the strain list (send the FULL list)
$api->patch("/products/{$id}/", ['strains' => [4572, 13220]]);

// Archive (listings cannot be deleted)
$api->patch("/products/{$id}/", ['listing_state' => 'Archived']);

// Search products
$api->get('/products/', ['name' => 'Blue Dream', 'category' => 5]);
```
