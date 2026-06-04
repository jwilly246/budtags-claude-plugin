# Products Domain — Products, Test Results, POS Mappings

The Distru Products domain covers the catalog model: Products with rich relationships to Brand, Category, Strain, and TestResult, plus POS-system cross-mappings.

**Reconciled with live wire shapes 2026-05-25** against a production tenant (3,915 products across 26 distinct categories, 57 Terpenes, 478 Packaging). Many previously-documented fields turned out to be **doc-only** (never emitted by the API) — they've been removed. Several wire-only fields have been added. See `DISTRU-NATIVE-CONVERSION/AUDIT-FIELD-MATRIX.md` in the BudTags repo for the field-by-field reconciliation.

## Endpoints

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/public/v1/products` | List products | Page size 5,000. Eventually consistent ~1s. |
| GET | `/public/v1/products/{id}` | Get one product | Same shape as list. |
| POST | `/public/v1/products` | Create or update | UPSERT. **Field name inversion** — read `vendor`/`product_group`, write `vendor_id`/`group_id`. |
| GET | `/public/v1/test-results` | List test results | **HYPHEN slug** (`/test_results` returns 404). Eventually consistent. |
| GET | `/public/v1/test-results/{id}` | Get one test result | |
| GET | `/public/v1/product-pos-mappings` | List POS mappings | **HYPHEN slug**. `id` is INTEGER, not UUID. |
| GET | `/public/v1/product-pos-mappings/{id}` | Get one POS mapping | |
| POST | `/public/v1/product-pos-mappings` | Create or update | UPSERT. |
| **DELETE** | `/public/v1/product-pos-mappings/{id}` | **DELETE** a POS mapping | **The ONLY DELETE in the entire Distru API.** |
| POST | `/public/v1/custom-fields` | Create custom field def | **HYPHEN slug, POST-only.** No GET — read via `custom_data[]` on entities. |

> No `/brands`, `/categories`, `/subcategories`, `/product-lines`, or `/units` endpoints exist. Reference data for these is only available embedded inside Product responses — extract via product scan.

## Product entity shape — actual wire (26 top-level keys)

```jsonc
{
  "id": "<uuid>",
  "name": "...",
  "sku": "<string|null>",                                        // company-defined SKU
  "external_name": "<string|null>",                              // public-facing name override
  "description": "<string|null>",                                // plain string OR HTML
  "description_markdown": "<string|null>",                       // markdown variant — present alongside description
  "is_active": <boolean>,                                        // READ field. WRITE uses `is_inactive` (inverted)
  "deleted_at": "<iso|null>",                                    // tombstone timestamp; only present when `deleted=include` is passed
  "menus": [ /* objects */ ],                                    // menu memberships array (may be empty)
  "custom_data": [ /* {id, name, value} */ ],                    // tenant custom field values
  "vendor": {                                                    // SUPPLIER (READ shape — full embed)
    "id": "<uuid>",
    "name": "...",
    "updated_datetime": "<iso>"
  },                                                              // WRITE: send `vendor_id` (UUID)
  "brand": {                                                     // 3 fields (READ embed)
    "id": "<uuid>",
    "name": "...",
    "updated_datetime": "<iso>"
  } | null,                                                       // WRITE: send `brand_id`
  "category": {                                                  // 3 fields — wire key is `category`, NOT `product_category`
    "id": "<uuid>",
    "name": "...",
    "type": "OTHER|..."                                          // tenant-defined enum
  },                                                              // WRITE: send `product_category_id`
  "subcategory": {                                               // wire key is `subcategory`, NOT `product_subcategory`
    "id": "<uuid>",
    "name": "..."
  } | null,                                                       // WRITE: send `product_subcategory_id`
  "product_group": {                                             // 2 fields
    "id": "<uuid>",
    "name": "..."
  } | null,                                                       // WRITE: send `group_id` (NOT `product_group_id`)
  "strain": {                                                    // 3 fields
    "id": "<uuid>",
    "name": "...",
    "strain_type": "SATIVA|INDICA|HYBRID|..."
  } | null,                                                       // WRITE: send `strain_id`
  "msrp": "<decimal-string|null>",                               // retail price (dollars)
  "unit_price": "<decimal-string|null>",                         // wholesale price (dollars)
  "unit_cost": "<decimal-string|null>",                          // per-unit cost (dollars)
  "units_per_case": "<integer|null>",                            // case-pack size
  "unit_net_weight": "<decimal-string|null>",                    // per-unit weight
  "unit_serving_size": "<decimal-string|null>",                  // serving size value
  "unit_type": {                                                 // {id, name} object — NOT a flat string
    "id": "<uuid>",
    "name": "Gram|Unit|..."
  },
  "unit_net_weight_serving_size_unit_type": {                    // SEPARATE UoM for the serving-size weight
    "id": "<uuid>",
    "name": "..."
  } | null,
  "images": [ /* array of image refs */ ],
  "updated_datetime": "<iso>"
}
```

### Fields NOT in the wire (formerly documented; removed 2026-05-25)

The following fields were previously listed in this skill but **never appear in live API responses** (verified across 3,915 products / 26 categories on a production tenant). They've been removed; treat any future sighting as a tenant extension or stale doc:

- `upc`
- `is_inactive` — read direction only; this is the WRITE field name (skill confused itself by listing both)
- `is_archived`
- `tags` (array)
- `primary_test_result` — embedded; only on `/packages` endpoint, NOT `/products`
- `compliance_type` (METRC|BIOTRACK|NONE) — **NOT EMITTED.** Previously documented as required; not in wire. Cannot be used to route cannabis-vs-non-cannabis classification; use a category allowlist instead.
- `metrc_item_name` — NOT EMITTED. Distru does not expose the Metrc-item name hint on /products.
- `metrc_item_category` — NOT EMITTED. Same.
- `internal_notes`
- `inserted_datetime`
- `image_urls` — wire key is `images`, NOT `image_urls`
- `wholesale_price` — wire key is `unit_price`
- `case_quantity` — wire key is `units_per_case`
- `unit_size` — wire key is `unit_net_weight`
- `product_category` (top-level) — wire key is `category` (and `category.name` is the actual category string)
- `product_subcategory` — wire key is `subcategory`
- `product_line` (at top level) — wire emits only `product_group`

### READ/WRITE field name inversions (write-side)

| Read field | Write field | Notes |
|---|---|---|
| `vendor` (full embed) | `vendor_id` (UUID) | |
| `product_group` (full embed) | `group_id` (UUID) | Note: `group_id`, NOT `product_group_id` |
| `is_active` | `is_inactive` | INVERTED BOOLEAN on write |
| `brand` (full embed) | `brand_id` (UUID) | |
| `category` (full embed) | `product_category_id` (UUID) | |
| `subcategory` (full embed) | `product_subcategory_id` (UUID) | |
| `strain` (full embed) | `strain_id` (UUID) | |

The mapping doc Section 10 documents the writeback translation.

### Brand has an `id` — even though `/brands` doesn't exist

Each `brand` object on a product is `{id, name, updated_datetime}`. Reference data is discoverable but only by scanning the product catalog and deduping by `brand.id`. There is no canonical brand list endpoint.

### Routing cannabis vs non-cannabis (importer-side decision)

Since `compliance_type` is not in the wire, there is no authoritative signal on a Distru product indicating "this is a cannabis-tracked Metrc SKU vs. a packaging/ingredient/swag SKU." The practical classifier requires a category allowlist. BudTags's importer (`ProductImporter::NON_CANNABIS_DISTRU_CATEGORIES`) currently lists:

```
Packaging, Services, Terpenes, Swag Apparel, Event Prop,
In-Store Display, Event Swag, Giveaway, Banners
```

Items in those categories route to BudTags's `non_metrc_items` (Components) table. Items in any other category route to `products` (cannabis) when at least one of `brand`/`strain`/`product_group` is set, otherwise also to `non_metrc_items`.

This allowlist is tenant-curation. Different Distru tenants invent different category vocabularies; this list reflects one production tenant's catalog and will need extension for others.

## Filter parameters — /products

| Filter | Type | Notes |
|---|---|---|
| `inserted_datetime` | comma-range | |
| `updated_datetime` | comma-range | Canonical incremental-sync filter |
| `name` | string | Substring match |
| `sku` | string | |
| `brand_id[]` | bracket array | |
| `category_id[]` | bracket array | NOTE: `category_id` not `product_category_id` |
| `vendor_id[]` | bracket array | |
| `deleted` | tri-state string | `?deleted=include` returns soft-deleted rows with `deleted_at` populated |
| `menu_id` | **comma-string** | `?menu_id=uuid1,uuid2` — NOT a bracket array — multi-value as comma-string |
| `page[number]` | integer | |

NO `tags[]` filter (no `tags` field exists). NO `upc` filter. NO `compliance_type` filter.

## Test Results entity shape (live wire — 19+ keys plus open `additional_test_results` map)

```jsonc
{
  "id": "<uuid>",
  "name": "<string|null>",                                       // test-result label
  "lab_name": "<string|null>",
  "lab_license_number": "<string|null>",                         // wire uses `lab_license_number`, NOT `license_number`
  "release_date": "<iso date|null>",                             // wire uses `release_date`, NOT `result_datetime`
  "package_id": "<uuid|null>",                                   // mutex with batch_id
  "batch_id": "<uuid|null>",
  "is_primary": <boolean>,
  "mg_per_unit_type": "<string|null>",
  "thc_percentage": "<decimal-string|null>",
  "total_thc_percentage": "<decimal-string|null>",
  "thc_mg_per_unit": "<decimal-string|null>",
  "total_thc_mg_per_unit": "<decimal-string|null>",
  "cbd_percentage": "<decimal-string|null>",
  "total_cbd_percentage": "<decimal-string|null>",
  "cbd_mg_per_unit": "<decimal-string|null>",
  "total_cbd_mg_per_unit": "<decimal-string|null>",
  "additional_test_results": {                                   // open map — ~100-300 keys typical, tenant-configurable
    "alpha_pinene_percentage": "<decimal-string>",
    "beta_caryophyllene_percentage": "<decimal-string>",
    "limonene_percentage": "<decimal-string>",
    "thca_percentage": "<decimal-string>",
    "cbg_percentage": "<decimal-string>",
    "arsenic_ug_per_g": "<decimal-string>",                       // heavy metals
    "lead_ug_per_g": "<decimal-string>",
    "cadmium_ug_per_g": "<decimal-string>",
    "mercury_ug_per_g": "<decimal-string>",
    "abamectin_ug_per_g": "<decimal-string>",                     // pesticides
    "fipronil_ug_per_g": "<decimal-string>",
    "myclobutanil_ug_per_g": "<decimal-string>",
    "benzene_ug_per_g": "<decimal-string>",                       // residual solvents
    "ethanol_ug_per_g": "<decimal-string>",
    "toluene_ug_per_g": "<decimal-string>"
    // ... ~100 more keys per record
  },
  "updated_datetime": "<iso>"
}
```

### Test Results fields NOT in the wire (removed 2026-05-25)

- `license_number` — wire uses `lab_license_number`
- `result_datetime` — wire uses `release_date`
- `potency_thc` / `potency_cbd` / `potency_total_cannabinoids` — wire uses the granular `thc_percentage` / `total_thc_percentage` / `thc_mg_per_unit` / `total_thc_mg_per_unit` set (×2 for CBD)
- `metrc_lab_test_id` — NOT EMITTED
- `product_id` — NOT EMITTED (test results reference `package_id` OR `batch_id`, not product directly)
- `sample_id`, `expiration_datetime`, `passed_test`, `test_status`, `moisture_content`, `water_activity` — NOT EMITTED
- `inserted_datetime` — NOT EMITTED

## Product POS Mappings shape

```jsonc
{
  "id": <INTEGER>,                                                // The ONLY integer id in the API
  "product_id": "<uuid>",                                         // FK to /products
  "pos_type": "BLAZE|DUTCHIE|TREEZ|...",                          // discriminator
  "inserted_at": "<iso>",                                         // `_at` suffix, unique to this endpoint
  "updated_at": "<iso>",
  // Per-pos_type fields (only populated for matching pos_type):
  "blaze_asset_id": "<string|null>",
  "blaze_product_id": "<string|null>",
  "blaze_retailer_id": "<string|null>",
  "dutchie_product_id": "<integer-stored-as-string|null>",
  "dutchie_retailer_id": "<string|null>",
  "treez_product_id": "<string|null>",
  "treez_retailer_id": "<string|null>"
}
```

`DELETE /product-pos-mappings/{id}` is the ONLY DELETE endpoint in the entire Distru API. Other resources don't support DELETE.

## Cross-references

- Image handling: a separate `images[]` array is returned on each product; BudTags has a dedicated `ImageImporter` (polymorphic across `product_images` and `non_metrc_item_images`) that walks `external_ids->distru_raw_payload->images`
- Inventory + actual cost: `/inventory` endpoint provides live on-hand qty + `cost_per_unit_actual` (separate from /products `unit_cost` static cost)
- Companies as vendors: see `categories/crm.md` — vendor.id on products references a /companies row
- Custom field handling: mapping doc Decision #20 (3-tier strategy)
- Field-by-field reconciliation against live wire: `DISTRU-NATIVE-CONVERSION/AUDIT-FIELD-MATRIX.md` in the BudTags repo
