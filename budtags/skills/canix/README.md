# Canix API Skill

Progressive disclosure documentation skill for the **Canix Cannabis ERP API v1.3.5**.

## Quick Facts

| Attribute | Value |
|-----------|-------|
| API Version | 1.3.5 |
| Base URL | `https://api.canix.com/api/v1` |
| Auth | `X-API-KEY` header |
| Total Operations | 68 across 8 domains |
| Pagination | Offset-based, max 2000 per page |
| Filtering | SQL-like `where` parameter |

## File Structure

```
canix/
├── SKILL.md              ← Always loaded (endpoint index + routing)
├── README.md             ← This file
├── ENTITY_TYPES.md       ← TypeScript type definitions
├── categories/           ← Domain-specific endpoint docs (Tier 2)
│   ├── sales-orders.md
│   ├── purchase-orders.md
│   ├── crm.md
│   ├── products-items.md
│   ├── cultivation.md
│   ├── inventory.md
│   ├── manufacturing.md
│   └── logistics-system.md
├── patterns/             ← Cross-cutting concerns (Tier 2)
│   ├── authentication.md
│   ├── pagination.md
│   ├── filtering.md
│   ├── facility-scoping.md
│   ├── error-handling.md
│   ├── date-formats.md
│   ├── async-submissions.md
│   └── write-safety.md
├── scenarios/            ← Multi-step workflow guides (Tier 2)
│   ├── sales-order-import-workflow.md
│   ├── product-import-workflow.md
│   ├── customer-import-workflow.md
│   ├── sales-order-writeback-workflow.md
│   └── manufacturing-import-workflow.md
└── schemas/              ← OpenAPI JSON specs (Tier 3)
    ├── openapi-sales-orders.json
    ├── openapi-purchase-orders.json
    ├── openapi-crm.json
    ├── openapi-products-items.json
    ├── openapi-cultivation.json
    ├── openapi-inventory.json
    ├── openapi-manufacturing.json
    ├── openapi-logistics-system.json
    └── openapi-shared.json
```

## Progressive Disclosure Tiers

| Tier | What | When Loaded | Context |
|------|------|-------------|---------|
| 1 | `SKILL.md` | Always | Endpoint index, routing rules, quick reference |
| 2 | `categories/`, `patterns/`, `scenarios/` | On demand | Domain docs, patterns, workflows |
| 3 | `schemas/` | On demand | Exact OpenAPI specs for request/response formats |

## API Domains

| Domain | Category File | Operations | Key Entities |
|--------|--------------|------------|-------------|
| Sales | `sales-orders.md` | 8 | SalesOrder, SalesOrderItem, Payment |
| Purchasing | `purchase-orders.md` | 6 | PurchaseOrder, PurchaseOrderItem |
| CRM | `crm.md` | 8 | Customer, Vendor |
| Products | `products-items.md` | 17 | Item, ItemType, SubType, Brand, NCI |
| Cultivation | `cultivation.md` | 12 | Strain, PlantBatch, Plant, Harvest |
| Inventory | `inventory.md` | 8 | Package, Location, WeightUnit |
| Manufacturing | `manufacturing.md` | 6 | ManuBatch, ManuBatchRun, BOM |
| System | `logistics-system.md` | 11 | Transfer, Facility, Submission, AuditedAction |

## Key Differences from LeafLink API

| Aspect | LeafLink | Canix |
|--------|----------|-------|
| Auth header | `Authorization: App {token}` | `X-API-KEY: {token}` |
| Pagination | Cursor + offset, page_size 50 | Offset only, limit max 2000 |
| Filtering | Django-style `__gte`, `__lte`, `__in` | SQL-like `where=status='Active'` |
| Response format | `{count, next, previous, results}` | Raw array |
| Trailing slashes | Required (!) | Not used |
| Company scoping | Seller vs buyer endpoints | Facility-based (facility_id param) |
| Write support | Limited (order transitions) | Full CRUD on orders, items, strains, vendors |
| Async operations | None | Submissions (Metrc-bound writes) |

## Source

Generated from: `resources/js/Components/Marketplace/Orders/canix.yaml`
OpenAPI: 3.0.3 | Canix API v1.3.5
