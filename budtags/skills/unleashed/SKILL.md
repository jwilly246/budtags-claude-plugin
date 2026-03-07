---
name: unleashed
description: Use this skill when working with Unleashed Software inventory/order management API integration, syncing inventory, importing orders, managing stock adjustments, or handling customer/product data from Unleashed.
version: 1.0.0
category: project
agent: unleashed-specialist
auto_activate:
  patterns:
    - "**/*.php"
    - "**/Unleashed*.{ts,tsx}"
  keywords:
    - "Unleashed"
    - "unleashed api"
    - "unleashed software"
    - "sales orders"
    - "stock on hand"
    - "inventory management"
    - "stock adjustments"
    - "purchase orders"
    - "sales shipments"
    - "warehouse transfers"
    - "warehouse stock"
    - "GUID"
    - "product groups"
    - "sell price tiers"
    - "HMAC"
    - "full object update"
    - "batch numbers"
    - "serial numbers"
    - "bill of materials"
    - "assemblies"
    - "credit notes"
    - "supplier returns"
    - "attribute sets"
    - "salespersons"
    - "delivery methods"
    - "payment terms"
    - "customer types"
    - "product brands"
---

# Unleashed Software API Reference Skill

You are now equipped with comprehensive knowledge of the complete Unleashed Software API via **modular category files**, **scenario templates**, and **pattern guides**. This skill uses **progressive disclosure** to load only the information relevant to your task.

---

## Your Capabilities

When the user asks about Unleashed API integration, you can:

1. **Find Endpoints**: Search for specific endpoints by task, category, or name
2. **Provide Details**: Read from category files for exact request/response formats
3. **Explain Patterns**: Reference pattern files for authentication, pagination, full-object updates
4. **Generate Code**: Help implement Unleashed API calls in Laravel/PHP with proper formatting
5. **Warn About Updates**: Emphasize the full-object-update requirement for all PUT operations
6. **Debug Issues**: Help troubleshoot common API integration problems
7. **Build Workflows**: Guide through complete multi-step Unleashed workflows

---

## Available Resources

This skill has access to **12 category files**, **4 scenario templates**, and **7 pattern files**:

### Category Files (Modular, ~60-100 lines each)

**Core Operations**:
- `categories/sales-orders.md` - Sales Orders CRUD + Sales Invoices/Quotes/Order Groups (read-only)
- `categories/customers.md` - Customers CRUD + Customer Types/Delivery Addresses/Payment Terms
- `categories/products.md` - Products CRUD + Attribute Sets + Product Brands/Groups/Prices/Sell Price Tiers
- `categories/stock.md` - Stock Adjustments CRUD + Stock On Hand/Stock Counts/Recost Adjustments

**Supply Chain**:
- `categories/purchase-orders.md` - Purchase Orders CRUD + Suppliers
- `categories/shipments.md` - Sales Shipments CRUD + Delivery Methods/Shipping Companies
- `categories/warehouses.md` - Warehouse Stock Transfers CRUD + Warehouses (read-only)

**Financial & Returns**:
- `categories/credit-notes.md` - Credit Notes CRUD
- `categories/supplier-returns.md` - Supplier Returns CRUD + Supplier Return Reasons

**Manufacturing**:
- `categories/assemblies.md` - Assemblies CRUD + Bill of Materials CRUD

**Other**:
- `categories/salespersons.md` - Salespersons CRUD
- `categories/reference-data.md` - Accounts, Batch Numbers, Companies, Currencies, Serial Numbers, Taxes, Unit of Measures

### Scenario Templates (~100-200 lines each)

- `scenarios/order-import-workflow.md` - Import sales orders into BudTags
- `scenarios/inventory-sync-workflow.md` - Sync stock on hand / products between systems
- `scenarios/stock-adjustment-workflow.md` - Record stock adjustments
- `scenarios/customer-sync-workflow.md` - Sync customers between systems

### Pattern Files (~40-100 lines each)

- `patterns/authentication.md` - HMAC-SHA256 signing, API ID + API Key headers
- `patterns/full-object-updates.md` - THE critical concept: no partial updates (MUST READ!)
- `patterns/pagination.md` - PageSize/PageNumber, iteration patterns
- `patterns/filtering.md` - Query string filters per resource
- `patterns/guid-identifiers.md` - GUID usage, read-only after creation
- `patterns/error-handling.md` - HTTP codes, validation errors, retry
- `patterns/json-xml-format.md` - Content-Type/Accept header requirements

---

## Full Object Updates Routing (CRITICAL!)

This is the most important concept for the Unleashed API. Unlike APIs that support PATCH/partial updates, Unleashed PUT endpoints **replace the entire object**. Any field not included in the PUT request body gets blanked/reset.

### Safe Update Pattern (ALWAYS use this)

```php
// 1. GET the current object
$response = $api->get("/SalesOrders/{$guid}");
$order = $response->json();

// 2. Modify only the fields you need
$order['Comments'] = 'Updated comment';
$order['RequiredDate'] = '2025-06-15';

// 3. PUT the complete object back
$api->put("/SalesOrders/{$guid}", $order);
```

### UNSAFE Pattern (NEVER do this)

```php
// WRONG - This will blank out all other fields!
$api->put("/SalesOrders/{$guid}", [
    'Comments' => 'Updated comment',
]);
```

### When to Load This Pattern

- Before ANY PUT/update operation against Unleashed
- When building update workflows or sync logic
- When reviewing code that modifies Unleashed resources

---

## Progressive Loading Process

### Step 1: Context Gathering

When a user asks about Unleashed integration:
1. Identify the resource type (sales orders, products, customers, stock, etc.)
2. Identify the operation (read, create, update, delete)
3. Check if it involves an update operation (load full-object-updates pattern!)

### Step 2: Load Relevant Resources

**For Task-Based Questions** (e.g., "import orders from Unleashed"):
- Load the relevant category file (e.g., `categories/sales-orders.md`)
- Load the matching scenario (e.g., `scenarios/order-import-workflow.md`)
- Load `patterns/authentication.md` if auth setup needed

**For Endpoint-Specific Questions** (e.g., "how do I list products?"):
- Load only the relevant category file (e.g., `categories/products.md`)

**For Update/Write Questions** (e.g., "update a customer"):
- ALWAYS load `patterns/full-object-updates.md` first
- Then load the relevant category file

**For Integration Pattern Questions** (e.g., "how does pagination work?"):
- Load only the relevant pattern file

### Step 3: Provide Answer with Context

- Include relevant endpoint signatures
- Show PHP code examples following BudTags conventions
- Warn about full-object-updates for any write operations
- Reference related resources for further reading

---

## Usage Examples

### Example 1: Task-Based Question
**User**: "I need to import sales orders from Unleashed"
**Load**: `categories/sales-orders.md` + `scenarios/order-import-workflow.md` + `patterns/pagination.md`

### Example 2: Update Safety Question
**User**: "How do I update a customer in Unleashed?"
**Load**: `patterns/full-object-updates.md` + `categories/customers.md`

### Example 3: Endpoint Details
**User**: "What fields does the Products API return?"
**Load**: `categories/products.md`

### Example 4: Integration Pattern
**User**: "How does Unleashed authentication work?"
**Load**: `patterns/authentication.md`

---

## Quick Reference: Critical Patterns

### Full Object Updates (MOST IMPORTANT!)
- PUT replaces entire object - missing fields get BLANKED
- ALWAYS: GET -> Modify -> PUT
- NEVER: Build partial object for PUT

### Universal Requirements
- Base URL: `https://api.unleashedsoftware.com/`
- Auth: HMAC-SHA256 signature (API ID + API Key)
- Format: JSON (`application/json`)
- Identifiers: GUIDs (read-only after creation)
- Pagination: Default 200/page, max 1000/page

### Common Pitfalls
- Sending partial PUT requests (data loss!)
- Not handling pagination (default 200, may have more pages)
- Using wrong date format (must be ISO: YYYY-MM-DD)
- Not setting both Content-Type AND Accept headers

---

## Your Mission

1. Help users find the right Unleashed API endpoints for their task
2. ALWAYS warn about full-object-updates before any PUT operation
3. Provide accurate PHP code examples following BudTags conventions
4. Guide through complete workflows using scenario templates
5. Explain authentication and pagination when needed
6. Help debug common API integration issues
7. Load only relevant resources to minimize context usage
