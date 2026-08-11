# Sales Domain — Orders and Invoices

The Distru Sales domain covers customer-facing orders and their billing artifacts. Orders carry line items inline and progress through a status lifecycle. Invoices are derived from Orders. Payments are **WRITE-ONLY** — they can be created via POST but the existing payment ledger cannot be read back via GET.

**Phase 0.5 audited 2026-05-21.** Mapping doc: `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md`.

## Endpoints

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/public/v1/orders` | List orders | Page size 500. **Cannot call unfiltered on high-volume orgs** — times out. Use `updated_datetime` window. |
| GET | `/public/v1/orders/{id}` | Get one order | Same 23-field shape as list (no detail-only fields). Eventually consistent ~1s. |
| POST | `/public/v1/orders` | Create or update order | UPSERT — same payload shape. **Non-sparse updates** — omitted items[] / charges[] get DELETED. |
| GET | `/public/v1/invoices` | List invoices | Page size 500. |
| GET | `/public/v1/invoices/{id}` | Get one invoice | Same 17-field shape as list. |
| POST | `/public/v1/invoices` | Create or update invoice | UPSERT. `order_id` required (NOT in formal docs Parameters table but required in practice). Non-sparse updates. |
| POST | `/public/v1/invoices/{id}/payments` | Insert payment | **WRITE-ONLY** — payments do NOT appear on GET responses anywhere. |

> Note: There is **no PUT** verb on /orders or /invoices anymore — POST handles both create and update via UPSERT.

## Order entity shape (25+ top-level fields)

```jsonc
{
  "id": "<uuid>",
  "order_number": "SO-123",
  "status": "COMPLETED",                          // 7-value enum, UPPERCASE in response
  "company": { "id": "<uuid>", "name": "...", "updated_datetime": "..." },
  "creator": { /* full User object — id, full_name, email, role, banned, deleted_at */ },
  "owner": { /* full User object | null */ },
  "billing_location": { /* Location | null — the BUYER's ship-to; carries the buyer's FLAT license_number */ },
  "shipping_location": { /* Location | null — the BUYER's ship-to (same object as billing on sampled orders), NOT the seller side */ },
  "inventory_source": { /* Location | null — the SELLER's ship-from; the only order-level field with the seller's FLAT license_number (live-verified 2026-08-06 on Evo prod) */ },
  "blaze_payment_type": null,                     // live-observed 2026-08-06; not in Distru's Models doc
  "order_datetime": "<iso>",
  "delivery_datetime": "<iso>",
  "due_datetime": "<iso>",
  "inserted_datetime": "<iso>",
  "updated_datetime": "<iso>",
  "payment_term_name": "<string|null>",
  "internal_notes": "<string|null>",
  "external_notes": "<string|null>",              // NEW Phase 0.5 — not in Distru's Models doc
  "metrc_transfer_id": <integer|null>,            // INTEGER on Distru (not string)
  "biotrack_id": "<string|null>",
  "leaflink_order_number": "<string|null>",
  "total": "<decimal string>",
  "items": [ /* SalesOrderItem[] inline; 15 fields each */ ],
  "charges": [ /* Charge[] inline */ ],
  "custom_data": []
}
```

### SalesOrderItem (15 fields)

Includes: `id`, `product`, `batch`, `package`, `location` (NEW Phase 0.5), `quantity`, `compliance_quantity` (NEW), `price`, `price_base` (NEW, pre-discount), `returned_quantity`, **`cost_per_unit`** (NO `_actual` suffix — Distru naming inconsistency vs BatchFull/PackageFull), `cost_per_unit_default`, `total_cost_actual`, `total_cost_default`, `is_sample` (NEW boolean).

## Status enum (7 values — UPPERCASE in response field)

`PENDING`, `PROCESSING`, `READY_TO_SHIP`, `DELIVERING`, `DELIVERED`, `COMPLETED`, **`CANCELED`** (single L! `CANCELLED` with double L returns HTTP 400).

When status appears as `order.status` embedded inside an Invoice response, it's Title Case (`"Pending"`, `"Completed"`). Same conceptual field, different casing depending on context.

## Filter parameters

| Filter | Type | Example | Notes |
|---|---|---|---|
| `delivery_datetime` | comma-range string | `2024-01-01T00:00:00Z,` | |
| `due_datetime` | comma-range string | `,2024-02-01T00:00:00Z` | |
| `inserted_datetime` | comma-range string | | |
| `order_datetime` | comma-range string | `2024-01-01T00:00:00Z,2024-02-01T00:00:00Z` | |
| `updated_datetime` | comma-range string | | **Canonical incremental-sync filter.** |
| `status` | bracket array | `?status[]=COMPLETED&status[]=CANCELED` | Multi-value enum. NOTE: SINGULAR `status[]` (vs `/packages` which uses plural `statuses[]`). |
| `company_id` | string | `?company_id=<uuid>` | **Undocumented but works** — only in examples, not in formal Parameters table. |
| `page[number]` | integer | `?page[number]=1` | |

**`/orders` unfiltered TIMES OUT** at HTTP 500 (~20s) on high-volume orgs. Always include `updated_datetime` (or `order_datetime`) window for the importer. 7-day window can sometimes work; 1-3 days is more reliable.

## Invoice entity shape (17 top-level fields)

```jsonc
{
  "id": "<uuid>",
  "invoice_number": "INV-123",
  "status": "NOT_PAID",                           // 4-value enum; UPPERCASE in response
  "company": { /* embedded ref */ },
  "creator": { /* full User */ },
  "owner": { /* full User */ },
  "order": {                                       // REDUCED 4-field sub-object
    "id": "<uuid>",
    "order_number": "...",
    "status": "Pending",                          // Title Case here! Not UPPERCASE.
    "total": "..."
  },
  "invoice_datetime": "<iso>",
  "due_datetime": "<iso>",
  "inserted_datetime": "<iso>",
  "updated_datetime": "<iso>",
  "total": "<decimal>",
  "paid_amount": "<decimal>",                     // AGGREGATE — no per-payment detail
  "remaining_amount": "<decimal>",
  "items": [ /* InvoiceItem[]; 12 fields each */ ],
  "charges": [ /* Charge[] inline */ ],
  "custom_data": []
  // payments: NOT EXPOSED — write-only via POST /invoices/{id}/payments
}
```

### InvoiceItem (12 fields)

Includes: `id`, `product`, `batch`, `package`, **`order_item_id`** (back-link to source SalesOrderItem), `quantity`, `price`, `returned_quantity`, `cost_per_unit` (NO `_actual`), `cost_per_unit_default`, `total_cost_actual`, `total_cost_default`.

Lacks (vs SalesOrderItem): `location`, `is_sample`, `compliance_quantity`, `price_base`.

## Invoice status enum (Title Case INPUT → UPPERCASE_UNDERSCORE RESPONSE)

Filter requires Title Case; response returns UPPERCASE_UNDERSCORE — Distru transforms the value:

| Filter value (Title Case) | Response value (UPPERCASE_UNDERSCORE) |
|---|---|
| `Not Paid` | `NOT_PAID` |
| `Over Paid` | `OVER_PAID` |
| `Fully Paid` | `FULLY_PAID` |
| `Partially Paid` | `PARTIALLY_PAID` |

## Invoice filter parameters (8 — richest in API)

| Filter | Type | Notes |
|---|---|---|
| `inserted_datetime` | comma-range | |
| `invoice_datetime` | comma-range | |
| `due_datetime` | comma-range | |
| `updated_datetime` | comma-range | |
| `invoice_number` | string | **Substring match** — e.g. `?invoice_number=001` |
| `order_id[]` | bracket array | UUID array — invoices for specific orders |
| `status[]` | bracket array | Title Case values |
| `page[number]` | integer | |

## Payment write (POST /invoices/{id}/payments)

```php
$response = $api->post("/invoices/{$invoiceId}/payments", [
    'payment_method_id' => '<uuid>',                            // REQUIRED
    'amount' => 100.01,                                         // REQUIRED — decimal, rounds to 2dp
    'payment_datetime' => '2020-01-01T00:00:00.000000Z',        // REQUIRED
    'description' => 'Payment for invoice',                     // REQUIRED
    'quickbooks_deposit_account_id' => 'QBD-123',               // EITHER this OR _name (mutex)
    // OR
    'quickbooks_deposit_account_name' => 'QBD-NAME',
]);
```

QB account type for invoice payments must be **"Bank"** or **"Other Current Asset"**. Differs from purchase payments which require **"Bank"** or **"Credit Card"**.

If user's company is integrated with Quickbooks, ONE of `quickbooks_deposit_account_id` or `quickbooks_deposit_account_name` is required.

## Charges shape (Decision #13 in mapping doc)

```jsonc
{
  "id": "<uuid>",
  "name": "C1",
  "type": "CHARGE",                                  // or DISCOUNT
  "unit_type": "PERCENT",                            // or PRICE
  "percent": "10.0000",
  "price": "1.00",
  "tax": { "id": "...", "name": "...", "percent": "..." } | null
}
```

## Write Safety

- POST is **UPSERT** — same payload creates if new, updates if `id` is provided.
- **Non-sparse updates** — `items[]` and `charges[]` arrays must be complete. Omitting a line item or charge DELETES it.
- **No idempotency keys** — capture response `id` and reconcile on retry.
- For **Blaze-retailer** orders, `blaze_payment_type` is required (returns 400 `can't be blank` otherwise).
- For Metrc transfer creation inline with the order, supply `metrc_transfer_template_*` fields (directions, recipient_license_number, status, transporter_info[], type).

## Payment readability — IMPORTANT BLOCKER

**Payment history is NOT exposed via the API.** Even on a fully-paid invoice, the response includes only `paid_amount` and `remaining_amount` (aggregates), not the line-by-line payments. The Models page lists `payments: array(InvoicePayment)` on Invoice, but live responses never include this field. Distru only exposes `POST /invoices/{id}/payments` (write).

Migration implication: customers migrating from Distru lose all historical payment line-item detail unless they export it via a different path (Distru CSV export, support API access, etc.).

## Cross-references

- Customer/company lookup: `categories/crm.md`
- Product lookup for line items: `categories/products.md`
- Batch lookup for line items: `categories/inventory.md`
- Workflow: `scenarios/order-import-workflow.md`, `scenarios/order-writeback-workflow.md`
- Write semantics deep-dive: `patterns/write-safety.md`
- Filter conventions: `patterns/filtering.md`
