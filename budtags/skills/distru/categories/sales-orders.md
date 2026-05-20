# Sales Domain — Orders and Invoices

The Distru Sales domain covers customer-facing orders and their billing artifacts. Orders carry line items inline and progress through a status lifecycle; Invoices are derived from Orders and accept payment insertions via a special `op: "INSERT payment"` PUT shape.

## Endpoints

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/public/v1/orders` | List orders | Page-number pagination; filters via query string |
| GET | `/public/v1/orders/{id}` | Get one order | Line items, charges, custom fields all inline |
| POST | `/public/v1/orders` | Create order | UPSERT — line items provided inline |
| PUT | `/public/v1/orders/{id}` | Update order | UPSERT — partial updates allowed |
| GET | `/public/v1/invoices` | List invoices | Page-number pagination |
| GET | `/public/v1/invoices/{id}` | Get one invoice | Includes payments, linked order id |
| PUT | `/public/v1/invoices/{id}` | Update invoice / insert payment | Use `op: "INSERT payment"` to append a payment record |

## Order entity shape (high-level)

```jsonc
{
  "id": "ord_...",
  "order_number": "SO-1042",
  "status": "FULFILLED",
  "company_id": "co_...",
  "billing_location_id": "loc_...",
  "shipping_location_id": "loc_...",
  "line_items": [
    {
      "id": "oli_...",
      "product_id": "prd_...",
      "batch_id": "bat_...",
      "quantity": 12,
      "unit_price": 25.00,
      "subtotal": 300.00,
      "custom_fields": { /* ... */ }
    }
  ],
  "charges": [ { "label": "Delivery", "amount": 25.00 } ],
  "subtotal": 300.00,
  "total": 325.00,
  "due_datetime": "2026-06-01T00:00:00Z",
  "completion_datetime": null,
  "custom_fields": { /* ... */ },
  "created_at": "2026-05-15T19:42:01Z",
  "updated_at": "2026-05-16T11:08:33Z"
}
```

> **Note:** The exact field set is confirmed live via Phase B importer transcription. Treat the schema above as a starting reference and verify against actual API responses.

## Status lifecycle (observed)

Common transitions (verify per-tenant configuration):
```
DRAFT → CONFIRMED → FULFILLED → INVOICED → PAID → COMPLETED
                                     └────→ VOID
```

## Invoice payment insertion (special write shape)

```php
$response = $api->put("/invoices/{$invoiceId}", [
    'op' => 'INSERT payment',
    'payment' => [
        'amount' => 150.00,
        'method' => 'ACH',
        'reference' => 'wire-12345',
        'received_at' => '2026-05-16T15:00:00Z',
    ],
]);
```

This shape **does not replace** existing payments; it appends a new one. Other PUT requests update invoice fields directly.

## Filters (query-string)

| Param | Meaning |
|-------|---------|
| `updated_at_from`, `updated_at_to` | Incremental sync window (ISO 8601) |
| `status` | Status filter |
| `company_id` | Filter to a single customer |
| `page[number]`, `page[size]` | Pagination |

> Filter parameter names are **per-endpoint** — always verify against Distru docs for the specific resource.

## Write Safety

- POST and PUT are both **UPSERT**. A POST that includes an existing record's identifying fields may update rather than fail.
- **No idempotency keys** — capture the response `id` and reconcile on retry.
- Line items are **inline** — a PUT that omits a line item may delete it (treat as full replacement unless documented otherwise).

See `patterns/write-safety.md` for the full UPSERT discussion.

## Cross-references

- Customer/company lookup: `categories/crm.md`
- Product lookup for line items: `categories/products.md`
- Batch lookup for line items: `categories/inventory.md`
- Workflow: `scenarios/order-import-workflow.md`, `scenarios/order-writeback-workflow.md`
