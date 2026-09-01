# CRM Domain — Companies, Contacts, Locations

The Distru CRM domain unifies customers AND vendors under a single `Company` model, plus `Contacts` (people) and `Locations` (addresses). The `relationship_type` field on Company is **tenant-customizable** — orgs define their own values (e.g. `Current Customer`, `Current Supplier`, `Brand`, `Potential Customer`).

**Reconciled with live wire shapes 2026-05-25** against an active production tenant (1,134 companies, 178 contacts, 16 locations). Many previously-documented fields turned out to be **doc-only** (never emitted by the API) and have been removed. Several **undocumented wire fields** have been added. See `../coverage/field-coverage-audit.md` for the field-by-field reconciliation (which fields BudTags maps + our gaps).

## Endpoints

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/public/v1/companies` | List companies | Page size **5,000**. |
| GET | `/public/v1/companies/{id}` | Get one company | Same shape as list. **Live-verified 2026-08-18 (HTTP 200)** — a BudTags in-code comment (`SyncMarketplaceCustomerToDistru.php` D6) claiming detail GETs 404 for companies is WRONG; response includes `updated_datetime`, so pre-write refresh/version checks ARE possible. |
| POST | `/public/v1/companies` | Create or update | UPSERT. `id` optional. |
| GET | `/public/v1/contacts` | List contacts | Page size **1,000**. Per-company filter via `company_id`. |
| GET | `/public/v1/contacts/{id}` | Get one contact | Same shape. |
| POST | `/public/v1/contacts` | Create or update | UPSERT. `full_name` is **server-derived** — do NOT send. |
| GET | `/public/v1/locations` | List locations | Page size **1,000**. |
| GET | `/public/v1/locations/{id}` | Get one location | Same shape. |
| POST | `/public/v1/locations` | Create or update | UPSERT. |

## Company entity shape (live wire — ~25 top-level fields observed)

```jsonc
{
  "id": "<uuid>",
  "name": "...",
  "legal_business_name": "<string|null>",
  "relationship_type": {                                  // OBJECT or null — NOT a flat string
    "id": "<uuid>",
    "name": "Current Customer"                            // tenant-customizable
  },
  "category": "<string|null>",                            // tenant-customizable scalar (e.g. "Retail", "Wholesale")
  "group": {                                              // OBJECT or null — separate from category
    "id": "<uuid>",
    "name": "..."
  },
  "owner_id": "<uuid|null>",                              // FK to User
  "phone_number": "<string|null>",                        // NOT `phone`
  "website": "<string|null>",
  "default_email": "<string|null>",                       // NOT `primary_email`
  "sales_order_email": "<string|null>",
  "purchase_order_email": "<string|null>",
  "invoice_email": "<string|null>",                       // NOT `billing_email`
  "order_shipment_email": "<string|null>",                // NOT `shipping_email`
  "default_sales_order_notes": "<string|null>",
  "default_purchase_order_notes": "<string|null>",
  "outstanding_balance_threshold": "<integer cents|null>", // INTEGER cents — not dollars
  "locations": [                                          // ARRAY — see nested shape below
    {
      "id": "<uuid>",
      "name": "<string|null>",
      "address": "<string>",                              // FLAT concatenated string
      "company_id": "<uuid|null>",
      "license_id": "<uuid|null>"                         // SCALAR UUID — NOT a nested object
    }
  ],
  "licenses": [                                           // RICHER than previously documented (live-verified 2026-08-18)
    {
      "id": "<uuid>",
      "license_number": "<string>",
      "active": true,
      "license_type": "<string|null>",                    // e.g. "Processor"
      "expiry_datetime": "<iso|null>",
      "issue_datetime": "<iso|null>"
    }
  ],
  "custom_data": [ /* see custom_data shape inversion below */ ],
  "inserted_datetime": "<iso>",                           // ADDED after 2026-05-25 — 830/830 live Evo companies (2026-09-01); BudTags ranks it first for business_partners.created_at
  "updated_datetime": "<iso>",
  "deleted_at": "<iso|null>"                              // Present when `deleted=include` is passed
  // Also observed on the 2026-09-01 wire, not in the shape above and population not audited:
  //   `tasks`, `outstanding_balance`, `default_payment_term`, `qb_customer_id`, `qb_vendor_id`,
  //   `leaflink_customer_id`, `leaflink_brand_id`
}
```

### Fields NOT in the wire (formerly documented; removed 2026-05-25)

The following fields were previously listed in this skill but **never appear in live API responses**. They've been removed. If you find one in a payload, treat it as a tenant-specific addition or stale doc:

- `dba`
- `primary_contact`, `primary_billing_location`, `primary_shipping_location`, `primary_license_holder`
- `emails`, `billing_email`, `shipping_email`, `primary_email`, `additional_emails`, `phone`, `additional_phones`
- `credit_limit`
- `tags`
- ~~`inserted_datetime`~~ — CORRECTION 2026-09-01: now emitted on every company (830/830 live Evo)
- `licenses[].license_expiration_date`, `licenses[].metrc_facility_license` (but NOTE 2026-08-18: `licenses[].license_type`, `licenses[].active`, `licenses[].expiry_datetime`, `licenses[].issue_datetime` DO appear in the live wire now — see entity shape above)
- `locations[].is_shipping`, `locations[].is_billing`, `locations[].is_archived`, `locations[].license` (nested object)

### What's still NOT here (compared to docs that hint at it)

- **No flat address fields** at the Company root. Address data lives only on `locations[]`.
- **No `payment_term_id`** — payment terms attach at the order level, not company level.
- **No relationship_type filter on GET** — `/companies?relationship_type=Customer` is silently ignored. Filter client-side after fetching all.

### Tenant-customizable `relationship_type`

`relationship_type` is `{id, name}|null` where the `name` is whatever the tenant configured. Observed in the wild: `Current Customer`, `Current Supplier`, `Brand`, `Potential Customer`. Strategy (mapping doc Decision #15):

1. On import, collect distinct `relationship_type.id` values into a `distru_relationship_type_mappings` table.
2. Surface unmapped values to an admin UI for manual customer/vendor routing.
3. Companies with `relationship_type: null` should fall through to a `default_for_null` mapping if one is configured.

## Contact entity shape (live wire — 17 paths observed)

```jsonc
{
  "id": "<uuid>",
  "first_name": "...",
  "last_name": "...",
  "full_name": "First Last",                              // SERVER-DERIVED — don't write
  "company": { "id": "<uuid>" },                          // Reduced ref — just `id`
  "owner": { "id": "<uuid>" } | null,                     // FK to User
  "email": "<string|null>",
  "phone_number": "<string|null>",                        // NOT `phone`
  "work_phone_number": "<string|null>",
  "title": "<string|null>",
  "description": "<string|null>",                         // NOT `notes`
  "driver_license_number": "<string|null>",
  "driver_license_issuing_state": "<string|null>",
  "custom_data": [ /* see shape inversion below */ ],
  "inserted_datetime": "<iso>",                           // ADDED after 2026-05-25 — 454/454 live Evo contacts (2026-09-01)
  "updated_datetime": "<iso>",                            // ADDED — same probe
  "deleted_at": "<iso|null>"                              // With `deleted=include`
  // Also observed 2026-09-01: `tasks`
}
```

### Contact fields NOT in the wire (removed 2026-05-25)

- `department`, `notes`, `birthdate`, `anniversary_date`, `tags` — none of these appeared in live responses for this tenant. Treat any sighting in the wild as tenant-extension or stale doc.
- ~~`inserted_datetime`, `updated_datetime`~~ — CORRECTION 2026-09-01: BOTH are now emitted on every contact (454/454 live Evo). `updated_datetime` makes incremental contact sync possible.

## Location entity shape

### When fetched via `/locations` endpoint (7 fields, **mixed `license` typing**)

```jsonc
{
  "id": "<uuid>",
  "name": "<string|null>",
  "address": "<single concatenated string>",
  "company_id": "<uuid|null>",
  "license_id": "<uuid|null>",                            // Always scalar UUID
  "license": <string|object|null>,                        // INCONSISTENT — see below
  "deleted_at": "<iso|null>"
}
```

The standalone `/locations` endpoint returns `license` with **mixed typing in the same response**: some records emit `license` as `{id, license_number}`, others emit `license` as a plain string (probably the license_number directly). Out of 16 records sampled: 12 objects, 4 strings. **Do not rely on the type of `license`** — use the always-scalar `license_id` UUID instead and join to `/licenses` data if you need license_number.

### When nested under `/companies.locations[]` (5 fields, **no `license`**)

```jsonc
{
  "id": "<uuid>",
  "name": "<string|null>",
  "address": "<string>",
  "company_id": "<uuid|null>",
  "license_id": "<uuid|null>"                             // ONLY license info present
}
```

The nested form does NOT return `license` at all — only `license_id`. To resolve license_number from a company's locations, you must either pre-fetch `/locations` (or maintain a `distru_locations` mirror) and join by `license_id`.

### Location fields NOT in the wire (removed 2026-05-25)

- `is_shipping`, `is_billing`, `is_archived` — none of these booleans appear in live responses. The previously-documented heuristic for picking a shipping address from `is_shipping=true` doesn't work; fall back to name-substring matching or pre-load `primary_shipping_location` from a UI export.

**`address` is a single string** — `"123 Main St, Springfield, IL 62701"`. Distru does not break it into line_1/line_2/city/state/zip. Importers must parse it or store the raw string in `raw_payload` and defer parsing.

## Filter parameters

### `/companies`
| Filter | Type | Notes |
|---|---|---|
| `inserted_datetime` | comma-range | |
| `updated_datetime` | comma-range | Canonical incremental-sync filter |
| `name` | string | Substring match |
| `license_number` | string | |
| `deleted` | tri-state | `include` returns soft-deleted rows with `deleted_at` set |
| `page[number]` | integer | |

NO `relationship_type` filter. NO `email` filter. NO `is_archived` filter. NO `tags[]` filter.

### `/contacts`
| Filter | Type | Notes |
|---|---|---|
| `inserted_datetime` | comma-range | |
| `updated_datetime` | comma-range | |
| `company_id` | string (uuid) | |
| `email` | string | Substring match |
| `deleted` | tri-state | |
| `page[number]` | integer | |

### `/locations`
| Filter | Type | Notes |
|---|---|---|
| `inserted_datetime` | comma-range | |
| `updated_datetime` | comma-range | |
| `company_id` | string (uuid) | |
| `deleted` | tri-state | |
| `page[number]` | integer | |

## custom_data shape inversion (read vs write)

Distru exposes custom fields on most entities, but **the JSON shape returned on GET differs from what you POST**. (Decision #20 in mapping doc.)

**On READ (`custom_data` field in response):**
```jsonc
[
  { "id": <integer field-definition-id>, "name": "Field Name", "type": "TEXT", "value": "..." }
]
```

**On WRITE (`custom_data` field in request body):**
```jsonc
[
  { "id": <integer>, "value": "..." }      // shape: just id+value, omit name+type
]
```

The shapes are **non-symmetric**. Reading-and-writing the same response will fail validation because `name` and `type` are read-only. Strip them before writeback.

## Write safety

- POST is UPSERT — `id` optional for create.
- For `/contacts` writes, do NOT send `full_name` — Distru rejects it with HTTP 400 (server-derived).
- `outstanding_balance_threshold` is in **integer cents** on the Company entity. Sending dollars (e.g. `100.00`) instead of cents (`10000`) silently coerces to `100` (1 dollar) — a 100× error.

## Cross-references

- Locations used as billing/shipping on orders: `categories/sales-orders.md`
- Companies referenced as supplier on purchases: `categories/purchase-orders.md`
- Customer import workflow: `scenarios/customer-import-workflow.md`
- Custom field handling: mapping doc Decision #20
- Filter conventions: `patterns/filtering.md`
- Field-by-field reconciliation against live wire (BudTags mapping + gaps, Phase 1 + Phase 2 findings): `../coverage/field-coverage-audit.md`
