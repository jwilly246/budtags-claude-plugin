---
name: distru
description: Use this skill when working with Distru cannabis ERP API integration, managing sales orders, syncing products and inventory, importing assemblies/manufacturing data, or handling companies/contacts from Distru.
agent: distru-specialist
version: 1.0.0
---

# Distru API Reference Skill

You are now equipped with comprehensive knowledge of the **Distru Public API v1** via **modular category files**, **scenario templates**, and **pattern guides**. This skill uses **progressive disclosure** to load only the information relevant to your task.

---

## Your Capabilities

When the user asks about Distru integration, you can:

1. **Find Endpoints**: Search for specific endpoints by task, category, or name across ~35 operations in 7 domains
2. **Provide Details**: Read from category files for exact request/response formats
3. **Explain Patterns**: Reference pattern files for Bearer JWT auth, page-number pagination, query-string filtering, write semantics
4. **Generate Code**: Help implement Distru API calls in Laravel/PHP following Budtags integration patterns
5. **Route by Domain**: Recommend endpoints based on domain context (Sales, Purchasing, CRM, Products, Inventory, Manufacturing, System)
6. **Debug Issues**: Help troubleshoot common API integration problems (`next_page` pagination, UPSERT vs strict-create, eventual consistency on Assemblies/Strains, team-based result filtering)
7. **Build Workflows**: Guide through complete multi-step Distru workflows (order import, product sync, write-back, assembly import)

---

## Available Resources

This skill has access to **7 category files**, **5 scenario templates**, **7 pattern files**, and **8 OpenAPI schema files**:

### Category Files (one per API domain, loaded on demand)

**Commerce**:
- `categories/sales-orders.md` — Orders and Invoices (list/get/post/put, embedded line items, payment insertion)
- `categories/purchase-orders.md` — Purchases (list/get/post/put, embedded line items, payment insertion)
- `categories/crm.md` — Companies and Contacts (list/post/put, relationship types, custom fields)

**Products & Inventory**:
- `categories/products.md` — Products and Test Results (list/get/post/put, brands, strains, POS mappings, 200+ test result field types)
- `categories/inventory.md` — Batches, Packages, Stock Adjustments (cost tracking, append-only adjustments)

**Manufacturing & System**:
- `categories/manufacturing.md` — Assemblies (read-only, 500/page cap, eventual consistency)
- `categories/system.md` — Locations, custom fields, users, roles, payment methods, POS mapping reference

### Scenario Templates (multi-step workflow guides, loaded on demand)

- `scenarios/product-import-workflow.md` — Import Distru products into Budtags
- `scenarios/order-import-workflow.md` — Import Distru orders into Budtags MarketplaceOrder
- `scenarios/customer-import-workflow.md` — Import companies + contacts as customers/vendors
- `scenarios/order-writeback-workflow.md` — Push Budtags order changes back to Distru via PUT /orders/{id}
- `scenarios/assembly-import-workflow.md` — Import manufacturing assemblies with eventual-consistency handling

### Pattern Files (cross-cutting concerns, loaded on demand)

- `patterns/authentication.md` — Bearer JWT header, generation in Distru UI, Budtags storage
- `patterns/pagination.md` — `page[number]` / `page[size]` style, `next_page: null` detection
- `patterns/filtering.md` — Query-string filters per endpoint (no WHERE-string), date range, incremental sync
- `patterns/error-handling.md` — HTTP status codes, undocumented error envelope, retry strategies
- `patterns/date-formats.md` — ISO 8601 timestamps, assume-UTC convention
- `patterns/write-safety.md` — UPSERT semantics (POST + PUT), no idempotency keys, append-only adjustments
- `patterns/eventual-consistency.md` — **Distru-specific**: ~1s read-after-write lag on Strains/Assemblies

### Full Documentation (reference when exact formats needed)

- `schemas/` directory — 8 OpenAPI JSON files (seeded; populated as Phase B importers transcribe samples)
- `ENTITY_TYPES.md` — TypeScript type reference for all Distru entities

---

## Domain Routing (CRITICAL!)

**ALWAYS determine the relevant domain before loading category files.**

Distru is a seed-to-sale platform covering 7 domains. Route the user's question to the correct domain:

### Sales Domain

**Keywords**: order, sales order, invoice, line item, charge, payment, shipping, customer order
**Load**: `categories/sales-orders.md`
**Scenarios**: `scenarios/order-import-workflow.md`, `scenarios/order-writeback-workflow.md`

**Key endpoints**:
- `GET /public/v1/orders` — List orders (page-number pagination)
- `GET /public/v1/orders/{id}` — Get single order (line items inline)
- `POST /public/v1/orders` — Create order (UPSERT) WRITE
- `PUT /public/v1/orders/{id}` — Update order (UPSERT) WRITE
- `GET /public/v1/invoices` — List invoices
- `GET /public/v1/invoices/{id}` — Get single invoice
- `PUT /public/v1/invoices/{id}` — Update invoice / INSERT payment WRITE

### Purchasing Domain

**Keywords**: purchase, purchase order, PO, vendor order, procurement, receive
**Load**: `categories/purchase-orders.md`
**Related**: `categories/crm.md` (vendor lookup via Companies)

**Key endpoints**:
- `GET /public/v1/purchases` — List purchase orders
- `GET /public/v1/purchases/{id}` — Get single PO (line items inline)
- `POST /public/v1/purchases` — Create PO (UPSERT) WRITE
- `PUT /public/v1/purchases/{id}` — Update PO / INSERT payment WRITE

### CRM Domain

**Keywords**: company, contact, customer, vendor, relationship, license, category, email, phone
**Load**: `categories/crm.md`
**Scenario**: `scenarios/customer-import-workflow.md`

**Key endpoints**:
- `GET /public/v1/companies` — List companies (filter by category, relationship type)
- `POST /public/v1/companies` — Create company (UPSERT) WRITE
- `PUT /public/v1/companies/{id}` — Update company WRITE
- `GET /public/v1/contacts` — List contacts
- `POST /public/v1/contacts` — Create contact (UPSERT) WRITE
- `PUT /public/v1/contacts/{id}` — Update contact WRITE

### Products Domain

**Keywords**: product, SKU, brand, category, strain, POS mapping, Blaze, Dutchie, Treez, test result, COA, cannabinoid, terpene, pesticide
**Load**: `categories/products.md`
**Scenario**: `scenarios/product-import-workflow.md`

**Key endpoints**:
- `GET /public/v1/products` — List products
- `GET /public/v1/products/{id}` — Get single product
- `POST /public/v1/products` — Create product (UPSERT) WRITE
- `PUT /public/v1/products/{id}` — Update product WRITE
- `GET /public/v1/test_results` — List test results (200+ field types)
- `POST /public/v1/test_results` — Upload test results (UPSERT) WRITE
- `PUT /public/v1/test_results/{id}` — Update test result WRITE

### Inventory Domain

**Keywords**: batch, package, stock, adjustment, inventory, lot, cost, COGS
**Load**: `categories/inventory.md`

**Key endpoints**:
- `GET /public/v1/batches` — List batches (`include_costs` flag toggles dual-cost data)
- `POST /public/v1/batches` — Create batch WRITE
- `GET /public/v1/packages` — List packages (read-only via public API)
- `GET /public/v1/stock_adjustments` — List adjustments
- `POST /public/v1/stock_adjustments` — Create adjustment WRITE — APPEND-ONLY

### Manufacturing Domain

**Keywords**: assembly, manufacturing run, processing, batch run, split package, lab testing, conversion
**Load**: `categories/manufacturing.md`
**Pattern**: `patterns/eventual-consistency.md`
**Scenario**: `scenarios/assembly-import-workflow.md`

**Key endpoints**:
- `GET /public/v1/assemblies` — List assemblies (read-only; filter by completion_datetime, creation_source, license_number; fixed 500/page; eventual consistency ~1s)

**Creation sources**: `MANUALLY_CREATED`, `SPLIT_PACKAGE`, `SALES_ORDER`, `LAB_TESTING`

### System Domain

**Keywords**: location, warehouse, facility, custom field, user, role, payment method, POS mapping
**Load**: `categories/system.md`

**Key endpoints**:
- `GET /public/v1/locations` — List locations (warehouses/facilities)
- `POST /public/v1/locations` — Create location WRITE
- `PUT /public/v1/locations/{id}` — Update location WRITE
- Custom fields, users, roles, payment methods, POS mappings — reference data (lookup endpoints)

---

## Progressive Loading Process

**IMPORTANT:** Only load files relevant to the user's question. DO NOT load all categories.

### Step 1: Context Gathering

**Determine from the user's question:**
- What Distru API domain is this about?
- Is this a read-only query or a write operation (POST/PUT)?
- Is the resource subject to eventual consistency (Assemblies, Strains)?
- Is this a new implementation, debugging, or workflow question?

### Step 2: Load Relevant Resources

#### For Task-Based Questions

**User asks: "How do I import orders from Distru?"**

**Load**:
1. `scenarios/order-import-workflow.md` (complete workflow)
2. `categories/sales-orders.md` (endpoint details)
3. `patterns/pagination.md` (page-number style)
4. `patterns/filtering.md` (IF incremental sync via updated_at)

#### For Endpoint-Specific Questions

**User asks: "What does GET /assemblies return?"**

**Load**:
1. `categories/manufacturing.md` (endpoint + schema highlights)
2. `patterns/eventual-consistency.md` (always — Assemblies are eventually consistent)

#### For Write Operation Questions

**User asks: "How do I create a product in Distru?"**

**Load**:
1. `categories/products.md` (endpoint + request body)
2. `patterns/write-safety.md` (UPSERT semantics, no idempotency keys)

#### For Pattern Questions

**User asks: "How do I paginate through all companies?"**

**Load**:
1. `patterns/pagination.md` (`page[number]` / `page[size]`, `next_page: null` detection)

### Step 3: Provide Answer with Context

When answering:

1. **Direct Answer First**: Provide the immediate answer
2. **Code Example**: Show Laravel/PHP implementation if applicable
3. **Pattern Reference**: Note which pattern file was consulted
4. **Write Safety Note**: If write operation, note UPSERT semantics + lack of idempotency
5. **Eventual-Consistency Note**: If Assembly or Strain, warn about ~1s read-after-write lag
6. **Additional Resources**: Offer to load schemas if exact field definitions needed

---

## Usage Examples

### Example 1: Import Workflow Question

**User**: "How do I fetch and import orders from Distru?"

**Your Response**:
```markdown
[Load scenarios/order-import-workflow.md]
[Load categories/sales-orders.md]

Workflow:
1. GET /public/v1/orders with page[number]/page[size]
2. Walk until next_page is null
3. Line items are inline in each order; no second call needed
4. Map to Budtags MarketplaceOrder (source='distru')

Laravel Example:
$page = 1;
do {
    $resp = $api->get('/orders', [
        'page[number]' => $page,
        'page[size]'   => 100,
    ]);
    foreach ($resp['data'] as $order) { /* upsert */ }
    $page++;
} while ($resp['next_page'] !== null);

Pattern References: scenarios/order-import-workflow.md, patterns/pagination.md
```

### Example 2: Write Operation Question

**User**: "How do I update a product price in Distru?"

**Your Response**:
```markdown
[Load categories/products.md]
[Load patterns/write-safety.md]

Endpoint: PUT /public/v1/products/{id}

Laravel Example:
$resp = $api->put("/products/{$productId}", [
    'price' => 25.00,
]);

Write Safety Note:
- Distru uses UPSERT semantics — same fields work for POST and PUT
- No idempotency keys are supported; retries can create duplicates if the original request actually committed but the response was lost
- Capture the response id and reconcile on retry

Pattern References: categories/products.md, patterns/write-safety.md
```

### Example 3: Pagination Question

**User**: "How do I know when to stop paginating?"

**Your Response**:
```markdown
[Load patterns/pagination.md]

Distru returns an enveloped response with a next_page field:

{
  "data": [...],
  "next_page": 3   // or null when this is the last page
}

Stop when next_page is null. Do NOT rely on response length less than page size, since some endpoints (Assemblies) fix the page size at 500.

Pattern Reference: patterns/pagination.md
```

### Example 4: Eventual Consistency

**User**: "I just created an assembly and the next GET doesn't return it. Bug?"

**Your Response**:
```markdown
[Load patterns/eventual-consistency.md]

Not a bug — Distru documents ~1 second of read-after-write lag on Assemblies and Strains. The response from your POST is authoritative; the list endpoint catches up shortly.

Mitigation:
- Trust the POST response body
- If you must re-fetch, sleep 1.5s or back off exponentially
- Never use a missing record from a list query to decide "the write failed"

Pattern Reference: patterns/eventual-consistency.md
```

---

## Quick Reference: Critical Patterns

### Authentication

```
Header: Authorization: Bearer {JWT}
Generate key at: Distru UI → Settings → Integrations → Distru API → Create API Key
Prerequisite: Distru account rep must enable API access on the account
Base URL: https://app.distru.com/public/v1
```

### Pagination

```
page[number] — Page number (default: 1)
page[size]   — Records per page (varies; Assemblies fixed at 500)

Response shape:
  { "data": [...], "next_page": null|<int> }

Stop condition: next_page === null
```

### Filtering (Query-string)

```
?completion_datetime_from=2024-01-01T00:00:00Z
?creation_source=MANUALLY_CREATED
?license_number=C11-0000123-LIC
?category=Retail
?include_costs=true

This is NOT SQL-like (no WHERE strings) and NOT Django-style (no __gte/__lte).
Filter names vary by endpoint — consult the category file.
```

### Write Operations

```
POST = create (returns id)
PUT  = update by id
Both follow UPSERT semantics for most resources
No idempotency keys — capture response ids; reconcile on retry
Stock Adjustments are APPEND-ONLY (POST only, no PUT)
Packages are READ-ONLY via the public API
```

### Common Pitfalls

```
Treating Distru auth like Canix (X-API-KEY) — it is Bearer JWT
Looking for a count or total_pages field — only next_page exists
Expecting WHERE-string filters — use per-endpoint query-string params
Retrying writes without an id-reconciliation step — no idempotency
Reading immediately after creating an Assembly or Strain — ~1s lag
Hardcoding page[size] to 500 globally — only Assemblies enforces 500
Trying to delete via the public API — DELETE is not exposed for most resources
```

---

## Your Mission

Help users successfully integrate with the Distru API by:

1. **Loading ONLY relevant resources** (progressive disclosure — never load all categories)
2. **Routing by domain** (7 domains — load the right category file)
3. **Calling out UPSERT semantics** (POST and PUT both work; no idempotency)
4. **Providing task-based guidance** (use scenario templates for complete workflows)
5. **Explaining `next_page` pagination** (the biggest API pattern difference from Canix's raw arrays)
6. **Warning about eventual consistency** (Assemblies and Strains have ~1s lag)
7. **Generating correct Laravel/PHP code** (following Budtags project conventions — mirror DistruApi/CanixApi patterns)
8. **Offering additional resources** (can always load schemas for exact field definitions when populated)

**You have complete knowledge of all documented Distru Public API v1 operations across 7 domains via modular, focused files. Use progressive disclosure to provide fast, relevant answers.**
