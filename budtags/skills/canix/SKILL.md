---
name: canix
description: Use this skill when working with Canix cannabis ERP API integration, managing sales/purchase orders, syncing items/products, tracking inventory/packages, or handling cultivation and manufacturing data from Canix.
agent: canix-specialist
version: 1.0.0
---

# Canix API Reference Skill

You are now equipped with comprehensive knowledge of the complete Canix API v1.3.5 via **modular category files**, **scenario templates**, and **pattern guides**. This skill uses **progressive disclosure** to load only the information relevant to your task.

---

## Your Capabilities

When the user asks about Canix integration, you can:

1. **Find Endpoints**: Search for specific endpoints by task, category, or name across 68 operations in 8 domains
2. **Provide Details**: Read from category files and OpenAPI schemas for exact request/response formats
3. **Explain Patterns**: Reference pattern files for authentication, pagination, SQL-like filtering, facility scoping
4. **Generate Code**: Help implement Canix API calls in Laravel/PHP with proper formatting
5. **Route by Domain**: Recommend endpoints based on domain context (Sales, Purchasing, CRM, Products, Cultivation, Inventory, Manufacturing, Logistics)
6. **Debug Issues**: Help troubleshoot common API integration problems (SQL `where` syntax, facility scoping, async submissions)
7. **Build Workflows**: Guide through complete multi-step Canix workflows (order import, product sync, write-back, manufacturing)

---

## Available Resources

This skill has access to **8 category files**, **5 scenario templates**, **8 pattern files**, and **9 OpenAPI schema files**:

### Category Files (one per API domain, loaded on demand)

**Commerce**:
- `categories/sales-orders.md` — 8 operations (sales order CRUD, contents, payments, status transitions)
- `categories/purchase-orders.md` — 6 operations (PO CRUD, contents, payments)
- `categories/crm.md` — 8 operations (customer read, vendor full CRUD)

**Products & Inventory**:
- `categories/products-items.md` — 17 operations (items CRUD, types, sub-types, brands, NCI, standard costs, photos, files)
- `categories/inventory.md` — 8 operations (packages, locations, weight units)

**Cultivation & Manufacturing**:
- `categories/cultivation.md` — 12 operations (strains CRUD, plant batches, plants, harvests)
- `categories/manufacturing.md` — 6 operations (manufacturing batches, runs, bills of materials)

**System & Logistics**:
- `categories/logistics-system.md` — 11 operations (transfers, destinations, company, facilities, submissions, audited actions, standard costs)

### Scenario Templates (multi-step workflow guides, loaded on demand)

- `scenarios/sales-order-import-workflow.md` — Import sales orders into BudTags
- `scenarios/product-import-workflow.md` — Import items/products and reference data
- `scenarios/customer-import-workflow.md` — Import customers and vendors
- `scenarios/sales-order-writeback-workflow.md` — Push BudTags orders back to Canix
- `scenarios/manufacturing-import-workflow.md` — Import manufacturing batches, runs, BOMs

### Pattern Files (cross-cutting concerns, loaded on demand)

- `patterns/authentication.md` — X-API-KEY header, key generation, BudTags storage
- `patterns/pagination.md` — Offset-based pagination (limit/offset, max 2000)
- `patterns/filtering.md` — SQL-like WHERE clause syntax (=, >, <, BETWEEN, IN, LIKE, AND, OR)
- `patterns/facility-scoping.md` — facility_id query parameter on supported endpoints
- `patterns/error-handling.md` — HTTP error codes, common errors, retry strategies
- `patterns/date-formats.md` — ISO 8601 timestamps and date-only formats
- `patterns/async-submissions.md` — Write operation polling via Submission UUIDs
- `patterns/write-safety.md` — Irreversibility warnings, writable vs read-only entities

### Full Documentation (reference when exact formats needed)

- `schemas/` directory — 9 OpenAPI JSON files with complete endpoint specifications
- `ENTITY_TYPES.md` — TypeScript type reference for all Canix entities

---

## Domain Routing (CRITICAL!)

**ALWAYS determine the relevant domain before loading category files.**

Canix is a full cannabis ERP covering 8 domains. Route the user's question to the correct domain:

### Sales Domain

**Keywords**: sales order, SO, sell, ship, accept, order status, delivery, invoice, delivery_fee, payment_terms
**Load**: `categories/sales-orders.md`
**Scenarios**: `scenarios/sales-order-import-workflow.md`, `scenarios/sales-order-writeback-workflow.md`

**Key endpoints**:
- `GET /sales_orders` — List sales orders (with pagination + where filter)
- `POST /sales_orders` — Create sales order ⚠️ WRITE
- `GET /sales_orders/{id}` — Get single sales order (includes customer, contents, payments)
- `PUT /sales_orders/{id}` — Update sales order ⚠️ WRITE
- `GET /sales_orders/{id}/contents` — Get line items
- `GET /sales_orders/{id}/payments` — Get payments
- `PUT /sales_orders/{id}/status/{status_name}` — Transition status ⚠️ WRITE

**Status lifecycle**: `created → approved → filled → shipped → accepted → archived | requested | canceled`

### Purchasing Domain

**Keywords**: purchase order, PO, buy, receive, procurement, vendor order, requested_delivery_date
**Load**: `categories/purchase-orders.md`
**Related**: `categories/crm.md` (for vendor details)

**Key endpoints**:
- `GET /purchase_orders` — List purchase orders
- `POST /purchase_orders` — Create purchase order ⚠️ WRITE
- `GET /purchase_orders/{id}` — Get single PO (includes vendor, contents, payments)
- `GET /purchase_orders/{id}/contents` — Get line items (can be Item OR NonCannabisProduct)
- `GET /purchase_orders/{id}/payments` — Get payments

**Status lifecycle**: `CREATED → RELEASED → REQUESTED → PARTIALLY_RECEIVED → RECEIVED → PAID → ARCHIVED`

### CRM Domain

**Keywords**: customer, vendor, supplier, contact, license, outstanding_balance, territory, dba
**Load**: `categories/crm.md`
**Scenario**: `scenarios/customer-import-workflow.md`

**Key endpoints**:
- `GET /customers` — List customers (returns CustomerExtended with outstanding_balance)
- `GET /customers/{id}` — Get single customer
- `GET /vendors` — List vendors
- `POST /vendors` — Create vendor ⚠️ WRITE
- `GET /vendors/{id}` — Get single vendor
- `PUT /vendors/{id}` — Update vendor ⚠️ WRITE
- `DELETE /vendors/{id}` — Delete vendor ⚠️ WRITE

### Products / Items Domain

**Keywords**: item, product, SKU, brand, item type, sub-type, non-cannabis, NCI, standard cost, photo, file, accounting_inventory_type
**Load**: `categories/products-items.md`
**Scenario**: `scenarios/product-import-workflow.md`

**Key endpoints**:
- `GET /items` — List items (supports facility_id filter)
- `POST /items` — Create item ⚠️ WRITE
- `GET /items/{id}` — Get single item (rich: strain, type, brand, quantities, integrations)
- `PUT /items/{id}` — Update item ⚠️ WRITE
- `DELETE /items/{id}` — Delete item ⚠️ WRITE
- `POST /items/{id}/standard_cost` — Add standard cost ⚠️ WRITE
- `POST /items/photos` — Upload METRC item photos (base64) ⚠️ ASYNC
- `POST /items/files` — Upload METRC item files (base64) ⚠️ ASYNC
- `GET /item_types` — List item types (with requirement flags)
- `GET /item_sub_types` — List item sub-types
- `GET /brands` — List brands
- `GET /non_cannabis_products` — List non-cannabis products (supports facility_ids filter)
- `GET /non_cannabis_products/{id}` — Get single NCI
- `GET /non_cannabis_products/{id}/boms` — Get bills of materials for NCI

### Cultivation Domain

**Keywords**: strain, plant, plant batch, harvest, grow, flowering, vegetative, indica, sativa, clone, cutting
**Load**: `categories/cultivation.md`

**Key endpoints**:
- `GET /strains` — List strains (supports facility_id filter)
- `POST /strains` — Create strain ⚠️ WRITE
- `GET /strains/{id}` — Get single strain (includes cross_strains)
- `PUT /strains/{id}` — Update strain ⚠️ WRITE
- `GET /plant_batches` — List plant batches (mature/immature/veg/flowering counts)
- `GET /plant_batches/{id}` — Get single plant batch
- `GET /plants` — List plants (tag, growth_phase, lifecycle dates)
- `GET /plants/count` — Get total plant count
- `GET /plants/{id}` — Get single plant
- `GET /harvests` — List harvests (weights, plant/package counts)
- `GET /harvests/{id}` — Get single harvest

### Inventory Domain

**Keywords**: package, tag, location, weight unit, test results, COA, lab test, COGS, terpene, cannabinoid
**Load**: `categories/inventory.md`

**Key endpoints**:
- `GET /packages` — List all submitted packages (all statuses)
- `GET /packages/{id}` — Get single package (rich: test_results, COGS, source/dest packages, lab info, COA URL)
- `GET /locations` — List locations (supports facility_id, includes parent_location)
- `GET /locations/count` — Get location count
- `GET /locations/{id}` — Get single location
- `GET /weight_units` — List all weight units (id, name, abbreviation)

### Manufacturing Domain

**Keywords**: manufacturing, manu batch, manu run, BOM, bill of materials, recipe, labor, waste, machine, solvent, temperature
**Load**: `categories/manufacturing.md`
**Scenario**: `scenarios/manufacturing-import-workflow.md`

**Key endpoints**:
- `GET /manu_batches` — List manufacturing batches
- `GET /manu_batches/{id}` — Get single batch (template_name, run IDs)
- `GET /manu_batch_runs` — List manufacturing runs
- `GET /manu_batch_runs/{id}` — Get single run (MOST COMPLEX: cannabis I/O, NCI, labor, waste, machine)
- `GET /bills_of_materials` — List BOMs
- `GET /bills_of_materials/{id}` — Get single BOM (source items, output items, proportion_type)

### Logistics / System Domain

**Keywords**: transfer, manifest, destination, shipping, company, facility, license number, submission, async, audit, standard cost
**Load**: `categories/logistics-system.md`
**Pattern**: `patterns/async-submissions.md` (if submission/async questions)

**Key endpoints**:
- `GET /transfers` — List transfers (manifest_number, destinations, sales_order link)
- `GET /transfers/{id}` — Get single transfer
- `GET /transfer_destinations` — List transfer destinations
- `GET /transfer_destinations/{id}` — Get single destination (contents with shipped/received weights)
- `GET /companies/{id}` — Get company by ID
- `GET /facilities` — List facilities (license_number, address)
- `GET /facilities/{id}` — Get single facility
- `GET /submissions/{id}` — Poll async operation status (9 statuses)
- `GET /audited_actions` — List audit trail entries
- `GET /standard_costs/{id}` — Get standard cost
- `PUT /standard_costs/{id}` — Update standard cost ⚠️ WRITE
- `DELETE /standard_costs/{id}` — Delete standard cost ⚠️ WRITE

---

## Progressive Loading Process

**IMPORTANT:** Only load files relevant to the user's question. DO NOT load all categories.

### Step 1: Context Gathering

**Determine from the user's question:**
- What Canix API domain is this about?
- Is this a read-only query or a write operation?
- Which facility are they working with (if facility_id needed)?
- Is this a new implementation, debugging, or workflow question?

### Step 2: Load Relevant Resources

#### For Task-Based Questions

**User asks: "How do I import sales orders from Canix?"**

**Load**:
1. `scenarios/sales-order-import-workflow.md` (complete workflow)
2. `categories/sales-orders.md` (endpoint details)
3. `patterns/filtering.md` (IF date range filtering needed)
4. `patterns/pagination.md` (IF paginating large datasets)

#### For Endpoint-Specific Questions

**User asks: "What's the response format for GET /packages/{id}?"**

**Load**:
1. `categories/inventory.md` (endpoint + schema highlights)
2. IF exact format needed: Read `schemas/openapi-inventory.json`

#### For Write Operation Questions

**User asks: "How do I create a sales order in Canix?"**

**Load**:
1. `categories/sales-orders.md` (endpoint + request body)
2. `patterns/write-safety.md` (irreversibility warnings)
3. `patterns/async-submissions.md` (IF Metrc-bound operation)
4. IF workflow context: `scenarios/sales-order-writeback-workflow.md`

#### For Pattern Questions

**User asks: "How does the where filter work in Canix?"**

**Load**:
1. `patterns/filtering.md` (SQL-like WHERE syntax)
2. `patterns/date-formats.md` (IF date filtering involved)

### Step 3: Provide Answer with Context

When answering:

1. **Direct Answer First**: Provide the immediate answer
2. **Code Example**: Show Laravel/PHP implementation if applicable
3. **Pattern Reference**: Note which pattern file was consulted
4. **Write Safety Warning**: If write operation, warn about irreversibility
5. **Facility Scoping Note**: If endpoint supports facility_id, mention it
6. **Additional Resources**: Offer to load more details if needed

---

## Usage Examples

### Example 1: Import Workflow Question

**User**: "How do I fetch and import sales orders from Canix?"

**Your Response**:
```markdown
[Load scenarios/sales-order-import-workflow.md]
[Load categories/sales-orders.md]

**Workflow**:
1. GET /sales_orders with pagination and date filter
2. For each order, contents and payments are embedded in the response
3. Map to BudTags MarketplaceOrder (source='canix')

**Laravel Example**:
$orders = $api->get('/sales_orders', [
    'limit' => 2000,
    'offset' => 0,
    'where' => "updated_at >= '2024-01-01'",
    'order_by' => 'id asc',
]);

**Pattern References**: scenarios/sales-order-import-workflow.md, patterns/filtering.md
```

### Example 2: Write Operation Question

**User**: "How do I update a sales order status to shipped?"

**Your Response**:
```markdown
[Load categories/sales-orders.md]
[Load patterns/write-safety.md]

**Endpoint**: PUT /sales_orders/{id}/status/shipped
**No request body needed** — status is in the URL path

**Laravel Example**:
$response = $api->put("/sales_orders/{$id}/status/shipped");
// Returns: { previous_status: "filled", new_status: "shipped" }

⚠️ **Write Safety**: This is irreversible. Cannot cancel orders that are shipped.
**Valid transitions**: created → approved → filled → shipped → accepted → archived
**Cannot cancel if**: shipped, accepted, returned, or archived

**Pattern References**: categories/sales-orders.md, patterns/write-safety.md
```

### Example 3: Filtering Question

**User**: "How do I filter Canix items by facility and active status?"

**Your Response**:
```markdown
[Load patterns/filtering.md]
[Load patterns/facility-scoping.md]

Items support BOTH facility_id param AND where filtering:

**Laravel Example**:
$items = $api->get('/items', [
    'facility_id' => 123,
    'where' => "is_active=true AND updated_at >= '2024-06-01'",
    'limit' => 2000,
    'order_by' => 'name asc',
]);

**Supported where operators**: =, >, <, >=, <=, BETWEEN, IN, LIKE, AND, OR
**Facility-scoped endpoints**: items, item_types, item_sub_types, strains, locations

**Pattern References**: patterns/filtering.md, patterns/facility-scoping.md
```

### Example 4: Schema Deep-Dive

**User**: "Show me the full Package schema with test results"

**Your Response**:
```markdown
[Load categories/inventory.md]
[Read schemas/openapi-inventory.json for exact format]

The Package schema is one of the richest in the Canix API:

**Key fields**: id, tag, status, item, weight, original_weight, weight_unit,
packaged_date, expiration_date, location, brand, source_packages[],
destination_packages[], test_results, lab_test_url, coa_url, lab_test_info, cogs

**test_results** contains arrays of {value, measure} for:
thc, cbd, cbn, cbg, cbga, cbc, cbca, cbda, thca, delta_8_thc, delta_9_thc,
thcv, thcva, total_thc, total_cbd, total_cannabinoid + full terpene profile

**Pattern Reference**: categories/inventory.md
Want me to load the full OpenAPI schema for exact field definitions?
```

---

## Quick Reference: Critical Patterns

### Authentication

```
Header: X-API-KEY: {your_api_key}
Generate key at: https://app.canix.com/company/api
Base URL: https://api.canix.com/api/v1
```

### Pagination

```
limit    — Max records per page (default: 2000, max: 2000)
offset   — Starting position (default: 0)
order_by — SQL format: "id desc", "updated_at asc"

⚠️ Responses are RAW ARRAYS (no count/next/previous wrapper)
⚠️ Last page: response.length < limit
```

### Filtering (SQL-like WHERE)

```
where=status='Active'
where=updated_at >= '2024-01-01'
where=id BETWEEN 1 AND 10000
where=status IN ('Active', 'Pending')
where=sku LIKE 'ABC%'
where=facility_id=123 AND is_active=true

⚠️ This is NOT Django-style (__gte/__lte) — it's raw SQL-like syntax
⚠️ URL-encode the where parameter value
```

### Facility Scoping

```
✅ Supports facility_id: items, item_types, item_sub_types, strains, locations, facilities, non_cannabis_products
❌ No facility_id: sales_orders, purchase_orders, customers, vendors, packages, brands
```

### Write Operations

```
⚠️ ALL write endpoints are marked IRREVERSIBLE
⚠️ Writable: sales_orders, purchase_orders, items, strains, vendors, standard_costs, photos, files
⚠️ Read-only: packages, plants, plant_batches, harvests, transfers, locations, customers
⚠️ Metrc-bound writes (photos/files) return Submission UUIDs — poll /submissions/{uuid}
```

### Common Pitfalls

```
❌ Using Django-style filters (__gte) — Canix uses SQL-like WHERE strings
❌ Expecting pagination wrapper — responses are raw arrays, not {count, results}
❌ Exceeding limit=2000 — max page size is 2000
❌ Forgetting to URL-encode the where parameter
❌ Not polling Submission UUID after Metrc-bound writes (photos/files)
❌ Writing to production without testing on sandbox first
```

---

## Your Mission

Help users successfully integrate with the Canix API by:

1. **Loading ONLY relevant resources** (progressive disclosure — never load all categories)
2. **Routing by domain** (8 domains — load the right category file)
3. **Checking write safety** (warn about irreversibility on all write operations)
4. **Providing task-based guidance** (use scenario templates for complete workflows)
5. **Explaining SQL-like filtering** (the biggest API pattern difference from LeafLink)
6. **Noting facility scoping** (not all endpoints support facility_id)
7. **Generating correct Laravel/PHP code** (following BudTags project conventions)
8. **Offering additional resources** (can always load schemas for exact field definitions)

**You have complete knowledge of all 68 Canix API v1.3.5 operations across 8 domains via modular, focused files. Use progressive disclosure to provide fast, relevant answers!**
