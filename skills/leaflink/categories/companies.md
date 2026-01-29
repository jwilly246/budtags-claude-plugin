# Companies & Organization - LeafLink API Category

Complete reference for company and organizational endpoints - 10 total operations.

---

## Collection Reference

**OpenAPI Schema:** `schemas/openapi-companies.json`
**Total Endpoints:** 10
**Company Compatibility:** All company types

---

## Endpoint Overview

### Companies

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/companies/` | List companies |
| GET | `/companies/{id}/` | Get company details |
| GET | `/companies/me/` | Get authenticated company |

### Company Staff

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/company-staff/` | List staff members |
| GET | `/company-staff/{id}/` | Get staff details |

### Brands

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/brands/` | List brands |
| GET | `/brands/{id}/` | Get brand details |

### Licenses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/licenses/` | List licenses |
| GET | `/licenses/{id}/` | Get license details |

### License Types

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/license-types/` | List license types |
| GET | `/license-types/{id}/` | Get license type |

---

## Common Use Cases

### 1. Get Authenticated Company

```php
// Get company associated with current API key
$response = $api->get('/companies/me/');
$company = $response->json();

// Response includes:
// - id, name, company_type (seller/buyer)
// - address, city, state, zip
// - licenses
// - settings and preferences
```

### 2. Get Company by ID

```php
$company = $api->get_company_by_id($companyId);
```

### 3. List Brands

```php
// Get all brands for a company
$brands = $api->get_brands($companyId);

// Brands are seller-specific product groupings
// Examples: "House Brand", "Premium Line", etc.
```

### 4. Get Company Licenses

```php
$response = $api->get('/licenses/', [
    'company' => $companyId,
    'active' => 'true'
]);

$licenses = $response->json('results');

// Each license includes:
// - license_number
// - license_type (retail, cultivation, manufacturing, etc.)
// - state, expiration_date
// - status (active, expired, pending)
```

### 5. Get Staff Members

```php
$response = $api->get('/company-staff/', [
    'company' => $companyId
]);

$staff = $response->json('results');
```

---

## Available Filters

### Company Filters
- `company_type` - 'seller' or 'buyer'
- `state` - State abbreviation
- `name__icontains` - Company name search

### Brand Filters
- `company` - Company ID
- `name__icontains` - Brand name search

### License Filters
- `company` - Company ID
- `license_type` - License type ID
- `state` - State abbreviation
- `active` - Active status (true/false)
- `expiration_date__gte`, `expiration_date__lte` - Expiration range

### Staff Filters
- `company` - Company ID
- `active` - Active status

---

## Important Notes

### Company Types

**Seller (Brand/Manufacturer)**:
- `company_type: "seller"`
- Has products, brands
- Receives orders from buyers

**Buyer (Retailer/Dispensary)**:
- `company_type: "buyer"`
- Places orders to sellers
- Has retail locations/facilities

### Checking Company Context

```php
// Always check company type to determine available features
$company = $api->get('/companies/me/')->json();

if ($company['company_type'] === 'seller') {
    // Show seller features: product management, incoming orders
} else {
    // Show buyer features: order placement, retailer inventory
}
```

### Brands vs Companies

- **Companies** = Organizations in LeafLink (sellers and buyers)
- **Brands** = Product brands owned by seller companies
- One seller company can have multiple brands

### Licenses Are Required

Cannabis businesses must have valid licenses:
- License numbers must match state records
- Expired licenses prevent orders/transactions
- License types determine allowed operations

---

## Related Resources

- **Patterns:** `patterns/company-scoping.md` - Understanding company context
- **Schema:** `schemas/openapi-companies.json`

---

## Quick Reference

```php
// Get authenticated company
$api->get('/companies/me/');

// Get company by ID
$api->get_company_by_id($id);

// Get brands
$api->get_brands($companyId);

// Get licenses
$api->get('/licenses/', ['company' => $companyId, 'active' => 'true']);
```
