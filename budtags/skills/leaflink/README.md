# LeafLink API Reference Skill - Package

A comprehensive, modular Claude skill providing complete LeafLink Marketplace V2 API reference using **progressive disclosure** - loading only the information relevant to each task.

## What's Included

This skill package uses a **progressive disclosure architecture** with:

- **skill.md** - Main orchestration file (~374 lines) - routes to relevant resources
- **categories/** - 8 modular category files (~60-100 lines each)
  - Focused endpoint documentation per category
  - Examples: orders.md, products.md, customers.md, inventory.md
- **scenarios/** - 4 task-based workflow templates (~100-150 lines each)
  - Step-by-step implementation guides
  - Examples: order-workflow.md, product-sync-workflow.md, inventory-workflow.md
- **patterns/** - 6 pattern files (~40-80 lines each)
  - authentication.md, company-scoping.md, pagination.md, filtering.md, date-formats.md, error-handling.md
  - Extracted from original LEAFLINK_API_RULES.md
- **schemas/** - All 9 OpenAPI specification files (315KB total)
  - Full endpoint details (methods, paths, parameters, request/response structures)
  - Valid OpenAPI 3.0 format
- **ENTITY_TYPES.md** - TypeScript type reference for all LeafLink entities
- **backups/** - Original comprehensive docs (preserved for reference)
  - LEAFLINK_API_RULES.md.backup
  - OPERATIONS_CATALOG.md.backup
  - CODE_EXAMPLES.md.backup
  - ERROR_HANDLING.md.backup

**Total Size**: ~480KB (with modular files)
**Total Operations**: 117+ operations across 8 categories
**Total Endpoints**: 60 paths with 117+ operations
**Context Efficiency**: 60-85% reduction in context usage vs monolithic approach

---

## Installation

### For You (Already Installed)
This skill is already installed in your project at:
```
.claude/skills/leaflink/
```

### For Your Partner

1. **Copy the entire directory**:
   ```bash
   # Copy this entire folder:
   .claude/skills/leaflink/

   # To their project's skills directory:
   their-project/.claude/skills/leaflink/
   ```

2. **Verify installation**:
   - The directory structure should match:
     ```
     .claude/skills/leaflink/
     ├── skill.md
     ├── README.md
     ├── ENTITY_TYPES.md
     ├── categories/
     │   ├── orders.md
     │   ├── products.md
     │   ├── customers.md
     │   ├── inventory.md
     │   ├── companies.md
     │   ├── crm.md
     │   ├── promotions.md
     │   └── reports.md
     ├── patterns/
     │   ├── authentication.md
     │   ├── company-scoping.md
     │   ├── pagination.md
     │   ├── filtering.md
     │   ├── date-formats.md
     │   └── error-handling.md
     ├── scenarios/
     │   ├── order-workflow.md
     │   ├── product-sync-workflow.md
     │   ├── inventory-workflow.md
     │   └── customer-workflow.md
     ├── schemas/
     │   └── (9 OpenAPI JSON files)
     └── backups/
         └── (Original comprehensive docs)
     ```

3. **Done!** Claude will automatically detect and load the skill.

---

## How to Use

### Method 1: Skill Tool (Recommended)
```
You: Use the leaflink skill to show me how to fetch orders

Claude: [Invokes skill, loads relevant resources, provides comprehensive guide]
```

### Method 2: Direct Questions
Just ask Claude about LeafLink integration - it will automatically use this skill:
```
You: How do I filter LeafLink orders by date range?

Claude: [Loads patterns/filtering.md and scenarios/order-workflow.md]
To filter orders by date range, use the __gte and __lte operators...
[Provides focused answer with progressive disclosure]
```

### Method 3: Category-Specific Questions
```
You: Show me all customer endpoints

Claude: [Loads categories/customers.md]
The customers category has 22 endpoints... [Lists endpoints]
```

---

## What Claude Can Do With This Skill

When this skill is active, Claude can:

✅ **Find Endpoints** - Search 117+ endpoints by name, category, method, or purpose
✅ **Provide Exact Details** - Read schema JSON files for request/response formats
✅ **Check Company Compatibility** - Warn about seller vs buyer restrictions
✅ **Explain Patterns** - Reference authentication, pagination, company scoping, filtering
✅ **Generate Code** - Create Laravel/PHP code examples with correct formats
✅ **Debug Integration Issues** - Help troubleshoot common LeafLink API problems
✅ **Load Only What's Needed** - Progressive disclosure reduces context usage by 60-85%

---

## Progressive Disclosure Benefits

### Before Refactoring (Monolithic)
- Loading all docs: ~4,000 lines
- High context usage
- Slow to find specific information
- Everything loaded even for simple questions

### After Refactoring (Modular)
- **Quick check**: ~400 lines (skill.md + 1-2 files) - **90% reduction**
- **Standard use**: ~600 lines (skill.md + 2-3 categories) - **85% reduction**
- **Comprehensive**: ~900 lines (skill.md + patterns + scenarios) - **78% reduction**
- Fast, focused answers
- Lower API costs
- Better performance

---

## Example Interactions

### Getting Started
```
You: What LeafLink operations are available?

Claude: [Loads skill.md router only]

I have complete documentation for 117+ LeafLink operations across 8 categories:

📦 Orders (21 endpoints) - Fetch, create, update, transition orders
🌿 Products & Catalog (24 endpoints) - Products, batches, images, strains, categories
👥 Customers & CRM (22 endpoints) - Customers, statuses, tiers, contacts, activities
📊 Inventory (20 endpoints) - Items, facilities, retailer inventory, batch tracking
🏢 Companies (10 endpoints) - Profiles, staff, brands, licenses
🎁 Promotions (5 endpoints) - Promo codes and discounts
📈 Reporting (3 endpoints) - Report generation and downloads

What category would you like to explore?
```

### Fetching Orders
```
You: How do I fetch LeafLink orders with date filters?

Claude: [Loads scenarios/order-workflow.md + patterns/filtering.md]

Use the get_orders() method with date range parameters:

```php
$orders = $api->get_orders(
    page: 1,
    status: 'confirmed',
    path: '/leaflink/orders',
    extraParams: [
        'created_date__gte' => '2025-01-01',
        'created_date__lte' => '2025-01-31',
    ]
);
```

**Context loaded**: ~250 lines (skill.md + scenario + pattern)
**Pattern References**: scenarios/order-workflow.md, patterns/filtering.md

Would you like to see how to transition order status?
```

### Company Context Question
```
You: Can buyer companies access /orders-received/?

Claude: [Loads patterns/company-scoping.md + categories/orders.md]

NO. Buyer companies CANNOT access /orders-received/ endpoints.

**Seller companies** use: /orders-received/* (incoming orders)
**Buyer companies** use: /buyer/orders/* (outgoing orders)

[Provides detailed explanation from company-scoping pattern]

**Context loaded**: ~120 lines (skill.md + 2 files)
**Pattern Reference**: patterns/company-scoping.md
```

---

## Skill Features

### 1. Progressive Loading
Load only the files needed for each question:
- **Router** (skill.md) always loaded first
- **Categories** loaded for endpoint questions
- **Patterns** loaded for integration questions
- **Scenarios** loaded for workflow questions
- **Schemas** loaded for detailed specs

### 2. Category Files
8 focused category files covering:
- Orders, Products, Customers, Inventory
- Companies, CRM, Promotions, Reports
- Each ~60-100 lines
- Endpoint lists, use cases, filters

### 3. Pattern Files
6 reusable pattern files:
- Authentication - API key setup
- Company Scoping - Seller vs buyer (CRITICAL!)
- Pagination - Offset-based patterns
- Filtering - 87 params for customers!
- Date Formats - ISO 8601
- Error Handling - Common errors

### 4. Scenario Workflows
4 step-by-step workflow guides:
- Order lifecycle management
- Product catalog sync
- Inventory tracking
- Customer relationships

### 5. OpenAPI Specifications
9 comprehensive schema files:
- Products (core + metadata)
- Orders, Customers, CRM
- Inventory, Companies
- Promotions, Reports
- Easy to reference

### 6. TypeScript Types
Complete type definitions for all LeafLink entities

---

## Package Structure

```
.claude/skills/leaflink/ (~480KB total)
├── skill.md (374 lines)                     # Main router
├── README.md (this file)
├── ENTITY_TYPES.md                          # TypeScript types
├── categories/ (~8 files, 60-100 lines each)
│   ├── orders.md
│   ├── products.md
│   ├── customers.md
│   ├── inventory.md
│   ├── companies.md
│   ├── crm.md
│   ├── promotions.md
│   └── reports.md
├── patterns/ (~6 files, 40-80 lines each)
│   ├── authentication.md
│   ├── company-scoping.md (CRITICAL!)
│   ├── pagination.md
│   ├── filtering.md
│   ├── date-formats.md
│   └── error-handling.md
├── scenarios/ (~4 files, 100-150 lines each)
│   ├── order-workflow.md
│   ├── product-sync-workflow.md
│   ├── inventory-workflow.md
│   └── customer-workflow.md
├── schemas/ (315KB)
│   ├── openapi-products-core.json (109KB)
│   ├── openapi-products-metadata.json (26KB)
│   ├── openapi-orders.json (132KB)
│   ├── openapi-customers-core.json (66KB)
│   ├── openapi-crm.json (27KB)
│   ├── openapi-inventory.json (42KB)
│   ├── openapi-companies.json (27KB)
│   ├── openapi-promotions-reports.json (15KB)
│   └── openapi-shared.json (14KB)
└── backups/ (Original comprehensive docs)
    ├── LEAFLINK_API_RULES.md.backup
    ├── OPERATIONS_CATALOG.md.backup
    ├── CODE_EXAMPLES.md.backup
    └── ERROR_HANDLING.md.backup
```

---

## Updates & Maintenance

### When LeafLink API Changes

1. **Update OpenAPI specs** - LeafLink provides updated specs periodically
2. **Update category files** - Document new endpoints in relevant categories
3. **Update patterns** - Add new integration patterns as needed
4. **Test workflows** - Verify all scenarios still work correctly

### Version History

**v2.0.0** - January 2025 (Progressive Disclosure Refactoring)
- ✅ Implemented progressive disclosure architecture
- ✅ Split into 8 category files, 6 pattern files, 4 scenarios
- ✅ 60-85% context reduction
- ✅ Improved performance and cost efficiency
- ✅ Consistent with metrc-api skill pattern

**v1.0.0** - January 2025 (Initial Release)
- ✅ Complete documentation for 117+ LeafLink operations
- ✅ OpenAPI specifications split into 9 optimized files
- ✅ 4 comprehensive workflow guides
- ✅ Complete TypeScript type definitions

---

## Troubleshooting

### Skill Not Loading

**Problem**: Claude doesn't seem to know about LeafLink operations

**Solutions**:
1. Verify file structure matches above
2. Check that `skill.md` exists in `.claude/skills/leaflink/`
3. Restart your Claude session
4. Try explicitly: "Use the leaflink skill to..."

### Files Not Found

**Problem**: References to category or pattern files not found

**Solutions**:
1. Verify all subdirectories exist (categories/, patterns/, scenarios/)
2. Check file names match exactly (case-sensitive)
3. Ensure you have the v2.0.0 refactored version

---

## License & Attribution

**API Documentation Source**: LeafLink Marketplace V2 API
**Provider**: LeafLink (https://www.leaflink.com/)
**Developer Docs**: https://developer.leaflink.com/

**BudTags Integration**: Custom integration built for cannabis industry compliance
**Skill Author**: Created for BudTags team internal use
**Skill Format**: Following Claude Code .claude/skills/ convention with progressive disclosure

---

## Support

### For LeafLink API Questions
- **Developer Portal**: https://developer.leaflink.com/
- **Support Email**: support@leaflink.com
- **API Status**: Check LeafLink status page

### For BudTags Integration Questions
- **Contact**: BudTags development team
- **Internal Docs**: See CLAUDE.md in project root
- **Service File**: `app/Services/Api/LeafLinkApi.php`

### For Skill Usage Questions
Ask Claude! The skill uses progressive disclosure to provide exactly what you need.

---

**Ready to use! Ask Claude anything about LeafLink integration.**
