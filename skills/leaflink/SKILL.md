---
name: leaflink
description: Use this skill when working with LeafLink wholesale marketplace integration, managing orders, syncing inventory/products, or handling customer/company data from LeafLink.
agent: leaflink-specialist
---

# LeafLink API Reference Skill

You are now equipped with comprehensive knowledge of the complete LeafLink Marketplace V2 API via **modular category files**, **scenario templates**, and **pattern guides**. This skill uses **progressive disclosure** to load only the information relevant to your task.

---

## Your Capabilities

When the user asks about LeafLink integration, you can:

1. **Find Endpoints**: Search for specific endpoints by task, category, or name
2. **Provide Details**: Read from category files and OpenAPI schemas for exact request/response formats
3. **Explain Patterns**: Reference pattern files for authentication, pagination, filtering, company scoping
4. **Generate Code**: Help implement LeafLink API calls in Laravel/PHP with proper formatting
5. **Route by Company Type**: Recommend endpoints based on company context (seller vs buyer)
6. **Debug Issues**: Help troubleshoot common API integration problems (trailing slashes, filters, etc.)
7. **Build Workflows**: Guide through complete multi-step LeafLink workflows

---

## Available Resources

This skill has access to **8 category files**, **4-6 scenario templates**, and **6 pattern files**:

### Category Files (Modular, ~60-100 lines each)

**Core Operations**:
- `categories/orders.md` - 21 endpoints (order management, transitions, line items)
- `categories/products.md` - 24 endpoints (CRUD, batches, categories, images, strains)
- `categories/customers.md` - 22 endpoints (CRUD, statuses, tiers, relationships)
- `categories/inventory.md` - 20 endpoints (items, facilities, retailer inventory)

**Organization & Relationships**:
- `categories/companies.md` - 10 endpoints (profiles, staff, brands, licenses)
- `categories/crm.md` - 12 endpoints (contacts, activity tracking)

**Additional Features**:
- `categories/promotions.md` - 5 endpoints (promo codes, discounts)
- `categories/reports.md` - 3 endpoints (report generation, downloads)

### Scenario Templates (~100-150 lines each)

- `scenarios/order-workflow.md` - Complete order lifecycle management
- `scenarios/product-sync-workflow.md` - Product catalog synchronization
- `scenarios/inventory-workflow.md` - Inventory tracking and updates
- `scenarios/customer-workflow.md` - Customer relationship management

### Pattern Files (~40-80 lines each)

- `patterns/authentication.md` - API key setup, headers, token types
- `patterns/company-scoping.md` - Seller vs buyer context (CRITICAL!)
- `patterns/pagination.md` - Offset-based pagination (limit/offset)
- `patterns/filtering.md` - Filter syntax (__gte, __lte, __in, __icontains, etc.)
- `patterns/date-formats.md` - ISO 8601 requirements, common date fields
- `patterns/error-handling.md` - HTTP codes, trailing slash errors, retry strategies

### Full Documentation (reference when needed)

- `schemas/` directory - 9 OpenAPI JSON files with complete endpoint details
- `ENTITY_TYPES.md` - TypeScript type reference for all LeafLink entities
- `.claude/docs/marketplace/pricing.md` - Currency conversion for order line items (cents vs dollars)

---

## Company Scoping Routing (CRITICAL!)

**ALWAYS determine company type before recommending endpoints.**

LeafLink operations are scoped to company context. Different company types access different endpoints:

### For Seller Companies (Brands/Manufacturers)

**Full Access To**:
- Orders received from buyers (`/orders-received/*`)
- Product catalog management (`/products/*`, `/product-lines/*`, `/strains/*`)
- Customer relationships (`/customers/*`, `/customer-statuses/*`, `/customer-tiers/*`)
- Inventory management (`/inventory-items/*`, `/facilities/*`)
- Company data (`/companies/*`, `/brands/*`)
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
- Product browsing (limited to seller catalogs)
- Retailer inventory (`/retailer-inventory/*`)
- Facility management
- Company data

**Typical Workflows**:
- Place orders with sellers
- Receive deliveries
- Track retailer inventory
- Manage POS integration

**Load These Categories**:
- `categories/orders.md` (buyer/orders endpoints)
- `categories/inventory.md` (retailer inventory focus)
- `categories/companies.md`

### Critical Company Context Rules

```markdown
✅ Seller (Brand/Manufacturer): Manages products, receives orders, ships to buyers
✅ Buyer (Retailer/Dispensary): Places orders, receives deliveries, manages retail inventory

⚠️  API keys are tied to ONE company
⚠️  All operations return data for that company only
⚠️  Orders: Sellers see "orders-received", Buyers see "buyer/orders"
```

---

## Progressive Loading Process

**IMPORTANT:** Only load files relevant to the user's question. DO NOT load all categories.

### Step 1: Context Gathering

**Ask the user or determine from context:**

"What LeafLink API task are you working on? Please provide:
- Goal/task description (e.g., 'fetch confirmed orders', 'sync product catalog')
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

**Context**: ~250-350 lines (60% reduction from loading all docs)

#### For Endpoint-Specific Questions

**User asks: "What's the request format for POST /orders-received/{id}/transition/accept/?"**

**Load**:
1. `categories/orders.md` (endpoints + descriptions)
2. IF needed: Read `schemas/openapi-orders.json` (full details)
3. `scenarios/order-workflow.md` (IF workflow context needed)

**Context**: ~100-200 lines (75% reduction)

#### For Company Context Questions

**User asks: "What's the difference between seller and buyer order endpoints?"**

**Load**:
1. `patterns/company-scoping.md` (complete company context explanation)
2. `categories/orders.md` (to show endpoint differences)

**Context**: ~120 lines (80% reduction)

#### For Integration Pattern Questions

**User asks: "How do I filter orders by date range?"**

**Load**:
1. `patterns/filtering.md` (filtering patterns + examples)
2. `patterns/date-formats.md` (IF date format questions arise)

**Context**: ~80 lines (85% reduction)

### Step 3: Provide Answer with Context

When answering:

1. **Direct Answer First**: Provide the immediate answer
2. **Code Example**: Show Laravel/PHP implementation if applicable
3. **Pattern Reference**: Note which pattern file was consulted
4. **Company Check**: Warn if endpoint has company type restrictions
5. **Additional Resources**: Offer to load more details if needed

---

## Usage Examples

### Example 1: Task-Based Question

**User**: "How do I fetch orders from LeafLink and filter by status?"

**Your Response**:
```markdown
To fetch orders with status filtering, use the GET /orders-received/ endpoint with status filters.

Let me load the order workflow guide for you...
[Load scenarios/order-workflow.md]
[Load patterns/filtering.md for filter syntax]

**Workflow**:
1. Authenticate with API key
2. Fetch orders with status filter: GET /orders-received/?status=confirmed
3. Handle pagination for large result sets

**Laravel Example**:
[Show code from scenario file]

**Company Compatibility**: Seller companies only (buyers use /buyer/orders/)
**Pattern References**: scenarios/order-workflow.md, patterns/filtering.md

Would you like to see how to transition order status after fetching?
```

### Example 2: Company Context Question

**User**: "Can buyer companies access the /orders-received/ endpoint?"

**Your Response**:
```markdown
NO. Buyer companies CANNOT access /orders-received/ endpoints.

[Load patterns/company-scoping.md for complete details]

**Seller companies (Brands/Manufacturers) CAN access**:
- /orders-received/* (incoming orders from buyers)
- /products/* (manage catalog)
- /customers/* (customer relationships)

**Buyer companies (Retailers/Dispensaries) SHOULD use**:
- /buyer/orders/* (outgoing orders to sellers)
- /retailer-inventory/* (retail inventory tracking)

Attempting to call /orders-received/ with a buyer API key will result in:
- No data returned (empty results)
- Or HTTP 403 Forbidden

**Pattern Reference**: patterns/company-scoping.md

Would you like to see buyer-specific order endpoints instead?
```

### Example 3: Endpoint Details Question

**User**: "Show me the request format for POST /products/"

**Your Response**:
```markdown
The POST /products/ endpoint creates a new product in your catalog.

[Load categories/products.md for endpoint list]
[Read schemas/openapi-products-core.json for exact format]

**Endpoint**: POST /products/
**Company Compatibility**: Seller companies only
**Required Fields**: name, category, company

**Request Body**:
[Show exact JSON structure from schema file]

**Laravel Example**:
[Show code implementation]

**IMPORTANT**: Don't forget the trailing slash! `/products/` not `/products`

**Pattern References**:
- categories/products.md
- patterns/error-handling.md (for trailing slash requirement)

Would you like to see how to upload product images after creation?
```

### Example 4: Integration Pattern Question

**User**: "How should I handle LeafLink pagination?"

**Your Response**:
```markdown
LeafLink uses offset-based pagination with limit and offset query parameters.

[Load patterns/pagination.md]

**Standard Pattern**:
- limit: Number of results per page (default: 50, max: 100)
- offset: Starting position (0-indexed)
- Response includes: count, next, previous, results

**Laravel Example**:
[Show iteration code from pattern file]

**Pattern Reference**: patterns/pagination.md

Would you like to see this applied to fetching all orders?
```

---

## Quick Reference: Critical Patterns

### Company Scoping (MOST IMPORTANT!)

```markdown
✅ Seller (Brand/Manufacturer):
   - /orders-received/* (incoming orders)
   - /products/*, /product-lines/*, /strains/* (catalog management)
   - /customers/* (customer relationships)
   - /inventory-items/* (seller inventory)

✅ Buyer (Retailer/Dispensary):
   - /buyer/orders/* (outgoing orders)
   - /retailer-inventory/* (retail inventory)
   - Limited product access (browsing only)

⚠️ API keys are company-scoped - you only see YOUR company's data
⚠️ Orders: Sellers see "orders-received", Buyers see "buyer/orders"
```

### Universal Requirements

```markdown
✅ ALL endpoint paths MUST end with trailing slash `/` (CRITICAL!)
✅ Date format: ISO 8601 (2025-01-15 or 2025-01-15T10:30:00Z)
✅ Pagination: Use limit and offset query params
✅ Filtering: Use Django-style filters (__gte, __lte, __in, __icontains)
✅ Content-Type: application/json for POST/PATCH requests
✅ Authorization: App {API_KEY} header format
```

### Common Pitfalls

```markdown
❌ Forgetting trailing slash (returns 400 Bad Request)
❌ Using wrong filter syntax (e.g., date> instead of date__gt)
❌ Not understanding company scoping (seeing no data)
❌ Not paginating large result sets (missing data)
❌ Using wrong date format (must be ISO 8601)
❌ Not clearing cache after bulk updates
```

---

## Your Mission

Help users successfully integrate with LeafLink API by:

1. **Loading ONLY relevant resources** (progressive disclosure)
2. **Checking company type compatibility FIRST** (prevent empty results)
3. **Providing task-based guidance** (use scenario templates)
4. **Explaining patterns clearly** (reference pattern files)
5. **Generating correct Laravel/PHP code** (following project conventions)
6. **Debugging integration issues** (error handling patterns, trailing slashes)
7. **Offering additional resources** (can always load more details)

**You have complete knowledge of all 117+ LeafLink API v2 endpoints via modular, focused files. Use progressive disclosure to provide fast, relevant answers!**
