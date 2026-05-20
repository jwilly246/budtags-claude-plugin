# Pattern — Write Safety

Distru's write surface is **UPSERT**. POST and PUT are semantically similar — POST creates by natural keys; PUT updates by `id`. There are **no documented idempotency keys**, so retry semantics are entirely the caller's responsibility.

## Write Matrix

| Resource | POST | PUT | DELETE | Notes |
|----------|------|-----|--------|-------|
| Orders | UPSERT | UPSERT | — | Line items inline; PUT may replace the line-items array |
| Invoices | — | UPSERT + `op: "INSERT payment"` | — | Payments are appended via `op` parameter |
| Purchases | UPSERT | UPSERT + `op: "INSERT payment"` | — | |
| Companies | UPSERT | UPSERT | — | |
| Contacts | UPSERT | UPSERT | — | Requires existing `company_id` |
| Products | UPSERT | UPSERT | — | |
| Test Results | UPSERT | UPSERT | — | |
| Batches | POST | (not documented) | — | |
| Packages | — | — | — | **Read-only** via public API |
| Stock Adjustments | POST | — | — | **Append-only** — corrections are new adjustments |
| Assemblies | — | — | — | **Read-only** via public API |
| Locations | UPSERT | UPSERT | — | |

DELETE is **not exposed** for any business resource via the public API.

## UPSERT Semantics

When you POST a resource that includes a natural-key match, Distru may **update the existing record** rather than fail with a conflict. Two implications:

1. POST is not strictly "create" — it cannot be relied on as a duplicate-detector.
2. If the caller intended to create-only, they must check for existing records first.

For Budtags importers, prefer PUT when you already know the id, and POST only for first-time creates after a deliberate existence check.

## No Idempotency Keys

A 5xx or network failure after a write leaves the caller in a state where:

- The write may have committed (and a duplicate retry would create a second record), OR
- The write may have not committed (and a retry is required).

**Recovery pattern**:

```php
try {
    $response = $api->post('/products', $payload);
    $productId = $response['data']['id'];
} catch (\Throwable $e) {
    // Re-fetch by natural key — SKU is the safest in this case
    $existing = $api->get('/products', ['sku' => $payload['sku']]);
    if (count($existing['data']) > 0) {
        // The write actually committed
        $productId = $existing['data'][0]['id'];
    } else {
        throw $e; // genuine failure — caller decides next step
    }
}
```

## Append-Only — Stock Adjustments

Stock Adjustments cannot be modified or deleted via the API. To "undo" an adjustment, **POST a counter-adjustment** with the opposite `delta`. Budtags should treat the adjustment ledger as immutable and reconcile by summing deltas.

## Payment Insertion

Invoices and Purchases accept a payment-append shape on PUT:

```php
$api->put("/invoices/{$invoiceId}", [
    'op' => 'INSERT payment',
    'payment' => [
        'amount' => 250.00,
        'method' => 'ACH',
        'reference' => 'wire-12345',
        'received_at' => '2026-05-16T15:00:00Z',
    ],
]);
```

This **does not replace** the payments array; it appends.

## Line-Item Semantics on PUT

It is not documented whether a PUT to `/orders/{id}` that omits a line item **deletes** that line item or **leaves it alone**. Safe default: **echo the full line-items array on every PUT**, including untouched lines. Verify with Distru support before relying on partial-update semantics.

## Cross-references

- Error handling and retries: `patterns/error-handling.md`
- Eventual consistency: `patterns/eventual-consistency.md`
