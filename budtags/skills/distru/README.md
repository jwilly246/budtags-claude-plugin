# Distru API Skill

Progressive disclosure documentation skill for the **Distru Public API v1**.

**Last reconciled with Phase 0.5 audit findings: 2026-05-21.** Authoritative project-level reference is `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md` — if this skill disagrees with that document, the mapping doc wins.

## Quick Facts

| Attribute | Value |
|-----------|-------|
| API Version | v1 (public) |
| Base URL | `https://app.distru.com/public/v1` |
| Auth | `Authorization: Bearer {JWT}` |
| URL convention | **Kebab-case for compound names** (e.g. `/test-results`, `/payment-methods`, `/product-pos-mappings`). Field/model names use snake_case. |
| Total documented endpoints | 18 GET + 4 POST-only + 1 DELETE (the only DELETE in the API) |
| Pagination | Page-number based (`page[number]`/`page[size]`). `page[size]` SILENTLY IGNORED on most endpoints. |
| Page-size caps | 500 (orders/purchases/menus), 1,000 (contacts/locations/users), 5,000 (most), 50,000 (strains) |
| Datetime filters | Comma-range strings (`field=from,to`), NOT `_from`/`_to` pairs |
| Multi-value filters | Inconsistent: some use `param[]=value` brackets, others use `param=val1,val2` comma-strings |
| Filter on unknown param | Silently ignored (returns unfiltered, no 400) |
| Response Envelope | `{ "data": [...], "next_page": "<full URL string>" \| null }` (next_page key may also be absent on final page) |
| Write Semantics | UPSERT (POST). Non-sparse updates on Orders/Invoices/Purchases. PUT only for write-only payment endpoints. DELETE only on `/product-pos-mappings/{id}`. |
| Idempotency | No idempotency keys |
| Webhooks | Not documented |
| Sandbox | Not documented (live-only) |
| Eventual consistency | Strains, Assemblies, Products, Test Results — ~1s read-after-write lag |

## File Structure

```
distru/
├── SKILL.md              ← Always loaded (endpoint index + routing + critical conventions)
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
├── coverage/             ← BudTags integration-coverage audits (Tier 2 — what OUR importers map + our gaps, NOT wire-contract)
│   ├── field-coverage-audit.md     ← Per-endpoint field-coverage matrix (5-state flag, gaps, live-probe findings)
│   └── cross-importer-audit.md     ← Distru vs LeafLink vs Canix importer comparison
└── schemas/              ← OpenAPI JSON specs (Tier 3 — partial; expand as samples are captured)
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
| 1 | `SKILL.md` | Always | Endpoint index, routing rules, critical conventions (kebab-case, etc.) |
| 2 | `categories/`, `patterns/`, `scenarios/` | On demand | Domain docs, patterns, workflows |
| 2 | `coverage/` | On demand | BudTags integration-coverage audits (which fields our importers map + our gaps) — distinct from the wire-contract category/schema docs |
| 3 | `schemas/` | On demand | OpenAPI specs (stubs; expanded from live samples) |

## API Domains and Endpoints (18 GET + 5 write)

| Domain | Category File | Endpoints | RBAC Permission |
|--------|--------------|-----------|-----------------|
| Sales | `sales-orders.md` | `/orders`, `/orders/{id}`, `/invoices`, `/invoices/{id}`, `POST /invoices/{id}/payments` | `orders_permissions_view` / `invoices_permissions_view` |
| Purchasing | `purchase-orders.md` | `/purchases`, `POST /purchases/{id}/payments` | `purchases_permissions_view` |
| CRM | `crm.md` | `/companies`, `/contacts`, `/locations` | `companies_permissions_view` / `contacts_permissions_view` |
| Products | `products.md` | `/products`, `/test-results` (HYPHEN!), `/product-pos-mappings` (incl. DELETE), `POST /custom-fields` | `products_permissions_view` |
| Inventory | `inventory.md` | `/batches`, `/packages`, `/adjustments` (NOT /stock_adjustments!), `/inventory` | `products_permissions_view` |
| Manufacturing | `manufacturing.md` | `/assemblies` | `assemblies_permissions_view` |
| System | `system.md` | `/strains`, `/users`, `/menus`, `/payment-methods` (HYPHEN!), `POST /file-attachments` (HYPHEN!) | `settings_permissions_strains` / `_manage_team` / `_payment_methods` / `_custom_fields` |

## Six slug corrections (URL must be kebab-case)

The following endpoints were initially documented with snake_case slugs in this skill; all are WRONG. The kebab-case versions on the right are the live API paths:

| Wrong (snake_case — returns 404) | Right (kebab-case — works) |
|---|---|
| ~~/stock_adjustments~~ | `/adjustments` |
| ~~/test_results~~ | `/test-results` |
| ~~/payment_methods~~ | `/payment-methods` |
| ~~/product_pos_mappings~~ | `/product-pos-mappings` |
| ~~/custom_fields~~ | `/custom-fields` |
| ~~/file_attachments~~ | `/file-attachments` |

## Key Differences from Canix API

| Aspect | Canix | Distru |
|--------|-------|--------|
| Auth header | `X-API-KEY: {token}` | `Authorization: Bearer {JWT}` |
| URL convention | snake_case | **kebab-case** for compound names |
| Pagination | Offset only (`limit`/`offset`), max 2000 | Page number; `next_page` is a full URL string |
| Filtering | SQL-like `where=status='Active'` | Per-endpoint query-string params; **comma-range datetimes** |
| Response format | Raw array | `{ data: [], next_page: <url\|null> }` |
| Last-page detection | `response.length < limit` | `empty($body['next_page'])` (handles null + missing-key) |
| Write support | Full CRUD with explicit POST/PUT/DELETE | UPSERT (POST/PUT) for most; DELETE only on `/product-pos-mappings/{id}` |
| Async operations | Submission UUID polling for Metrc-bound writes | None documented |
| Eventual consistency | Not documented | **Yes** — Strains, Assemblies, Products, Test Results |
| Facility scoping | `facility_id` query param on supported endpoints | Implicit via API key's team permissions; tenant-customizable RBAC |
| Idempotency | Not documented | Not documented (capture id, reconcile on retry) |
| Filter param naming | Consistent | INCONSISTENT — e.g., `status[]` (orders) vs `statuses[]` (packages); `product_id` (batches) vs `product_ids[]` (packages) |
| Unknown filter param | Returns 400 | Silently IGNORED (returns 200 with unfiltered results) |

## Key Differences from LeafLink API

| Aspect | LeafLink | Distru |
|--------|----------|--------|
| Auth header | `Authorization: App {token}` | `Authorization: Bearer {JWT}` |
| Pagination | Cursor + offset, page_size 50 | Page number; `next_page` is URL string |
| Filtering | Django-style `__gte`, `__lte`, `__in` | Per-endpoint comma-range datetimes; bracket/comma multi-value |
| Response format | `{count, next, previous, results}` | `{data, next_page}` |
| Trailing slashes | Required | Not used |
| Write support | Limited (order transitions) | UPSERT on most resources |

## Source

Documentation root: `https://apidocs.distru.dev/#distru-api`

This skill was originally seeded from public documentation, then **Phase 0.5-audited (2026-05-21)** against live API responses + the user's docs-paste pages. All six slug corrections, all filter parameter tables, response shape verifications, enum value confirmations, and cross-endpoint inconsistency catalog are documented in the project-level mapping file:

→ `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md`

That file is the canonical source. If this skill ever conflicts with it, the mapping doc wins.
