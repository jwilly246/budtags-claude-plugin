# Purchasing Domain — Purchases

The Distru Purchasing domain covers supplier-facing purchase orders. Purchases follow a tight 5-value lifecycle and exhibit the same UPPERCASE-response casing convention as Invoices, but unlike Orders/Invoices the wire payload was markedly leaner at the 2026-05-26 probe — no creator/owner, no billing/shipping locations, no per-line cost columns. **Re-probed 2026-09-01 (Evo, 500 records): the payload has grown to 25 top-level keys** — see "2026-09-01 wire growth" below before trusting the 12-field shape.

**Phase 0.5 audited 2026-05-21.** **Re-probed against live API 2026-05-26 (563 records / 16,837 line items)** — that probe overturned several documented fields the original audit had wrong; see "Probe corrections" below.

Mapping doc: `/Users/budtags/Desktop/budtags/DISTRU-INTEGRATION-MAPPING.md`.

## Endpoints

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/public/v1/purchases` | List purchases | Page size 500. |
| GET | `/public/v1/purchases/{id}` | Get one purchase | Same 12-field shape as list. |
| POST | `/public/v1/purchases` | Create or update purchase | UPSERT. **Cannot edit status past `Pending`** (Distru server-side rule — returns HTTP 400 on attempt). |
| POST | `/public/v1/purchases/{id}/payments` | Insert payment | **WRITE-ONLY** — payment ledger not exposed via GET. |

### 2026-09-01 wire growth (live re-probe, Evo Pharms, 500 records)

The 12-field shape below is still correct for the keys it lists, but the wire now carries **25 top-level keys**. Newly present (all previously documented as absent): `creator` (500/500, full `DistruUser`), `owner` (495/500, `DistruUser`), `payments`, `billing_location`, `supplier_location`, `location`, `metrc_transfer_id`, `biotrack_id`, `qb_bill_id`, `paid`, `payment_status`, `description`, `tasks` (`[]`). Population of the non-user keys was not audited. Distru's changelog dates `owner` (full user object) on purchases to the 2026-07-29 parity pass and `tasks` to 2026-08-26; the 2026-09-01 spec snapshot lists 25 `Purchase` properties. Still absent: `shipping_location`, `purchase_datetime`, `delivery_datetime`, `completion_datetime`, `notes`. The endpoint table's "payment ledger not exposed via GET" claim needs re-checking now that a `payments` key is emitted.

## Purchase entity shape (12 top-level fields — all 563/563 records populate every field; SEE 2026-09-01 growth note above)

```jsonc
{
  "id": "<uuid>",
  "purchase_number": "PO-0000603",                 // human-readable, preserved on import
  "status": "COMPLETED",                            // 5-value enum, UPPERCASE in response
  "company": {                                      // SUPPLIER company — 3-field embed
    "id": "<uuid>",
    "name": "...",
    "updated_datetime": "..."
  },
  "order_datetime": "2026-05-22T15:58:20.656000Z", // ISO timestamp — when PO was placed
  "due_datetime":   "2026-05-30T15:58:20.000000Z", // ISO timestamp — expected receipt
  "inserted_datetime": "2026-05-22T15:58:20.000Z", // ISO timestamp — Distru record create
  "updated_datetime":  "2026-05-22T16:04:20.940Z", // ISO timestamp — incremental sync pivot
  "total": "10358.94",                              // signed decimal string
  "items":      [ /* PurchaseLineItem[] inline — 11 fields each */ ],
  "charges":    [ /* Charge[] inline — typically empty (~96.5% of records) */ ],
  "custom_data": []                                 // tenant custom fields
  // FIELDS THAT DID NOT EXIST on /purchases at the 2026-05-26 probe (see "Probe corrections"):
  //   creator, owner, payments, billing_location, shipping_location,
  //   purchase_datetime, delivery_datetime, completion_datetime, notes,
  //   metrc_transfer_id
  // 2026-09-01 CORRECTION: creator, owner, payments, billing_location and metrc_transfer_id
  //   ARE emitted now — see the wire-growth note above. Only shipping_location,
  //   purchase_datetime, delivery_datetime, completion_datetime and notes remain absent.
}
```

### PurchaseLineItem (11 fields — all 16,837/16,837 line items populate every field)

```jsonc
{
  "id": "<uuid>",
  "product": {                                     // 4-field embed
    "id": "<uuid>",
    "name": "LJA Holdings | Bulk | Trim",
    "sku":  "LJA-BUL-MTR",
    "updated_datetime": "..."
  },
  "batch": {                                       // 3-field embed (or null)
    "id": "<uuid>",
    "name": "B1",
    "batch_number": null
  },
  "package": {                                     // 5-field embed — includes metrc_label
    "id": "<uuid>",
    "metrc_label": "1A4050300029D89000020513",
    "compliance_label": "1A4050300029D89000020513",
    "batch_number": null,
    "status": "active"
  },
  "location": {                                    // 5-field embed — includes address
    "id": "<uuid>",
    "name": "Freezer",
    "address": "24247 Gibson Dr, Warren, MI 48089, US",
    "company_id": "<uuid>",
    "license_id": "<uuid>"
  },
  "quantity":            "100.000000000",          // 9-digit decimal precision
  "compliance_quantity": "100.0000",               // 4-digit precision when present
  "received_quantity":   "100.000000000",
  "price":      "12.34",                            // post-discount unit price
  "price_base": "15.00",                            // pre-discount unit price (Distru's MSRP alt)
  "is_sample":  false
  // NO cost fields — cost lives on the linked Batch/Package, NOT on PO line items.
  // NO returned_quantity — PO line items only ship received_quantity (returns happen
  //                         via separate adjustment, not as a PO line-item field).
}
```

## Status enum (5 values — Title Case INPUT → UPPERCASE RESPONSE)

| Filter value (Title Case) | Response value (UPPERCASE) |
|---|---|
| `Pending` | `PENDING` |
| `Partial` | `PARTIAL` |
| `Received` | `RECEIVED` |
| `Returned` | `RETURNED` |
| `Canceled` | `CANCELED` (single L!) |

Distru transforms the filter input to UPPERCASE in the response. The filter param `status[]` accepts the Title Case form only. In live data (563 records on the audit tenant): 559 COMPLETED, 4 PENDING — most POs land at COMPLETED quickly.

## Filter parameters

| Filter | Type | Notes |
|---|---|---|
| `due_datetime` | comma-range string | |
| `order_datetime` | comma-range string | |
| `inserted_datetime` | comma-range string | |
| `updated_datetime` | comma-range string | **Canonical incremental-sync filter.** |
| `status[]` | bracket array | Title Case values (`Pending`, `Received`, etc.) |
| `purchase_number` | string | Substring match |
| `page[number]` | integer | |

> **Removed filters** (claimed by docs but not verified against live API): `purchase_datetime`, `delivery_datetime`. The /purchases wire response doesn't include either as a top-level field — and Distru's silent-ignore-unknown-filter policy means a typo'd filter returns unfiltered data. Stick to the verified set above.

## Server-side immutability — IMPORTANT WRITE CONSTRAINT

**A purchase whose status has advanced past `Pending` cannot be edited.** Distru returns HTTP 400 with an error along the lines of `"Cannot edit a purchase that is not Pending"`. This breaks the typical "sync down → edit locally → write back" loop for received/returned/canceled purchases.

Migration implication: writeback to a Distru purchase only works while it's still `Pending`. Once received, the purchase is effectively frozen. Plan writeback to be staged at the `Pending` state only.

## Write safety

- POST is **UPSERT** — same payload creates if new, updates if `id` provided (and current status is `Pending`).
- **Non-sparse updates** — omitting items[] or charges[] from a PATCH-equivalent POST deletes them. Always send the complete current state.
- No idempotency keys — reconcile via response `id` capture on retry.
- For Metrc transfer creation inline with the purchase, `metrc_transfer_template_*` fields are accepted (same as on /orders).
- Like Orders/Invoices, payments are **write-only** via `POST /purchases/{id}/payments`.

## Payment write (POST /purchases/{id}/payments)

```php
$response = $api->post("/purchases/{$purchaseId}/payments", [
    'payment_method_id' => '<uuid>',                            // REQUIRED
    'amount' => 100.01,                                         // REQUIRED — decimal
    'payment_datetime' => '2020-01-01T00:00:00.000000Z',        // REQUIRED
    'description' => 'Payment for purchase',                    // REQUIRED
    'quickbooks_deposit_account_id' => 'QBD-123',               // EITHER this OR _name
    // OR
    'quickbooks_deposit_account_name' => 'QBD-NAME',
]);
```

**Differs from invoice payments**: QB account type for purchase payments must be **"Bank"** or **"Credit Card"** (NOT "Other Current Asset"). Distru enforces this server-side.

## Cross-references

- Vendor/company lookup: `categories/crm.md`
- Product/batch lookup: `categories/products.md`, `categories/inventory.md`
- Inventory consequence (received purchases create batches/packages): `scenarios/order-import-workflow.md`
- Write semantics deep-dive: `patterns/write-safety.md`
- Filter conventions: `patterns/filtering.md`
