# Unleashed Software API Reference Skill - Package

Comprehensive, modular Claude skill for the Unleashed Software inventory and order management API.

---

## What's Included

This skill provides progressive-disclosure access to the Unleashed Software API:

- **12 Category Files** (~60-100 lines each) - Endpoint documentation grouped by resource
- **7 Pattern Files** (~40-100 lines each) - Cross-cutting concerns (auth, pagination, etc.)
- **4 Scenario Templates** (~100-200 lines each) - Complete BudTags integration workflows
- **UNLEASHED_API_RULES.md** - Comprehensive API rules and conventions
- **SKILL.md** - Main orchestration with progressive loading instructions

Total: ~26 files covering 13 editable and 26 read-only API resources.

---

## How to Use

### Method 1: Skill Tool
```
/unleashed-help How do I import sales orders?
```

### Method 2: Direct Questions
Ask about any Unleashed API topic and Claude will load the relevant category/pattern files.

### Method 3: Category-Specific
Reference a specific resource:
- "Show me the Unleashed Products API endpoints"
- "How does Unleashed authentication work?"
- "What's the full object update pattern?"

---

## What Claude Can Do With This Skill

- Find endpoints for any Unleashed resource
- Provide exact field names, types, and constraints
- Generate PHP code for API calls following BudTags conventions
- Warn about full-object-update requirements on PUT operations
- Guide through multi-step integration workflows
- Help debug common API issues (auth, pagination, validation)

---

## Package Structure

```
unleashed/
├── README.md
├── SKILL.md
├── UNLEASHED_API_RULES.md
├── categories/
│   ├── sales-orders.md
│   ├── customers.md
│   ├── products.md
│   ├── stock.md
│   ├── purchase-orders.md
│   ├── shipments.md
│   ├── credit-notes.md
│   ├── supplier-returns.md
│   ├── assemblies.md
│   ├── warehouses.md
│   ├── salespersons.md
│   └── reference-data.md
├── patterns/
│   ├── authentication.md
│   ├── full-object-updates.md
│   ├── pagination.md
│   ├── filtering.md
│   ├── guid-identifiers.md
│   ├── error-handling.md
│   └── json-xml-format.md
└── scenarios/
    ├── order-import-workflow.md
    ├── inventory-sync-workflow.md
    ├── stock-adjustment-workflow.md
    └── customer-sync-workflow.md
```

---

## License & Attribution

API documentation sourced from [Unleashed Software API Docs](https://apidocs.unleashedsoftware.com/). Built for BudTags integration.

## Changelog

- **v1.0.0** - Initial release with complete endpoint coverage
