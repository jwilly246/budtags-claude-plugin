# Distru API Skill

Progressive disclosure documentation skill for the **Distru Public API v1**.

## Quick Facts

| Attribute | Value |
|-----------|-------|
| API Version | v1 (public) |
| Base URL | `https://app.distru.com/public/v1` |
| Auth | `Authorization: Bearer {JWT}` |
| Total Operations | ~35 across 7 domains |
| Pagination | Page-number based (`page[number]`/`page[size]`), `next_page: null` ends |
| Filtering | Query-string parameters per endpoint (no WHERE strings, no Django-style) |
| Response Envelope | `{ "data": [...], "next_page": null\|<int> }` |
| Write Semantics | UPSERT (POST + PUT); no idempotency keys |
| Webhooks | Not documented |
| Sandbox | Not documented |

## File Structure

```
distru/
├── SKILL.md              ← Always loaded (endpoint index + routing)
├── README.md             ← This file
├── ENTITY_TYPES.md       ← TypeScript type definitions
├── categories/           ← Domain-specific endpoint docs (Tier 2)
│   ├── sales-orders.md
│   ├── purchase-orders.md
│   ├── crm.md
│   ├── products.md
│   ├── inventory.md
│   ├── manufacturing.md
│   └── system.md
├── patterns/             ← Cross-cutting concerns (Tier 2)
│   ├── authentication.md
│   ├── pagination.md
│   ├── filtering.md
│   ├── error-handling.md
│   ├── date-formats.md
│   ├── write-safety.md
│   └── eventual-consistency.md
├── scenarios/            ← Multi-step workflow guides (Tier 2)
│   ├── product-import-workflow.md
│   ├── order-import-workflow.md
│   ├── customer-import-workflow.md
│   ├── order-writeback-workflow.md
│   └── assembly-import-workflow.md
└── schemas/              ← OpenAPI JSON specs (Tier 3 — seeded; populated as samples are captured)
    ├── openapi-sales-orders.json
    ├── openapi-purchase-orders.json
    ├── openapi-crm.json
    ├── openapi-products.json
    ├── openapi-inventory.json
    ├── openapi-manufacturing.json
    ├── openapi-system.json
    └── openapi-shared.json
```

## Progressive Disclosure Tiers

| Tier | What | When Loaded | Context |
|------|------|-------------|---------|
| 1 | `SKILL.md` | Always | Endpoint index, routing rules, quick reference |
| 2 | `categories/`, `patterns/`, `scenarios/` | On demand | Domain docs, patterns, workflows |
| 3 | `schemas/` | On demand | OpenAPI specs (seeded — populated as Phase B importers capture samples) |

## API Domains

| Domain | Category File | Resources | Key Entities |
|--------|--------------|-----------|-------------|
| Sales | `sales-orders.md` | Orders, Invoices | Order, OrderLineItem, Invoice, Payment, Charge |
| Purchasing | `purchase-orders.md` | Purchases | Purchase, PurchaseLineItem, Payment |
| CRM | `crm.md` | Companies, Contacts | Company, Contact, RelationshipType |
| Products | `products.md` | Products, Test Results | Product, Brand, Strain, PosMapping, TestResult |
| Inventory | `inventory.md` | Batches, Packages, Stock Adjustments | Batch, Package, StockAdjustment, Cost |
| Manufacturing | `manufacturing.md` | Assemblies | Assembly, CreationSource |
| System | `system.md` | Locations, CustomFields, Users, Roles, PaymentMethods, PosMappings | Location, CustomField, User, Role |

## Key Differences from Canix API

| Aspect | Canix | Distru |
|--------|-------|--------|
| Auth header | `X-API-KEY: {token}` | `Authorization: Bearer {JWT}` |
| Pagination | Offset only (`limit`/`offset`), max 2000 | Page number (`page[number]`/`page[size]`), `next_page` flag |
| Filtering | SQL-like `where=status='Active'` | Query-string params per endpoint (no WHERE) |
| Response format | Raw array | `{ data: [], next_page: null\|<int> }` |
| Last-page detection | `response.length < limit` | `next_page === null` |
| Write support | Full CRUD with explicit POST/PUT/DELETE | UPSERT (POST/PUT) for most resources; DELETE not exposed |
| Async operations | Submission UUID polling for Metrc-bound writes | None documented |
| Eventual consistency | Not documented | **Yes** — Strains and Assemblies have ~1s read-after-write lag |
| Facility scoping | `facility_id` query param on supported endpoints | Implicit via API key's team permissions |
| Idempotency | Not documented | Not documented (capture id, reconcile on retry) |

## Key Differences from LeafLink API

| Aspect | LeafLink | Distru |
|--------|----------|--------|
| Auth header | `Authorization: App {token}` | `Authorization: Bearer {JWT}` |
| Pagination | Cursor + offset, page_size 50 | Page number, `next_page` flag |
| Filtering | Django-style `__gte`, `__lte`, `__in` | Per-endpoint query-string params |
| Response format | `{count, next, previous, results}` | `{data, next_page}` |
| Trailing slashes | Required | Not used |
| Write support | Limited (order transitions) | UPSERT on most resources |

## Source

Documentation root: `https://apidocs.distru.dev/#distru-api`

This skill is **seeded from public documentation**. Per-endpoint field schemas in `schemas/` are populated incrementally as Budtags importers capture live request/response samples (Phase B work in `PLAN-distru-api-integration.md`).
