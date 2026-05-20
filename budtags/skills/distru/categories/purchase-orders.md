# Purchasing Domain — Purchases

The Distru Purchasing domain covers vendor-facing purchase orders. Structurally similar to Orders (line items inline, payment-insertion shape on PUT), but the counterparty Company is a vendor rather than a customer.

## Endpoints

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/public/v1/purchases` | List purchases | Page-number pagination |
| GET | `/public/v1/purchases/{id}` | Get one purchase | Line items, payments, custom fields inline |
| POST | `/public/v1/purchases` | Create purchase | UPSERT — line items inline |
| PUT | `/public/v1/purchases/{id}` | Update purchase / insert payment | Same `op: "INSERT payment"` shape as Invoices |

## Purchase entity shape (high-level)

```jsonc
{
  "id": "pur_...",
  "purchase_number": "PO-205",
  "status": "RECEIVED",
  "company_id": "co_...",      // vendor company
  "line_items": [
    {
      "id": "pli_...",
      "product_id": "prd_...",
      "batch_id": "bat_...",   // received-into batch
      "quantity": 50,
      "unit_cost": 12.50,
      "subtotal": 625.00
    }
  ],
  "payments": [
    { "amount": 625.00, "method": "ACH", "received_at": "..." }
  ],
  "subtotal": 625.00,
  "total": 625.00,
  "received_datetime": "2026-05-10T14:00:00Z",
  "custom_fields": { /* ... */ },
  "created_at": "...",
  "updated_at": "..."
}
```

## Status lifecycle (observed)

```
DRAFT → CONFIRMED → RECEIVED → PAID → COMPLETED
                          └────→ VOID
```

## Payment insertion shape

Same as Invoices — see `categories/sales-orders.md` for the canonical example. Substitute the URL for `/public/v1/purchases/{id}`.

## Filters (query-string)

| Param | Meaning |
|-------|---------|
| `updated_at_from`, `updated_at_to` | Incremental sync window |
| `status` | Status filter |
| `company_id` | Filter to a single vendor |

## Write Safety

- POST and PUT are both **UPSERT**.
- **No idempotency keys** — capture `id` and reconcile.
- Line items are inline — treat PUT as full replacement of the line-items array unless verified otherwise.

## Cross-references

- Vendor lookup: `categories/crm.md`
- Product/batch lookup: `categories/products.md`, `categories/inventory.md`
- Write semantics: `patterns/write-safety.md`
