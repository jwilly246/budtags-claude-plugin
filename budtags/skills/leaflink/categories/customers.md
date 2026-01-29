# Customers & CRM - LeafLink API Category

Complete reference for customer relationship management endpoints - 22 total operations.

---

## Collection Reference

**OpenAPI Schemas:**
- `schemas/openapi-customers-core.json` - Customer CRUD
- `schemas/openapi-crm.json` - Contacts and activity tracking

**Total Endpoints:** 22
**Company Compatibility:** Seller companies only
**Notable:** `/customers/` endpoint has **87 filter parameters** - most complex filtering in LeafLink API!

---

## Endpoint Overview

### Customers (Core)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers/` | List customers (87 filters!) |
| POST | `/customers/` | Create customer |
| GET | `/customers/{id}/` | Get customer details |
| PATCH | `/customers/{id}/` | Update customer |
| DELETE | `/customers/{id}/` | Delete customer |

### Customer Statuses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customer-statuses/` | List statuses |
| POST | `/customer-statuses/` | Create status |
| GET | `/customer-statuses/{id}/` | Get status |
| PATCH | `/customer-statuses/{id}/` | Update status |
| DELETE | `/customer-statuses/{id}/` | Delete status |

### Customer Tiers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customer-tiers/` | List tiers |
| POST | `/customer-tiers/` | Create tier |
| GET | `/customer-tiers/{id}/` | Get tier |
| PATCH | `/customer-tiers/{id}/` | Update tier |
| DELETE | `/customer-tiers/{id}/` | Delete tier |

### Contacts (CRM)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/contacts/` | List contacts |
| POST | `/contacts/` | Create contact |
| GET | `/contacts/{id}/` | Get contact |
| PATCH | `/contacts/{id}/` | Update contact |
| DELETE | `/contacts/{id}/` | Delete contact |

### Activity Entries (CRM)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/activity-entries/` | List activities |
| GET | `/activity-entries/{id}/` | Get activity |

---

## Common Use Cases

### 1. Get Customer by ID

```php
$customer = $api->get_customer_by_id($customerId);

// Response includes:
// - id, name, email, phone
// - licenses (array of license info)
// - address, city, state, zip
// - status, tier
// - payment terms, credit limit
```

### 2. Get Multiple Customers with Filters

```php
$customers = $api->get_customers(
    ids: [123, 456, 789],
    fields: ['id', 'name', 'email', 'licenses', 'status']
);
```

### 3. Search Customers with Complex Filters

```php
// The /customers/ endpoint has 87 filter parameters!
$response = $api->get('/customers/', [
    'license_types__in' => 'retail,cultivation',  // Multiple license types
    'status' => 'active',                         // Only active
    'state' => 'CO',                              // Colorado only
    'city' => 'Denver',                           // In Denver
    'name__icontains' => 'green',                 // Name contains "green"
    'created_date__gte' => '2024-01-01',         // Created this year
    'tier' => 5,                                  // Specific tier
    'limit' => 100
]);
```

### 4. Update Customer

```php
$response = $api->patch("/customers/{$customerId}/", [
    'email' => 'newemail@example.com',
    'phone' => '555-0123',
    'status' => $statusId
]);
```

### 5. Create Customer Status

```php
$response = $api->post('/customer-statuses/', [
    'name' => 'VIP Customer',
    'company' => $companyId,
    'color' => '#FFD700'
]);
```

---

## Available Filters (87 Total!)

### Basic Information
- `name__icontains`, `name__startswith` - Name search
- `email__icontains` - Email search
- `phone__icontains` - Phone search
- `status` - Customer status ID
- `tier` - Customer tier ID

### Location Filters
- `city`, `state`, `zip_code`, `country`
- `address__icontains` - Address search

### License Filters
- `license_types__in` - Multiple license types
- `license_numbers__icontains` - License number search

### Relationship Filters
- `company` - Filter by company ID
- `sales_rep` - Filter by sales rep ID

### Business Filters
- `payment_terms` - Payment terms
- `credit_limit__gte`, `credit_limit__lte` - Credit limit range
- `tax_exempt` - Tax exempt status

### Date Filters
- `created_date__gte`, `created_date__lte` - Creation date range
- `modified__gte`, `modified__lte` - Last modified range
- `last_order_date__gte`, `last_order_date__lte` - Last order range

**...and 60+ more filters!** See OpenAPI schema for complete list.

---

## Important Notes

### Company Scoping

- Only **seller companies** can manage customers
- Customers represent buyer-seller relationships
- Each customer is unique per seller company

### Customer Statuses & Tiers

**Statuses** - Custom labels for customer lifecycle:
- Examples: "Active", "Inactive", "VIP", "Pending Approval"
- Fully customizable per company

**Tiers** - Customer segmentation:
- Examples: "Gold", "Silver", "Bronze"
- Can affect pricing, discounts, order minimums

### Licenses Are Critical

Customers (buyers/retailers) must have valid licenses to:
- Place orders
- Receive cannabis products
- Maintain compliance

Always verify `licenses` field when managing customers.

---

## Related Resources

- **Scenarios:** `scenarios/customer-workflow.md` - Customer relationship workflows
- **Patterns:** `patterns/filtering.md` - Mastering the 87 filter parameters
- **Patterns:** `patterns/company-scoping.md` - Seller-customer relationships
- **Schemas:** `schemas/openapi-customers-core.json`, `schemas/openapi-crm.json`

---

## Quick Reference

```php
// Get customer
$customer = $api->get_customer_by_id($id);

// Search customers
$api->get('/customers/', ['state' => 'CO', 'status' => 'active', 'name__icontains' => 'green']);

// Update customer
$api->patch("/customers/{$id}/", ['email' => 'new@example.com']);

// Create status
$api->post('/customer-statuses/', ['name' => 'VIP', 'company' => $companyId]);

// Create tier
$api->post('/customer-tiers/', ['name' => 'Gold', 'company' => $companyId]);
```
