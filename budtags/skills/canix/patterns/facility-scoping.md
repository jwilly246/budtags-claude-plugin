# Canix API Facility Scoping

## Overview

Many Canix endpoints accept an optional `facility_id` query parameter to filter results to a specific facility. This is similar to Metrc's license-based scoping but uses Canix's internal facility IDs.

## Endpoints WITH facility_id Support

These endpoints accept `facility_id` as an optional query parameter:

| Endpoint | Parameter | Notes |
|----------|-----------|-------|
| `GET /items` | `facility_id` (integer) | Filter items by facility |
| `GET /item_types` | `facility_id` (integer) | Facility-specific item types |
| `GET /item_sub_types` | `facility_id` (integer) | Facility-specific sub-types |
| `GET /strains` | `facility_id` (integer) | Facility-specific strains |
| `GET /locations` | `facility_id` (integer) | Facility-specific locations |
| `GET /locations/count` | `facility_id` (integer) | Count locations in facility |
| `GET /facilities` | `facility_id` (integer) | Filter to specific facility |
| `GET /non_cannabis_products` | `facility_ids` (array) | Note: plural! Accepts array |

### Usage Example

```php
// Fetch items for a specific facility
$items = $api->get('/items', [
    'facility_id' => 123,
    'limit' => 2000,
]);

// Non-cannabis products use facility_ids (plural, array)
$nci = $api->get('/non_cannabis_products', [
    'facility_ids' => [123, 456],
    'limit' => 2000,
]);
```

## Endpoints WITHOUT facility_id Support

These endpoints do NOT filter by facility — they return all data for the company:

- `GET /sales_orders` (and sub-resources)
- `GET /purchase_orders` (and sub-resources)
- `GET /customers`
- `GET /vendors`
- `GET /packages`
- `GET /brands`
- `GET /plant_batches`
- `GET /plants`
- `GET /harvests`
- `GET /transfers`
- `GET /transfer_destinations`
- `GET /manu_batches`
- `GET /manu_batch_runs`
- `GET /bills_of_materials`
- `GET /audited_actions`
- `GET /weight_units`

Some of these entities have a `facility_id` field in the response that can be filtered using the `where` parameter:

```php
// Use where instead of facility_id for sales orders
$api->get('/sales_orders', [
    'where' => "facility_id=123",
]);
```

## Facility Discovery

Use the facilities endpoint to discover available facilities:

```php
$facilities = $api->get('/facilities');
// Returns: [{ id: 123, name: "Main Facility", license_number: "4a-x123", ... }]
```

## BudTags Integration

In BudTags, facility_id maps to the Metrc facility concept. When a Canix API key is facility-scoped (stored with `metrc_facility_id` in the secrets table), automatically pass the corresponding Canix facility_id on supported endpoints.

---

**See:** `patterns/filtering.md` for using `where=facility_id=X` on endpoints that don't have native facility_id support
