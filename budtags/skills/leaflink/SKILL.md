---
name: leaflink
description: Use this skill when working with LeafLink wholesale marketplace integration, managing orders, syncing inventory/products, or handling customer/company data from LeafLink.
agent: leaflink-specialist
version: 1.1.0
---

# LeafLink API Reference Skill

You are now equipped with knowledge of the LeafLink Marketplace V2 API via **modular category files**, **scenario templates**, and **pattern guides**. This skill uses **progressive disclosure** to load only the information relevant to your task.

**Write behaviour was proven live on the sandbox on 2026-10-16.** `patterns/verified-behavior.md` holds those facts with their evidence files. When any other file in this skill disagrees with it, `verified-behavior.md` wins.

---

## Your Capabilities

When the user asks about LeafLink integration, you can:

1. **Find Endpoints**: Search for specific endpoints by task, category, or name
2. **Provide Details**: Read from category files and OpenAPI schemas for exact request/response formats
3. **Explain Patterns**: Reference pattern files for authentication, pagination, filtering, company scoping
4. **Generate Code**: Help implement LeafLink API calls in Laravel/PHP with proper formatting
5. **Route by Company Type**: Recommend endpoints based on company context (seller vs buyer)
6. **Debug Issues**: Troubleshoot integration problems (ignored filters, unit fields, line duplicates, dates)
7. **Build Workflows**: Guide through complete multi-step LeafLink workflows

---

## Available Resources

This skill has access to **9 category files**, **4 scenario templates**, and **7 pattern files**:

### Category Files (Modular, ~60-100 lines each)

**Core Operations**:
- `categories/orders.md` - order management, transitions, line items, payments
- `categories/products.md` - listings CRUD, batches, categories, images, strains
- `categories/customers.md` - customers, statuses, tiers, relationships
- `categories/inventory.md` - product inventory fields, `/inventory/items/` + `/inventory/facilities/` (BETA), retailer inventory

**Organization & Relationships**:
- `categories/companies.md` - profiles, staff, brands, licenses
- `categories/crm.md` - contacts, activity tracking

**Additional Features**:
- `categories/promotions.md` - promo codes
- `categories/reports.md` - report generation, downloads

**Inbound Events**:
- `categories/webhooks.md` - 2 event types (order, product), HMAC-SHA256 signing, envelope shape, receiver design. **Load this whenever implementing or debugging the webhook receiver; the public LeafLink docs omit critical field paths.** There is no webhook-registration API (subscriptions are made in the LeafLink UI).

### Scenario Templates (~100-150 lines each)

- `scenarios/order-workflow.md` - Complete order lifecycle management
- `scenarios/product-sync-workflow.md` - Product catalog synchronization
- `scenarios/inventory-workflow.md` - Inventory tracking and updates
- `scenarios/customer-workflow.md` - Customer relationship management

### Pattern Files

- `patterns/verified-behavior.md` - **sandbox-proven write and read behaviour (2026-10-16), with evidence. Load for ANY write.**
- `patterns/authentication.md` - API key setup, headers, token types, rate limits
- `patterns/company-scoping.md` - Seller vs buyer context (CRITICAL!)
- `patterns/pagination.md` - limit/offset (default 50, max 500), which endpoints honour `ordering`
- `patterns/filtering.md` - real filter names + the honoured/ignored parameter table
- `patterns/date-formats.md` - Mountain-time reads, `T17:00:00Z` writes, real date fields
- `patterns/error-handling.md` - HTTP codes, real error bodies, safe retry rules

### Full Documentation (reference when needed)

- `schemas/` directory - 9 OpenAPI JSON files with endpoint details (official spec copy: `~/budtags-audits/2026-10-15/leaflink_docs_gap_audit/official_openapi.json`)
- `ENTITY_TYPES.md` - TypeScript type reference for LeafLink entities
- `.claude/docs/marketplace/pricing.md` - Currency conversion for order line items (cents vs dollars)

---

## Company Scoping Routing (CRITICAL!)

**ALWAYS determine company type before recommending endpoints.** A company's type comes from `seller` / `buyer` booleans on `/companies/` (there is no `company_type` field).

### For Seller Companies (Brands/Manufacturers)

**Full Access To**:
- Orders received from buyers (`/orders-received/*`, `/line-items/*`, `/order-payments/*`)
- Product catalog management (`/products/*`, `/product-lines/*`, `/strains/*`)
- Customer relationships (`/customers/*`, `/customer-statuses/*`, `/customer-tiers/*`)
- Inventory: the product's own `quantity` / `reserved_qty` / `available_inventory`, plus `/inventory/items/` and `/inventory/facilities/` (BETA)
- Company data (`/companies/*`, `/brands/*`, `/licenses/*`)
- CRM (`/contacts/*`, `/activity-entries/*`)

**Typical Workflows**:
- Receive orders from buyers
- Manage product catalog
- Track customer relationships
- Ship orders to buyers

**Load These Categories**:
- `categories/orders.md` (orders-received endpoints)
- `categories/products.md`
- `categories/customers.md`
- `categories/inventory.md`

### For Buyer Companies (Retailers/Dispensaries)

**Full Access To**:
- Orders placed to sellers (`/buyer/orders/*`)
- Product browsing (seller catalogs)
- Retailer inventory (`/retailer-inventory/*`)
- Company data

**Load These Categories**:
- `categories/orders.md` (buyer/orders endpoints)
- `categories/inventory.md` (retailer inventory focus)
- `categories/companies.md`

### Critical Company Context Rules

```markdown
✅ Seller (Brand/Manufacturer): Manages products, receives orders, ships to buyers
✅ Buyer (Retailer/Dispensary): Places orders, receives deliveries, manages retail inventory

⚠️  App keys are tied to ONE company (User tokens span every company the user can access)
⚠️  Orders: Sellers see "orders-received", Buyers see "buyer/orders"
```

---

## Progressive Loading Process

**IMPORTANT:** Only load files relevant to the user's question. DO NOT load all categories. For ANY write (POST/PATCH/DELETE), also load `patterns/verified-behavior.md`.

### Step 1: Context Gathering

**Ask the user or determine from context:**

"What LeafLink API task are you working on? Please provide:
- Goal/task description (e.g., 'fetch submitted orders', 'sync product catalog')
- Company type (seller/brand OR buyer/retailer) OR
- Specific endpoint name/category OR
- Integration problem to debug"

**Determine scope:**
- What's the user's company type? (determines available endpoints and data visibility)
- Is this a task-based question or endpoint-specific?
- Is this a new implementation or debugging existing code?

### Step 2: Load Relevant Resources

#### For Task-Based Questions

**User asks: "How do I fetch and process incoming orders?"**

**Load**:
1. `scenarios/order-workflow.md` (complete workflow guide)
2. `categories/orders.md` (endpoint details)
3. `patterns/filtering.md` (IF date range or status filtering needed)
4. `patterns/pagination.md` (IF fetching multiple pages)

#### For Endpoint-Specific Questions

**User asks: "What's the request format for POST /orders-received/{number}/transition/accept/?"**

**Load**:
1. `categories/orders.md` (endpoints + descriptions)
2. `patterns/verified-behavior.md` (transition table, what each one does)
3. IF needed: Read `schemas/openapi-orders.json` (full details)

#### For Company Context Questions

**Load**:
1. `patterns/company-scoping.md`
2. `categories/orders.md` (to show endpoint differences)

#### For Integration Pattern Questions

**User asks: "How do I filter orders by date range?"**

**Load**:
1. `patterns/filtering.md` (real filter names + honoured/ignored table)
2. `patterns/date-formats.md` (IF date format questions arise)

### Step 3: Provide Answer with Context

When answering:

1. **Direct Answer First**: Provide the immediate answer
2. **Code Example**: Show Laravel/PHP implementation if applicable
3. **Pattern Reference**: Note which pattern file was consulted
4. **Company Check**: Warn if endpoint has company type restrictions
5. **Verified?**: Say whether the behaviour is sandbox-proven (`verified-behavior.md`) or only documented

---

## Usage Examples

### Example 1: Task-Based Question

**User**: "How do I fetch orders from LeafLink and filter by status?"

**Your Response**:
```markdown
Use GET /orders-received/ with a `status` filter (case-insensitive) and `ordering=id`.

[Load scenarios/order-workflow.md]
[Load patterns/filtering.md for filter syntax]

**Workflow**:
1. Authenticate with the App key
2. GET /orders-received/?status=Submitted&ordering=id&limit=100
3. Page with offset until `next` is null

Real statuses: Draft, Submitted, Accepted, Backorder, Fulfilled, Shipped, Complete, Rejected, Combined, Cancelled.

**Company Compatibility**: Seller companies only (buyers use /buyer/orders/)
**Pattern References**: scenarios/order-workflow.md, patterns/filtering.md
```

### Example 2: Company Context Question

**User**: "Can buyer companies access the /orders-received/ endpoint?"

**Your Response**:
```markdown
No. /orders-received/ is the seller's view of incoming orders. Buyers use /buyer/orders/.

[Load patterns/company-scoping.md for complete details]

Check the key's company first: GET /companies/ and read the `seller` / `buyer` booleans.

**Pattern Reference**: patterns/company-scoping.md
```

### Example 3: Endpoint Details Question

**User**: "Show me the request format for POST /products/"

**Your Response**:
```markdown
[Load categories/products.md]
[Load patterns/verified-behavior.md (unit fields, create rules)]
[Read schemas/openapi-products-core.json for exact format]

**Endpoint**: POST /products/
**Company Compatibility**: Seller companies only
**Required Fields (spec)**: name, description, retail_price, wholesale_price, sale_price, minimum_order, maximum_order, listing_state, inventory_management, unit_of_measure, unit_denomination, category, sub_category, seller, brand, manufacturer, strain_classification, sku, license

**Watch out (sandbox-proven 2026-10-16)**:
- `unit_denomination` is an integer id (11 = "28"); a word or "28" is a 400
- `maximum_order` key must be present; send null for no maximum
- `sub_category` must belong to `category`

**IMPORTANT**: Don't forget the trailing slash! `/products/` not `/products`
```

### Example 4: Integration Pattern Question

**User**: "How should I handle LeafLink pagination?"

**Your Response**:
```markdown
LeafLink uses offset-based pagination with limit and offset query parameters.

[Load patterns/pagination.md]

**Standard Pattern**:
- limit: results per page (default 50, max 500; 1000 is a 400)
- offset: starting position (0-indexed)
- Response includes: count, next, previous, results
- Pass ordering=id where it is honoured; /products/ ignores ordering and id__gt, so dedupe by id

**Pattern Reference**: patterns/pagination.md
```

---

## Quick Reference: Critical Patterns

### Company Scoping (MOST IMPORTANT!)

```markdown
✅ Seller (Brand/Manufacturer):
   - /orders-received/* (incoming orders, keyed by `number`)
   - /products/*, /product-lines/*, /strains/* (catalog management)
   - /customers/* (customer relationships)
   - product quantity / reserved_qty / available_inventory (seller inventory)

✅ Buyer (Retailer/Dispensary):
   - /buyer/orders/* (outgoing orders)
   - /retailer-inventory/* (retail inventory)

⚠️ App keys are company-scoped - you only see YOUR company's data
⚠️ Company type = `seller` / `buyer` booleans on /companies/
```

### Universal Requirements

```markdown
✅ ALL endpoint paths MUST end with trailing slash `/`
✅ Day-only datetime fields: send YYYY-MM-DDT17:00:00Z; LeafLink returns Mountain time
✅ Pagination: limit (default 50, max 500) + offset; ordering=id where honoured
✅ Filters: only names the spec lists for that endpoint, checked against filtering.md
✅ Content-Type: application/json for POST/PATCH requests
✅ Authorization: App {API_KEY} header format
```

### Verified Write Rules (sandbox 2026-10-16, evidence in patterns/verified-behavior.md)

```markdown
Products
✅ unit_denomination = integer id ONLY (11 = "28"); unit_of_measure is a separate field
✅ PATCH is partial: omitted fields (incl. unit_multiplier) are kept
✅ sell_in_unit_of_measure clears only with null or ""
✅ quantity = listing units (Gram/28: 1 unit = 28 g); a case = unit_multiplier units
✅ strains (and product_data_items) = whole-list replace; [] clears
✅ Thresholds flip listing_state on a quantity push; read it from the PATCH response
✅ maximum_order key required on create (null ok); sub_category must match category

Orders
✅ Tax = rate x (lines + SHIPPING), before discount; tax_type "%" only, rate 0-1
✅ discount "%" = 0-1 fraction; always send discount AND discount_type together
✅ sale_price clear = {"amount":"0.00"} (null 400, on_sale forbidden)
✅ Order PATCH line_items = UPSERT: entry without id = NEW line; [] = 400; omitted lines kept
✅ DELETE /line-items/{id}/ works on every status
✅ Nested order PATCH refused on Cancelled/Rejected; /line-items/{id}/ PATCH still works
✅ Shipped -> Rejected ok (clears ship_date + payment_due_date); Complete -> Rejected 400
✅ paid cannot be PATCHed; an exact-balance payment settles; overpay 400
✅ Payment POST is NOT idempotent; payments are accepted on Cancelled/Rejected

Customers / contacts
✅ Top-level address overwrites BOTH addresses; partial nested address blanks the rest
✅ archived:false un-archives; ein is ignored
✅ Contact phone = 10 bare digits; deleted contacts are in the default list (delete=false)
```

### Common Pitfalls

```markdown
❌ Forgetting trailing slash (returns 400 Bad Request)
❌ Trusting a filter that LeafLink ignores (returns the WHOLE list with 200)
❌ Sending unit_denomination as a word
❌ Retrying a POST/PATCH that creates something after a timeout (duplicates)
❌ Sending local midnight for a day-only date (lands on the previous day)
❌ Treating a 200 as proof (sales_reps, ein come back unchanged)
```

---

## Your Mission

Help users successfully integrate with LeafLink API by:

1. **Loading ONLY relevant resources** (progressive disclosure)
2. **Checking company type compatibility FIRST** (prevent empty results)
3. **Checking `verified-behavior.md` before any write**
4. **Providing task-based guidance** (use scenario templates)
5. **Generating correct Laravel/PHP code** (following project conventions)
6. **Debugging integration issues** (ignored filters, unit fields, duplicates, dates)

**The official spec has 66 paths. Use progressive disclosure to provide fast, relevant answers.**
