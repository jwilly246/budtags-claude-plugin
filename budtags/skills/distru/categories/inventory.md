# Inventory Domain — Batches, Packages, Adjustments, Inventory Snapshot

The Distru Inventory domain covers stock-keeping units: Batches (cost-layer groupings), Packages (Metrc/inventory-unit primitives), Adjustments (stock-event ledger), and Inventory (current on-hand snapshot, grouped by dimensions). Several cross-endpoint inconsistencies are documented below — singular vs plural filter names, `include_costs` gating, snake-vs-bracket multi-value syntax.

**Phase 0.5 audited 2026-05-21.** Mapping doc: `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md`.

## Endpoints

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/public/v1/batches` | List batches | Page size 5,000. Filter: SINGULAR `product_id`. |
| GET | `/public/v1/batches/{id}` | Get one batch | |
| GET | `/public/v1/packages` | List packages | Page size 5,000. Filter: PLURAL `product_ids[]` AND `statuses[]` (plural!). |
| GET | `/public/v1/packages/{id}` | Get one package | |
| GET | `/public/v1/adjustments` | List adjustments | **Kebab-case is correct** — `/stock_adjustments` and `/stock-adjustments` BOTH return 404. The Distru docs page URL hash is `#stock-adjustments` but the actual API path is `/adjustments`. Page size 5,000. Minimal filter surface. |
| GET | `/public/v1/adjustments/{id}` | Get one adjustment | |
| GET | `/public/v1/inventory` | Snapshot grouped by dimensions | Page size 5,000. `grouping[]` bracket array REQUIRED. |

> No POST endpoints on `/batches`, `/packages`, `/adjustments`, or `/inventory`. Inventory is a side-effect of Orders/Purchases/Assemblies — you cannot directly create or adjust stock via the API.

## Batch entity shape

```jsonc
{
  "id": "<uuid>",
  "batch_number": "<string>",
  "product": { /* full Product embed | null */ },
  "creation_source": "PURCHASE|ORDER|ASSEMBLY|ADJUSTMENT|MANUAL|...",  // SCALAR, not array
  "creator": { /* User ref | null */ },
  "location": { /* Location ref | null */ },
  "strain": { /* Strain ref | null */ },
  "quantity": "<decimal>",
  "compliance_quantity": "<decimal>",                              // for compliance reporting
  "production_datetime": "<iso|null>",
  "expiration_datetime": "<iso|null>",
  "use_by_datetime": "<iso|null>",
  "metrc_facility_license": "<string|null>",
  "metrc_package_id": "<string|null>",
  "biotrack_id": "<string|null>",
  "inserted_datetime": "<iso>",
  "updated_datetime": "<iso>",

  // Cost fields — included ONLY when ?include_costs=true is passed
  "cost_per_unit_actual": "<decimal>",
  "cost_per_unit_default": "<decimal>",
  "total_cost_actual": "<decimal>",
  "total_cost_default": "<decimal>"
  // ... see Cost Fidelity in mapping doc Section 7 for full layering details
}
```

### `include_costs=true` gating

Without `?include_costs=true`, cost fields are **omitted entirely** from the response (NOT null). The field key doesn't appear in JSON. This affects schema validation — code must treat cost fields as optional unless `include_costs` was set.

## Batch filter parameters

| Filter | Type | Notes |
|---|---|---|
| `inserted_datetime` | comma-range | |
| `updated_datetime` | comma-range | Canonical incremental-sync filter |
| `product_id` | **string (SINGULAR)** | Note: NOT `product_ids[]`. Single batch query at a time. |
| `location_id[]` | bracket array | |
| `strain_id[]` | bracket array | |
| `creation_source` | string | Single value (the response field is also scalar). |
| `license_number` | string | |
| `include_costs` | boolean | `?include_costs=true` to add cost fields to response |
| `page[number]` | integer | |

## Package entity shape

```jsonc
{
  "id": "<uuid>",
  "package_id": "<string>",                                        // human-readable Metrc-like ID
  "product": { /* Product ref */ },
  "batch": { /* Batch ref | null */ },
  "location": { /* Location ref */ },
  "status": "active|finished|sold|transferred|discontinued|selling|assembling",  // Distru status enum (lowercase on RESPONSE, uppercase on FILTER input)
  "quantity": "<decimal>",
  "compliance_quantity": "<decimal>",
  "expiration_datetime": "<iso|null>",
  "use_by_datetime": "<iso|null>",
  "metrc_package_id": "<string|null>",
  "metrc_facility_license": "<string|null>",
  "biotrack_id": "<string|null>",
  "parent_package_id": "<uuid|null>",                              // for split tracking
  "inserted_datetime": "<iso>",
  "updated_datetime": "<iso>",

  // Cost fields — also gated by ?include_costs=true
  "cost_per_unit_actual": "<decimal>",
  "cost_per_unit_default": "<decimal>",
  // ...
}
```

## Package filter parameters

| Filter | Type | Notes |
|---|---|---|
| `inserted_datetime` | comma-range | |
| `updated_datetime` | comma-range | |
| `product_ids[]` | **bracket array PLURAL** | Note: `product_ids[]` here. /batches uses SINGULAR. |
| `statuses[]` | **bracket array PLURAL** | Note: `statuses[]` plural. /orders uses SINGULAR `status[]`. Enum (7 values verified live): `active`, `finished`, `sold`, `transferred`, `discontinued`, `selling`, `assembling`. RESPONSE returns lowercase; FILTER input uppercase (confirmed via wire). |
| `location_id[]` | bracket array | |
| `batch_id[]` | bracket array | |
| `include_costs` | boolean | |
| `page[number]` | integer | |

### Cross-endpoint inconsistency: filter naming

- `/batches` → `product_id` (singular string)
- `/packages` → `product_ids[]` (plural bracket array)
- `/orders` → `status[]` (singular STATUS, bracket array)
- `/packages` → `statuses[]` (plural STATUSES, bracket array)

These are not typos. Each endpoint was built independently and the inconsistency is wire-stable. Importer code must use the exact form per endpoint.

## Adjustment entity shape

Phase 0 verified. See `schemas/openapi-inventory.json` for full field grid.

Key fields:

```jsonc
{
  "id": "<uuid>",
  "package_id": "<uuid>",
  "quantity_delta": "<decimal>",                                   // signed delta (+/-)
  "reason": "<string>",                                            // TENANT-CUSTOMIZABLE enum
  "category": "<string>",                                          // TENANT-CUSTOMIZABLE enum
  "creator": { /* User ref */ },
  "adjusted_datetime": "<iso>",
  "inserted_datetime": "<iso>",
  "updated_datetime": "<iso>"
}
```

Distru's adjustment `reason` and `category` are tenant-configurable but commonly align with Metrc reason codes ("Entry Error", "Mandatory State Destruction", etc.). The importer should preserve verbatim and map at import time.

## Adjustment filter parameters (minimal)

| Filter | Type | Notes |
|---|---|---|
| `inserted_datetime` | comma-range | |
| `updated_datetime` | comma-range | |
| `package_id` | string | |
| `page[number]` | integer | |

No `creator_id`, no `reason`, no `category` filter — fetch and filter client-side.

## /inventory snapshot endpoint

This is **not a queryable history** — it's a current-state grouped aggregation. The response shape changes based on the `grouping[]` parameter (which is REQUIRED).

```bash
GET /public/v1/inventory?grouping[]=PRODUCT&grouping[]=LOCATION
```

Valid `grouping[]` values:
- `PRODUCT`
- `LOCATION`
- `BATCH_NUMBER`
- `PACKAGE`
- `STRAIN`

Multiple groupings combine — `grouping[]=PRODUCT&grouping[]=LOCATION` returns a row per product+location pair. The shape of each row depends on which dimensions were requested.

**Cardinality warning:** `grouping[]=PACKAGE` for an org with 10k+ packages returns 10k+ rows. Paginate via `page[number]`.

### Inventory filter parameters

| Filter | Type | Notes |
|---|---|---|
| `grouping[]` | **REQUIRED** bracket array | Without it, returns HTTP 400 |
| `location_id[]` | bracket array | |
| `product_id[]` | bracket array | |
| `batch_id[]` | bracket array | |
| `strain_id[]` | bracket array | |
| `as_of_datetime` | iso8601 string | Snapshot point-in-time (recent only — Distru doesn't store deep history) |
| `page[number]` | integer | |

## Inventory writes — NONE

The Inventory domain is **read-only** through the API. To create inventory:
- Receive a Purchase (creates Batches/Packages as side-effect)
- Complete an Assembly (creates output Batches/Packages)
- Use the Distru web UI (not the API) for manual adjustments

There is no public endpoint for direct adjustment creation, package splitting, or batch creation.

## Budtags overlap with inventory events

Budtags already tracks inventory events and package splits independently. The trigger for inventory adjustments in Budtags is the package split event. Distru's `/adjustments` and Budtags's existing inventory_events table should overlap conceptually — the importer maps Distru adjustments to corresponding Budtags inventory_events records, preserving both source IDs for traceability.

## Cross-references

- Products that backs each Batch: `categories/products.md`
- Cost-layer details: mapping doc Section 7 (Cost Fidelity)
- Adjustment reason mapping: mapping doc Decision #11
- Eventual consistency: `patterns/eventual-consistency.md`
- Filter conventions: `patterns/filtering.md`
