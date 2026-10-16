# Promotions - LeafLink API Category

Reference for promotional code endpoints - 5 operations. Checked against the official spec (`~/budtags-audits/2026-10-15/leaflink_docs_gap_audit/official_openapi.json`); not exercised in the 2026-10-16 sandbox tests.

---

## Collection Reference

**OpenAPI Schema:** `schemas/openapi-promotions-reports.json`
**Total Endpoints:** 5
**Company Compatibility:** Seller companies (codes belong to a brand)

---

## Endpoint Overview

### Promo Codes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/promocodes/` | List promo codes for brands in the company's scope |
| POST | `/promocodes/` | Create promo code (unique per brand + code) |
| GET | `/promocodes/{id}/` | Get promo code details |
| PATCH | `/promocodes/{id}/` | Update a code's `start_date` and `end_date` |
| DELETE | `/promocodes/{id}/` | Delete promo code (204) |

---

## PromoCode Fields (spec)

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | Read-only |
| `brand` | integer | **Required** |
| `code` | string | **Required**; unique per brand |
| `discount_type` | string | Enum `%` only |
| `discount_amount` | string | "Percent discount for Order" |
| `start_date` | string | **Required** |
| `end_date` | string | **Required** |

There is no `discount_value`, `minimum_order`, `max_uses`, `active` or `company` field, and no fixed-amount promo code.

---

## Common Use Cases

### 1. Create Promo Code

```php
$response = $api->post('/promocodes/', [
    'brand' => $brandId,
    'code' => 'SPRING2025',
    'discount_type' => '%',
    'discount_amount' => '10',
    'start_date' => '2025-03-01',
    'end_date' => '2025-03-31',
]);
```

The spec does not say whether `discount_amount` is 0-100 or a 0-1 fraction (order-level `%` discounts are 0-1 fractions, verified 2026-10-16 (sandbox, w_d_discount_tax.txt)). Read one existing code back before writing new ones.

### 2. List Promo Codes for a Brand

```php
$response = $api->get('/promocodes/', [
    'brand' => $brandId,
    'limit' => 50,
]);

$promoCodes = $response->json('results');
```

### 3. Extend a Promo Code

```php
// The spec documents PATCH for the date fields only
$response = $api->patch("/promocodes/{$promoId}/", [
    'end_date' => '2025-04-30',
]);
```

### 4. Find a Code

```php
$response = $api->get('/promocodes/', [
    'code' => 'SPRING2025',
]);
```

### 5. Remove a Code

```php
$response = $api->delete("/promocodes/{$promoId}/");   // 204
```

To stop a code early without deleting it, PATCH its `end_date` to today.

---

## Available Filters (spec)

- `brand` - Brand id
- `code` - Code
- `company_slug` - Company slug
- `limit`, `offset` - Paging

No `__icontains`, `active`, date-range or value-range filters exist.

---

## Related Resources

- **Schema:** `schemas/openapi-promotions-reports.json`
- **Orders:** `categories/orders.md` - order-level `discount` / `discount_type`

---

## Quick Reference

```php
// Create promo
$api->post('/promocodes/', ['brand' => $brandId, 'code' => 'SAVE10', 'discount_type' => '%', 'discount_amount' => '10', 'start_date' => '2025-03-01', 'end_date' => '2025-03-31']);

// List for a brand
$api->get('/promocodes/', ['brand' => $brandId]);

// Extend
$api->patch("/promocodes/{$id}/", ['end_date' => '2025-04-30']);

// Delete
$api->delete("/promocodes/{$id}/");
```
