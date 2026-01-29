# Promotions - LeafLink API Category

Complete reference for promotional code management endpoints - 5 total operations.

---

## Collection Reference

**OpenAPI Schema:** `schemas/openapi-promotions-reports.json`
**Total Endpoints:** 5
**Company Compatibility:** Seller companies only

---

## Endpoint Overview

### Promo Codes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/promocodes/` | List promo codes |
| POST | `/promocodes/` | Create promo code |
| GET | `/promocodes/{id}/` | Get promo code details |
| PATCH | `/promocodes/{id}/` | Update promo code |
| DELETE | `/promocodes/{id}/` | Delete promo code |

---

## Common Use Cases

### 1. Create Promo Code

```php
$response = $api->post('/promocodes/', [
    'code' => 'SPRING2025',
    'discount_type' => 'percentage',  // or 'fixed_amount'
    'discount_value' => 10.00,  // 10% off or $10 off
    'start_date' => '2025-03-01',
    'end_date' => '2025-03-31',
    'minimum_order' => 100.00,  // Minimum order amount
    'max_uses' => 100,  // Max redemptions
    'active' => true,
    'company' => $companyId
]);
```

### 2. List Active Promo Codes

```php
$response = $api->get('/promocodes/', [
    'active' => 'true',
    'start_date__lte' => now()->toDateString(),
    'end_date__gte' => now()->toDateString(),
    'limit' => 50
]);

$promoCodes = $response->json('results');
```

### 3. Update Promo Code

```php
$response = $api->patch("/promocodes/{$promoId}/", [
    'discount_value' => 15.00,  // Increase discount
    'max_uses' => 200,  // Increase usage limit
    'end_date' => '2025-04-30'  // Extend expiration
]);
```

### 4. Deactivate Promo Code

```php
$response = $api->patch("/promocodes/{$promoId}/", [
    'active' => false
]);
```

### 5. Search Promo Codes

```php
$response = $api->get('/promocodes/', [
    'code__icontains' => 'spring',
    'discount_type' => 'percentage',
    'active' => 'true'
]);
```

---

## Available Filters

### Basic Filters
- `code__icontains` - Code search
- `active` - Active status
- `discount_type` - 'percentage' or 'fixed_amount'

### Date Filters
- `start_date__gte`, `start_date__lte` - Start date range
- `end_date__gte`, `end_date__lte` - End date range
- `created_date__gte`, `created_date__lte` - Creation date range

### Value Filters
- `discount_value__gte`, `discount_value__lte` - Discount amount range
- `minimum_order__gte`, `minimum_order__lte` - Minimum order range
- `max_uses__gte`, `max_uses__lte` - Usage limit range

---

## Discount Types

### Percentage Discount

```php
'discount_type' => 'percentage',
'discount_value' => 10.00  // 10% off
```

- Applied as percentage of order total
- Value should be between 0-100
- Examples: 5%, 10%, 25% off

### Fixed Amount Discount

```php
'discount_type' => 'fixed_amount',
'discount_value' => 50.00  // $50 off
```

- Applied as flat dollar amount
- Subtracted from order total
- Examples: $10 off, $50 off

---

## Important Notes

### Promo Code Rules

- **Unique codes**: Each code must be unique per company
- **Case-insensitive**: "SPRING2025" = "spring2025"
- **Expiration**: Automatically inactive after end_date
- **Usage limits**: max_uses caps total redemptions
- **Minimum order**: Optional requirement for code to apply

### Validation

Before accepting promo code:
1. Check `active` status
2. Verify current date is between start_date and end_date
3. Check usage count < max_uses
4. Verify order total >= minimum_order

### Company Scoping

- Only seller companies can create promo codes
- Codes apply to that seller's products only
- Buyers see and use codes during checkout

---

## Related Resources

- **Schema:** `schemas/openapi-promotions-reports.json`

---

## Quick Reference

```php
// Create promo
$api->post('/promocodes/', ['code' => 'SAVE10', 'discount_type' => 'percentage', 'discount_value' => 10]);

// List active
$api->get('/promocodes/', ['active' => 'true', 'end_date__gte' => now()->toDateString()]);

// Update
$api->patch("/promocodes/{$id}/", ['discount_value' => 15]);

// Deactivate
$api->patch("/promocodes/{$id}/", ['active' => false]);
```
