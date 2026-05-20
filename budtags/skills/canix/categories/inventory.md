# Inventory — Packages, Locations, Weight Units

Inventory endpoints cover packages (with rich lab test data), facility locations, and weight unit reference data. All endpoints are **read-only**.

**Note for BudTags integration**: Packages overlap with Metrc package data stored in Redis. These are typically skipped during import since Metrc is the source of truth. However, the Canix package schema contains richer lab test and COGS data than Metrc.

## Package Endpoints (2 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/packages` | List all submitted packages | All statuses, paginated |
| GET | `/packages/{id}` | Get single package | Very rich schema |

## Location Endpoints (3 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/locations` | List active locations | Supports `facility_id` |
| GET | `/locations/count` | Get location count | Supports `facility_id` + `where` |
| GET | `/locations/{id}` | Get single location | Includes parent_location |

## Weight Unit Endpoints (1 operation)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/weight_units` | List all weight units | ID, name, abbreviation |

## Package Schema (Rich)

The Package is one of the most data-rich entities in the Canix API:

```json
{
  "id": 1001,
  "tag": "1A4FF0000000022000000719",
  "is_active": true,
  "status": "Active",
  "item": { "id": 7036, "name": "Blue Dream - Trim", ... },
  "weight": 500.0,
  "original_weight": 520.0,
  "weight_unit": "Grams",
  "packaged_date": "2021-05-24",
  "production_batch_date": "2021-05-20",
  "expiration_date": "2022-05-24",
  "received_date": "2021-05-25",
  "location": { "id": 5, "name": "Vault A" },
  "production_batch": "PB-2021-05",
  "lot_id": "LOT-001",
  "cultivation_tax": 10.50,
  "available_for_sale": true,
  "cannabis_cogs": 30.00,
  "non_cannabis_inventory_cogs": 5.00,
  "cogs": { "labor": 10.0, "non_cannabis": 120.0, "cannabis": 30.0, "total": 160.0 },
  "source_packages": [
    { "id": 900, "tag": "1A4FF...", "weight": 100, "weight_unit": "Grams", "item": { "id": 50, "name": "Trim" } }
  ],
  "destination_packages": [
    { "id": 1100, "tag": "1A4FF...", "weight": 50, "weight_unit": "Grams", "item": { "id": 60, "name": "Preroll" } }
  ],
  "source_facility": "401-N0909",
  "source_facility_name": "Main Grow",
  "source_harvests": "H-2021-01",
  "notes": "Premium trim",
  "brand": { "id": 1, "name": "Premium" },
  "lab_test_url": "https://www.lab.com/lab-test/123456",
  "coa_url": "https://s3.amazonaws.com/bucket/coa/abc123.pdf?...",
  "lab_test_info": {
    "testing_facility_name": "Lab Corp",
    "testing_facility_license": "LIC-LAB-001"
  },
  "tested_package_tag": "1A4FF...",
  "test_status": "passed",
  "test_date": "2021-06-01",
  "test_results": { ... },
  "updated_at": "2021-06-15T08:00:00.000Z"
}
```

### Test Results (Comprehensive Cannabinoid + Terpene Profiles)

```json
{
  "thc": [
    { "value": 12.345, "measure": "percent" },
    { "value": 0.12345, "measure": "mg/g" },
    { "value": 5.6789, "measure": "mg" }
  ],
  "cbd": [ ... ],
  "cbn": [ ... ],
  "cbg": [ ... ],
  "cbga": [ ... ],
  "cbc": [ ... ],
  "cbca": [ ... ],
  "cbda": [ ... ],
  "thca": [ ... ],
  "delta_8_thc": [ ... ],
  "delta_9_thc": [ ... ],
  "delta_9_thca": [ ... ],
  "delta_8_thca": [ ... ],
  "thcv": [ ... ],
  "thcva": [ ... ],
  "total_cbd": [ ... ],
  "total_cbg": [ ... ],
  "total_delta_9_thc": [ ... ],
  "total_thc": [ ... ],
  "total_cannabinoid": [ ... ],
  "test_status": "passed",
  "tested_package_tag": "1A4FF...",
  "test_date": "2021-06-01",
  "terpenes": {
    "measure": "percent",
    "top_three": {
      "beta_myrcene": "0.051",
      "delta_limonene": "0.048",
      "linalool": "0.019"
    },
    "values": {
      "beta_myrcene": "0.051",
      "delta_limonene": "0.048",
      "linalool": "0.019",
      "alpha_pinene": "0.005",
      "beta_pinene": "0.008",
      "beta_caryophyllene": "0.015",
      "alpha_humulene": "0.006",
      "camphene": "0.001",
      "geraniol": "0.001",
      "borneol": "0.001",
      "alpha_bisabolol": "0.002",
      "caryophyllene_oxide": "0.001",
      "terpinolene": "0.001",
      "l_fenchone": "0.001",
      "menthol": "0.006",
      "endo_fenchyl_alcohol": "0.004"
    }
  }
}
```

**Each cannabinoid** is an array of `{ value, measure }` objects where measure is one of: `mg`, `mg/g`, `mg/serving`, `percent`.

**Terpenes** include 28+ individual terpene values plus a `top_three` summary.

### COGS Breakdown

```json
{
  "labor": 10.0,
  "non_cannabis": 120.0,
  "cannabis": 30.0,
  "total": 160.0
}
```

## Location Schema

```json
{
  "id": 123,
  "name": "Vault A - Section 2",
  "sqft": 14.4,
  "num_lights": 42,
  "parent_location": {
    "id": 100,
    "name": "Vault A",
    "sqft": 500.0,
    "num_lights": 200,
    "is_active": true
  },
  "is_active": true,
  "updated_at": "2018-11-06T08:00:00.000Z"
}
```

Locations have a **parent-child hierarchy** via `parent_location`.

## WeightUnit Schema

```json
{ "id": 1, "name": "Grams", "abbreviation": "g" }
```

Reference data — use the `id` in write operations (e.g., `weight_unit_id` in PurchaseOrderItem).

## Common Queries

```php
// Fetch active packages
$api->get('/packages', [
    'where' => "is_active=true AND available_for_sale=true",
    'limit' => 2000,
    'order_by' => 'packaged_date desc',
]);

// Fetch locations for a facility
$api->get('/locations', [
    'facility_id' => 123,
    'limit' => 2000,
]);

// Get all weight units (reference data)
$weight_units = $api->get('/weight_units');
```

---

**See:** `categories/products-items.md` for items referenced by packages
**See:** `patterns/facility-scoping.md` for facility_id on locations
