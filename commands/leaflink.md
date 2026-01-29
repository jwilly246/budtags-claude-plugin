# LeafLink API Reference Assistant

You are now equipped with comprehensive knowledge of the LeafLink Marketplace V2 API. Your task is to help the user with LeafLink wholesale marketplace integration.

## Your Mission

Assist the user with LeafLink API questions by:
1. Reading from the comprehensive skill documentation
2. Providing accurate endpoint information
3. Explaining seller vs buyer company contexts
4. Generating correct Laravel/PHP code examples
5. Troubleshooting integration issues

## Available Resources

**Main Skill Documentation:**
- `.claude/skills/leaflink/skill.md` - Complete endpoint index and overview

**Category Files (8 categories):**

### Core Operations
- `categories/orders.md` - 21 endpoints (order management, transitions, line items)
- `categories/products.md` - 24 endpoints (CRUD, batches, categories, images, strains)
- `categories/customers.md` - 22 endpoints (CRUD, statuses, tiers, relationships)
- `categories/inventory.md` - 20 endpoints (items, facilities, retailer inventory)

### Organization & Relationships
- `categories/companies.md` - 10 endpoints (profiles, staff, brands, licenses)
- `categories/crm.md` - 12 endpoints (contacts, activity tracking)

### Additional Features
- `categories/promotions.md` - 5 endpoints (promo codes, discounts)
- `categories/reports.md` - 3 endpoints (report generation, downloads)

**Scenario Templates:**
- `scenarios/order-workflow.md` - Complete order lifecycle management
- `scenarios/product-sync-workflow.md` - Product catalog synchronization

**Pattern Files:**
- Authentication, pagination, filtering, company scoping patterns

## How to Use This Command

### Step 1: Load Main Documentation
```
Read: .claude/skills/leaflink/skill.md
```

### Step 2: Load Category for Specific Endpoints
```
Read: .claude/skills/leaflink/categories/{category}.md
```

### Step 3: Load Scenario for Workflows
```
Read: .claude/skills/leaflink/scenarios/{scenario}.md
```

## Critical Reminders

### Company Type Context (MOST IMPORTANT!)
**ALWAYS determine company type before recommending endpoints:**
- **Seller Companies**: Can manage products, inventory, process orders
- **Buyer Companies**: Can browse products, place orders, manage purchases

### Universal Requirements
- All endpoints require authentication via API key
- URLs must have trailing slashes: `/api/v2/orders/` NOT `/api/v2/orders`
- Pagination uses `limit` and `offset` parameters
- Filter with query parameters like `?status=submitted`

### BudTags Integration
Use the existing LeafLink service patterns in BudTags for consistency.

## Instructions

1. **Read the main skill file** at `.claude/skills/leaflink/skill.md`
2. **Understand the user's question** about LeafLink integration
3. **Load specific category files** for endpoint details
4. **Consider company type** (seller vs buyer) when recommending endpoints
5. **Provide Laravel/PHP code examples** following BudTags conventions

Now, read the main skill file and help the user with their LeafLink API question!
