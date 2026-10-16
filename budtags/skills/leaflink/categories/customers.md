# Customers & CRM - LeafLink API Category

Reference for the seller's customer (CRM) records, statuses, tiers and contacts.

Write behaviour below was verified on the LeafLink sandbox on 2026-10-16. `patterns/verified-behavior.md` is the source of truth; raw files are in `~/budtags-audits/2026-10-15/leaflink_sandbox_tests/out/`.

---

## Collection Reference

**OpenAPI Schemas:**
- `schemas/openapi-customers-core.json` - Customer CRUD
- `schemas/openapi-crm.json` - Contacts and activity tracking

**Company Compatibility:** Seller companies only
**Notable:** `GET /customers/` lists 88 query parameters in the official spec. Several are silently IGNORED (see Filters below).

---

## Endpoint Overview

### Customers (Core)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers/` | List customers |
| POST | `/customers/` | Create customer (required: `owner`, `name`) |
| GET | `/customers/{id}/` | Get customer details |
| PATCH | `/customers/{id}/` | Update customer (partial) |
| DELETE | `/customers/{id}/` | "Archive a customer by ID." (spec) |

### Customer Statuses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customer-statuses/` | List statuses |
| POST | `/customer-statuses/` | Create status (required: `state`, `owner`) |
| GET | `/customer-statuses/{id}/` | Get status |
| PATCH | `/customer-statuses/{id}/` | Update status |
| DELETE | `/customer-statuses/{id}/` | Delete status |

Status fields: `id`, `state` (the label), `order`, `description`, `owner`, `is_stock`, `hex_color` (spec `CompanyCustomerStatus`).

### Customer Tiers (read-only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customer-tiers/` | List tiers |
| GET | `/customer-tiers/{id}/` | Get tier |

The spec has no POST/PATCH/DELETE for tiers. Tier fields: `id`, `rank`, `sort`, `created_on`, `modified`.

### Contacts and Activity Entries

See `categories/crm.md`.

---

## Customer Fields (spec `CustomerResponse`)

`id`, `owner`, `name`, `nickname`, `dba`, `license_number`, `old_license_number`, `license_inactive`, `license_type`, `business_identifier`, `ein` (read-only), `status`, `tier`, `managers` (sales rep ids), `price_schedule`, `service_zone`, `discount_percent`, `payment_term`, `payment_methods`, `available_payment_options`, `address`, `unit_number`, `city`, `county`, `state`, `zipcode`, `country`, `corporate_address`, `delivery_address`, `phone`, `phone_extension`, `email`, `website`, `archived`, `delinquent`, `partner` (linked LeafLink buyer company), `external_id`, `external_ids`, `ext_acct_id`, `created_on`, `modified`.

There is no `licenses` array, no `credit_limit`, and no `customer_status` / `customer_tier` field. Use `license_number`, `status`, `tier`.

---

## Common Use Cases

### 1. Get Customer by ID

```php
$customer = $api->get_customer_by_id($customerId);
```

### 2. Get Multiple Customers

```php
// id__in is honoured - verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)
$response = $api->get('/customers/', [
    'id__in' => '123,456,789',
    'fields_include' => 'id,name,license_number,status',
]);
```

### 3. Find a Customer by Licence

```php
// One call per licence. license_number is exact AND case-sensitive.
// license_number__in / __iexact / __icontains are IGNORED and return the whole list.
// verified 2026-10-16 (sandbox, r3_a_param_sweep.txt)
$response = $api->get('/customers/', ['license_number' => 'AU-R-000171']);
```

### 4. Update Customer

```php
// PATCH is partial: only the keys you send change.
// verified 2026-10-16 (sandbox, g_customers.txt step 1)
$response = $api->patch("/customers/{$customerId}/", [
    'email' => 'newemail@example.com',
    'status' => $statusId,
]);
```

### 5. Create Customer Status

```php
$response = $api->post('/customer-statuses/', [
    'state' => 'VIP Customer',
    'owner' => $companyId,
    'hex_color' => '#FFD700',
]);
```

---

## Customer PATCH Rules (verified 2026-10-16, sandbox)

- **Partial.** A nickname-only PATCH kept every other field (g_customers.txt step 1).
- **Top-level `address` / `city` / `zipcode` overwrite BOTH `corporate_address` and `delivery_address`** (g_customers.txt step 2).
- A nested `delivery_address` or `corporate_address` PATCH changes only that address; top-level `address` mirrors delivery (g_customers.txt steps 8, 9).
- **A partial nested object replaces the whole address.** `{"corporate_address": {"city": "Warren"}}` blanked address, state and zipcode (g_customers.txt step 10). Always send the full nested object.
- **`archived: false` un-archives**, `archived: true` archives; other edits work while archived (g_customers.txt steps 3-5). Never send `archived` unless you mean it.
- **`ein` is ignored**: 200, still reads `null` (g_customers.txt step 6). Spec (release 2.36.0): "DEPRECATED for writes", read-only and inherited from the linked LeafLink buyer company.
- Customer `phone` accepts a formatted value like `(313) 555-0101` (r2_t14_customer_create.txt). Contact phones do not (see `crm.md`).

---

## Filters

Names come from the official spec. "Verified" marks what the sandbox sweep proved (r3_a_param_sweep.txt). An ignored parameter returns the WHOLE list with a 200.

### Identity
- `id`, `id__in` (verified honoured)
- `name`, `name__in`, `name__startswith` - `name` is exact match only (verified: a partial name returns 0)
- `nickname`, `dba`, `business_license_name`, `business_identifier`, `email`, `phone`, `website`, `address` (each with `__in`, `__startswith`)
- `external_id`, `external_id__in`, `ext_acct_id`, `ext_acct_id__isnull`, `external_id_key` + `external_id_values`

### Licence
- `license_number` - exact, case-sensitive (verified; lowercase gives 0 rows)
- `license_number__in` - listed in the spec but IGNORED (verified)
- `license_number__iexact`, `license_number__icontains` - IGNORED (verified; not in the spec)
- `old_license_number`, `license_type` (id), `license_inactive`

### Relationship and status
- `status`, `tier`, `state`, `partner` (comma lists of ids per the spec)
- `owner`, `brand`, `price_schedule`, `service_zone`, `delinquent`
- `archived` / `is_archived`, `leaflink_source`

### Dates
- `created_on__gt/__gte/__lt/__lte`
- `modified__gt/__gte/__lt/__lte` (verified honoured)
- `next_contact_date__*`

### Response shape
- `fields_include`, `fields_exclude`
- `include_children` - `tags`, `service_zone`, `managers`, `contacts`, `license_type` (`contacts,managers` verified honoured)
- `ordering=id` / `-id` - not in the spec for `/customers/`, but honoured (verified)

There is no `created_date__*`, `payment_terms`, `credit_limit__*`, `name__icontains`, `city`, `zip_code`, `license_types__in` or `tax_exempt` filter.

---

## Important Notes

### Company Scoping

- Only **seller companies** manage customers
- A customer is the seller's CRM record of a buyer; `partner` links it to the buyer's LeafLink company
- Each customer is unique per seller company

### Contacts on a Customer

Read a customer's contacts with `GET /customers/?include_children=contacts` (verified honoured). Deleted contacts stay in `/contacts/` lists; see `crm.md`.

---

## Related Resources

- **Scenarios:** `scenarios/customer-workflow.md`
- **Patterns:** `patterns/verified-behavior.md`, `patterns/filtering.md`, `patterns/company-scoping.md`
- **Schemas:** `schemas/openapi-customers-core.json`, `schemas/openapi-crm.json`

---

## Quick Reference

```php
// Get customer
$customer = $api->get_customer_by_id($id);

// Find by licence (exact, case-sensitive, one per call)
$api->get('/customers/', ['license_number' => $licence]);

// Changed since
$api->get('/customers/', ['modified__gte' => '2026-10-16T15:00:00Z', 'ordering' => 'id']);

// Update (partial; send full nested address objects)
$api->patch("/customers/{$id}/", ['email' => 'new@example.com']);

// Create status
$api->post('/customer-statuses/', ['state' => 'VIP', 'owner' => $companyId]);
```
