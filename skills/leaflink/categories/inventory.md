# Inventory - LeafLink API Category

Complete reference for inventory and facility management endpoints - 20 total operations.

---

## Collection Reference

**OpenAPI Schema:** `schemas/openapi-inventory.json`
**Total Endpoints:** 20
**Company Compatibility:**
- Seller companies: Use `/inventory-items/*` for seller inventory
- Buyer companies: Use `/retailer-inventory/*` for POS inventory

---

## Endpoint Overview

### Inventory Items (Seller)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory-items/` | List seller inventory |
| POST | `/inventory-items/` | Create inventory item |
| GET | `/inventory-items/{id}/` | Get item details |
| PATCH | `/inventory-items/{id}/` | Update inventory |

### Retailer Inventory (Buyer/POS)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/retailer-inventory/` | List retailer inventory |
| POST | `/retailer-inventory/` | Create retailer inventory |
| GET | `/retailer-inventory/{id}/` | Get retailer inventory |
| PATCH | `/retailer-inventory/{id}/` | Update retailer inventory |

### Facilities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/facilities/` | List facilities |
| GET | `/facilities/{id}/` | Get facility details |

### Batches

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/batches/` | List batches |
| POST | `/batches/` | Create batch |
| GET | `/batches/{id}/` | Get batch |
| PATCH | `/batches/{id}/` | Update batch |

### Batch Documents (COAs, Test Results)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/batch-documents/` | List batch documents |
| POST | `/batch-documents/` | Upload document |
| GET | `/batch-documents/{id}/` | Get document |
| DELETE | `/batch-documents/{id}/` | Delete document |

---

## Common Use Cases

### 1. Get Seller Inventory

```php
// Get inventory items for seller
$response = $api->get('/inventory-items/', [
    'product' => $productId,
    'facility' => $facilityId,
    'quantity__gt' => 0,  // Only items in stock
    'limit' => 100
]);

$items = $response->json('results');
```

### 2. Update Inventory Quantity

```php
$response = $api->patch("/inventory-items/{$itemId}/", [
    'quantity' => 150,
    'facility' => $facilityId
]);
```

### 3. Get Enriched Inventory (BudTags Helper)

```php
// Helper method that enriches inventory with relationships
$inventory = $api->get_inventory_items_enriched($orgId);

// Returns inventory with:
// - Product details
// - Facility information
// - Batch data
// - Available quantities
```

### 4. Manage Retailer Inventory (Buyers)

```php
// For buyer companies - POS inventory
$response = $api->get('/retailer-inventory/', [
    'product' => $productId,
    'facility' => $storeId,
    'limit' => 100
]);
```

### 5. Create Batch with COA

```php
// Create batch
$batch = $api->post('/batches/', [
    'name' => 'Batch-2025-001',
    'product' => $productId,
    'quantity' => 100,
    'harvest_date' => '2025-01-01'
]);

// Upload COA/test results
$api->post('/batch-documents/', [
    'batch' => $batch['id'],
    'document_url' => 'https://example.com/coa.pdf',
    'document_type' => 'coa'
]);
```

---

## Available Filters

### Inventory Filters
- `product` - Product ID
- `facility` - Facility ID
- `quantity__gt`, `quantity__gte`, `quantity__lte` - Quantity range
- `batch` - Batch ID

### Batch Filters
- `product` - Product ID
- `name__icontains` - Batch name search
- `harvest_date__gte`, `harvest_date__lte` - Harvest date range
- `test_date__gte`, `test_date__lte` - Test date range

### Date Filters
- `created_date__gte`, `created_date__lte`
- `modified__gte`, `modified__lte`

---

## Important Notes

### Seller vs Buyer Inventory

**Seller Inventory** (`/inventory-items/`):
- Warehouse/production inventory
- Tracks quantities at seller facilities
- Used for order fulfillment

**Retailer Inventory** (`/retailer-inventory/`):
- Point-of-sale inventory
- Tracks quantities at retail locations
- Used for customer sales

### Facilities

Facilities represent physical locations:
- Warehouses, grow facilities (sellers)
- Retail stores, dispensaries (buyers)
- Each inventory item is tied to a facility

---

## Related Resources

- **Scenarios:** `scenarios/inventory-workflow.md` - Inventory management workflows
- **Patterns:** `patterns/company-scoping.md` - Seller vs buyer inventory
- **Schema:** `schemas/openapi-inventory.json`

---

## Quick Reference

```php
// Get inventory
$api->get('/inventory-items/', ['product' => $id, 'quantity__gt' => 0]);

// Update quantity
$api->patch("/inventory-items/{$id}/", ['quantity' => 150]);

// Get enriched (BudTags helper)
$api->get_inventory_items_enriched($orgId);

// Retailer inventory
$api->get('/retailer-inventory/', ['facility' => $storeId]);
```
