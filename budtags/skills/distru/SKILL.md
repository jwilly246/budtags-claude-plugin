---
name: distru
description: Use this skill when working with Distru cannabis ERP API integration, managing sales orders, syncing products and inventory, importing assemblies/manufacturing data, or handling companies/contacts from Distru.
agent: distru-specialist
version: 2.0.0
---

# Distru API Reference Skill

You are now equipped with comprehensive knowledge of the **Distru Public API v1** via **modular category files**, **scenario templates**, and **pattern guides**. This skill uses **progressive disclosure** to load only the information relevant to your task.

**Skill content last reconciled with Phase 0.5 audit findings: 2026-05-21.** Authoritative project-level reference is `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md` — if this skill disagrees with that document, the mapping doc wins.

---

## Critical conventions (read first)

These are **NON-OBVIOUS** facts derived from live API verification:

### URL slugs use KEBAB-CASE for compound names

Distru URLs use kebab-case for multi-word resource names. Field/model names within payloads use snake_case. **The two are different naming spaces.** Six endpoints were initially documented with snake_case URLs in this skill and turned out to all be wrong:

| Wrong (snake_case) | Right (kebab-case) |
|---|---|
| `/stock_adjustments` | `/adjustments` |
| `/test_results` | `/test-results` |
| `/payment_methods` | `/payment-methods` |
| `/product_pos_mappings` | `/product-pos-mappings` |
| `/custom_fields` | `/custom-fields` |
| `/file_attachments` | `/file-attachments` |

Single-word URLs have no separator: `/companies`, `/contacts`, `/locations`, `/products`, `/strains`, `/batches`, `/packages`, `/orders`, `/invoices`, `/purchases`, `/assemblies`, `/menus`, `/users`, `/inventory`.

### `next_page` is a FULL URL STRING, not an integer

```jsonc
{
  "data": [...],
  "next_page": "https://app.distru.com/public/v1/orders?page[number]=2&page[size]=100"
  // OR null when no more pages
  // OR the key may be ABSENT entirely (not null) on the last page
}
```

Terminal check: `while (! empty($body['next_page'])) { ... }` — works for both null and missing-key cases.

### `page[size]` is non-functional on most endpoints

Small endpoints (`/companies`, `/contacts`, `/locations`, `/products`, `/test-results`, `/adjustments`, `/strains`) ignore `page[size]` and return the entire dataset (or up to their page cap) in one response. Large endpoints (`/packages`, `/invoices`, `/purchases`, `/assemblies`, `/orders`, `/batches`) cap at their implicit page size regardless of what you request.

### Page sizes vary by endpoint (4 distinct caps)

| Cap | Endpoints |
|---|---|
| 500 | `/orders`, `/purchases`, `/menus` |
| 1,000 | `/contacts`, `/locations`, `/users` |
| 5,000 | `/products`, `/packages`, `/companies`, `/batches`, `/adjustments`, `/test-results` |
| 50,000 | `/strains` |

### Distru silently ignores unknown filter params

A typo in a filter name returns HTTP 200 with **unfiltered results** (not 400). Combined with the 5,000-record cap, this can mask bugs — your code thinks it's getting filtered data, but actually getting random records. Always sanity-check by comparing filtered vs unfiltered counts in test code.

### Datetime filters use COMMA-RANGE strings (NOT `_from`/`_to` pairs)

```
?updated_datetime=2024-01-01T00:00:00Z,2024-02-01T00:00:00Z   ← from,to
?updated_datetime=2024-01-01T00:00:00Z,                       ← from only
?updated_datetime=,2024-02-01T00:00:00Z                       ← to only
```

Applies to ALL datetime filters (`updated_datetime`, `inserted_datetime`, `completion_datetime`, `delivery_datetime`, `due_datetime`, `order_datetime`, `invoice_datetime`).

### Multi-value filters: inconsistent across endpoints

Some endpoints use bracket arrays (`status[]=A&status[]=B`); others use comma-strings (`menu_id=uuid1,uuid2`). No universal rule — see per-endpoint category files.

### Tenant-customizable "enums"

Several fields look like fixed enums in docs but are actually tenant-defined: `Company.relationship_type`, `Adjustment.reason`, `Company.category`, `Product.category`. Different tenants have different values. Don't hard-code matchers against the documented enum list.

### Detail GETs (`/{id}`) are almost universally unavailable

Only `/orders/{id}` and `/invoices/{id}` work. Every other `GET /{resource}/{id}` returns 404. Importers walk lists.

---

## Your Capabilities

When the user asks about Distru integration, you can:

1. **Find Endpoints**: Search ~22 documented endpoints across 7 domains
2. **Provide Details**: Read from category files for exact request/response formats
3. **Explain Patterns**: Reference pattern files for Bearer JWT auth, kebab-case URLs, comma-range filters, etc.
4. **Generate Code**: Help implement Distru API calls in Laravel/PHP following Budtags integration patterns
5. **Route by Domain**: Recommend endpoints based on domain context
6. **Debug Issues**: Help troubleshoot common API integration problems (slug errors, silent-ignore filters, casing inconsistencies)
7. **Build Workflows**: Guide through complete multi-step Distru workflows

---

## Available Resources

8 category files, 5 scenario templates, 7 pattern files, 9 OpenAPI schema files, 2 coverage audits:

> **UPSTREAM DRIFT WARNING (2026-09-01):** Distru shipped a major API expansion
> June–Sept 2026 (39 audited paths → 113 live). The per-category docs and
> per-category schema stubs below were audited 2026-05 and do NOT cover the new
> surface. Consult `UPSTREAM-CHANGELOG.md` (verbatim upstream changelog) and
> `schemas/openapi-full-2026-09-01.json` (complete live spec) for anything
> recent. Known stale claims: purchases CAN now be created at any status and
> matched to Metrc transfers; ALL POSTs are now sparse (see the 2026-09-01
> addendum in `patterns/write-safety.md`); `inserted_at` was renamed
> `inserted_datetime` on /adjustments, /returns, /product-pos-mappings
> (2026-08-03); GET `/packages/{id}` and POST `/locations` were removed.

### Category Files (one per API domain)

- `categories/sales-orders.md` — Orders and Invoices (write-only payments)
- `categories/purchase-orders.md` — Purchases (cannot edit past Pending; non-sparse updates)
- `categories/crm.md` — Companies, Contacts, Locations
- `categories/products.md` — Products, TestResults (lab data), POS mappings
- `categories/inventory.md` — Batches, Packages, Adjustments, Inventory snapshot endpoint
- `categories/manufacturing.md` — Assemblies (3-level nesting; scalar creation_source filter)
- `categories/system.md` — Locations, Users, Menus, PaymentMethods, Strains, CustomFields, FileAttachments
- `categories/webhooks.md` — Webhook wire contract (payload shape, nested-entity triggers, HMAC signing, ordering/retries; captured 2026-09-01; NOT in the OpenAPI spec)

### Pattern Files

- `patterns/authentication.md` — Bearer JWT
- `patterns/pagination.md` — URL-string `next_page`, page-size variance, terminal detection
- `patterns/filtering.md` — kebab-case URLs, comma-range datetimes, bracket vs comma-string arrays, silent-ignore-unknown
- `patterns/error-handling.md` — HTTP status semantics (400 vs 422), opaque error bodies
- `patterns/date-formats.md` — ISO 8601
- `patterns/write-safety.md` — UPSERT, non-sparse updates, can't-edit-past-Pending
- `patterns/eventual-consistency.md` — ~1s lag on Strains, Assemblies, Products, Test Results

### Scenario Templates

- `scenarios/product-import-workflow.md`
- `scenarios/order-import-workflow.md`
- `scenarios/customer-import-workflow.md`
- `scenarios/order-writeback-workflow.md`
- `scenarios/assembly-import-workflow.md`

### Coverage Audits (BudTags integration-coverage, NOT wire-contract)

These are **BudTags-app-specific** docs: which fields *our* importers persist to native primitives, and where *our* gaps are — distinct from the API-contract category/schema docs that describe what Distru sends on the wire.

- `coverage/field-coverage-audit.md` — Per-endpoint field-coverage matrix (5-state mapped flag M/P/R/D/U, retention legend, gap/risk analysis, live-probe findings, file:line evidence) across all 18 read endpoints
- `coverage/cross-importer-audit.md` — Code-verified Distru vs LeafLink vs Canix order-importer comparison (11-concern matrix + gap findings A–H)

### Full Documentation

- `schemas/` — 8 curated per-category OpenAPI stubs (May 2026 audit) + `openapi-full-2026-09-01.json`, the complete live spec (113 paths, authoritative for anything the stubs lack)
- `UPSTREAM-CHANGELOG.md` — Distru's own API changelog, verbatim (2024-10 → 2026-09-01)
- `ENTITY_TYPES.md` — TypeScript type reference

---

## Domain Routing

### Sales Domain

**Keywords**: order, sales order, invoice, line item, charge, payment, shipping, customer order
**Load**: `categories/sales-orders.md`
**Scenarios**: `scenarios/order-import-workflow.md`, `scenarios/order-writeback-workflow.md`

**Key endpoints**:
- `GET /public/v1/orders` — List orders. Page size 500. Status enum: 7 values (PENDING/PROCESSING/READY_TO_SHIP/DELIVERING/DELIVERED/COMPLETED/**CANCELED**). Note CANCELED with single L; CANCELLED returns 400.
- `GET /public/v1/orders/{id}` — Detail (eventually consistent ~1s)
- `POST /public/v1/orders` — UPSERT. Non-sparse updates. `blaze_payment_type` required for Blaze retailers.
- `GET /public/v1/invoices` — Page size 500. Status: Title Case INPUT (`Not Paid`, `Fully Paid`, etc.); response returns UPPERCASE_UNDERSCORE (`NOT_PAID`, `FULLY_PAID`).
- `GET /public/v1/invoices/{id}` — Detail
- `POST /public/v1/invoices` — UPSERT. `order_id` required (not in formal docs table but required in practice).
- `POST /public/v1/invoices/{id}/payments` — Insert payment. **WRITE-ONLY** — `payments[]` is NOT in GET responses. QB account type must be "Bank" or "Other Current Asset".

### Purchasing Domain

**Keywords**: purchase, purchase order, PO, vendor order, procurement, receive
**Load**: `categories/purchase-orders.md`

**Key endpoints**:
- `GET /public/v1/purchases` — Page size 500. Status filter uses Title Case INPUT (`Completed`, `Pending`, `Partially Received`, etc.); response returns UPPERCASE. CANNOT update PO past Pending status. Non-sparse updates.
- `POST /public/v1/purchases` — Create/update PO
- `POST /public/v1/purchases/{id}/payments` — Insert payment (WRITE-ONLY; QB account type "Bank" or "Credit Card")

### CRM Domain

**Keywords**: company, contact, customer, vendor, relationship, license, category, email, phone
**Load**: `categories/crm.md`
**Scenario**: `scenarios/customer-import-workflow.md`

**Key endpoints**:
- `GET /public/v1/companies` — Page size 5,000. **`relationship_type` is TENANT-CUSTOMIZABLE**, NOT the documented CUSTOMER/VENDOR enum. Examples observed: `Current Customer`, `Current Supplier`, `Brand`, `Potential Customer`. NO `relationship_type` filter exists. Only filters: `inserted_datetime`, `updated_datetime`, `deleted` (tri-state), `page`.
- `POST /public/v1/companies` — UPSERT
- `GET /public/v1/contacts` — Page size 1,000. Minimal filters (datetimes + deleted). `full_name` is server-derived from first+last.
- `POST /public/v1/contacts` — UPSERT
- `GET /public/v1/locations` — Page size 1,000. Belongs to companies RBAC group. `address` is FLAT STRING (not nested object).

### Products Domain

**Keywords**: product, SKU, brand, category, strain, POS mapping, Blaze, Dutchie, Treez, test result, COA, cannabinoid, terpene, pesticide
**Load**: `categories/products.md`
**Scenario**: `scenarios/product-import-workflow.md`

**Key endpoints**:
- `GET /public/v1/products` — Page size 5,000. Filters: `product_name` (substring), `menu_id` (COMMA-SEPARATED string, NOT bracket array), `menu_name`, `inserted_datetime`, `updated_datetime`, `deleted` (tri-state), `ids[]`. Field name `vendor` in response (Distru docs say `company`). `product_group` field exists (~35% populated). Brand response has `{id, name, updated_datetime}` (3 fields), NOT just `name`.
- `POST /public/v1/products` — UPSERT. WRITE side has read/write inversions: `is_active`↔`is_inactive`, `product_group`↔`group_id`.
- `GET /public/v1/test-results` — **HYPHEN slug!** Page size 5,000. 19 fields with `additional_test_results` open object map (~100 keys typical per record from 300+ field catalog).
- `POST /public/v1/test-results` — Permission: `products_permissions_edit`
- `GET /public/v1/product-pos-mappings` — **HYPHEN slug!** POLYMORPHIC response by `pos_type`. `id` is INTEGER (only endpoint!). Per-POS filter params (`blaze_retailer_id`, etc.).
- `POST /public/v1/product-pos-mappings` — Returns 201 for create, 200 for update (unique status distinction).
- `DELETE /public/v1/product-pos-mappings/{id}` — **The ONLY DELETE in the entire API.**

### Inventory Domain

**Keywords**: batch, package, stock, adjustment, inventory, lot, cost, COGS
**Load**: `categories/inventory.md`

**Key endpoints**:
- `GET /public/v1/batches` — Page size 5,000. **`include_costs=true` required** for cost fields (gated, NOT in formal docs Parameters table). Filters: `batch_ids[]`, `product_id` (SINGULAR scalar, NOT product_ids[]), `batch_number`, datetimes, `deleted`.
- `GET /public/v1/packages` — Page size 5,000. `include_costs=true` required. Filters: `ids[]`, `product_ids[]` (PLURAL), `location_ids[]`, **`statuses[]` (PLURAL!)** — different from /orders `status[]`. Embedded `primary_test_result` provides cannabinoid summary.
- `GET /public/v1/inventory` — **`grouping[]` required** (PHP bracket array). Values: `PRODUCT` (required in every call), `LOCATION`, `BATCH_NUMBER`. Field `cost_default_per_unit` (word order reversed vs other endpoints).
- `GET /public/v1/adjustments` — **NOT `/stock_adjustments`** (that 404s). Page size 5,000. **ONLY 2 filters**: `inserted_datetime`, `completion_datetime`. No entity-targeted filters — mirror is load-bearing for queries.
- `POST /public/v1/adjustments` — Strict validation: exactly ONE of batch_id/package_id/product_id; `compliance_quantity` required for package adjustments; `waste` reason requires negative quantity.

### Manufacturing Domain

**Keywords**: assembly, manufacturing run, processing, batch run, split package, lab testing, conversion
**Load**: `categories/manufacturing.md`
**Pattern**: `patterns/eventual-consistency.md`
**Scenario**: `scenarios/assembly-import-workflow.md`

**Key endpoints**:
- `GET /public/v1/assemblies` — Page size 500. 3-level nesting: `outputs[].ingredients[]` (inputs) + `outputs[].additional_costs[]`. Filters: `completion_datetime` (NOT updated_datetime!), `creation_source` (SCALAR, not array), `license_number`. 4 creation_source values: MANUALLY_CREATED, SPLIT_PACKAGE (often 75%+ of records), SALES_ORDER, LAB_TESTING. 3 compliance_type: METRC, BIOTRACK, NONE.

### System Domain (reference data)

**Keywords**: location, warehouse, facility, custom field, user, role, payment method, POS mapping, strain, menu, file attachment
**Load**: `categories/system.md`

**Key endpoints**:
- `GET /public/v1/strains` — Page size **50,000** (largest in API). Permission: `settings_permissions_strains`. Fields: id, name, strain_type. NO `deleted` filter (strains not soft-deletable).
- `GET /public/v1/users` — Page size 1,000. Permission: `settings_permissions_manage_team`. Role is `{id, name}` object.
- `GET /public/v1/menus` — Page size 500. Permission: `products_permissions_view`. Filters: `active`, `visibility` (PUBLIC/PRIVATE/PASSCODE_PROTECTED). No datetime filters!
- `GET /public/v1/payment-methods` — **HYPHEN slug!** Permission: `settings_permissions_payment_methods`. Only filter: `deleted` tri-state.
- `POST /public/v1/custom-fields` — **HYPHEN slug!** POST-ONLY, no GET. Permission: `settings_permissions_custom_fields`. `id` is INTEGER. Field types: text, date, dropdown, checkbox.
- `POST /public/v1/file-attachments` — **HYPHEN slug!** POST-ONLY. Multipart/form-data. 15 mutually-exclusive parent reference fields (exactly one required). HTTP 422 on quota exceeded.

---

## RBAC Permissions Reference

Full Phase B import requires **8 distinct permission grants**:

| Permission | Endpoints |
|---|---|
| `orders_permissions_view` | /orders, /orders/{id} |
| `purchases_permissions_view` | /purchases |
| `invoices_permissions_view` | /invoices, /invoices/{id} |
| `products_permissions_view` | /products, /batches, /packages, /adjustments, /test-results, /menus, /product-pos-mappings |
| `companies_permissions_view` | /companies, /contacts, /locations |
| `assemblies_permissions_view` | /assemblies |
| `settings_permissions_strains` | /strains |
| `settings_permissions_manage_team` | /users |
| `settings_permissions_payment_methods` | /payment-methods |
| `settings_permissions_custom_fields` | POST /custom-fields |

---

## Progressive Loading Process

**IMPORTANT:** Only load files relevant to the user's question. DO NOT load all categories.

### Step 1: Context Gathering

Determine from the user's question:
- What Distru API domain is this about?
- Is this a read-only query or a write operation (POST/PUT/DELETE)?
- Is the resource subject to eventual consistency (Strains, Assemblies, Products, Test Results)?
- Is this a new implementation, debugging, or workflow question?

### Step 2: Load Relevant Resources

For task-based questions: load `scenarios/` + relevant `categories/` + `patterns/pagination.md` + `patterns/filtering.md`.

For endpoint-specific questions: load the relevant `categories/` file.

For write operation questions: also load `patterns/write-safety.md` (UPSERT, non-sparse updates).

### Step 3: Provide Answer

Always note:
- **Slug**: use kebab-case for compound names (test-results, payment-methods, etc.)
- **Filter conventions** specific to that endpoint
- **Write-safety**: UPSERT semantics, no idempotency keys
- **Eventual consistency** when applicable

---

## Quick Reference: Critical Patterns

### Authentication

```
Header: Authorization: Bearer {JWT}
Base URL: https://app.distru.com/public/v1
Generate key at: Distru UI → Settings → Integrations → Distru API
Prerequisite: Distru account rep must enable API access on the account
```

### Pagination

```
page[number] — 1-based page index
page[size]   — Usually IGNORED (small endpoints return everything; large ones cap at their implicit limit)

Response envelope:
  { "data": [...], "next_page": "<full URL string>" | null }
  (next_page key may also be absent on final page)

Stop condition: empty($body['next_page'])
```

### Datetime filters (comma-range)

```
?updated_datetime=<from>,<to>
?updated_datetime=<from>,         (open-ended end)
?updated_datetime=,<to>           (open-ended start)
```

### Write Operations

```
POST = create OR update (UPSERT — same payload shape)
PUT  = only used for invoice/purchase payment insertion: PUT /invoices/{id}/payments
DELETE = ONLY on /product-pos-mappings/{id} (the sole DELETE endpoint)
No idempotency keys — capture response ids; reconcile on retry
Non-sparse updates on /orders, /purchases, /invoices: omitted items/charges get DELETED
```

### Common Pitfalls

```
Using snake_case URLs (e.g., /stock_adjustments) — must be kebab-case (/adjustments)
Treating Distru auth like Canix (X-API-KEY) — it is Bearer JWT
Expecting `next_page` to be an integer — it is a full URL string when present
Looking for a count or total_pages field — only next_page exists
Expecting WHERE-string filters — use per-endpoint query-string params
Expecting `_from`/`_to` paired datetime filters — use comma-range strings
Retrying writes without an id-reconciliation step — no idempotency
Reading immediately after creating an Assembly or Strain — ~1s lag
Trusting `page[size]` to limit response volume — silently ignored on most endpoints
Calling /orders unfiltered on high-volume orgs — times out at 500 after ~20s; use updated_datetime
Treating `quantity` / `total_cost` as floats — they arrive as signed string decimals
Treating `unit_type` as a string — it is a `{id, name}` object
Filter typo (e.g., `status[]=active` on /packages where it's `statuses[]`) — silently ignored, returns unfiltered
CANCELLED (double L) — Distru uses CANCELED (single L); double L returns 400
Trying to filter /companies by `relationship_type` — no such filter; tenant-customizable enum anyway
Trying to filter /adjustments by package_id — no such filter; mirror table is load-bearing
Trying to filter /test-results by package_id — no such filter; mirror is load-bearing
Hard-coding the relationship_type/reason/category enum — they're TENANT-CUSTOMIZABLE
Assuming /custom-fields, /file-attachments, /test_results/{id}, etc. have GETs — many don't
```

---

## Your Mission

Help users successfully integrate with the Distru API by:

1. **Loading ONLY relevant resources** (progressive disclosure)
2. **Routing by domain** (7 domains)
3. **Surfacing the per-endpoint quirks** documented in this skill
4. **Calling out UPSERT and non-sparse-update semantics**
5. **Explaining `next_page` URL pagination**
6. **Warning about eventual consistency** (Strains/Assemblies + Products/TestResults per Phase 0.5)
7. **Verifying slug naming** (always kebab-case for compound names)
8. **Generating correct Laravel/PHP code** following Budtags' DistruApi/CanixApi mirror patterns
9. **Pointing to `DISTRU-INTEGRATION-MAPPING.md`** as the authoritative source when this skill might be stale

**You have comprehensive Phase 0.5-verified knowledge of all documented Distru Public API v1 operations. Use progressive disclosure to provide fast, relevant answers.**
