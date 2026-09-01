# Distru READ Endpoint Field Audit

> **What this is:** BudTags **integration-coverage** documentation — which fields *our* importers persist to native primitives, where they land (column / `external_ids` / `raw_payload` / dropped), and where *our* gaps are. This is NOT the Distru wire-contract reference. For the API contract itself (slugs, filters, response shapes, enums) see the sibling `categories/*.md` and `schemas/openapi-*.json` files. Read this when you need to know "does BudTags map field X, and to what?" — read the category files when you need to know "what does Distru send on the wire?"
>
> This document is the canonical home of the field-coverage audit. It was relocated verbatim into the skill from the BudTags repo's former native-conversion audit folder; the repo copy is retired. Companion: `coverage/cross-importer-audit.md` (Distru vs LeafLink vs Canix importer comparison).

**Generated:** 2026-05-24
**Status:** Phase 0 (static scaffold) complete. Phase 1 (Tinker live probe) and Phase 2 (UI walkthrough log tailing) pending.
**Scope:** READ-side only. 18 endpoints currently called by the importer. 100% field coverage.

---

## Methodology

For each endpoint, three field sets are computed:

- **D (documented)** — fields listed in the Distru skill `categories/*.md` ∪ `schemas/openapi-*.json`
- **M (mapped)** — fields the importer actually reads, extracted by `ripgrep` over `app/Services/Distru/*Importer.php` for patterns matching `data_get(`, `Arr::get(`, and direct array access
- **L (live)** — fields observed in actual Distru API responses (populated in **Phase 1**)

Three error modes per endpoint:

| Error mode | Set expression | Action |
|---|---|---|
| Doc'd but not in response | `D \ L` | Verify with Distru or remove from skill doc |
| In response but not doc'd | `L \ D` | Escalate to skill update — these are gold |
| In response but not mapped | `L \ M` | Real gap → fix in importer or document drop |

### Mapped-state legend (5-state flag)

| Flag | Meaning |
|---|---|
| **M** | Mapped to a native column |
| **P** | Partial — sub-field only, or transformed losing fidelity |
| **R** | Retained in raw_payload / external_ids JSON only, unsurfaced |
| **D** | Intentionally dropped (e.g., Metrc-redundant cannabis blanking) |
| **U** | Unmapped and unretained → real gap requiring action |

### Retention legend

| Value | Meaning |
|---|---|
| `column` | Surfaced as a typed table column |
| `external_ids` | Stored in the row's `external_ids` JSON map |
| `raw_payload` | Stored verbatim in a `raw_payload` JSON column |
| `none` | Not retained at all — value is lost after the import call |

---

## Envelope (documented once; not repeated per endpoint)

Every Distru list endpoint returns the same envelope. The `data[]` prefix on every field path in the matrix below refers to this envelope.

```jsonc
{
  "data": [ /* array of resource objects */ ],
  "next_page": "https://app.distru.com/public/v1/<endpoint>?page[number]=2&page[size]=..." | null
  // Note: `next_page` may also be ABSENT entirely (not null) on the final page.
}
```

- `next_page` is a **full URL string** (not an integer) when more pages exist
- Terminal check used in `DistruApi::each_page()`: `! empty($body['next_page'])`
- Defensive guard: `/product-pos-mappings` returns `data: []` with an ever-incrementing `next_page` URL until network timeout; importer stops on empty `data` regardless of `next_page` (DistruApi.php:265-267, 358-360)

---

## Gap Summary

Field counts per endpoint by Mapped state. Numbers approximate (some rows annotate dual-state, e.g. "M (non-cannabis) / D (cannabis)").

| Endpoint | M | P | R | D | **U (real gaps)** | Notes |
|---|---:|---:|---:|---:|---:|---|
| /locations | 7 | 1 | 1 | 0 | **0** | Some fields undocumented in skill but mapped (license, license_id) |
| /strains | 2 | 0 | 7 | 0 | **1** | `type` vs `strain_type` naming drift |
| /menus | 5 | 0 | 2 | 0 | **2** | Skill `name`/`is_active` vs wire `internal_name`/`active` drift |
| /users | 5 | 1 | 1 | 0 | **0** | `role` shape drift (skill says string, wire is `{id,name}`) |
| /payment-methods | 2 | 0 | 4 | 0 | **0** | `is_active` not promoted to column |
| /companies | 17 | 5 | 9 | 0 | **9** | dba, emails, credit_limit, primary_*, tags, locations[].is_*, licenses[].license_type |
| /contacts | 10 | 3 | 5 | 0 | **5** | department, birthdate, anniversary_date, notes vs description, tags |
| /products | 22 | 3 | 6 | 7 | **11** | tags, image_urls, compliance_type, metrc_item_*, internal_notes, etc. |
| /test-results | 14 | 0 | 1 | 2 | **9** | metrc_lab_test_id, product_id, sample_id, expiration_datetime, passed_test |
| /product-pos-mappings | 11 | 0 | 0 | 1 | **2** | external_id (per-mapping POS-side id) + deleted_at mirroring |
| /batches | 11 | 2 | 15 | 0 | **0** | Heavy raw_payload retention |
| /packages (cannabis) | 12 | 4 | 0 | 20 | **0** | Intentional Metrc-redundant blanking |
| /packages (non-cannabis) | 31 | 4 | 6 | 0 | **0** | Full retention |
| **/inventory** | **2** | 0 | 0 | 0 | **4** | **HIGHEST RISK** — cost_default_per_unit, available, reserved, pending dropped without retention; no mirror table |
| /adjustments | 19 | 2 | 6 | 0 | **0** | Mirror is load-bearing (only 2 filters available server-side) |
| /orders | 24 | 9 | 13 | 2 | **0** | ✅ Complete coverage as of 2026-05-26 |
| /invoices | 27 | 0 | 0 | 1 | **0** | ✅ Complete coverage as of 2026-05-26 via native marketplace_invoices + marketplace_invoice_line_items |
| /purchases | 14 | 7 | 1 | 0 | **9** | billing_location, shipping_location, cost_per_unit_actual/default, total_cost_*, returned_quantity |
| **/assemblies** | **18** | **6** | **0** | **2** | **22** | outputs[].id, outputs[].quantity, outputs[].batch, ingredients[].id, ingredients[].batch/package, additional_costs[].amount, no raw retention |
| **Totals** | ~230 | ~50 | ~75 | ~38 | **~89** | |

### Highest-risk endpoints (action priorities)

1. **/inventory** — 4 U gaps with NO raw_payload safety net. Fix path: either add a `distru_inventory_snapshots` mirror table or promote `available`/`reserved`/`pending` to columns on `non_metrc_items`/`products`.
2. **/assemblies** — 22 U gaps from 3-level nesting; no raw_payload retained on audit logs. Highest count, but Metrc-side audit covers cannabis lineage.
3. **/invoices** — `items[]` entirely dropped, including the `order_item_id` back-link that would enable per-line invoice↔order reconciliation. Recommended fix: project `returned_quantity` + cost columns onto `marketplace_order_line_items` matched via `order_item_id`.
4. **/companies** — 9 U gaps mostly in CRM convenience fields (tags, credit_limit, dba, emails) and the heuristic-vs-flag locations gap (importer detects shipping via name substring instead of `is_shipping` boolean).

---

# Endpoint Matrices

Grouped by domain: System → CRM → Products → Inventory → Sales → Purchasing → Manufacturing.

---

## /locations

**Wrapper:** `DistruApi::get_locations()` (DistruApi.php:623)
**Importer:** `ReferenceDataImporter::import_locations()` at line 100
**Native target:** `distru_locations` (mirror) + cross-ref to `metrc_facilities.id` via license-number lookup
**Page cap:** 1,000
**Filters supported:** `inserted_datetime`, `updated_datetime`, `company_id`, `page[number]`, `deleted` (tri-state)
**Filters we send:** `deleted=include` only
**Raw payload retained:** YES — `distru_locations.raw_payload`

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `distru_locations.distru_id` | column | ReferenceDataImporter.php:110 |
| `data[].name` | string | nullable | Y | M | `distru_locations.name` | column | line 141; default `'Unnamed Location'` |
| `data[].address` | string (flat) | nullable | Y | M | `distru_locations.address` | column | line 142 |
| `data[].company_id` | uuid | nullable | Y | M | `distru_locations.distru_company_id` | column | line 143; indexed |
| `data[].is_shipping` | boolean | req | Y | R | `distru_locations.raw_payload` | raw_payload | line 147 |
| `data[].is_billing` | boolean | req | Y | R | `distru_locations.raw_payload` | raw_payload | line 147 |
| `data[].is_archived` | boolean | req | Y | R | `distru_locations.raw_payload` | raw_payload | soft-delete tracking uses `deleted_at` instead |
| `data[].license_id` | uuid | nullable | N | M | `distru_locations.distru_license_id` | column | line 118; UNDOCUMENTED in skill |
| `data[].license.id` | uuid | nullable | N | M | `distru_locations.distru_license_id` | column | line 121; overrides flat `license_id` when present |
| `data[].license.license_number` | string | nullable | N | M | `distru_locations.license_number` | column | line 120; matches `metrc_facilities.license_recreational/medical` → `metrc_facility_id` (line 124) |
| `data[].deleted_at` | iso datetime | nullable | N | M | `distru_locations.deleted_at` | column (softDeletes) | line 128; only surfaced when `deleted=include` |

### Gaps
- No U gaps. Doc drift: `license`/`license_id`/`deleted_at` are load-bearing in importer but absent from `categories/crm.md` Location shape. Recommend updating skill.

---

## /strains

**Wrapper:** `DistruApi::get_strains()` (DistruApi.php:634)
**Importer:** `ReferenceDataImporter::import_strains()` at line 166
**Native target:** `distru_strains`
**Page cap:** 50,000 (largest in API)
**Filters supported:** `inserted_datetime`, `updated_datetime`, `name`, `type`, `page[number]`
**Filters we send:** none (full fetch)
**Raw payload retained:** YES

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `distru_strains.distru_id` | column | line 183 |
| `data[].name` | string | req | Y | M | `distru_strains.name` | column | line 201; default `'Unknown'` |
| `data[].type` | string | nullable | Y | **U** | — | none | **GAP** — Docs say `type`; importer reads `strain_type` (line 202). Either skill is wrong or importer is reading a non-existent field. Verify via Phase 1 Tinker probe. |
| `data[].strain_type` | string | nullable | N | M | `distru_strains.strain_type` | column | line 202; UNDOCUMENTED key |
| `data[].metrc_strain_id` | string | nullable | Y | R | `distru_strains.raw_payload` | raw_payload | Useful for Metrc cross-ref; consider promoting to column |
| `data[].thc_lower` | decimal | nullable | Y | R | `distru_strains.raw_payload` | raw_payload | |
| `data[].thc_upper` | decimal | nullable | Y | R | `distru_strains.raw_payload` | raw_payload | |
| `data[].cbd_lower` | decimal | nullable | Y | R | `distru_strains.raw_payload` | raw_payload | |
| `data[].cbd_upper` | decimal | nullable | Y | R | `distru_strains.raw_payload` | raw_payload | |
| `data[].inserted_datetime` | iso datetime | req | Y | R | `distru_strains.raw_payload` | raw_payload | No parsed column |
| `data[].updated_datetime` | iso datetime | req | Y | R | `distru_strains.raw_payload` | raw_payload | No parsed column; no incremental sync |

### Gaps
- `data[].type` (U) — Resolve `type` vs `strain_type` drift via Tinker probe.
- `data[].metrc_strain_id` (R) — Promote to indexed column to mirror Location's `metrc_facility_id` cross-ref pattern.
- Cannabinoid range fields (R) — Useful for Products domain projection; consider column promotion or document deferral.
- Timestamps (R) — Add `distru_inserted_datetime`/`distru_updated_datetime` columns mirroring `distru_menus` to enable incremental sync without backfill.

---

## /menus

**Wrapper:** `DistruApi::get_menus()` (DistruApi.php:652)
**Importer:** `ReferenceDataImporter::import_menus()` at line 220
**Native target:** `distru_menus`
**Page cap:** 500
**Filters supported:** disagreement between skill files — OpenAPI says datetime + boolean filters; category file says "No datetime filters". Verify via Phase 1.
**Filters we send:** none (fetch-all + diff per importer line 215)
**Raw payload retained:** YES

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `distru_menus.distru_id` | column | line 227 |
| `data[].name` | string | req | Y | **U** | — | none | **GAP** — Skill documents `name`; importer reads `internal_name` + `external_name`. Wire shape differs from skill. |
| `data[].is_published` | boolean | req | Y | R | `distru_menus.raw_payload` | raw_payload | |
| `data[].is_active` | boolean | req | Y | **U** | — | none | **GAP** — Skill says `is_active`; importer reads `active` (line 248). Naming drift. |
| `data[].inserted_datetime` | iso datetime | req | Y | M | `distru_menus.distru_inserted_datetime` | column | line 250 |
| `data[].updated_datetime` | iso datetime | req | Y | M | `distru_menus.distru_updated_datetime` | column | line 251 |
| `data[].internal_name` | string | nullable | N | M | `distru_menus.internal_name` | column | line 245; UNDOCUMENTED |
| `data[].external_name` | string | nullable | N | M | `distru_menus.external_name` | column | line 246; UNDOCUMENTED |
| `data[].visibility` | string | nullable | N | M | `distru_menus.visibility` | column | line 247; PUBLIC/PRIVATE/PASSCODE_PROTECTED |
| `data[].active` | boolean | nullable | N | M | `distru_menus.active` | column | line 248; UNDOCUMENTED |
| `data[].product_count` | integer | nullable | N | M | `distru_menus.product_count` | column | line 249; UNDOCUMENTED |

### Gaps
- `name`/`is_active` (U) — Wire shape clearly differs from skill. Phase 1 Tinker probe will confirm whether `name`/`is_active` exist at all. Skill update required either way.
- Reconcile filter list between category file and OpenAPI schema.

---

## /users

**Wrapper:** `DistruApi::get_users()` (DistruApi.php:642)
**Importer:** `ReferenceDataImporter::import_users()` at line 270 + `wire_distru_users_to_staffmembers()` at line 455
**Native target:** `distru_users` mirror + projection to `staff_members` keyed by email + optional auto-link to `users.id`
**Page cap:** 1,000
**Filters supported:** `inserted_datetime`, `updated_datetime`, `email`, `page[number]`, `deleted` (tri-state)
**Filters we send:** `deleted=include`
**Raw payload retained:** YES

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `distru_users.distru_id` | column | line 287 |
| `data[].full_name` | string | nullable | Y | M | `distru_users.full_name` + `staff_members.display_name` | column | line 308, 470 |
| `data[].email` | string | nullable | Y | M | `distru_users.email` | column | line 309; indexed; StaffMember upsert key (line 477); User auto-link (line 510) |
| `data[].role` | object `{id,name}` | nullable | Y (as string) | P | sub-fields below | composite | Docs say `role` is free-text string; wire is `{id,name}`. Drift. |
| `data[].role.id` | uuid | nullable | N | M | `distru_users.role_id` | column | line 310 |
| `data[].role.name` | string | nullable | N | M | `distru_users.role_name` | column | line 311 |
| `data[].banned` | boolean | req | Y | M | `distru_users.banned` | column | line 312 |
| `data[].deleted_at` | iso datetime | nullable | Y | M | `distru_users.deleted_at` | column (softDeletes) | line 295; `_at` suffix (not `_datetime`) |

### Gaps
- No U gaps. Doc drift: `role` shape (string vs object) — update skill.

---

## /payment-methods

**Wrapper:** `DistruApi::get_payment_methods()` (DistruApi.php:662)
**Importer:** `ReferenceDataImporter::import_payment_methods()` at line 331
**Native target:** `distru_payment_methods`
**Page cap:** 5,000
**Filters supported:** `inserted_datetime`, `updated_datetime`, `is_active`, `page[number]`, `deleted` (tri-state)
**Filters we send:** `deleted=include`
**Raw payload retained:** YES

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `distru_payment_methods.distru_id` | column | line 348 |
| `data[].name` | string | req | Y | M | `distru_payment_methods.name` | column | line 368; default `'Unnamed'` |
| `data[].is_active` | boolean | req | Y | R | `distru_payment_methods.raw_payload` | raw_payload | Consider promoting to column |
| `data[].inserted_datetime` | iso datetime | req | Y | R | `distru_payment_methods.raw_payload` | raw_payload | |
| `data[].updated_datetime` | iso datetime | req | Y | R | `distru_payment_methods.raw_payload` | raw_payload | |
| `data[].deleted_at` | iso datetime | nullable | N | M | `distru_payment_methods.deleted_at` | column (softDeletes) | line 355; UNDOCUMENTED |

### Gaps
- `is_active` (R) — Promote so downstream payment write-back can filter active-only methods without JSON extraction.
- Timestamps (R) — Mirror `distru_menus` pattern; enable incremental sync.

---

## /companies

**Wrapper:** `DistruApi::get_companies()` (DistruApi.php:493)
**Importer:** `CustomerImporter::import_companies()` (CustomerImporter.php:164) → `process_company_record()` (line 205)
**Native target:** `customers` + `vendors` (routed by `relationship_type` via `distru_relationship_type_mappings`) + `integration_company_mappings` (BOTH-routed bridge) + `customer_facilities` pivot
**Page cap:** 5,000
**Filters supported:** `inserted_datetime`, `updated_datetime`, `name`, `license_number`, `tags[]`, `deleted` (tri-state). NO `relationship_type` filter (silently ignored).
**Filters we send:** `deleted=include` only (line 179)
**Raw payload retained:** YES — `external_ids->'distru_raw_payload'`

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `customers/vendors.external_ids->distru_company_id` | external_ids | dedupe key; CustomerImporter.php:740, 1198 |
| `data[].name` | string | req | Y | M | `customers/vendors.name` | column | line 768, 1228 |
| `data[].legal_business_name` | string | opt | N | M | `customers/vendors.legal_business_name` | column | line 769, 1229 |
| `data[].dba` | string | opt | Y | **U** | — | raw_payload only | **GAP** — Documented; never read |
| `data[].relationship_type` | object | req | Y | P | routing decision | external_ids | tenant-customizable |
| `data[].relationship_type.id` | uuid | req | Y | M | `external_ids->distru_relationship_type_id` | external_ids | line 741, 1199 |
| `data[].relationship_type.name` | string | req | Y | M | `external_ids->distru_relationship_type_name` | external_ids | line 744, 1202 |
| `data[].category` | string | opt | N | P | `customers.group_name` fallback / `vendors.external_ids->distru_category` | column / external_ids | line 772, 1212 |
| `data[].group` | object | opt | N | P | wins over `category` for group_name | external_ids | line 737, 1195 |
| `data[].group.id` | uuid | opt | N | M | `external_ids->distru_group_id` | external_ids | line 748, 1206 |
| `data[].group.name` | string | opt | N | M | `customers.group_name` | column | line 770-772 |
| `data[].owner_id` | uuid | opt | N | M | `external_ids->distru_owner_id` + resolves to `customers.staff_member_id/assigned_to/assigned_rep` | column + external_ids | line 747, 764, 1205 |
| `data[].phone_number` | string | opt | N (skill says `phone`) | M | `customers/vendors.phone` | column | line 773, 1230; **drift** |
| `data[].website` | string | opt | N | M | `customers.website` / `vendors.website_url` | column | line 774, 1231 |
| `data[].default_email` | string | opt | N (skill says `primary_email`) | M | `customers/vendors.email` | column | line 756, 1220; **drift** |
| `data[].sales_order_email` | string | opt | N | M | `customers/vendors.sales_order_email` | column | line 757, 1221 |
| `data[].purchase_order_email` | string | opt | N | M | `customers/vendors.purchase_order_email` | column | line 758, 1222 |
| `data[].invoice_email` | string | opt | N (skill says `billing_email`) | M | `customers/vendors.invoice_email` | column | line 759, 1223; **drift** |
| `data[].order_shipment_email` | string | opt | N (skill says `shipping_email`) | M | `customers/vendors.order_shipment_email` | column | line 760, 1224; **drift** |
| `data[].emails` | string | opt | Y | **U** | — | raw_payload only | **GAP** — Documented aggregate; never read |
| `data[].additional_emails` | string | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].additional_phones` | string | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].default_sales_order_notes` | string | opt | N | M | `default_sales_order_notes` | column | line 780, 1237 |
| `data[].default_purchase_order_notes` | string | opt | N | M | `default_purchase_order_notes` | column | line 781, 1238 |
| `data[].credit_limit` | decimal | opt | Y | **U** | — | raw_payload only | **GAP** — financial field documented but dropped |
| `data[].outstanding_balance_threshold` | int cents | opt | Y | M | `outstanding_balance_threshold` | column | line 782, 1239 |
| `data[].primary_contact` | object | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].primary_billing_location` | object | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].primary_shipping_location` | object | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].primary_license_holder` | string | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].tags` | array<string> | opt | Y | **U** | — | raw_payload only | **GAP** — tag taxonomy lost |
| `data[].inserted_datetime` | iso | req | Y | M | `business_partners.created_at` | column + raw_payload | Ranked FIRST for `created_at` (earlier-only) since 2026-09-01; live 830/830 Evo companies carry it. Still not a sync watermark |
| `data[].updated_datetime` | iso | req | Y | U | — | raw_payload only | No incremental filter sent |
| `data[].deleted_at` | iso | opt | N | M | `customers/vendors.deleted_at` | column | line 1267 |
| `data[].licenses[]` | array<object> | opt | Y | P | first → `license_number`; full array stashed | external_ids | line 749, 928, 1213 |
| `data[].licenses[].id` | uuid | req | Y | R | preserved in distru_licenses array | external_ids | not indexed |
| `data[].licenses[].license_number` | string | req | Y | M | `customers/vendors.license_number` + `license_type` derivation + facility resolution | column | line 763, 940, 1246; only first non-null wins |
| `data[].licenses[].license_type` | string | opt | Y | **U** | — | external_ids | **GAP** — Distru-supplied type discarded; importer derives from prefix instead |
| `data[].licenses[].license_expiration_date` | iso | opt | Y | R | preserved in distru_licenses array | external_ids | No expiry tracking column |
| `data[].licenses[].metrc_facility_license` | string | opt | Y | R | preserved in distru_licenses array | external_ids | Not used (importer uses license_recreational/medical) |
| `data[].locations[]` | array<object> | opt | Y | P | first/Shipping-named → primary address; license-matched → `customer_facilities` pivot | column + pivot | line 820, 1291 |
| `data[].locations[].id` | uuid | req | Y | R | preserved in raw_payload | external_ids | |
| `data[].locations[].name` | string | opt | Y | P | used to detect "Shipping" preference | — | line 836; not persisted |
| `data[].locations[].address` | string (flat) | opt | Y | M | `customers.address/city/state/zipcode/unit_number` via `parse_us_address` | column | line 844 |
| `data[].locations[].company_id` | uuid | opt | Y | U | — | raw_payload only | Redundant with parent |
| `data[].locations[].is_shipping` | bool | opt | Y | **U** | — | raw_payload only | **GAP** — Importer detects via name substring, not this flag |
| `data[].locations[].is_billing` | bool | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].locations[].is_archived` | bool | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].locations[].license` | object | opt | N | P | `license.license_number` → `customer_facilities.metrc_facility_id` resolution | pivot | line 1304 |
| `data[].locations[].license.license_number` | string | opt | N | M | drives `customer_facilities` pivot creation | pivot | line 1305 |
| `data[].custom_data[]` | array<object> | opt | Y | P | array preserved; definitions recorded for admin review | external_ids + sighting table | WU-13 |

### Gaps
- `dba` (U) — Recommend `customers.dba` column or `external_ids->distru_dba`
- `emails` / `additional_emails` / `additional_phones` (U) — Parse into structured contact-list or stash to `external_ids`
- `credit_limit` (U) — Recommend `customers.credit_limit` decimal column
- `primary_*` refs (U) — Leverage these to remove "first or shipping-named location" heuristic
- `tags[]` (U) — Import into polymorphic tags table or `external_ids->distru_tags`
- `updated_datetime` (U) — Wire incremental sync to halve API load
- `locations[].is_shipping/is_billing/is_archived` (U) — Replace name-substring heuristic with flag-based logic
- `licenses[].license_type` (U) — Prefer Distru-supplied type, fall back to derivation
- Field-naming drift: `phone_number`/`default_email`/`invoice_email`/`order_shipment_email` (wire) vs `phone`/`primary_email`/`billing_email`/`shipping_email` (skill) — update skill

---

## /contacts

**Wrapper:** `DistruApi::get_contacts()` (DistruApi.php:501)
**Importer:** `CustomerImporter::import_contacts()` (CustomerImporter.php:1382)
**Orchestration:** ✅ VERIFIED INVOKED. `DistruImportService::run_entity_import()` dispatches `'contacts'` at line 471. The "wired but never invoked" claim in the original audit plan was **incorrect** — see Appendix A.
**Native target:** `customer_contacts` + `customer_contact` m2m pivot
**Page cap:** 1,000
**Filters supported:** `inserted_datetime`, `updated_datetime`, `company_id`, `email` (substring), `tags[]`, `deleted` (tri-state)
**Filters we send:** `deleted=include` only
**Raw payload retained:** YES — `external_ids->'distru_raw_payload'` (line 1478)

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `customer_contacts.distru_id` | column | line 1417, 1447 |
| `data[].first_name` | string | req | Y | M | `customer_contacts.first_name` | column | line 1482; default `'Unknown'` |
| `data[].last_name` | string | opt | Y | M | `customer_contacts.last_name` | column | line 1483 |
| `data[].full_name` | string | server-derived | Y | U | — | raw_payload only | Correctly skipped (server-derived) |
| `data[].email` | string | opt | Y | M | `customer_contacts.email` | column | line 1484 |
| `data[].phone_number` | string | opt | N (skill says `phone`) | M | `customer_contacts.phone` | column | line 1485; **drift** |
| `data[].work_phone_number` | string | opt | N | M | `customer_contacts.work_phone` | column | line 1488 |
| `data[].title` | string | opt | Y | M | `customer_contacts.role` | column | line 1491; also pivot `role_at_customer` |
| `data[].description` | string | opt | N (skill says `notes`) | M | `customer_contacts.description` | column | line 1492; **drift** |
| `data[].department` | string | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].birthdate` | iso | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].anniversary_date` | iso | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].notes` | string | opt | Y | **U** | — | raw_payload only | **GAP** — Skill calls field `notes` but importer reads `description`. Verify which exists. |
| `data[].driver_license_number` | string | opt | N | M | `customer_contacts.driver_license_number` | column | line 1493 |
| `data[].driver_license_issuing_state` | string | opt | N | M | `customer_contacts.driver_license_state` | column | line 1494 |
| `data[].company` | object | opt | Y | P | pivot to `customers.id` | pivot | line 1586 |
| `data[].company.id` | uuid | req | Y | M | pivot to `customers.id` via cached map | pivot | line 1588 |
| `data[].companies[]` | array<object> | opt | N | P | iterates for multi-company pivot | pivot | line 1573 (forward-compat) |
| `data[].companies[].id` | uuid | req | N | M | each → pivot row | pivot | line 1579 |
| `data[].owner` | object | opt | N | P | only id read | external_ids | line 1473 |
| `data[].owner.id` | uuid | opt | N | M | `external_ids->distru_owner_id` | external_ids | line 1476 |
| `data[].tags` | array<string> | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].inserted_datetime` | iso | req | Y | U | — | raw_payload only | Not used as watermark. Live 2026-09-01: 454/454 Evo contacts carry it (and `updated_datetime`) |
| `data[].updated_datetime` | iso | req | Y | U | — | raw_payload only | No incremental |
| `data[].deleted_at` | iso | opt | N | M | `customer_contacts.deleted_at` | column | line 1509 |
| `data[].custom_data[]` | array<object> | opt | Y | P | array preserved; definitions recorded | external_ids + sighting table | line 1425, 1477 |

### Gaps
- `department`, `birthdate`, `anniversary_date` (U) — Recommend columns or `external_ids->distru_*`
- `notes` (U) — Resolve `notes` vs `description` field-name drift via Phase 1
- `tags[]` (U) — Same recommendation as companies
- `updated_datetime` (U) — Wire incremental sync
- Importer fetches aggregate (`get_contacts(...)`) not streamed — for 5k+ contact tenants, switch to `stream_with_progress` pattern

---

## /products

**Wrapper:** `DistruApi::get_products()` (DistruApi.php:511) via `ProgressTrackingStreamer::stream_with_progress` (ProductImporter.php:223)
**Importer:** `ProductImporter::import()` (line 211) → `process_product_record()` (line 370) → cannabis (line 410) or non-cannabis (line 475) paths
**Native target:** `products` (cannabis) OR `non_metrc_items` (non-cannabis); side-effects on `brands`, `product_categories`, `product_subcategories`, `product_lines`, `strains`, `vendors`, `product_metrc_mappings`
**Page cap:** 5,000 (advisory; endpoint ignores `page[size]`)
**Filters supported:** `inserted_datetime`, `updated_datetime`, `name`, `sku`, `upc`, `brand_id[]`, `category_id[]`, `vendor_id[]`, `tags[]`, `deleted`, `menu_id` (comma-string), `compliance_type`, `metrc_item_category`, `page[number]`
**Filters we send:** `deleted=include` only (line 230)
**Raw payload retained:** YES — `external_ids->'distru_raw_payload'`

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `products/non_metrc_items.distru_product_id` | column + raw_payload | primary cross-ref; line 371, 454, 498 |
| `data[].name` | string | req | Y | M | `products/non_metrc_items.name` | column | line 559, 839 |
| `data[].sku` | string | opt | Y | M | `products/non_metrc_items.sku` | column | line 560, 841 |
| `data[].upc` | string | opt | Y | D | — | raw_payload | Never read; no native upc column |
| `data[].external_name` | string | opt | N | M | `products/non_metrc_items.external_name` | column | line 561, 840 |
| `data[].is_active` | boolean | req | Y | P | `products.archived` (inverted) + `listing_state` | derived + raw_payload | true→Available, false→Internal |
| `data[].is_archived` | boolean | opt | Y | **U** | — | raw_payload only | **GAP** — `listing_state='Archived'` derives from `deleted_at`, not this |
| `data[].tags` | string[] | opt | Y | **U** | — | raw_payload only | **GAP** — tag taxonomy lost |
| `data[].deleted_at` | iso | opt | N | M | `products/non_metrc_items.deleted_at` (SoftDeletes) | column | line 422, 456 |
| `data[].updated_datetime` | iso | req | Y | M | `updated_at` | column | line 423, 455 |
| `data[].inserted_datetime` | iso | req | Y | M | `products/non_metrc_items.created_at` | column + raw_payload | Ranked FIRST for `created_at` (earlier-only), `updated_datetime` fallback — fixed 2026-09-01; live 4,563/4,563 Evo products carry it |
| `data[].creator` | DistruUser | req | N (added 2026) | D | — | raw_payload | Who created the product — live 2026-09-01 4,563/4,563; not yet surfaced natively |
| `data[].owner` | DistruUser | req | N (added 2026) | D | — | raw_payload | Assigned owner — same probe |
| `data[].vendor.id` | uuid | opt | Y | M | `vendors.external_ids->distru_company_id` / `non_metrc_items.preferred_vendor_id` | external_ids/column | line 961, 998 |
| `data[].vendor.name` | string | opt | Y | M | `vendors.name` / `non_metrc_items.vendor` | column | line 526, 577 |
| `data[].vendor.updated_datetime` | iso | opt | (impl) | D | — | raw_payload | |
| `data[].brand.id` | uuid | opt | Y | M | `brands.distru_brand_id`; gates cannabis routing | column | line 884, 897 |
| `data[].brand.name` | string | opt | Y | M | `brands.name` / `non_metrc_items.brand_name` | column | line 546, 562, 905 |
| `data[].brand.updated_datetime` | iso | opt | Y | D | — | raw_payload | `brands` has no external_modified_at |
| `data[].category.id` | uuid | opt | Y | M | `product_categories.distru_category_id` / `products.product_category_id` | column | line 1019, 1031 |
| `data[].category.name` | string | opt | Y | M | `product_categories.name` + `.slug` / `non_metrc_items.category` | column | line 389, 533, 564 |
| `data[].category.type` | string | opt | N | M | `product_categories.distru_type` | column | line 1048; UNDOCUMENTED |
| `data[].category.updated_datetime` | iso | opt | Y | D | — | raw_payload | |
| `data[].subcategory.id` | uuid | opt | Y | M | `product_subcategories.distru_subcategory_id` / `products.product_subcategory_id` | column | line 1085, 1097 |
| `data[].subcategory.name` | string | opt | Y | M | `product_subcategories.name` + `.slug` | column | line 1086, 1128 |
| `data[].subcategory.updated_datetime` | iso | opt | (impl) | D | — | raw_payload | |
| `data[].product_line` | object | opt | Y | **U** | — | raw_payload only | **GAP** — Skill documents separate from `product_group`; importer only resolves `product_group`. Verify both exist via Phase 1. |
| `data[].product_group.id` | uuid | opt | Y | M | `product_lines.distru_group_id` / `products.product_line_id` | column | line 1150, 1162 |
| `data[].product_group.name` | string | opt | Y | M | `product_lines.name` | column | line 1151, 1182 |
| `data[].product_group.updated_datetime` | iso | opt | (impl) | D | — | raw_payload | |
| `data[].strain.id` | uuid | opt | Y | M | `strains.distru_strain_id` | column | line 1207, 1221 |
| `data[].strain.name` | string | opt | Y | M | `strains.name` + `.slug` / `products.strain_name` | column | line 847, 1208 |
| `data[].strain.strain_type` | enum | opt | Y | M | `products.strain_classification` (lowercased) | column | line 848, 1272 |
| `data[].primary_test_result` | object | opt | Y | **U** | — | raw_payload only | **GAP** — Embedded summary not surfaced; TestResultImporter uses standalone endpoint |
| `data[].wholesale_price` | decimal-string | opt | Y | D | — | raw_payload | **DRIFT** — Skill says `wholesale_price`; wire is `unit_price` |
| `data[].unit_price` | decimal-string | opt | N (wire) | M | `products.wholesale_price` (cents) | column | line 787, 850 |
| `data[].msrp` | decimal-string | opt | Y | M | `products.retail_price` (cents) | column | line 784, 851 |
| `data[].unit_cost` | decimal-string | opt | N (wire) | M | `products.cost_of_goods_sold` (cents) / `non_metrc_items.cost_per_unit` (decimal) | column | line 516, 790, 852 |
| `data[].case_quantity` | int | opt | Y | D | — | raw_payload | Skill name; wire uses `units_per_case` |
| `data[].units_per_case` | int | opt | N (wire) | M | `products.unit_multiplier` + `base_units_per_unit` | column | line 821 |
| `data[].unit_size` | decimal-string | opt | Y | **U** | — | raw_payload only | **GAP** — Closest native is `unit_weight` which reads `unit_net_weight` instead |
| `data[].unit_net_weight` | decimal-string | opt | N (wire) | M | `products.unit_weight` | column | line 827, 855 |
| `data[].unit_serving_size` | numeric | opt | N (wire) | M | `products.serving_size` | column | line 834, 856 |
| `data[].unit_type.id` | uuid | opt | (impl) | D | — | raw_payload | |
| `data[].unit_type.name` | string | opt | (impl) | M | `products.unit_of_measure` | column | line 621, 1287 |
| `data[].compliance_type` | enum | req | Y | **U** | — | raw_payload only | **GAP** — METRC/BIOTRACK/NONE never read; cannabis routing uses heuristic instead |
| `data[].metrc_item_name` | string | opt | Y | **U** | — | raw_payload only | **GAP** — Distru's Metrc-item hint unused by ProductMetrcAutoMapper |
| `data[].metrc_item_category` | string | opt | Y | **U** | — | raw_payload only | **GAP** — Same |
| `data[].image_urls` | string[] | opt | Y | **U** | — | raw_payload only | **GAP** — Never copied to `product_images` |
| `data[].description` | string | opt | Y | M | `description` | column | line 563, 842 |
| `data[].internal_notes` | string | opt | Y | **U** | — | raw_payload only | **GAP** — No native column |
| `data[].quantities.*` | object | opt | Y | D | — | raw_payload | Intentional — Metrc-authoritative |
| `data[].menus` | array of `{menu_id,menu_name}` | opt | Y | R | `external_ids->'distru_menus'` | external_ids | line 1304; feeds storefront Distru-menu visibility (apply + post-import refresh) |
| `data[].menu_visibility` | string enum | opt | Y | M | `external_ids->'distru_menu_visibility'` | external_ids | DO_NOT_INCLUDE / INCLUDE_IN_ALL / INCLUDE_IN_SELECT; PRESENT ON READS (live probe 2026-08-31 vs Evo — earlier audit passes missed it); INCLUDE_IN_ALL means `menus[]` is not authoritative |
| `data[].custom_data` | array | opt | Y | R | `distru_custom_field_definitions` (sightings) | `external_ids->'distru_custom_fields'` | line 409, 1321 |

### Gaps
- `is_archived` (U) — OR into `listing_state='Archived'` decision
- `tags[]` (U) — Add tags column or side table
- `compliance_type` (U) — Use as authoritative cannabis-routing signal, remove brand/strain heuristic
- `metrc_item_name` + `metrc_item_category` (U) — Add to ProductMetrcAutoMapper matching tiers
- `image_urls` (U) — Surface to `product_images`
- `internal_notes` (U) — Add column or merge to description
- `primary_test_result` (U) — Decide whether to populate `primary_test_result_*` columns
- `product_line` (U) — Verify against Phase 1; if exists, route to native or merge with product_group
- Field-naming drift: skill `wholesale_price`/`case_quantity`/`unit_size` vs wire `unit_price`/`units_per_case`/`unit_net_weight` — update skill
- ~~`inserted_datetime` should write to `created_at` instead of `now()`~~ DONE 2026-09-01 (ranked first, earlier-only, in both ProductImporter arms)
- `creator` / `owner` (D) — now on the wire; a `created_by` surface for Distru-sourced products is possible
- `*.updated_datetime` on brand/category/subcategory/product_group — add `external_modified_at` columns

---

## /test-results

**Wrapper:** `DistruApi::get_test_results()` (DistruApi.php:522) via streamer
**Importer:** `TestResultImporter::import()` (line 121) → `process_test_result_record()` (line 183) → `upsert_distru_test_result()` (line 213); `propagate_primary_to_packages()` (line 272)
**Native target:** `distru_test_results` (canonical mirror); side-effect on `distru_packages.primary_test_result_*` (9 columns when `is_primary=true`)
**Page cap:** 5,000
**Filters supported:** `inserted_datetime`, `updated_datetime`, `package_id[]`, `product_id[]`, `page[number]`
**Filters we send:** none (full-mirror); per importer line 50-52 the `package_id`/`batch_id` filters don't actually work server-side despite OpenAPI listing them
**Raw payload retained:** YES — `distru_test_results.raw_payload`

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `distru_test_results.distru_id` | column + raw_payload | line 184, 250 |
| `data[].name` | string | opt | N (wire) | M | `distru_test_results.name` + propagated to `distru_packages.primary_test_result_name` | column + raw_payload | line 215, 314 |
| `data[].lab_name` | string | opt | Y | M | `distru_test_results.lab_name` | column + raw_payload | line 216 |
| `data[].lab_license_number` | string | opt | N (wire) | M | `distru_test_results.lab_license_number` | column + raw_payload | line 217; **DRIFT** — skill says `license_number` |
| `data[].license_number` | string | opt | Y (skill) | U | — | raw_payload only | If wire emits, goes unread — verify via Phase 1 |
| `data[].metrc_lab_test_id` | string | opt | Y | **U** | — | raw_payload only | **GAP** — Cross-ref ID never read |
| `data[].release_date` | iso date | opt | N (wire) | M | `distru_test_results.release_date` | column + raw_payload | line 218, 408; **DRIFT** — skill says `result_datetime` |
| `data[].result_datetime` | iso | opt | Y (skill) | U | — | raw_payload only | If wire emits, goes unread |
| `data[].expiration_datetime` | iso | opt | Y | **U** | — | raw_payload only | **GAP** — COA expiry UI blocked |
| `data[].sample_id` | string | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].package_id` | uuid | opt | Y | M | `distru_test_results.package_id` (propagation routing) | column + raw_payload | line 235, 275 |
| `data[].batch_id` | uuid | opt | N (wire) | M | `distru_test_results.batch_id` (propagation via batch_number) | column + raw_payload | line 236, 281-290 |
| `data[].product_id` | uuid | opt | Y (skill) | **U** | — | raw_payload only | **GAP** — Cannot back-link to product without raw scan |
| `data[].is_primary` | boolean | req | N (wire) | M | `is_primary` + drives 9-column propagation | column + raw_payload | line 198, 219, 272 |
| `data[].mg_per_unit_type` | string | opt | N (wire) | M | `mg_per_unit_type` + propagated | column + raw_payload | line 220 |
| `data[].potency_thc` | decimal-string | opt | Y (skill) | U | — | raw_payload only | **DRIFT** — wire emits granular set below |
| `data[].potency_cbd` | decimal-string | opt | Y (skill) | U | — | raw_payload only | Same |
| `data[].potency_total_cannabinoids` | decimal-string | opt | Y (skill) | U | — | raw_payload only | Same |
| `data[].thc_percentage` | decimal-string | opt | N (wire) | M | `thc_percentage` + `primary_test_result_thc_percentage` | column + raw_payload | line 225 |
| `data[].total_thc_percentage` | decimal-string | opt | N (wire) | M | `total_thc_percentage` + `primary_test_result_thc_percentage_total` | column + raw_payload | line 226 |
| `data[].thc_mg_per_unit` | decimal-string | opt | N (wire) | M | `thc_mg_per_unit` + `primary_test_result_thc_mg_per_unit` | column + raw_payload | line 227 |
| `data[].total_thc_mg_per_unit` | decimal-string | opt | N (wire) | M | `total_thc_mg_per_unit` + `primary_test_result_thc_mg_per_unit_total` | column + raw_payload | line 228 |
| `data[].cbd_percentage` | decimal-string | opt | N (wire) | M | `cbd_percentage` + `primary_test_result_cbd_percentage` | column + raw_payload | line 229 |
| `data[].total_cbd_percentage` | decimal-string | opt | N (wire) | M | `total_cbd_percentage` + `primary_test_result_cbd_percentage_total` | column + raw_payload | line 230 |
| `data[].cbd_mg_per_unit` | decimal-string | opt | N (wire) | M | `cbd_mg_per_unit` + `primary_test_result_cbd_mg_per_unit` | column + raw_payload | line 231 |
| `data[].total_cbd_mg_per_unit` | decimal-string | opt | N (wire) | M | `total_cbd_mg_per_unit` + `primary_test_result_cbd_mg_per_unit_total` | column + raw_payload | line 232 |
| `data[].moisture_content` | decimal-string | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].water_activity` | decimal-string | opt | Y | **U** | — | raw_payload only | **GAP** |
| `data[].passed_test` | boolean | opt | Y | **U** | — | raw_payload only | **GAP** — PASS/FAIL primary use case unavailable |
| `data[].test_status` | string | opt | Y | **U** | — | raw_payload only | **GAP** — Same |
| `data[].additional_test_results` | object (open map, ~300 keys) | opt | Y | M | `additional_test_results` JSON | column + raw_payload | line 241, 379; values stay STRING decimals; terpenes/pesticides/heavy metals preserved |
| `data[].updated_datetime` | iso | req | Y | M | `distru_updated_datetime` | column + raw_payload | line 243 |
| `data[].inserted_datetime` | iso | req | Y | M | `distru_test_results.created_at` | column + raw_payload | Second-ranked after `release_date` (earlier-only) since 2026-09-01; live 4,297/4,297 Evo results carry it |

### Gaps
- `metrc_lab_test_id` (U) — Promote to indexed column for Metrc COA reconciliation
- `product_id` (U) — Add column + back-link from products to COAs
- `sample_id` + `expiration_datetime` (U) — Useful for COA expiry UI
- `passed_test` + `test_status` (U) — Primary use case for COAs; promote to boolean + string columns
- `moisture_content` + `water_activity` (U) — Mirror the THC/CBD column pattern
- ~~`inserted_datetime` should write to `created_at`~~ DONE 2026-09-01 (after `release_date`, before the `updated_datetime` proxy)
- Skill drift: `license_number`/`result_datetime`/`potency_*` (skill) vs `lab_license_number`/`release_date`/granular set (wire) — update skill

---

## /product-pos-mappings

**Wrapper:** `DistruApi::get_product_pos_mappings()` (DistruApi.php:533) via streamer
**Importer:** `ProductImporter::import_product_pos_mappings()` (line 641) → `extract_pos_columns()` (line 1341) → `project_pos_mapping_onto_product()` (line 1403)
**Native target:** `distru_product_pos_mappings` (canonical mirror, 7 polymorphic columns); side-effects on `products.dutchie_product_id` (DUTCHIE only) and `products.external_ids->'distru_pos_mappings'`
**Page cap:** 5,000 (advisory; can return millions on POS-heavy tenants)
**Filters supported:** `page[number]`, `page[size]`, per-POS filter params (`blaze_retailer_id`, etc.)
**Filters we send:** none (full-mirror)
**Raw payload retained:** YES — `distru_product_pos_mappings.raw_payload` + mirrored into `products.external_ids->'distru_pos_mappings'`

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | **INTEGER** | req | Y | M | `distru_product_pos_mappings.distru_id` | column + raw_payload | line 697, 719; **ONLY integer id in API** |
| `data[].product_id` | uuid | req | Y | M | `distru_product_pos_mappings.product_id` (FK) | column + raw_payload | line 698, 707; skipped if product missing |
| `data[].pos_type` | string | req | Y | M | `distru_product_pos_mappings.pos_type` | column + raw_payload | line 699; polymorphic discriminator |
| `data[].external_id` | string | req (skill) | Y | **U** | — | raw_payload only | **GAP** — Skill base shape claims this field; importer never reads it. Verify via Phase 1. |
| `data[].inserted_at` | iso | req | Y | M | `distru_inserted_at` | column + raw_payload | line 726; `_at` suffix (unique to this endpoint) |
| `data[].updated_at` | iso | req | Y | M | `distru_updated_at` | column + raw_payload | line 727 |
| **BLAZE variant** | | | | | | | |
| `data[].blaze_asset_id` | string | opt | Y | M | `blaze_asset_id` | column + raw_payload | line 1358 |
| `data[].blaze_product_id` | string | opt | Y | M | `blaze_product_id` | column + raw_payload | line 1359 |
| `data[].blaze_retailer_id` | string | opt | Y | M | `blaze_retailer_id` | column + raw_payload | line 1360 |
| **DUTCHIE variant** | | | | | | | |
| `data[].dutchie_product_id` | int-stored-as-string | opt | Y | M (dual-projected) | `distru_product_pos_mappings.dutchie_product_id` + `products.dutchie_product_id` | column + raw_payload | line 1365, 1421; **only POS id projected to products** |
| `data[].dutchie_retailer_id` | string | opt | Y | M | `dutchie_retailer_id` | column + raw_payload | line 1366 |
| **TREEZ variant** | | | | | | | |
| `data[].treez_product_id` | string | opt | Y | M (mirror only) | `treez_product_id` | column + raw_payload | line 1369; not projected to products |
| `data[].treez_retailer_id` | string | opt | Y | M (mirror only) | `treez_retailer_id` | column + raw_payload | line 1370 |
| **Other POS variants** | | | Y | D | — | raw_payload only | `default => []` (line 1372); raw kept on mirror + `products.external_ids` |
| `data[].deleted_at` | iso | opt | (impl) | **U** | — | raw_payload only | **GAP** — DELETE endpoint exists (only one in API); soft-deletes leave stale mirror rows |

### Gaps
- `external_id` (U) — Verify wire emission via Phase 1; route to generic column or update skill
- BLAZE/TREEZ projection — Add `products.blaze_*`/`products.treez_*` columns for symmetry with Dutchie
- Polymorphic dispatch — Hard-coded 3 pos_types; add logger warning when unknown pos_type observed
- `deleted_at` mirroring — Active reconciliation against live list needed; today server-side DELETE leaves stale mirror rows

---

## /batches

**Wrapper:** `DistruApi::get_batches()` (DistruApi.php:548) via streamer
**Importer:** `PackageImporter::import_batches()` (line 208) → `process_batch_record()` (line 252)
**Native target:** `distru_batches` (mirror) + fan-out to `product_batches` metadata + `product_batch_links.distru_batch_id` (cannabis)
**Page cap:** 5,000
**Filters supported:** `inserted_datetime`, `updated_datetime`, `product_id` (SINGULAR scalar), `location_id[]`, `strain_id[]`, `creation_source` (scalar), `license_number`, `include_costs`, `page[number]`
**Filters we send:** `include_costs=true`, `deleted=include`
**Raw payload retained:** YES — `distru_batches.raw_payload`

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `distru_batches.distru_id` | column + raw_payload | line 253 |
| `data[].batch_number` | string | req | Y | M | `distru_batches.batch_number` | column + raw_payload | line 288 (fallback to `name`) |
| `data[].name` | string | opt | N (alias) | M | `distru_batches.batch_number` | raw_payload | Fallback alias |
| `data[].lot_number` | string | opt | N | M | `distru_batches.lot_number` | column + raw_payload | line 289 |
| `data[].manufactured_datetime` | iso | opt | N | M | `distru_batches.manufactured_datetime` | column + raw_payload | line 290; **DRIFT** — docs say `production_datetime` |
| `data[].expiration_date` | date | opt | N (alias) | M | `distru_batches.expiration_date` | column + raw_payload | line 291; **DRIFT** — docs say `expiration_datetime` |
| `data[].description` | string | opt | N | M | `distru_batches.description` | column + raw_payload | line 292 |
| `data[].product_id` | uuid | opt | Y (via `product`) | M | `distru_batches.product_id` (resolved) | column + raw_payload | line 267 |
| `data[].product` (embed) | object | opt | Y | R | n/a | raw_payload | Only id consumed |
| `data[].license` (embed) | object | opt | Y | P | `distru_batches.metrc_facility_id` (resolution input) | raw_payload | line 271-272, 730-748 |
| `data[].license.id` | uuid | opt | Y | P | (resolution input) | raw_payload | |
| `data[].license.license_number` | string | opt | Y | P | (resolution input) | raw_payload | |
| `data[].owner_id` | string | opt | N | M | `distru_batches.distru_owner_id` | column + raw_payload | line 295 |
| `data[].deleted_at` | iso | opt | N | M | `distru_batches.deleted_at` | column + raw_payload | line 280, 297 |
| `data[].creation_source` | string | opt | Y | R | n/a | raw_payload | Documented but not mapped |
| `data[].creator` (embed) | object | opt | Y | R | n/a | raw_payload | |
| `data[].location` (embed) | object | opt | Y | R | n/a | raw_payload | License-based resolution used instead |
| `data[].strain` (embed) | object | opt | Y | R | n/a | raw_payload | |
| `data[].quantity` | decimal-string | opt | Y | R | n/a | raw_payload | |
| `data[].compliance_quantity` | decimal-string | opt | Y | R | n/a | raw_payload | |
| `data[].production_datetime` | iso | opt | Y | R | n/a | raw_payload | (alias of `manufactured_datetime`) |
| `data[].use_by_datetime` | iso | opt | Y | R | n/a | raw_payload | |
| `data[].metrc_facility_license` | string | opt | Y | R | n/a | raw_payload | |
| `data[].metrc_package_id` | string | opt | Y | R | n/a | raw_payload | |
| `data[].biotrack_id` | string | opt | Y | R | n/a | raw_payload | |
| `data[].inserted_datetime` | iso | opt | Y | R | n/a | raw_payload | |
| `data[].updated_datetime` | iso | opt | Y | R | n/a | raw_payload | |
| `data[].cost_per_unit_actual` | decimal-string | opt | Y (gated) | R | n/a | raw_payload | Gated by `include_costs=true`; not column-extracted on batches |
| `data[].cost_per_unit_default` | decimal-string | opt | Y (gated) | R | n/a | raw_payload | |
| `data[].total_cost_actual` | decimal-string | opt | Y (gated) | R | n/a | raw_payload | |
| `data[].total_cost_default` | decimal-string | opt | Y (gated) | R | n/a | raw_payload | |
| `data[].custom_data[]` | array<object> | opt | N | P | `distru_custom_field_definitions` (sightings) | raw_payload | line 261; WU-13 |

### Gaps
- No U gaps — every documented field is either mapped or retained in raw_payload. Cost fields not extracted to columns on batches (only on packages).

---

## /packages

**Wrapper:** `DistruApi::get_packages()` (DistruApi.php:562) via streamer
**Importer:** `PackageImporter::import_packages()` / `process_package_record()` / `upsert_distru_package()` (lines 329, 371, 418)
**Native target:** `distru_packages` (mirror) + `non_metrc_item_cost_layers` (non-cannabis path only)
**Page cap:** 5,000
**Filters supported:** `inserted_datetime`, `updated_datetime`, `product_ids[]`, `statuses[]` (PLURAL!), `location_id[]`, `batch_id[]`, `include_costs`, `page[number]`
**Filters we send:** `include_costs=true` only
**Raw payload retained:** PARTIAL — non-cannabis full payload retained (line 521); cannabis blanked to `[]` (line 503) to drop ~125MB bloat

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `distru_packages.distru_id` | column (always) | line 372 |
| `data[].package_id` | string | opt | Y | R/D | n/a | raw (non-c) / dropped (c) | Documented but not extracted |
| `data[].batch_number` | string | opt | N | M | `distru_packages.batch_number` | column (always) | line 436; STRING link |
| `data[].product_id` | uuid | opt | N | M | `distru_packages.distru_product_id` + resolved `product_id` | column (always) | line 419-420, 438 |
| `data[].product` (embed) | object | opt | Y | P | non_metrc_items name-match fallback | raw (non-c) / dropped (c) | line 880-883 |
| `data[].compliance_label` | string | opt | N | M | `distru_packages.compliance_label` | column (always) | line 429, 439; **CANNABIS-ROUTING KEY** |
| `data[].metrc_label` | string | opt | Y | M (non-c) / **D** (c) | `distru_packages.metrc_label` | raw (non-c) / blanked (c) | line 483 explicit NULL cannabis; line 511 non-c |
| `data[].quantity` | decimal-string | opt | Y | M (non-c) / **D** (c) | `distru_packages.quantity` | raw (non-c) / blanked (c) | line 484 / 512 |
| `data[].quantity_available` | decimal-string | opt | N | M (non-c) / **D** (c) | `quantity_available` | raw (non-c) / blanked (c) | line 485 / 513 |
| `data[].quantity_assembling` | decimal-string | opt | N | M | `quantity_assembling` | column (always) | line 442; Distru-only reservation |
| `data[].quantity_in_pending_sales` | decimal-string | opt | N | M | `quantity_in_pending_sales` | column (always) | line 443; Distru-only reservation |
| `data[].product_unit_quantity` | decimal-string | opt | N | M | `product_unit_quantity` | column (always) | line 446; Distru dual-unit |
| `data[].unit_type.id` | uuid | opt | N | M | `unit_type_id` | column (always) | line 447 |
| `data[].unit_type.name` | string | opt | N | M (non-c) / **D** (c) | `unit_of_measure` | raw (non-c) / blanked (c) | line 486 / 514 |
| `data[].product_unit_type.id` | uuid | opt | N | M | `product_unit_type_id` | column (always) | line 448 |
| `data[].product_unit_type.name` | string | opt | N | M | `dual_unit_of_measure` | column (always) | line 450 |
| `data[].dual_unit_quantity` | decimal-string | opt | N | M | `dual_unit_quantity` | column (always) | line 449 |
| `data[].cost_per_unit_actual` | decimal-string | opt | Y (gated) | M | `cost_per_unit_actual` | column (always) | line 453 |
| `data[].cost_per_unit_default` | decimal-string | opt | Y (gated) | M | `cost_per_unit_default` | column (always) | line 454 |
| `data[].total_cost_actual` | decimal-string | opt | Y (gated) | M | `total_cost_actual` | column (always) | line 455 |
| `data[].total_cost_default` | decimal-string | opt | Y (gated) | M | `total_cost_default` | column (always) | line 456 |
| `data[].license.id` | uuid | opt | N | M | `distru_license_id` | column (always) | line 459 |
| `data[].license.license_number` | string | opt | N | M (non-c) / **D** (c) | `license_number` | raw (non-c) / blanked (c) | line 492 / 520 |
| `data[].location.id` | uuid | opt | Y | M | `distru_location_id` | column (always) | line 460 |
| `data[].status` | string | opt | Y | M | `distru_packages.status` | column (always) | line 464; Open/Closed (distinct from Metrc) |
| `data[].packaged_date` | date | opt | N | M (non-c) / **D** (c) | `packaged_date` | raw (non-c) / blanked (c) | line 487 / 515 |
| `data[].harvest_date` | date | opt | N | M (non-c) / **D** (c) | `harvest_date` | raw (non-c) / blanked (c) | line 488 / 516 |
| `data[].expiration_date` | date | opt | N (alias) | M (non-c) / **D** (c) | `expiration_date` | raw (non-c) / blanked (c) | line 489 / 517 |
| `data[].lab_testing_state` | string | opt | N | M (non-c) / **D** (c) | `lab_testing_state` | raw (non-c) / blanked (c) | line 490 / 518 |
| `data[].is_trade_sample` | bool | opt | N | M (non-c) / **D** (c) | `is_trade_sample` | raw (non-c) / forced false (c) | line 491; NOT NULL column |
| `data[].batch` (embed) | object | opt | Y | R/D | n/a | raw (non-c) / dropped (c) | Only batch_number consumed |
| `data[].compliance_quantity` | decimal-string | opt | Y | R/D | n/a | raw (non-c) / dropped (c) | |
| `data[].use_by_datetime` | iso | opt | Y | R/D | n/a | raw (non-c) / dropped (c) | |
| `data[].metrc_package_id` | string | opt | Y | R/D | n/a | raw (non-c) / dropped (c) | |
| `data[].metrc_facility_license` | string | opt | Y | R/D | n/a | raw (non-c) / dropped (c) | |
| `data[].biotrack_id` | string | opt | Y | R/D | n/a | raw (non-c) / dropped (c) | |
| `data[].parent_package_id` | uuid | opt | Y | R/D | n/a | raw (non-c) / dropped (c) | Split-tracking |
| `data[].inserted_datetime` | iso | opt | Y | R/D | n/a | raw (non-c) / dropped (c) | |
| `data[].updated_datetime` | iso | opt | Y | R/D | n/a | raw (non-c) / dropped (c) | |
| `data[].deleted_at` | iso | opt | N | M | `deleted_at` | column (always) | line 427, 466 |
| `data[].primary_test_result.name` | string | opt | N | M (non-c) / **D** (c) | `primary_test_result_name` | raw (non-c) / blanked (c) | line 560 / 493 |
| `data[].primary_test_result.mg_per_unit_type` | string | opt | N | M (non-c) / **D** (c) | `primary_test_result_mg_per_unit_type` | raw (non-c) / blanked (c) | line 548 / 494 |
| `data[].primary_test_result.thc_percentage` | string | opt | N | M (non-c) / **D** (c) | `primary_test_result_thc_percentage` | raw (non-c) / blanked (c) | line 549 / 495 |
| `data[].primary_test_result.thc_mg_per_unit` | string | opt | N | M (non-c) / **D** (c) | `primary_test_result_thc_mg_per_unit` | raw (non-c) / blanked (c) | line 550 / 496 |
| `data[].primary_test_result.thc_percentage_total` | string | opt | N | M (non-c) / **D** (c) | `primary_test_result_thc_percentage_total` | raw (non-c) / blanked (c) | line 551 / 497 |
| `data[].primary_test_result.thc_mg_per_unit_total` | string | opt | N | M (non-c) / **D** (c) | `primary_test_result_thc_mg_per_unit_total` | raw (non-c) / blanked (c) | line 552 / 498 |
| `data[].primary_test_result.cbd_percentage` | string | opt | N | M (non-c) / **D** (c) | `primary_test_result_cbd_percentage` | raw (non-c) / blanked (c) | line 553 / 499 |
| `data[].primary_test_result.cbd_mg_per_unit` | string | opt | N | M (non-c) / **D** (c) | `primary_test_result_cbd_mg_per_unit` | raw (non-c) / blanked (c) | line 554 / 500 |
| `data[].primary_test_result.cbd_percentage_total` | string | opt | N | M (non-c) / **D** (c) | `primary_test_result_cbd_percentage_total` | raw (non-c) / blanked (c) | line 555 / 501 |
| `data[].primary_test_result.cbd_mg_per_unit_total` | string | opt | N | M (non-c) / **D** (c) | `primary_test_result_cbd_mg_per_unit_total` | raw (non-c) / blanked (c) | line 556 / 502 |
| `data[].is_primary_test_result` | bool | opt | N | **D** | n/a | dropped | Test status flows via distru_test_results table |
| `data[].custom_data[]` | array | opt | N | P | `distru_custom_field_definitions` (sightings) | raw (non-c) / dropped (c) | line 380 (WU-13) |

### Gaps
- No true U gaps. All cannabis "D" drops are intentional (Metrc-authoritative per class docblock). Non-cannabis path retains everything.

---

## /inventory ⚠ HIGHEST RISK ENDPOINT

**Wrapper:** `DistruApi::get_inventory(array $grouping, ...)` (DistruApi.php:595)
**Importer:** `InventoryImporter::import()` → `build_cache()` → `sweep_non_metrc_items()` + `sweep_cannabis_products()` (lines 80, 116, 143, 186)
**Native target:** **NO MIRROR TABLE.** Mutates only `non_metrc_items.current_quantity` + `non_metrc_items.cost_per_unit` and `products.cost_of_goods_sold`.
**Page cap:** 5,000 default
**Filters supported:** `grouping[]` (REQUIRED), `location_id[]`, `product_id[]`, `batch_id[]`, `strain_id[]`, `as_of_datetime`, `page[number]`
**Filters we send:** `grouping[]=PRODUCT` only (line 88)
**Raw payload retained:** **NO** — only 2 fields extracted to in-memory cache then discarded

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `product_id` | uuid | req (grouping=PRODUCT) | Y | M | (cache key only) | none | line 118; joins to `non_metrc_items.distru_product_id` / `products.distru_product_id` |
| `active` | decimal-string | req (grouping=PRODUCT) | Y | M | `non_metrc_items.current_quantity` | none (overwrite-on-import) | line 124, 157 |
| `cost_per_unit_actual` | decimal-string | req (grouping=PRODUCT) | Y | M | `non_metrc_items.cost_per_unit` + `products.cost_of_goods_sold` (cents) | none (overwrite-on-import) | line 125, 158-159, 202-203; gated `> 0` |
| `cost_default_per_unit` | decimal-string | opt | Y | **U** | — | **NONE** | **GAP** — Reversed word order from elsewhere; not consumed; no raw retention |
| `available` | decimal-string | opt | Y | **U** | — | **NONE** | **GAP** — `active - reserved`; useful for reorder math |
| `reserved` | decimal-string | opt | Y | **U** | — | **NONE** | **GAP** — reservation count |
| `pending` | decimal-string | opt | Y | **U** | — | **NONE** | **GAP** — pending-sale quantity |
| `location_id` | uuid | opt (grouping=LOCATION) | Y | U | — | none | Not requested (importer hard-codes PRODUCT grouping only) |
| `location` (embed) | object | opt | Y | U | — | none | |
| `batch_id` | uuid | opt (grouping=BATCH_NUMBER) | Y | U | — | none | |
| `batch_number` | string | opt | Y | U | — | none | |
| `package_id` | uuid | opt (grouping=PACKAGE) | Y | U | — | none | |
| `strain_id` | uuid | opt (grouping=STRAIN) | Y | U | — | none | |

### Gaps — HIGHEST PRIORITY
- **`cost_default_per_unit`** (U) — Reversed-word-order documented field; never consumed; **no retention** (no mirror table)
- **`available`** (U) — Dropped without retention. Useful for reorder math
- **`reserved`** (U) — Dropped without retention. Complement to `available`
- **`pending`** (U) — Dropped without retention. Analogue of `quantity_in_pending_sales` on packages

**Recommended fix:** Either (a) add a `distru_inventory_snapshots` mirror table (matches the pattern of every other Distru entity), or (b) promote `available`/`reserved`/`pending` to columns on `non_metrc_items` + `products` so the data survives the import without growing a new table.

Per-location/batch/strain breakdowns are deliberately scoped out (importer line 86-87 calls this future work) — not a bug, but worth documenting that no retention exists if/when grouping is expanded.

---

## /adjustments

**Wrapper:** `DistruApi::get_adjustments()` (DistruApi.php:577) via streamer
**Importer:** `AdjustmentImporter::import()` / `process_adjustment_record()` / `upsert_distru_adjustment()` (lines 155, 228, 264)
**Native target:** `distru_adjustments` (mirror) + downstream mutations on `non_metrc_item_cost_layers` (paths B/C/D); cannabis = mirror only
**Page cap:** 5,000
**Filters supported:** `inserted_datetime`, `completion_datetime` — ONLY 2 filters
**Filters we send:** Precedence: `inserted_datetime=<since>,` (incremental) OR `completion_datetime=1970-01-01T00:00:00Z,` (fresh)
**Raw payload retained:** YES — `distru_adjustments.raw_payload`

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `distru_id` | column + raw_payload | line 229 |
| `data[].package_id` | uuid | opt | Y | M | `distru_package_id` | column + raw_payload | line 271 |
| `data[].batch_id` | uuid | opt | N | M | `distru_batch_id` | column + raw_payload | line 272 |
| `data[].product_id` | uuid | opt | N | M | `distru_product_id` | column + raw_payload | line 273 |
| `data[].quantity` | signed decimal-string | opt | Y (as `quantity_delta`) | M | `distru_adjustments.quantity` | column + raw_payload | line 274; **DRIFT** — docs say `quantity_delta` |
| `data[].compliance_quantity` | signed decimal-string | opt | N | M | `compliance_quantity` | column + raw_payload | line 275 |
| `data[].unit_type.id` | uuid | opt | N | M | `unit_type_id` | column + raw_payload | line 276 |
| `data[].unit_type.name` | string | opt | N | R | n/a | raw_payload | |
| `data[].compliance_unit_type.id` | uuid | opt | N | M | `compliance_unit_type_id` | column + raw_payload | line 277-279 |
| `data[].compliance_unit_type.name` | string | opt | N | R | n/a | raw_payload | |
| `data[].reason` | string (tenant-customizable) | req | Y | M | `reason` | column + raw_payload | line 280; verbatim; drives revaluation routing |
| `data[].category` | string | opt | Y | R | n/a | raw_payload | Documented; not extracted |
| `data[].description` | text | opt | N | M | `description` | column + raw_payload | line 281 |
| `data[].total_cost` | decimal-string | opt | N | M | `total_cost` | column + raw_payload | line 282; drives revaluation math |
| `data[].completion_datetime` | iso | opt | Y (filter axis) | M | `completion_datetime` | column + raw_payload | line 283 |
| `data[].inserted_at` | iso | opt | N (alias) | M | `distru_inserted_at` | column + raw_payload | line 284; **DRIFT** — docs say `inserted_datetime` |
| `data[].license_id` | uuid | opt | N | M | `license_id` | column + raw_payload | line 285 |
| `data[].location_id` | uuid | opt | N | M | `location_id` | column + raw_payload | line 286 |
| `data[].owner_id` | string | opt | N | M | `owner_id` | column + raw_payload | line 287 |
| `data[].creator` (embed) | object | opt | Y | R | n/a | raw_payload | Importer uses `owner_id` instead |
| `data[].adjusted_datetime` | iso | opt | Y | R | n/a | raw_payload | Importer uses `completion_datetime` |
| `data[].inserted_datetime` | iso | opt | Y | R | n/a | raw_payload | Docs name; wire alias `inserted_at` used |
| `data[].updated_datetime` | iso | opt | Y | R | n/a | raw_payload | |
| `data[].custom_data[]` | array | opt | N | P | `distru_custom_field_definitions` (sightings) | raw_payload | line 236-241 (WU-13) |

### Gaps
- No U gaps. Mirror is intentionally fat (load-bearing for queries given only 2 server-side filters).

---

## /orders

**Wrapper:** `DistruApi::each_page()` via `ProgressTrackingStreamer::stream_with_progress`
**Importer:** `OrderImporter::import_orders_only()` → `process_order_record()` → `build_order_payload()` + `sync_line_items()` (OrderImporter.php:177, 408, 887)
**Native target:** `marketplace_orders` + `marketplace_order_line_items` (+ side-effects on `customers.payment_term`, `distru_locations`, `integration_company_mappings`)
**Page cap:** 500
**Filters supported:** `updated_datetime`, `inserted_datetime`, `order_datetime`, `delivery_datetime`, `due_datetime`, `status[]`, `company_id`, `page[number]`
**Filters we send:** incremental `updated_datetime=<since>,` OR fresh `inserted_datetime=1970-01-01T00:00:00Z,` (line 323)
**Raw payload retained:** **SELECTIVE** — NO full payload stash by design (user-rejected). Every wire field has a documented home: top-level sub-objects in `external_ids` (`distru_creator`, `distru_owner`, `distru_billing_location`, `distru_shipping_location`, `distru_company`, `distru_custom_fields`, `distru_order_datetime`, `distru_biotrack_id`); per-line-item `distru_product`/`distru_batch`/`distru_package`/`distru_location`; full `charges[]` in `order_taxes`

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `external_ids->distru_order_id` (virtual indexed column) | external_ids + vcol | line 220, 450-451 |
| `data[].order_number` | string | req | Y | M | `order_number` | column | line 469; fallback `DST-<uuid8>` |
| `data[].status` | enum (7 values) | req | Y | M | `marketplace_orders.status` | column | line 471 via `map_order_status()` |
| `data[].company` | object | opt | Y | R+P | resolved → `customer_id` + `external_ids->distru_company` (full obj) | column + external_ids | line 447, 470, 654; full object stashed for parity with creator/owner/locations |
| `data[].company.id` | uuid | req | Y | P | `customers.external_ids->distru_company_id` via bridge | column | line 660 |
| `data[].company.name` | string | req | Y | P | auto-create `Customer.name` when no bridge | column (indirect) | line 694, 706 |
| `data[].creator` (full User obj) | object | opt | Y | R | `external_ids->distru_creator` | external_ids | line 452 (verbatim) |
| `data[].owner` (full User obj) | object | opt | Y | R | `external_ids->distru_owner` | external_ids | line 453 |
| `data[].billing_location` (full obj) | object | opt | Y | R | `external_ids->distru_billing_location` | external_ids | line 454; license_id NOT used to derive billing license |
| `data[].shipping_location` (full obj) | object | opt | Y | P | `external_ids` + projected to `seller_license`/`metrc_facility_id` | external_ids + cols | line 455, 515-526, 762-852 |
| `data[].shipping_location.license.license_number` | string | opt | Y | M | `seller_license` + `metrc_facilities` match → `metrc_facility_id` | column | line 805, 812-816 |
| `data[].shipping_location.license_id` | uuid | opt | Y | P | `distru_locations.distru_license_id` cache | side table | line 763-765 |
| `data[].order_datetime` | iso | req | Y | R | `external_ids->distru_order_datetime` | external_ids | line 460; operator-mutable in Distru UI, preserved verbatim |
| `data[].delivery_datetime` | iso | req | Y | M | `ship_date` (date-only) | column | line 476, 1207 |
| `data[].due_datetime` | iso | req | Y | M | `payment_due_date` (date-only) | column | line 477 |
| `data[].inserted_datetime` | iso | req | Y | P | `created_at` ON CREATE ONLY | column | line 531-535 |
| `data[].updated_datetime` | iso | req | Y | M | `external_modified_at` | column | line 478 |
| `data[].payment_term_name` | string | opt | Y | M | `payment_term` + `customers.payment_term` side-effect | column + side | line 473, 277-304 |
| `data[].internal_notes` | string | opt | Y | M | `internal_notes` | column | line 474 |
| `data[].external_notes` | string | opt | Y | M | `external_notes` | column | line 475 |
| `data[].metrc_transfer_id` | int | opt | Y | M | `metrc_transfer_id` (int cast) | column | line 493-496 |
| `data[].biotrack_id` | string | opt | Y | R | `external_ids->distru_biotrack_id` | external_ids | line 463; BioTrack-state analog of metrc_transfer_id, null on Metrc orgs |
| `data[].leaflink_order_number` | string | opt | Y | M | `external_ids->leaflink_order_number` (dedupe) + `leaflink_order_id` bigint when numeric | external_ids + column | line 477-480, 520-522; bigint projection added 2026-05-26, defensive null when non-numeric |
| `data[].total` | decimal-string | req | Y | M | `marketplace_orders.total` | column | line 472 |
| `data[].custom_data` | array | opt | Y | P | `external_ids->distru_custom_fields` + sightings | external_ids + side | line 228-232, 456 |
| `data[].charges[]` | array<Charge> | opt | Y | P | projected to 4 totals + full preserved in `order_taxes` | columns + JSON | line 448, 562-630 |
| `data[].charges[].id` | uuid | — | Y | R | within `order_taxes` JSON | longtext JSON | |
| `data[].charges[].name` | string | — | Y | P | switches `shipping` / "tax" substring branches | projection | line 621, 647, 653; TAX-1: CHARGE with name containing "tax" routes into `tax` aggregate |
| `data[].charges[].type` | enum CHARGE/DISCOUNT/TAX | — | Y | P | routes to `tax`/`cultivation_tax`/`shipping`/`discount` | projection | line 620, 624-663; TAX-1: type=CHARGE+name~"tax" also feeds `tax` column |
| `data[].charges[].unit_type` | string PERCENT/PRICE | — | Y | R | within `order_taxes` JSON | longtext JSON | |
| `data[].charges[].percent` | decimal-string | — | Y | R | within `order_taxes` JSON | longtext JSON | metadata only |
| `data[].charges[].price` | decimal-string | — | Y | M | summed into tax/cultivation_tax/shipping/discount | column | line 593 |
| `data[].charges[].tax.name` | string | — | Y | P | case-insensitive 'cultivation' match | projection | line 598-601 |
| `data[].items[]` | array | opt | Y | M | `marketplace_order_line_items` rows | child table | line 887-962 |
| `data[].items[].id` | uuid | req | Y | M | `external_ids->distru_line_item_id` (dedupe key) | external_ids | line 929, 999 |
| `data[].items[].product.id` | uuid | — | Y | M | `product_id` via `products.distru_product_id` lookup | column + external_ids | line 982, 984 |
| `data[].items[].product.name` | string | — | Y | M | `product_name` | column | line 1009; fallback `'Unknown Distru Product'` |
| `data[].items[].product.sku` | string | — | Y | M | `product_sku` | column | line 1012 |
| `data[].items[].product` (full obj) | object | — | Y | R | `marketplace_order_line_items.external_ids->distru_product` | external_ids | line 1053; frozen-at-order-time snapshot for forensic queries |
| `data[].items[].batch` (full obj) | object | — | Y | R | `external_ids->distru_batch` | external_ids | line 1001 |
| `data[].items[].package` (full obj) | object | — | Y | R | `external_ids->distru_package` | external_ids | line 1002 |
| `data[].items[].location` (full obj) | object | — | Y | R | `external_ids->distru_location` | external_ids | line 1003 |
| `data[].items[].quantity` | decimal-string | req | Y | M | `quantity` | column | line 986, 1014 |
| `data[].items[].compliance_quantity` | decimal-string | opt | Y | M | `compliance_quantity` (WU-10) | column | line 993 |
| `data[].items[].price` | decimal-string | req | Y | M | `unit_price`; drives `subtotal`/`total` | column | line 987, 996 |
| `data[].items[].price_base` | decimal-string | opt | Y | M | `unit_price_base` (WU-10) | column | line 988 |
| `data[].items[].returned_quantity` | decimal-string | req | Y | M | `returned_quantity` (WU-10) | column | line 994 |
| `data[].items[].cost_per_unit` | decimal-string | opt | Y | M | `unit_cost_actual` (renamed WU-01) | column | line 989 |
| `data[].items[].cost_per_unit_default` | decimal-string | opt | Y | M | `unit_cost_default` | column | line 990 |
| `data[].items[].total_cost_actual` | decimal-string | opt | Y | M | `total_cost_actual` (WU-01) | column | line 991 |
| `data[].items[].total_cost_default` | decimal-string | opt | Y | M | `total_cost_default` | column | line 992 |
| `data[].items[].is_sample` | bool | req | Y | M | `is_sample` (WU-10) | column | line 1025 |

### Gaps
- ✅ All wire fields documented (as of 2026-05-26). Every top-level `/orders` field and every `items[]` sub-field has a documented native target or `external_ids` retention slot. No `raw_payload` safety net (user-rejected for storage cost) — enumeration is the contract.

---

## /invoices ✅ COMPLETE COVERAGE (2026-05-26 INV-1)

**Wrapper:** `DistruApi::each_page()` via streamer
**Importer:** `InvoiceImporter::import()` → `process_invoice_record()` → `upsert_invoice()` + `sync_invoice_line_items()` (InvoiceImporter.php)
**Native target:** `marketplace_invoices` + `marketplace_invoice_line_items` (first-class entity, NOT projected onto marketplace_orders)
**Page cap:** 500 (server clamps; importer passes 5000 advisory)
**Filters supported:** `inserted_datetime`, `invoice_datetime`, `due_datetime`, `updated_datetime`, `invoice_number`, `order_id[]`, `status[]` (Title Case), `page[number]`
**Filters we send:** Per-importer `build_window_filter()` (mirrors orders pattern: incremental `updated_datetime=<since>,` when prior completed job exists, fresh `inserted_datetime=1970-01-01T00:00:00Z,` otherwise)
**Raw payload retained:** **FULL** — every wire field has a documented home (column or `external_ids` JSON key). Order-row projection (the legacy 6 scalars on `marketplace_orders.external_ids`) is GONE — sole source of truth is now the `marketplace_invoices` table.

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `marketplace_invoices.distru_invoice_id` (virtual col from external_ids) | column + external_ids | UPSERT key |
| `data[].invoice_number` | string | req | Y | M | `marketplace_invoices.invoice_number` | column | unique per seller_organization |
| `data[].status` | enum | req | Y | M | `marketplace_invoices.status` (lowercase native enum) + verbatim in `external_ids.distru_invoice_status` | column + JSON | `DistruImportUtils::map_invoice_status` normalizes `NOT_PAID`/`FULLY_PAID`/`PARTIAL_PAID`/`VOID`/`OPEN` |
| `data[].company` | full obj | opt | Y | R | `external_ids.distru_company` (verbatim full object) | JSON | parity with how /orders stashes creator/owner/locations |
| `data[].creator` (full User) | object | opt | Y | R | `external_ids.distru_creator` (verbatim full User) | JSON | |
| `data[].owner` (full User) | object | opt | Y | R | `external_ids.distru_owner` (verbatim full User) | JSON | |
| `data[].order` | obj (4 fields) | req | Y | P | resolved `marketplace_order_id` FK + verbatim in `external_ids.distru_embedded_order` | column + JSON | resolve via `MarketplaceOrder.distru_order_id`; orphans land with `marketplace_order_id=NULL` (no longer skipped) |
| `data[].order.id` | uuid | req | Y | M | join against `distru_order_id` virtual column | lookup | InvoiceImporter::resolve_linked_order |
| `data[].order.order_number` | string | req | Y | R | within `external_ids.distru_embedded_order` | JSON | |
| `data[].order.status` | enum (Title Case) | req | Y | R | within `external_ids.distru_embedded_order` (snapshot at invoice time) | JSON | order's own status comes from /orders pass — no re-projection |
| `data[].order.total` | decimal-string | req | Y | R | within `external_ids.distru_embedded_order` | JSON | |
| `data[].invoice_datetime` | iso | req | Y | M | `marketplace_invoices.invoice_date` (Carbon datetime) + verbatim in `external_ids.distru_invoice_datetime` | column + JSON | |
| `data[].due_datetime` | iso | req | Y | M | `marketplace_invoices.due_date` (Carbon date) + verbatim in `external_ids.distru_due_datetime` | column + JSON | distinct from order's `payment_due_date` — can diverge for partial invoices |
| `data[].inserted_datetime` | iso | req | Y | P | `marketplace_invoices.created_at` on CREATE + verbatim in `external_ids.distru_inserted_datetime` | column + JSON | |
| `data[].updated_datetime` | iso | req | Y | M | `marketplace_invoices.external_modified_at` AND `paid_at` (when newly fully_paid) | column | |
| `data[].total` | decimal-string | req | Y | M | `marketplace_invoices.total` | column | |
| `data[].paid_amount` | decimal-string | req | Y | M | `marketplace_invoices.paid_amount`. Observer recomputes parent order's `paid_amount` aggregate across all linked invoices | column + observer side-effect | |
| `data[].remaining_amount` | decimal-string | req | Y | M | `marketplace_invoices.balance`. Observer recomputes parent order's `balance` | column + observer side-effect | |
| `data[].charges[]` | array | opt | Y | M | `marketplace_invoices.invoice_charges` (verbatim JSON) + projected to `tax`/`cultivation_tax`/`shipping`/`discount` columns | column + JSON | same projection logic as orders (`project_charges`) including the TAX-1 charge-name-contains-"tax" branch |
| `data[].custom_data` | array | opt | Y | R + side-effect | `external_ids.distru_custom_fields` + records sightings via `DistruCustomFieldDefinitionService::record_sightings(orgId, 'Invoice', ...)` | JSON + side-table | parallel to the 'Order' call site on OrderImporter |
| `data[].items[]` | array | opt | Y | M | `marketplace_invoice_line_items` rows | child table | full 1:1 line-item mirror |
| `data[].items[].id` | uuid | req | Y | M | dedupe key; `external_ids.distru_line_item_id` | external_ids | invoice line's own UUID (distinct from order_item_id) |
| `data[].items[].order_item_id` | uuid | req | Y | M | `marketplace_invoice_line_items.marketplace_order_line_item_id` FK (resolved via `MarketplaceOrderLineItem.external_ids->distru_line_item_id`) + `external_ids.distru_order_item_id` | FK column + JSON | **NEW** — enables per-line partial-invoicing reconciliation |
| `data[].items[].product` | obj | — | Y | M + R | resolved `product_id` + frozen snapshot in `external_ids.distru_product` | FK column + JSON | snapshot survives even if Distru mutates the product later |
| `data[].items[].batch` | obj | — | Y | R | `external_ids.distru_batch` (verbatim) | JSON | |
| `data[].items[].package` | obj | — | Y | R | `external_ids.distru_package` (verbatim) | JSON | |
| `data[].items[].quantity` | decimal-string | req | Y | M | `marketplace_invoice_line_items.quantity` | column | |
| `data[].items[].price` | decimal-string | req | Y | M | `marketplace_invoice_line_items.unit_price` (drives derived `subtotal`/`total`) | column | |
| `data[].items[].compliance_quantity` | decimal-string | opt | Y | M | `marketplace_invoice_line_items.compliance_quantity` | column | |
| `data[].items[].returned_quantity` | decimal-string | req | Y | M | `marketplace_invoice_line_items.returned_quantity` | column | invoice's view of returns can post-date /orders — now captured separately |
| `data[].items[].cost_per_unit` | decimal-string | opt | Y | M | `marketplace_invoice_line_items.unit_cost_actual` | column | |
| `data[].items[].cost_per_unit_default` | decimal-string | opt | Y | M | `marketplace_invoice_line_items.unit_cost_default` | column | |
| `data[].items[].total_cost_actual` | decimal-string | opt | Y | M | `marketplace_invoice_line_items.total_cost_actual` | column | |
| `data[].items[].total_cost_default` | decimal-string | opt | Y | M | `marketplace_invoice_line_items.total_cost_default` | column | |
| `payments[]` | array | n/a | Y (docs) / N (wire) | D | — | dropped | WRITE-ONLY field; never on GET — verified Phase 0.5. `DistruOutboundSync::sync_payment` posts to it. |

### Gaps — ✅ NONE

All wire fields have a documented native home as of INV-1 (2026-05-26). The
previous projection-onto-marketplace_orders pattern dropped 13+ fields; the
new native `marketplace_invoices` + `marketplace_invoice_line_items` tables
capture every Distru-shipped value. Round-trip write-back is unblocked.

**Cut-over notes:**
- The 6 scalars previously stashed on `marketplace_orders.external_ids`
  (`distru_invoice_id`, `_number`, `_status`, `_paid_amount`,
  `_remaining_amount`, `_total`) are NO LONGER WRITTEN. The 2 production
  readers in `DistruOutboundSync` (`ensure_distru_invoice_exists` line 343,
  `sync_payment` line 460) were rewritten to query `MarketplaceInvoice` via
  the `marketplace_order_id` FK. Existing data in those JSON keys remains
  on previously-imported orders (cosmetic; no reader looks at it anymore)
  and a re-import will not refresh them — operators can wipe via a one-time
  cleanup if desired.
- `payments[]` (D) — Distru-side blocker; flag in org-onboarding docs.

---

## /purchases

**Wrapper:** `DistruApi::get_purchases()` (DistruApi.php:479)
**Importer:** `PurchaseImporter::import()` (line 175); `process_purchase_record()` (line 218)
**Native target:** `purchase_orders` + `purchase_order_line_items` (non-cannabis lines) AND `marketplace_orders` + `marketplace_order_line_items` (cannabis lines)
**Page cap:** 500
**Filters supported:** `delivery_datetime`, `due_datetime`, `purchase_datetime`, `inserted_datetime`, `updated_datetime`, `status[]`, `purchase_number`, `page[number]`
**Filters we send:** incremental `updated_datetime=<since>,` OR fresh `inserted_datetime=1970-01-01T00:00:00Z,` (line 347-355)
**Raw payload retained:** PARTIAL — `company`, `charges`, `custom_data` in `external_ids->distru_vendor`/`distru_charges`/`distru_custom_fields`

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `purchase_orders.distru_purchase_id` + `marketplace_orders.external_ids->distru_purchase_id` | column | line 219, 368, 388, 660, 723 |
| `data[].purchase_number` | string | opt | Y | M | `purchase_orders.po_number` + `marketplace_orders.order_number` | column | line 429, 724, 766-775 |
| `data[].status` | string | req | Y | P | `purchase_orders.status` / `marketplace_orders.status` (mapped) | column | line 430, 481-491, 731; lossy collapse onto BudTags enum |
| `data[].company` | object | opt | Y | P | resolved to `vendor_id`; preserved under `external_ids->distru_vendor` | column + JSON | line 420, 725, 929-1055 |
| `data[].company.id` | uuid | req | Y | M | `purchase_orders.vendor_id` | column | line 935-953 |
| `data[].company.name` | string | opt | Y | P | `vendors.name` (auto-create only) | column + JSON | line 967-1033 |
| `data[].company.updated_datetime` | iso | opt | Y | R | within distru_vendor object | JSON | |
| `data[].billing_location` | object | opt | Y | **U** | — | — | **GAP** — Vendor billing address dropped |
| `data[].shipping_location` | object | opt | Y | **U** | — | — | **GAP** — Receiving address dropped |
| `data[].purchase_datetime` | iso | opt | Y | **U** | — | — | **GAP** — Docs claim this field; importer reads `order_datetime` instead. Possible doc drift. |
| `data[].delivery_datetime` | iso | opt | Y | **U** | — | — | **GAP** — Documented; never read |
| `data[].due_datetime` | iso | opt | Y | M | `expected_delivery_date` + `payment_due_date` | column | line 436, 733 |
| `data[].inserted_datetime` | iso | opt | Y | P | `created_at` on initial insert only | column | line 440-444, 748-752 |
| `data[].updated_datetime` | iso | opt | Y | P | `marketplace_orders.external_modified_at` (cannabis only) | column | line 734; **PO row drops this** |
| `data[].total` | decimal-string | opt | Y | M | `purchase_orders.total` + `marketplace_orders.total` | column | line 425, 434, 732 |
| `data[].order_datetime` | iso | opt | N | M | `purchase_orders.po_date` | column | line 435; **DRIFT** — wire alias not documented |
| `data[].metrc_transfer_id` | int | opt | N | M (cannabis) / U (non-c) | `marketplace_orders.metrc_transfer_id` | column | line 743-746 |
| `data[].items[]` | array | opt | Y | P | routed to `purchase_order_line_items` (non-c) or `marketplace_order_line_items` (c) | column | line 238, 284-293 |
| `data[].items[].id` | uuid | req | Y | M | `distru_line_item_id` / `external_ids->distru_line_item_id` | column | line 522, 540, 807, 863 |
| `data[].items[].product.id` | uuid | req | Y | M | `non_metrc_item_id` / `product_id` | column | line 559-561, 849-851 |
| `data[].items[].product.name` | string | opt | Y | P | `description` (composed) / `product_name` | column | line 598-606, 877 |
| `data[].items[].product.sku` | string | opt | Y | P | `description` (composed) / `product_sku` | column | line 599-608, 880 |
| `data[].items[].product.unit_type.name` | string | opt | Y | P | `unit_of_measure` | column | line 622-632 |
| `data[].items[].batch` | object | opt | Y | P | UoM fallback only (non-c) / full in `external_ids->distru_batch` (c) | column + JSON | line 634-640, 865 |
| `data[].items[].package` | object | opt | Y | P | classification key (non-c) / full in `external_ids->distru_package` (c) | JSON | line 309-335, 866 |
| `data[].items[].quantity` | decimal-string | req | Y | M | `quantity` | column | line 563, 854 |
| `data[].items[].compliance_quantity` | decimal-string | opt | Y | M | `compliance_quantity` | column | line 566, 577, 857, 883 |
| `data[].items[].price` | decimal-string | req | Y | M | `unit_cost`/`unit_price` + `line_total` | column | line 564, 567, 855, 891 |
| `data[].items[].returned_quantity` | decimal-string | opt | Y | **U** | — | — | **GAP** — Docs claim; importer reads `received_quantity` (undocumented). Cannabis branch reuses `returned_quantity` COLUMN for `received_quantity` (semantically inverted). |
| `data[].items[].cost_per_unit_actual` | decimal-string | opt | Y | **U** | — | — | **GAP — CRITICAL** — Documented canonical purchase cost; never read. Importer uses `price` for unit cost. |
| `data[].items[].cost_per_unit_default` | decimal-string | opt | Y | **U** | — | — | **GAP** |
| `data[].items[].total_cost_actual` | decimal-string | opt | Y | **U** | — | — | **GAP** — Cannabis branch comment notes "cost lives on Batch/Package" but no backfill implemented |
| `data[].items[].total_cost_default` | decimal-string | opt | Y | **U** | — | — | **GAP** |
| `data[].items[].is_sample` | bool | opt | N | M | `is_sample` | column | line 578, 902 |
| `data[].items[].received_quantity` | decimal-string | opt | N | M | `quantity_received` / `returned_quantity` (cannabis remap) | column | line 565, 579, 858, 890 |
| `data[].items[].price_base` | decimal-string | opt | N | M (cannabis) / U (non-c) | `unit_price_base` (cannabis) | column | line 856, 892 |
| `data[].items[].location` | object | opt | N | R (cannabis) / U (non-c) | `external_ids->distru_location` | JSON | line 867 |
| `data[].charges[]` | array | opt | Y | P | projected to tax/shipping/discount/subtotal + preserved | column + JSON | same logic as orders |
| `data[].custom_data[]` | array | opt | Y | R | sighting + `external_ids->distru_custom_fields` | JSON | line 232-236, 421, 726 |

### Gaps
- `billing_location`/`shipping_location` (U) — Vendor address + receiving address dropped
- `purchase_datetime`/`delivery_datetime` (U) — Documented timestamps never read
- `updated_datetime` (P) — PO branch loses external_modified_at
- `items[].returned_quantity` (U) — Cannabis branch semantically inverts the column; non-cannabis drops entirely
- **`items[].cost_per_unit_actual`/`cost_per_unit_default`/`total_cost_actual`/`total_cost_default` (U)** — Critical cost-fidelity gap. Documented canonical cost columns dropped; importer falls back to `price`. Cannabis branch leaves cost columns null pending unimplemented Batch/Package backfill.
- Wire-only fields (`order_datetime`, `metrc_transfer_id`, `is_sample`, `received_quantity`, `price_base`, `location`) — Read but not in skill — update skill

---

## /assemblies ⚠ HIGHEST GAP COUNT

**Wrapper:** `DistruApi::get_assemblies()` (DistruApi.php:613)
**Importer:** `AssemblyImporter::import()` (AssemblyImporter.php:223)
**Native targets:** Fan-out — `metrc_audit_logs` (every assembly), `non_metrc_inventory_logs` (non-SPLIT: per-ingredient + per-output cogs_summary), `package_recipe_templates` + components + `item_recipe_templates` pivot (MANUALLY_CREATED only), `metrc_package_local_metadata` (non-SPLIT only)
**Page cap:** 500 fixed
**Filters supported:** `inserted_datetime`, `completion_datetime`, `status`, `creation_source` (SCALAR), `location_id[]`, `license_number`, `page[number]`
**Filters we send:** `completion_datetime={modifiedSince|epoch},`
**Raw payload retained:** **NO** — `metrc_audit_logs.request_payload`/`response_body` intentionally null

### Field matrix

| Field path | Type | Required | Doc'd? | Mapped | Native target | Retention | Notes |
|---|---|---|---|---|---|---|---|
| `data[].id` | uuid | req | Y | M | `non_metrc_inventory_logs.distru_assembly_id` + `package_recipe_templates.distru_assembly_id` | column | line 270, 373, 475, 500, 716, 770 |
| `data[].assembly_number` | string | req | Y | M | fan-out: audit description + production_batch_number + local_pb + template name fallback | column | lines 580-584, 729, 780, 811, 1163 |
| `data[].status` | string | req | Y | D | — | none | Only COMPLETED imported (Decision #19) |
| `data[].creator.id` | uuid | opt | Y | **U** | — | none | **GAP** |
| `data[].creator.name` | string | opt | Y | **U** | — | none | **GAP** — user attribution dropped |
| `data[].location.id` | uuid | opt | Y | **U** | — | none | **GAP** |
| `data[].location.name` | string | opt | Y | **U** | — | none | **GAP** — assembly facility location dropped |
| `data[].started_datetime` | iso | opt | Y | **U** | — | none | **GAP** — cycle-time analysis impossible |
| `data[].completion_datetime` | iso | opt | Y | M | `metrc_audit_logs.submitted_at` | column | line 578; also the filter axis |
| `data[].inserted_datetime` | iso | req | Y | **U** | — | none | **GAP** |
| `data[].creation_source` | string (4 enum) | req | Y | M | `action_type` via ACTION_TYPE_MAP; gates template synthesis | column | line 155-160, 579, 823-825 |
| `data[].compliance_type` | enum METRC/BIOTRACK/NONE | req | Y | **U** | — | none | **GAP** — Discriminator dropped; routing uses heuristic instead |
| `data[].license_number` | string | opt | Y | M | `metrc_audit_logs.facility_license` | column | line 598 |
| `data[].license` | string | opt | N | M | `facility_license` fallback | column | line 590; undocumented alias |
| `data[].description` | string | opt | N | P (MANUAL only) | `package_recipe_templates.description` | column | line 1179, 1194 |
| `data[].custom_data[]` | array | opt | N | M (sightings) | `distru_custom_field_definitions` | sighting table | line 281-285 (WU-13) |
| `data[].outputs[]` | array | req | Y | M | fan-out per row | various | empty → skip (line 298-309) |
| `data[].outputs[].id` | uuid | req | Y | **U** | — | none | **GAP** — per-output identity dropped |
| `data[].outputs[].product.id` | uuid | req | Y | M | cogs_summary.metrc_item_id / template pivot key | column | line 379, 397, 410, 416, 518, 771 |
| `data[].outputs[].product.name` | string | opt | Y | P (MANUAL only) | template name primary surface | column | line 1156, 1159 |
| `data[].outputs[].batch.id` | uuid | opt | Y | **U** | — | none | **GAP** |
| `data[].outputs[].batch.batch_number` | string | opt | Y | **U** | — | none | **GAP** |
| `data[].outputs[].package.id` | uuid | opt | Y | **U** | — | none | **GAP** |
| `data[].outputs[].package.metrc_label` | string | opt | Y | M | `object_tag` / `metrc_package_id` / `metrc_package_tag` | column | line 605, 721, 776, 808 |
| `data[].outputs[].compliance_label` | string | opt | N | M | primary tag surface; also `inventory_logs.notes` | column | line 837-839, 1239 |
| `data[].outputs[].quantity` | decimal-string | req | Y | **U** | — | none | **GAP** — output produced quantity dropped |
| `data[].outputs[].compliance_type` | enum | req | Y | **U** | — | none | **GAP** — per-output discriminator dropped |
| `data[].outputs[].expiration_datetime` | iso | opt | N | M | embedded in inventory_logs.notes as `expires=<iso>` | text | line 654, 1242-1244; no dedicated column |
| `data[].outputs[].cost_per_unit_actual` | decimal-string | req | Y | **U** | — | none | **GAP** — output unit-cost dropped |
| `data[].outputs[].cost_per_unit_default` | decimal-string | req | Y | **U** | — | none | **GAP** |
| `data[].outputs[].total_cost_actual` | decimal-string | req | Y | M | `non_metrc_inventory_logs.total_package_cogs` (cogs_summary) | column | line 763, 779 |
| `data[].outputs[].total_cost_default` | decimal-string | req | Y | **U** | — | none | **GAP** — default-allocation total dropped |
| `data[].outputs[].ingredients[]` | array | req | Y | M | non-cannabis only → `non_metrc_inventory_logs` per ingredient; flattened to template components on MANUAL | column | line 658-732; cannabis skipped (lineage via Metrc SourcePackageLabels) |
| `data[].outputs[].ingredients[].id` | uuid | req | Y | **U** | — | none | **GAP** — ingredient identity dropped |
| `data[].outputs[].ingredients[].product.id` | uuid | req | Y | M | `non_metrc_inventory_logs.non_metrc_item_id` / template pivot | column | line 668, 717, 924, 940 |
| `data[].outputs[].ingredients[].product.name` | string | opt | Y | P | warning log + component label | log + column | line 682, 944, 1203 |
| `data[].outputs[].ingredients[].batch.id` | uuid | opt | Y | **U** | — | none | **GAP** |
| `data[].outputs[].ingredients[].batch.batch_number` | string | opt | Y | **U** | — | none | **GAP** |
| `data[].outputs[].ingredients[].package.id` | uuid | opt | Y | **U** | — | none | **GAP** — source package dropped |
| `data[].outputs[].ingredients[].package.metrc_label` | string | opt | Y | **U** | — | none | **GAP** — source Metrc tag for cannabis dropped (intentional — Metrc SourcePackageLabels) |
| `data[].outputs[].ingredients[].quantity_used` | decimal-string | req | Y | M | `change_quantity` (negated) | column | line 692-694, 711, 722 |
| `data[].outputs[].ingredients[].cost_per_unit_actual` | decimal-string | req | Y | M | `cost_per_unit_actual` | column | line 695-697, 725 |
| `data[].outputs[].ingredients[].cost_per_unit_default` | decimal-string | req | Y | M | `cost_per_unit_default` | column | line 698-700, 726 |
| `data[].outputs[].ingredients[].total_cost_actual` | decimal-string | req | Y | M | `total_cost_actual` | column | line 701-703, 727 |
| `data[].outputs[].ingredients[].total_cost_default` | decimal-string | req | Y | M | `total_cost_default` | column | line 704-706, 728 |
| `data[].outputs[].additional_costs[]` | array | req | Y | P (MANUAL flatten; LABOR sum always) | template components on MANUAL; LABOR sum to inventory_logs.labor_cost otherwise | column | line 539-545, 875-901; **non-MANUAL non-LABOR types dropped** |
| `data[].outputs[].additional_costs[].id` | uuid | req | Y | **U** | — | none | **GAP** |
| `data[].outputs[].additional_costs[].name` | string | req | Y | M | template_components.label | column | line 972-974, 989 |
| `data[].outputs[].additional_costs[].type` | enum LABOR/MACHINE/OVERHEAD/OTHER | req | Y | M | template_components.component_type | column | line 889, 976-977 |
| `data[].outputs[].additional_costs[].amount` | decimal-string | req | Y | **U** | — | none | **GAP** — Documented field dropped; importer reads undocumented `cost_per_unit * quantity` synthesis instead |
| `data[].outputs[].additional_costs[].cost_per_unit` | decimal-string | opt | N | M | template_components.cost_rate_actual; LABOR sum | column | line 969, 990 |
| `data[].outputs[].additional_costs[].cost_per_unit_default` | decimal-string | opt | N | M | template_components.cost_rate_default | column | line 970, 991 |
| `data[].outputs[].additional_costs[].quantity` | decimal-string | opt | N | M | template_components.quantity_needed | column | line 968, 986 |
| `data[].outputs[].additional_costs[].notes` | string | opt | Y | **U** | — | none | **GAP** |

### Gaps — HIGHEST COUNT
- `creator`/`location` (U) — User attribution + facility dropped
- `started_datetime`/`inserted_datetime` (U) — Cycle-time analysis blocked
- `compliance_type` (both levels, U) — METRC/BIOTRACK/NONE discriminator dropped
- `outputs[].id` / `ingredients[].id` / `additional_costs[].id` (U) — Identity tracking blocked
- `outputs[].batch` / `ingredients[].batch` (U) — Batch references dropped entirely
- `outputs[].package.id` / `ingredients[].package` (U) — Package identity dropped (cannabis source via Metrc is intentional, but the loss is total)
- `outputs[].quantity` (U) — Produced quantity dropped (only ingredient consumption stored)
- `outputs[].cost_per_unit_actual/default` (U) — Output unit-cost dropped
- `outputs[].total_cost_default` (U) — Only actual rolled up
- **`additional_costs[].amount` (U)** — Documented field dropped; possible doc/payload mismatch; Phase 1 verify
- `additional_costs[].notes` (U)
- **Non-MANUAL additional_costs** (D) — For SALES_ORDER/LAB_TESTING non-split assemblies, only LABOR survives; MACHINE/OVERHEAD/OTHER dropped
- **No raw payload retention** — Replay/diff against upstream changes impossible
- **No `updated_datetime` on assembly** — Distru API limitation; post-completion edits undetectable via date-window resync

### ASM-* update (2026-05-27) — pre-first-import retrofit

Live probe (Phase 0.5 + ASM preflight) revealed the original skill docs were wrong on the assembly wire shape. The matrix above is based on the skill; below are the **live-verified** corrections applied to AssemblyImporter:

**Wire-shape corrections** (skill was wrong):
- `creator.{id,name}` — does **NOT exist**; actual field is `owner_id` (scalar)
- `inserted_datetime`, `started_datetime` — do **NOT exist** on /assemblies wire (skill claimed they did)
- `license` — is an **ARRAY** of `{id, license_number, license_type}` (REC + MED), NOT a scalar. AssemblyImporter::resolve_facility_license() now iterates correctly.
- Per-output wire fields: `quantity` (not `quantity_used`), `cost_per_unit` (not `cost_per_unit_actual`). Per-output `total_cost_actual` is NOT shipped — the importer now derives total = `cost_per_unit × quantity`.
- `ingredients[]` and `additional_costs[]` are **nested per-output**, not top-level on the assembly

**Newly captured fields** (ASM-2):
- All 16 top-level assembly fields now stored verbatim in `package_recipe_templates.external_ids` JSON (replaces the previous "no raw payload retention" gap). The 7 previously dropped top-level fields — `compliance_type`, `estimated_start_date`, `estimated_work_hours`, `estimated_work_minutes`, `fulfilled`, `is_metrc_processing_job`, `owner_id` — are now retained for the future raw-assemblies UI + Distru write-back.
- `metrc_audit_logs.request_payload` now holds the full assembly JSON (mirrors Canix audit pattern) — replay/diff is now feasible.

**New cost-rollup columns** (ASM-1 + ASM-2):
- `non_metrc_inventory_logs.machine_cost` decimal(12,2) — Distru `additional_costs[].type='MACHINE'` rollup
- `non_metrc_inventory_logs.overhead_cost` decimal(12,2) — Distru `additional_costs[].type='OVERHEAD'` rollup
- `OTHER` folds into the existing per-row total without a dedicated column (catch-all bucket has no UI surface yet)

**NONE-compliance routing** (ASM-4):
- New `NonMetrcInventoryReason::DistruProductionBatch` enum value (`distru_production_batch`)
- For `compliance_type=NONE` assemblies: `metrc_audit_logs` write is **skipped** (no Metrc tag); material logs route to `reason='distru_production_batch'`; cogs_summary keys on `non_metrc_item_id` instead of `metrc_item_id`; recipe template synthesis still fires on MANUALLY_CREATED.

**Perf retrofit** (ASM-3):
- AssemblyImporter::import() now wrapped in `MarketplaceCacheService::within_batch` + `DistruInboundContext::within_inbound` (mirrors InvoiceImporter / PurchaseImporter). Eliminates per-row Redis SCAN pattern busts and prevents observer-driven outbound write-back echo loops.

**Deferred** (REVISIT tasks #84–86):
- Unify deduction with `InventoryService::deduct_for_package` — semantic mismatch risk (Distru events are after-the-fact; the service actively deducts)
- Non-cannabis audit UI label for `distru_production_batch`
- Distru-style raw-assemblies UI rendering `external_ids` JSON

---

# Appendix A: /contacts orchestration status (verified non-gap)

**Original audit-plan claim:** `/contacts` is wired in `DistruApi::get_contacts()` and `CustomerImporter::import_contacts()` but not invoked by the orchestrator.

**Verified:** **INCORRECT.** The CRM subagent (Phase 0) traced the dispatch path:

1. `RunDistruImport::run_import()` at line 45 delegates to `DistruImportService::import()`
2. `DistruImportService::run_entity_import()` at line 471 has a match arm dispatching `'contacts'` → `customer_importer->import_contacts()`
3. Additionally, `CustomerImporter::import()` (line 146) chains `import_companies()` → `import_contacts()` when called directly

**No code change needed.** The orchestration is correct.

**Sources verified:**
- `app/Jobs/RunDistruImport.php:45`
- `app/Services/DistruImportService.php:440-484`
- `app/Services/Distru/CustomerImporter.php:146, 1382-1386`

---

# Appendix B: Per-importer field-consumption index (M-set)

For each importer, the importer file:line numbers of every Distru-field consumption site. Use this index when adding new field mappings to know where the existing M-set lives.

## `app/Services/Distru/ReferenceDataImporter.php`
- `/locations` import: lines 100-150 (key consumption at 110, 118-128, 141-147)
- `/strains` import: lines 166-205
- `/menus` import: lines 220-255
- `/users` import: lines 270-315; staffmember projection 455-510
- `/payment-methods` import: lines 331-370

## `app/Services/Distru/CustomerImporter.php`
- `/companies` import: lines 164-1100 (process at 205, customer build 729-790, vendor build 1190-1260)
- `/contacts` import: lines 1382-1600 (process at 1417-1500, pivot at 1573-1590)
- Soft-delete: 1267, 1509
- Custom fields sighting: 216, 1425

## `app/Services/Distru/ProductImporter.php`
- `/products` import: lines 211-340 (process at 370, cannabis 410-470, non-cannabis 475-580)
- Brand/category/strain resolution: 884-1290
- `/product-pos-mappings` import: lines 641-700 (extract 1341-1380, project 1403-1430)

## `app/Services/Distru/TestResultImporter.php`
- Process record: 183-244
- Upsert mirror: 213-250
- Primary propagation: 272-320
- Map of denormalized propagation: PRIMARY_PROPAGATION_MAP constant near top of file

## `app/Services/Distru/PackageImporter.php`
- `/batches` import: lines 208-300 (process at 252-298)
- `/packages` import: lines 329-525 (process at 371-419, cannabis 480-510, non-cannabis 510-525)
- Primary test result flattening: 546-571
- License/facility resolution: 730-748

## `app/Services/Distru/InventoryImporter.php`
- Import: 80-90
- Build cache: 116-130
- Non-metrc sweep: 143-170
- Cannabis sweep: 186-210

## `app/Services/Distru/AdjustmentImporter.php`
- Import: 155-200
- Process record: 228-260
- Upsert mirror: 264-300
- Filter build: 210-218

## `app/Services/Distru/OrderImporter.php`
- `/orders` import: lines 177-540 (process at 408, build payload 442-540, line items 887-1030)
- `/invoices` import: lines 1044-1185 (process at 1080-1100, resolve order 1118-1135, apply state 1140-1185)
- Custom fields sighting: 228-232 (ONLY for Order, not Invoice — gap)
- Build orders filter: 323
- Build invoices filter: 1047

## `app/Services/Distru/PurchaseImporter.php`
- Import: 175-225
- Process: 218-260
- Cannabis classification: 309-335
- Build PO: 380-460
- Build cannabis MO: 660-755
- Line items (non-c): 540-610
- Line items (cannabis): 805-905
- Vendor resolution: 929-1055
- Charges projection: 1145-1209

## `app/Services/Distru/AssemblyImporter.php`
- Import: 223-310
- Audit log builder: 575-620
- Material logs (per-ingredient): 658-732
- COGS rollup: 760-790
- Template synthesis (MANUAL only): 408-545
- Template components: 918-994
- Local PB metadata: 800-815
- Extract output Metrc tag: 836-848
- Action-type map: 155-160
- Filter build: 1128-1135

---

# Phase 1: Live API Probe Results (L-sets)

Probed 2026-05-24 against organization `019e1c7f-f807-73e0-b2be-5fe76ae65e05` (mike@evopharms.com tenant) using user `9c01c638-37fc-42ae-ba6e-eda5956dc62a` (jwilly246@gmail.com). All 18 endpoints returned HTTP 200. Records examined: 3-5 per endpoint via `page[size]=3` (most endpoints ignore page[size]).

## Live-set summary table

| Endpoint | L paths | Records returned in probe | Notes |
|---|---:|---:|---|
| /locations | 7 | 16 | scalar `license` field (NOT object) — surprising |
| /strains | 3 | 279 | only id/name/strain_type — many docs missing |
| /menus | 8 | 4 | wire shape matches importer; skill is wrong |
| /users | 8 | 21 | role IS `{id,name}` object |
| /payment-methods | 3 | 5 | only id/name/deleted_at |
| /companies | 29 | 729 | importer field names correct; many doc'd fields absent |
| /contacts | 17 | 178 | wire uses `phone_number`+`description` (not skill's `phone`+`notes`) |
| /products | 39 | 3,860 | 4 undocumented new fields discovered |
| /test-results | 126 | 3,249 | 109 additional_test_results.* leaf keys |
| /product-pos-mappings | 0 | 0 | empty in this org (no POS systems configured) |
| /batches | 11 | 510 | embedded `primary_test_result` on batches (new) |
| /packages | 43 | 5,000 | wire emits qty/cost/labels |
| /adjustments | 20 | 1,022 | mostly matches importer |
| /orders | 90 | 500 | `biotrack_id` IS in wire — confirmed gap |
| /invoices | 70 | 500 | `items[]` IS in wire — confirmed major gap |
| /purchases | 43 | 500 | `billing_location`/`shipping_location` NOT in wire — skill bug |
| /assemblies | 77 | 500 | 9 undocumented new fields including labor/timing |

## Per-endpoint L\D, D\L, L\M analysis

### /locations
**L\D (in wire, not doc'd):** `data[].license_id`, `data[].license` (returned as scalar string here, not the `{id,license_number}` object the skill shows)
**D\L (doc'd, NOT in wire):** `data[].is_shipping`, `data[].is_billing`, `data[].is_archived` — three booleans the skill claims exist but aren't emitted. **These rows in the matrix should be reclassified: not real gaps, skill needs correction.**
**L\M (real gaps):** none — all live keys are mapped.

### /strains
**L\D:** none — wire has fewer fields than docs
**D\L (skill bugs):** `data[].metrc_strain_id`, `thc_lower`, `thc_upper`, `cbd_lower`, `cbd_upper`, `inserted_datetime`, `updated_datetime`, `type` — **8 documented fields not emitted.** The "promote metrc_strain_id to column" recommendation is moot — that data doesn't exist in responses. Skill needs major correction.
**L\M:** `data[].strain_type` is the actual wire field (confirms importer correct; resolves drift)

### /menus
**L\D:** none
**D\L (skill bugs):** `data[].name`, `data[].is_active`, `data[].is_published` — skill is wrong; wire uses `internal_name`/`external_name`/`active`/`visibility`/`product_count`. Skill correction needed; importer is correct.
**L\M:** none — importer matches wire

### /users
**L\D:** `data[].role.id`, `data[].role.name` (skill says role is flat string)
**D\L:** none
**L\M:** none — importer correctly reads role as object

### /payment-methods
**D\L (skill bugs):** `data[].is_active`, `data[].inserted_datetime`, `data[].updated_datetime` — **3 documented fields not emitted.** The "promote is_active to column" recommendation is moot. Skill correction needed.
**L\M:** none

### /companies
**L\D:** all importer-read fields match wire (phone_number, default_email, invoice_email, etc.) — importer is correct, skill names are stale
**D\L (skill bugs — 17 fields):** `data[].dba`, `data[].emails`, `data[].additional_emails`, `data[].additional_phones`, `data[].credit_limit`, `data[].primary_contact`, `data[].primary_billing_location`, `data[].primary_shipping_location`, `data[].primary_license_holder`, `data[].tags`, `data[].inserted_datetime`, `data[].licenses[].license_type`, `data[].licenses[].license_expiration_date`, `data[].licenses[].metrc_facility_license`, `data[].locations[].is_shipping`, `data[].locations[].is_billing`, `data[].locations[].is_archived`, `data[].locations[].license` — **these "gaps" disappear.** They're documented but never returned for this org. **Major reduction in real /companies gaps from 9 to 0.**
**L\M:** none for this org — all returned fields are mapped

### /contacts
**L\D:** `data[].driver_license_number`, `data[].driver_license_issuing_state`, `data[].work_phone_number` (importer-read but not in skill)
**D\L (skill bugs — 7 fields):** `data[].department`, `data[].birthdate`, `data[].anniversary_date`, `data[].notes` (skill name; wire has `description`), `data[].tags`, `data[].inserted_datetime`, `data[].updated_datetime`, `data[].companies[]` — **gaps disappear for this org.**
**L\M:** none

### /products
**L\D (new undocumented fields — 4 high-value finds):**
- `data[].description_markdown` — NEW; rich-text product description (markdown variant of `description`)
- `data[].images` (array) — the actual field name for product images (skill calls it `image_urls`)
- `data[].unit_net_weight_serving_size_unit_type` (object `{id,name}`) — NEW; separate UoM for the serving-size weight
**D\L (skill bugs — 11 fields):** `data[].is_inactive`, `data[].is_archived`, `data[].tags`, `data[].inserted_datetime`, `data[].upc`, `data[].compliance_type`, `data[].metrc_item_name`, `data[].metrc_item_category`, `data[].internal_notes`, `data[].quantities`, `data[].product_line`, `data[].primary_test_result`, `data[].image_urls`
**L\M (CONFIRMED real gaps — 4):**
- `data[].images` (U) — emitted as `images` array; importer never reads it (skill called it `image_urls` and importer didn't either). **Real gap — Distru-imported products have empty product_images native table.**
- `data[].description_markdown` (U) — NEW gap; rich-text not surfaced
- `data[].unit_net_weight_serving_size_unit_type` (U) — NEW gap
- `data[].category.type` partial — importer reads it (line 1048) → mapped; not a gap

### /test-results
**L\D (new — `additional_test_results.*` has 109 distinct keys in this org's data):** Terpenes (alpha_pinene_percentage, beta_caryophyllene_percentage, limonene_percentage, etc.), pesticides (abamectin_ug_per_g, fipronil_ug_per_g, malathion_ug_per_g, etc.), heavy metals (arsenic_ug_per_g, cadmium_ug_per_g, lead_ug_per_g, mercury_ug_per_g, etc.), residual solvents (benzene_ug_per_g, ethanol_ug_per_g, toluene_ug_per_g, etc.), mycotoxins. All preserved as JSON map by importer — good.
**D\L (skill bugs — 9 fields):** `data[].metrc_lab_test_id`, `data[].product_id`, `data[].sample_id`, `data[].expiration_datetime`, `data[].passed_test`, `data[].test_status`, `data[].moisture_content`, `data[].water_activity`, `data[].inserted_datetime` — **these "U gaps" disappear.** The high-value "passed_test"/"test_status" gap was theoretical; Distru doesn't emit those fields for this tenant.
**L\M:** None for top-level cannabinoid fields; granular fields (thc_percentage, total_thc_percentage, mg_per_unit variants) all mapped to mirror columns

### /product-pos-mappings
**Empty for this org** — no POS systems configured. Live shape unverifiable; importer logic untested via Phase 1.

### /batches
**L\D (new — 1 high-value find):** `data[].primary_test_result` — embedded test result summary directly on batch rows. UNDOCUMENTED in skill and UNMAPPED by importer. **NEW REAL GAP.**
**D\L (skill bugs — many):** `data[].creation_source`, `data[].creator`, `data[].location`, `data[].strain`, `data[].quantity`, `data[].compliance_quantity`, `data[].production_datetime`, `data[].use_by_datetime`, `data[].metrc_facility_license`, `data[].metrc_package_id`, `data[].biotrack_id`, `data[].inserted_datetime`, `data[].updated_datetime`, `data[].license`, `data[].cost_per_unit_actual`, `data[].cost_per_unit_default`, `data[].total_cost_actual`, `data[].total_cost_default` — none of these are in the response despite `include_costs=true`!
**L\M (NEW real gap):**
- `data[].primary_test_result` — embedded test summary on batches not surfaced

**⚠ Major surprise:** Despite `include_costs=true`, the 4 cost fields don't appear in `/batches` responses at all. This deviates from skill claim. Verify with Distru — possible API change or doc bug.

### /packages
**L\D:** wire matches importer column set well; `quantity_in_pending_sales` and `dual_unit_quantity` flagged in importer (lines 442-449) but **NOT in wire response for this org**. The `batch` embed flagged as documented is also absent.
**D\L (skill bugs):** `data[].package_id` (human-readable id documented but not emitted), `data[].batch` embed, `data[].compliance_quantity`, `data[].use_by_datetime`, `data[].metrc_package_id`, `data[].metrc_facility_license`, `data[].biotrack_id`, `data[].parent_package_id`, `data[].inserted_datetime`, `data[].updated_datetime`, `data[].deleted_at`, `data[].is_primary_test_result`
**L\M:** None — wire keys are all mapped

### /adjustments
**L\D:** All wire fields match importer
**D\L (skill bugs):** `data[].category`, `data[].creator`, `data[].adjusted_datetime`, `data[].inserted_datetime`, `data[].updated_datetime`, `data[].custom_data` (notably absent from this probe — may exist on other adjustments)
**L\M:** none

### /orders
**L\D:** importer reads everything in wire
**D\L:** none material (all skill-documented fields are present)
**L\M (CONFIRMED real gaps):**
- `data[].order_datetime` (U) — **CONFIRMED present in wire**, dropped by importer (real gap)
- `data[].biotrack_id` (U) — **CONFIRMED present in wire**, dropped by importer (real gap)

### /invoices
**L\D:** importer drops most of what wire emits
**D\L:** `data[].invoice_datetime` flagged as U in matrix — **CONFIRMED present in wire**
**L\M (CONFIRMED real gaps — multiple):**
- `data[].items[]` entire array — **CONFIRMED emitted**; importer reads NONE of it. Largest concrete gap in the audit.
- `data[].charges[]` — **CONFIRMED emitted**; dropped
- `data[].creator`, `data[].owner`, `data[].company` — **CONFIRMED full objects emitted**; dropped (inconsistent vs /orders pass)
- `data[].invoice_datetime`, `data[].due_datetime`, `data[].inserted_datetime` — **CONFIRMED emitted**; dropped
- `data[].custom_data` — **CONFIRMED emitted**; dropped (sightings only recorded for orders, not invoices)
- `data[].items[].order_item_id` — **CONFIRMED emitted**; this is the back-link that would enable per-line invoice↔order reconciliation

### /purchases
**L\D (importer drift — these wire fields lack skill documentation):**
- `data[].order_datetime` — wire uses `order_datetime` (importer correct, line 435); skill calls it `purchase_datetime` (which is NOT in wire)
- `data[].items[].received_quantity` — wire emits this; importer reads it; not in skill
**D\L (skill bugs — 5 fields):** `data[].billing_location`, `data[].shipping_location`, `data[].purchase_datetime`, `data[].delivery_datetime`, `data[].metrc_transfer_id` — **none of these are in wire responses.** The 5 U gaps in the matrix for these fields disappear.
**L\M:** none — wire matches importer's reads

**⚠ Major correction:** `/purchases` originally flagged with 9 U gaps; Phase 1 reveals that 5 of those 9 (`billing_location`, `shipping_location`, `purchase_datetime`, `delivery_datetime`, `metrc_transfer_id`) are documented but not emitted. **Real /purchases gap count drops from 9 to 4** (the `cost_per_unit_actual/default` and `total_cost_actual/default` items remain — confirmed not in wire for purchases either, so they're skill bugs too. Real count drops to ~0.)

### /assemblies
**L\D (9 NEW undocumented fields — high-value finds):**
- `data[].estimated_start_date` — when assembly was scheduled to start
- `data[].estimated_work_hours` — labor planning
- `data[].estimated_work_minutes` — labor planning
- `data[].fulfilled` — boolean fulfillment flag
- `data[].is_metrc_processing_job` — discriminator (different from `compliance_type`)
- `data[].outputs[].is_finished_good` — output classification
- `data[].outputs[].is_production_batch` — output classification
- `data[].outputs[].package_datetime` — output packaged timestamp
- `data[].outputs[].package_unit_type` (object `{id,name}`) — output unit-type
**D\L (skill bugs):** `data[].creator`, `data[].location`, `data[].started_datetime`, `data[].inserted_datetime` — these "U gaps" disappear
**L\M (CONFIRMED real gaps — many):**
- `data[].outputs[].quantity` — **CONFIRMED emitted**, dropped (real gap)
- `data[].outputs[].compliance_label` — present and consumed via `extract_output_metrc_tag()`
- `data[].outputs[].cost_per_unit` + `data[].outputs[].cost_per_unit_default` — **CONFIRMED emitted**, dropped at output level (mapped only at ingredient level)
- `data[].outputs[].total_cost_default` — **CONFIRMED emitted**, dropped
- `data[].outputs[].expiration_datetime` — **CONFIRMED emitted**, embedded in notes string instead of dedicated column
- `data[].outputs[].ingredients[].location` — **CONFIRMED emitted**, dropped
- 9 newly-discovered L\D fields above are all U

**Note:** `outputs[].id`, `ingredients[].id`, `additional_costs[].id`, `additional_costs[].amount`, `additional_costs[].notes` — all flagged as U in matrix; Phase 1 confirms **NONE are in wire** (Distru doesn't emit row identities or `amount`). Skill should be corrected; these are not real gaps.

---

## Revised Gap Summary (post-Phase 1)

| Endpoint | Original U count | Revised U count | Change | Reason |
|---|---:|---:|---:|---|
| /locations | 0 | 0 | 0 | — |
| /strains | 1 | 1 | 0 | `type` vs `strain_type` drift confirmed; importer correct |
| /menus | 2 | 0 | -2 | Skill names not in wire (drift); importer correct |
| /users | 0 | 0 | 0 | — |
| /payment-methods | 0 | 0 | 0 | — |
| /companies | 9 | 0 | **-9** | All 9 doc'd-but-missing fields drop |
| /contacts | 5 | 0 | **-5** | All 5 doc'd-but-missing fields drop |
| /products | 11 | **4** | -7 | `images`, `description_markdown`, `unit_net_weight_serving_size_unit_type`, `category.type` confirmed; skill bugs removed |
| /test-results | 9 | 0 | **-9** | All 9 doc'd fields not actually emitted |
| /product-pos-mappings | 2 | ? | unverified | No data in org for live probe |
| /batches | 0 | **1** | +1 | `primary_test_result` embedded on batches — new gap |
| /packages | 0 | 0 | 0 | — |
| **/inventory** | **4** | **4** | 0 | Live probe didn't include `/inventory` separately; gaps remain documented |
| /adjustments | 0 | 0 | 0 | — |
| /orders | 2 | **2** | 0 | `order_datetime`+`biotrack_id` CONFIRMED real |
| /invoices | 13+ | **13+** | 0 | All confirmed real — items[], charges[], creator, owner, company, custom_data, invoice_datetime, due_datetime, etc. |
| /purchases | 9 | **0** | **-9** | 5 doc'd fields absent; 4 cost fields also absent; real gaps drop to 0 |
| /assemblies | 22 | **17** | -5 | 5 doc'd-but-missing fields drop; 9 NEW L\D gaps added; outputs[].id/ingredients[].id/additional_costs[].id/amount/notes confirmed not in wire |
| **Revised Total** | ~89 | ~42 | **-47** | Roughly half the original "gaps" were skill-doc bugs |

## Key insights from Phase 1

1. **The Distru skill is significantly stale.** ~30-40 documented fields across endpoints aren't emitted by the API. This is the bigger story than missing importer maps — about half our "gaps" turned out to be skill bugs.

2. **The real high-priority gaps are concentrated in 4 endpoints:**
   - **/invoices** — items[] entirely dropped (12+ leaf fields), plus charges[], creator, owner, company, custom_data, invoice_datetime, due_datetime
   - **/assemblies** — outputs[].quantity (produced qty), output-level costs, 9 newly-discovered fields (estimated_*, fulfilled, package_datetime, is_finished_good, is_production_batch, etc.)
   - **/inventory** — available/reserved/pending/cost_default_per_unit, all dropped without retention
   - **/products** — `images` array, `description_markdown`, `unit_net_weight_serving_size_unit_type`

3. **New L\D discoveries (high-priority skill update candidates):**
   - `/products`: `description_markdown`, `images`, `unit_net_weight_serving_size_unit_type`
   - `/batches`: embedded `primary_test_result`
   - `/assemblies`: `estimated_start_date`, `estimated_work_hours`, `estimated_work_minutes`, `fulfilled`, `is_metrc_processing_job`, `outputs[].is_finished_good`, `outputs[].is_production_batch`, `outputs[].package_datetime`, `outputs[].package_unit_type`
   - `/contacts`: `driver_license_number`, `driver_license_issuing_state`, `work_phone_number` (importer reads; skill missing)
   - `/locations`: `license_id`, `license` (scalar form), `deleted_at`
   - `/users`: `role.id`, `role.name`

4. **Caveats:**
   - Probe used `page[size]=3` and inspected only the FIRST record per endpoint. Sparse fields (only present on some records) may be missed. A second-pass probe across 100+ records per endpoint would catch sparse-field cases. For the matrix to be 100% airtight, this is the next step.
   - `/product-pos-mappings` returned 0 records — live shape unverifiable for this org.
   - `/inventory` separate probe returned HTTP 400 with `grouping[]=PRODUCT` (the form the importer uses successfully). Cause unclear — may need an additional parameter the importer adds elsewhere, or a tinker-session auth-state issue. Phase 2 (live UI walkthrough) will surface the working request shape.
   - The probe was against one organization (`019e1c7f-f807-73e0-b2be-5fe76ae65e05`). Other orgs may emit different shapes due to tenant-configurable enums, custom fields, etc.

---

# Phase 2: Live UI walkthrough — Companies findings (executed 2026-05-25)

Findings from running the actual UI import for `reference_data` → `companies`. The live walkthrough surfaced one production bug, one UX trap, and several data-quality observations that Phase 0 and Phase 1 (static + first-record probe) couldn't have caught.

## P2-FINDING-1: `customer_facilities` pivot never populated — **FIXED**

**Severity:** HIGH (cross-link broken for every Distru company).

**Symptom:** Importer completed successfully; `customer_facilities` pivot had 0 rows for any Distru-sourced customer despite 1,078 companies having location data with valid license_ids (1,746 location-license tuples).

**Root cause:** `CustomerImporter::upsert_customer_locations()` (pre-fix lines 1303-1306) read `$location['license']['license_number']` (nested object). Wire actually returns `$location['license_id']` (scalar UUID) when locations are nested inside `/companies`. Phase 1's first-record probe missed this because `walk_keys` couldn't descend into a non-existent object. Phase 2 verified across all 1,134 companies: `locations[].license` is absent from every nested location; `locations[].license_id` is present in 1,746 instances.

**Fix:** Read `$location['license_id']`, resolve to license_number via the `distru_locations` mirror (populated by `ReferenceDataImporter::import_locations()`), then proceed with the existing facility-resolution + pivot-creation logic. Pre-load a per-import cache `distru_license_id_to_number_map()` to avoid N+1 queries. Landed in `CustomerImporter.php` 2026-05-25 with regression test in `tests/Feature/Distru/CustomerImporterTest.php`. All 47 tests pass.

**Audit-matrix delta:** /companies "U gap" count revised from 0 → 1 → 0 (after fix).

## P2-FINDING-2: Relationship-type-mappings UX trap (the 85% skip)

**Severity:** MEDIUM (no data lost, but operator can't tell anything went wrong).

**Symptom:** First companies run reported `171 imported, 0 updated, 963 skipped` — looks like success but 85% of records were silently dropped. After flipping routing toggles in the WU-15 onboarding UI, second run was `963 imported, 171 updated, 0 skipped`.

**Root cause:** `ReferenceDataImporter::import_relationship_type_mappings()` seeds new rows with all-false defaults (`routes_to_customers=0`, `routes_to_vendors=0`, `default_for_null=0`) so an admin can make the routing decision intentionally. But the reference_data import reports success without flagging that the system is left in an unroutable state. The companies import then silently skips every company whose relationship_type maps to all-false flags.

**Recommendations (not yet implemented):**
- Emit a high-visibility warning at the end of `reference_data` import: `"WARNING: N relationship-type mappings have all routing flags off — visit /distru/relationship-type-mappings/page or N% of companies will be skipped on the next import."`
- Or: have `companies` import bail with an obvious error if it would skip >50% of records.

## P2-FINDING-3: Unmapped-type UI lets users create a dead "null" mapping — **FIXED**

**Severity:** MEDIUM (user-visible bug; affects routing config trust).

**Symptom:** User visited `/distru/relationship-type-mappings/unmapped/page` after the first companies run and saw "null" listed as an unmapped relationship type (because 171 customers had `external_ids->distru_relationship_type_id = literal JSON null`). They created a mapping for it with `routes_to_customers=1`. The mapping had no effect — `route_company()` at line 362 short-circuits null relationship_types BEFORE consulting the mappings table, so the dead row just sits in the DB.

**Root cause:** `DistruImportController::build_unmapped_relationship_types_payload()` used `whereNotNull(JSON_EXTRACT(external_ids, '$.distru_relationship_type_id'))` to filter out missing keys. But JSON_EXTRACT returns JSON null (not SQL NULL) when the key exists with a null value — so 171 null-rt rows passed the filter and got grouped as a phantom "null" sighting.

**Fix:** Added a JSON_TYPE filter — `where(JSON_TYPE(...) = 'STRING')` — to reject both missing-key and JSON-null cases at the SQL level. Existing stale `name='null'` row deleted from `distru_relationship_type_mappings` (1 row removed; 4 legitimate rows remain). Landed in `DistruImportController.php:438-458` 2026-05-25. Controller test suite (30 tests) still passes.

## P2-FINDING-4: 62 license collisions creating duplicate rows

**Severity:** LOW (data-quality; not a code bug per se).

**Symptom:** Across 1,134 Distru companies, 62 cases where two distinct `company.id` UUIDs share the same `license_number`. Examples: `Skunkz | Grand Rapids` appears twice with same license `AU-R-001265`, `JARS | *` has 8 storefront-locations all sharing license `AU-P-000518`.

**Root cause:** Distru tracks per-storefront records; Michigan licensing is held at the chain level. The importer's dedupe chain (`CustomerImporter.php:417-419`) matches by license first, then by distru_company_id. When license matches but distru_company_id differs, it creates a separate row to avoid clobbering — by design — but the result is 62 duplicate customer/vendor rows for the same physical license-holder.

**Recommendation (deferred):**
- Business decision needed: (a) accept duplicates as separate Distru records, (b) add admin merge tool, (c) tighten dedupe to prefer license-match over distru_company_id mismatch.

## P2-FINDING-5: 171 null-relationship-type companies categorized

**Severity:** INFORMATIONAL (helps inform the WU-15 enhancement decision).

When companies have `relationship_type: null` (171 records), the importer routes them to customers by default. Categorization showed they break into 3 distinct cohorts:

- **107 active licensed Michigan cannabis businesses** (correctly routed to customers): Skymint (16 locations), JARS (8), Levels (6), Bloom City Club (4), New Standard, Harbor Farmz, etc. — all with `AU-P`/`AU-R`/`AU-G` license prefixes.
- **47 active unlicensed companies (LIKELY MISROUTED to customers, should be vendors):** packaging/print/hardware suppliers like 4imprint, Sticker Mule, UPrinting, Puffco, HBI International, Custom Cones USA, Abstrax, True Terpenes, Alibaba, etc. Plus a few brand collabs (Gold Crown variants, LegaSea).
- **17 soft-deleted** (test data; correctly stayed out): TEST, Test, gramz, hre, fat pack, Gramazon, etc.

**Implication:** The current routing system can't conditionally route by license_number presence (null-rt → customers blanket rule). A simple enhancement — "if relationship_type is null AND license_number is absent, route to vendors instead" — would correctly classify the 47 unlicensed-vendor cohort without manual intervention. The cleaner long-term fix is to set `relationship_type` in Distru itself for those 47 companies.

## P2-FINDING-6: JSON literal-null SQL query gotcha

**Severity:** INFORMATIONAL (affects future SQL queries against `external_ids`).

When `CustomerImporter` stores a null-rt company, Eloquent's JSON cast serializes the PHP null into a literal JSON null token inside `external_ids`. JSON_EXTRACT then returns JSON null (not SQL NULL) when reading back. Practical implication for queries:

- ❌ `WHERE JSON_EXTRACT(external_ids, '$.distru_relationship_type_id') IS NULL` — doesn't match
- ✅ `WHERE JSON_TYPE(JSON_EXTRACT(external_ids, '$.distru_relationship_type_id')) = 'NULL'` — matches null-valued keys
- ✅ `WHERE JSON_EXTRACT(external_ids, '$.distru_relationship_type_id') = CAST('null' AS JSON)` — alternative match

This pattern trapped both my initial Phase 2 query AND the unmapped-types controller's `whereNotNull` filter. Worth flagging for any future report-writing against Distru-stored external_ids.

## P2-FINDING-7: `/contacts` live verification — clean (executed 2026-05-25 01:24)

**Severity:** INFORMATIONAL (entity is in proper shape; no bugs found).

**Run result:** `184 imported, 0 updated, 0 skipped` in 0.1 seconds, 168.5 MB peak memory, zero warnings. The wire returns 184 records with `deleted=include` (178 active + 6 soft-deleted), exactly matching `customer_contacts` insertion counts. **182 of 184 contacts pivoted to customers** (99.1%); the 2 orphans are explainable Distru data-quality cases, NOT importer bugs:

| Orphan | Reason |
|---|---|
| **"SKYMINT MENU"** (no email, no last name) | Synthetic contact created by Distru's menu integration; Distru itself has `company: null` on the record |
| **"Jukoada Sexton"** (`retail@craft-leaf.com`) | Real person who works at "Craft Leaf \| Coldwater" — but Distru's contact record has `company: null` despite the email implying the affiliation. Fix is in Distru's UI, not Budtags. |

**Phase 1 predictions all verified:**
- Wire field renames the importer reads (`phone_number`, `description`, `work_phone_number`, `driver_license_number`, `driver_license_issuing_state`, `owner.id`) all populated correctly in `customer_contacts` columns.
- Phantom fields confirmed absent in live data: `department`, `birthdate`, `anniversary_date`, `notes`, `tags`, `inserted_datetime`, `updated_datetime` — none appear in wire response across 184 records. Skill doc rewrite (Phase 2 task B1) was correct.
- `customer_contact` m2m pivot table has 182 rows matching the contacts-with-non-null-company.id population in Distru.

**Audit-matrix delta:** /contacts revised U gap count: **0** (unchanged from Phase 1 reconciliation; live run confirmed no surprises).

---

## Revised /companies Gap Summary (post-Phase 2 fixes)

| Metric | Pre-fix | Post-fix |
|---|---:|---:|
| L\M gaps (importer drops wire fields) | 1 (`license_id` nested) | **0** (fixed via distru_locations resolution) |
| D\L gaps (skill claims field, wire doesn't emit) | 17 | 0 (skill rewritten) |
| L\D gaps (wire emits, skill missing) | 13 | 0 (skill now has them) |
| customer_facilities pivot rows | 0 | **2** (verified 2026-05-25 01:20: EVO Pharms ↔ both org Metrc facilities via license_ids `…897d1`/`…a953a`; sparse-by-design — only the org's own customer pivots) |
| 171-null-rt routing | unverifiable | confirmed routes to customers; categorization documented |

---

## Phase 2 entity-by-entity completion checklist

| Entity | Run status | Records | U gaps (post-live) | Notable findings |
|---|---|---:|---:|---|
| **reference_data** (locations, strains, menus, users, payment-methods) | ✅ Verified 2026-05-25 00:38 | 329 + 1,134 (companies sweep) | 0 | Clean. Identified the relationship_type_mappings UX trap (P2-FINDING-2). |
| **companies** | ✅ Verified 2026-05-25 01:20 (post-fix) | 1,134 (954 customers + 180 vendors) | 0 (was 1 pre-fix) | customer_facilities pivot bug found + fixed (P2-FINDING-1). 2 pivot rows landed correctly. |
| **contacts** | ✅ Verified 2026-05-25 01:24 | 184 (178 + 6 soft-deleted) | 0 | Clean (P2-FINDING-7). 99% pivot rate; 2 orphans are Distru-side data quality. |
| products | Pending | (~3,860 expected) | 4 (Phase 1) | Watch for `images`, `description_markdown`, `unit_net_weight_serving_size_unit_type` field surprises. |
| product-pos-mappings | Pending | (0 expected — no POS configured) | TBD | May skip if empty. |
| test-results | Pending | (~3,249 expected) | 0 (Phase 1) | 109-key `additional_test_results` open map; ensure full preservation. |
| batches | Pending | (~510 expected) | 1 (Phase 1) | Watch for embedded `primary_test_result` handling. |
| packages | Pending | (~5,000+ expected) | 0 cannabis / 0 non-cannabis | Cannabis Metrc-redundant blanking intentional. |
| inventory | Pending | (PRODUCT grouping) | 4 (high-risk — no raw_payload safety) | `available`/`reserved`/`pending`/`cost_default_per_unit` dropped without retention. |
| adjustments | Pending | (~1,022 expected) | 0 | Mirror is load-bearing. |
| orders | Pending | (~500/page) | 2 (Phase 1) | `order_datetime` + `biotrack_id` confirmed emitted but unmapped. |
| invoices | Pending | (~500/page) | 13+ (Phase 1) | `items[]` array entirely dropped — largest single gap in audit. |
| purchases | Pending | (~500/page) | 0 (Phase 1 revised down from 9) | Phase 1 proved most Phase 0 "gaps" were skill-doc drift. |
| assemblies | Pending | (~500/page) | 17+ (Phase 1) | 9 newly-discovered wire fields including `estimated_*`, `fulfilled`, output `package_datetime`. |

# Phase 2: Remaining entities (pending user)

User to run full importer through UI **one entity at a time** in the following sequence so log rows correlate cleanly:

```
Reference data (locations, strains, menus, users, payment-methods)
  → companies
  → contacts
  → products → product-pos-mappings → test-results
  → batches → packages → inventory → adjustments
  → orders → invoices
  → purchases
  → assemblies
```

During each entity import, two log layers are tailed in parallel:

**Layer A — `logs` DB table polling** (every ~10s via mcp__laravel-boost__database-query):
```sql
SELECT id, timestamp, title, notes
FROM logs
WHERE title LIKE 'Distru%'
  AND timestamp > NOW() - INTERVAL 5 MINUTE
ORDER BY id DESC
LIMIT 200;
```
Catches per-page metadata, errors, and importer warnings.

**Layer B — `tail -f storage/logs/horizon.log | grep -i distru`** (background bash):
Catches stack traces and exceptions outside `LogService::store()`.

Goal of Phase 2: catch any **dynamic** issues (timing, large-payload OOM, sparse-field edges, real-data shape variations) that the static Phase 0 + targeted Phase 1 probes can miss.

---

# Phase 3: Reconciliation (after Phase 2)

Update Gap Summary final counts. File skill-update issues for the L\D and D\L findings from Phase 1. Open work units for each confirmed L\M gap requiring importer changes.
