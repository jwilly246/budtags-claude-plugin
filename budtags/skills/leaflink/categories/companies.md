# Companies & Organization - LeafLink API Category

Reference for company, staff, brand and licence endpoints (all read-only).

Behaviour lines are tagged "verified 2026-10-16 (sandbox, <file>)"; raw files are in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/` (and `logs/requests.jsonl` one level up). `patterns/verified-behavior.md` wins on any conflict.

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
| GET | `/companies/` | "List companies the requesting user is a staff member of." (spec) |
| GET | `/companies/{id}/` | Get company details |

`/companies/me/` is NOT in the official spec. Do not depend on it. With an App key, `GET /companies/` returned exactly the key's own company (count 1) - verified 2026-10-16 (sandbox, logs/requests.jsonl first call).

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
| GET | `/licenses/` | "List all licenses for a user's companies." (spec) |
| GET | `/licenses/{id}/` | Get license details |

### License Types

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/license-types/` | List license types |
| GET | `/license-types/{id}/` | Get license type |

---

## Fields (spec)

- **Company** (`CompanyResponse`): `id`, `name`, `dba`, `slug`, `seller` (bool), `buyer` (bool), `address`, `city`, `state`, `zipcode`, `business_identifier`, `business_license_name`, `batch_enabled`, `sts_enabled` (Metrc integration), `has_accting` (QuickBooks), `apply_ancillary_tax`, `apply_arms_length_tax`, `hide_attached_packages`, `image`, `description`, `announcement`. **There is no `company_type` field** and no licences array.
- **Brand** (`BrandResponse`): `id`, `name`, `company`, `description`, `image`, `banner`.
- **License** (`ComplianceLicense`): `id`, `number`, `type`, `display_type`, `classification`. No expiration date or status.
- **Staff** (`CompanyStaffResponse`): `id`, `user`, `company`, `is_admin`, `is_active`, `is_poc`, `email`, `phone`, `display_name`, `username`, `identification_number`.

---

## Common Use Cases

### 1. Get the Key's Company

```php
// /companies/ lists the companies the key's user belongs to.
// An App key returned one row (its own company) - verified 2026-10-16 (sandbox, logs/requests.jsonl).
$company = $api->get('/companies/')->json('results.0');

// $company['seller'] / $company['buyer'] are booleans (spec)
```

### 2. Get Company by ID

```php
$company = $api->get_company_by_id($companyId);
```

### 3. List Brands

```php
// ?company= is in the spec but the sandbox sweep marked it IGNORED: same count (3) with or
// without it. With an App key the list is already the key's company's brands.
// verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)
$brands = $api->get('/brands/')->json('results');
```

### 4. Get Company Licenses

```php
// Filters in the spec: number, number__in, id, company_slug.
// ?company= is not in the spec and was IGNORED - verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)
$licenses = $api->get('/licenses/', ['number' => 'PR-000120'])->json('results');
```

### 5. Get Staff Members

```php
$staff = $api->get('/company-staff/', [
    'company' => $companyId,   // spec filter (not sandbox-tested)
    'is_active' => 'true',
])->json('results');
```

---

## Available Filters (spec)

- **Companies:** `limit`, `offset` only. There is no `company_type`, `state` or `name__icontains` filter.
- **Brands:** `company`, `company__in`, `company_slug` (`company` verified IGNORED)
- **Licenses:** `number`, `number__in`, `id`, `company_slug`
- **Staff:** `company`, `is_admin`, `is_active`, `company_slug`
- **Product lines** (`/product-lines/`): `?company=` verified IGNORED (r3_a_param_sweep.txt)

An ignored filter returns the whole list with a 200, so filter client-side on the `company` field of each row.

---

## Important Notes

### Seller vs Buyer

Use the company's `seller` and `buyer` booleans (spec: "Does the company sell / buy on the LeafLink marketplace?"). A company can be both.

```php
$company = $api->get('/companies/')->json('results.0');

if ($company['seller']) {
    // Seller features: product management, incoming orders
}
if ($company['buyer']) {
    // Buyer features: order placement
}
```

### Brands vs Companies

- **Companies** = organizations in LeafLink (sellers and buyers)
- **Brands** = product brands owned by seller companies
- One seller company can have several brands

---

## Related Resources

- **Patterns:** `patterns/company-scoping.md`, `patterns/verified-behavior.md`
- **Schema:** `schemas/openapi-companies.json`

---

## Quick Reference

```php
// The key's company
$api->get('/companies/');

// Company by ID
$api->get_company_by_id($id);

// Brands (filter by company client-side)
$api->get('/brands/');

// Licence by number
$api->get('/licenses/', ['number' => $number]);
```
